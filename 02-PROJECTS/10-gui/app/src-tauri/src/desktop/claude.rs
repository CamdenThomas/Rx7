//! Claude Code, headless, in the tree (D-406). A run follows CLAUDE.md with write access to
//! the record and git; a chat (Explain, Discuss, the chat panel) can only read. Every line
//! Claude Code prints (stream-json) is passed to the window as it comes, untouched.

use super::{tool, Tree};
use serde_json::json;
use std::collections::HashMap;
use std::io::{BufRead, BufReader};
use std::process::{Child, Command, Stdio};
use std::sync::{Arc, Mutex};
use tauri::{AppHandle, Emitter, State};

#[derive(Default)]
pub struct Runs(Arc<Mutex<HashMap<String, Child>>>);

impl Runs {
    /// Whether any Claude Code process — a run or a chat — is alive in the tree.
    pub fn live(&self) -> bool {
        self.0.lock().map(|t| !t.is_empty()).unwrap_or(true)
    }
}

const RUN_TOOLS: &[&str] = &[
    "Read", "Edit", "Write", "Glob", "Grep",
    "Bash(python3 tools/rx7.py:*)", "Bash(python tools/rx7.py:*)", "Bash(git:*)",
];

const READ_TOOLS: &[&str] = &[
    "Read", "Glob", "Grep",
    "Bash(python3 tools/rx7.py get:*)", "Bash(python3 tools/rx7.py sql:*)",
    "Bash(python3 tools/rx7.py find:*)", "Bash(python3 tools/rx7.py status:*)",
    "Bash(python3 tools/rx7.py tables:*)", "Bash(python3 tools/rx7.py blocks:*)",
    "Bash(python3 tools/rx7.py inbox:*)", "Bash(python3 tools/rx7.py picks:*)",
];

fn args(mode: &str, prompt: &str, session: Option<&str>) -> Vec<String> {
    let mut a: Vec<String> = ["-p", prompt, "--output-format", "stream-json", "--verbose", "--include-partial-messages"]
        .iter()
        .map(|s| s.to_string())
        .collect();
    if mode == "run" {
        a.extend(["--permission-mode", "acceptEdits", "--allowedTools"].map(String::from));
        a.extend(RUN_TOOLS.iter().map(|s| s.to_string()));
    } else {
        a.extend(["--model", "sonnet", "--allowedTools"].map(String::from));
        a.extend(READ_TOOLS.iter().map(|s| s.to_string()));
        a.extend(["--disallowedTools", "Edit", "Write", "NotebookEdit"].map(String::from));
    }
    if let Some(s) = session.filter(|s| !s.is_empty()) {
        a.extend(["--resume".to_string(), s.to_string()]);
    }
    a
}

/// Start Claude Code under the id the window chose (so it listens before the first line);
/// its output arrives as `claude:<id>` events, one JSON line each, ending with
/// `{"type":"exit","code":…}`.
#[tauri::command]
pub fn claude_start(
    app: AppHandle,
    tree: State<Tree>,
    runs: State<Runs>,
    id: String,
    mode: String,
    prompt: String,
    session: Option<String>,
) -> Result<String, String> {
    if id.is_empty() || !id.chars().all(|c| c.is_ascii_alphanumeric() || c == '-') {
        return Err("a run id is letters, digits and -".into());
    }
    let mut child = Command::new(tool("claude"))
        .args(args(&mode, &prompt, session.as_deref()))
        .current_dir(tree.root())
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Claude Code could not start: {e}"))?;
    let stdout = child.stdout.take().ok_or("no output from Claude Code")?;
    let stderr = child.stderr.take();
    runs.0.lock().map_err(|e| e.to_string())?.insert(id.clone(), child);

    let event = format!("claude:{id}");
    if let Some(err) = stderr {
        let (app, event) = (app.clone(), event.clone());
        std::thread::spawn(move || {
            for line in BufReader::new(err).lines().map_while(Result::ok) {
                let _ = app.emit(&event, json!({"type": "stderr", "text": line}).to_string());
            }
        });
    }
    let (table, key) = (runs.0.clone(), id.clone());
    std::thread::spawn(move || {
        for line in BufReader::new(stdout).lines().map_while(Result::ok) {
            let _ = app.emit(&event, line);
        }
        let code = table
            .lock()
            .ok()
            .and_then(|mut t| t.remove(&key))
            .and_then(|mut c| c.wait().ok())
            .and_then(|s| s.code());
        let _ = app.emit(&event, json!({"type": "exit", "code": code}).to_string());
    });
    Ok(id)
}

#[tauri::command]
pub fn claude_stop(runs: State<Runs>, id: String) -> Result<(), String> {
    if let Some(child) = runs.0.lock().map_err(|e| e.to_string())?.get_mut(&id) {
        child.kill().map_err(|e| e.to_string())?;
    }
    Ok(())
}
