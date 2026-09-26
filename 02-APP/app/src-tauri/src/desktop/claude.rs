//! Claude Code, headless, in the tree (D-406). A run follows CLAUDE.md with write access to
//! the record and git; a chat (Explain, Discuss, the chat panel) can only read. Every line
//! Claude Code prints (stream-json) is passed to the window as it comes, untouched.

use super::{tool, Tree};
use serde::Deserialize;
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

/// The read-only commands a chat may run. CLAUDE.md writes `python`, this machine has
/// `python3`, and the model types either: both spellings are allowed (plan P13).
const READ_COMMANDS: &[&str] = &[
    "get", "sql", "find", "status", "tables", "blocks", "inbox", "picks", "cites", "selftest", "export --out",
];

fn read_tools() -> Vec<String> {
    let mut t: Vec<String> = ["Read", "Glob", "Grep"].map(String::from).to_vec();
    for c in READ_COMMANDS {
        t.push(format!("Bash(python3 tools/rx7.py {c}:*)"));
        t.push(format!("Bash(python tools/rx7.py {c}:*)"));
    }
    t
}

/// What the window chose for this process (plan P06): the model and effort per kind of run,
/// a spending cap, a fallback when the model is unavailable, and whether the session is kept.
#[derive(Deserialize, Default, Clone)]
pub struct RunOpts {
    pub model: Option<String>,
    pub effort: Option<String>,
    pub budget: Option<f64>,
    pub fallback: Option<String>,
    pub persist: Option<bool>,
}

fn args(mode: &str, prompt: &str, session: Option<&str>, opts: &RunOpts) -> Vec<String> {
    let mut a: Vec<String> = ["-p", prompt, "--output-format", "stream-json", "--verbose", "--include-partial-messages"]
        .iter()
        .map(|s| s.to_string())
        .collect();
    if mode == "run" {
        a.extend(["--permission-mode", "acceptEdits", "--allowedTools"].map(String::from));
        a.extend(RUN_TOOLS.iter().map(|s| s.to_string()));
    } else {
        a.push("--allowedTools".into());
        a.extend(read_tools());
        a.extend(["--disallowedTools", "Edit", "Write", "NotebookEdit"].map(String::from));
    }
    let model = opts.model.clone().filter(|m| !m.is_empty()).or_else(|| (mode != "run").then(|| "sonnet".to_string()));
    if let Some(m) = model {
        a.extend(["--model".to_string(), m]);
    }
    if let Some(e) = opts.effort.as_deref().filter(|e| !e.is_empty()) {
        a.extend(["--effort".to_string(), e.to_string()]);
    }
    if let Some(b) = opts.budget.filter(|b| *b > 0.0) {
        a.extend(["--max-budget-usd".to_string(), format!("{b}")]);
    }
    if let Some(f) = opts.fallback.as_deref().filter(|f| !f.is_empty()) {
        a.extend(["--fallback-model".to_string(), f.to_string()]);
    }
    if opts.persist == Some(false) && session.filter(|s| !s.is_empty()).is_none() {
        a.push("--no-session-persistence".into());
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
    opts: Option<RunOpts>,
) -> Result<String, String> {
    if id.is_empty() || !id.chars().all(|c| c.is_ascii_alphanumeric() || c == '-') {
        return Err("a run id is letters, digits and -".into());
    }
    let opts = opts.unwrap_or_default();
    let mut child = Command::new(tool("claude"))
        .args(args(&mode, &prompt, session.as_deref(), &opts))
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
