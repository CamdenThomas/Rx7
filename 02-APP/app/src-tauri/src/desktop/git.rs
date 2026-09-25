//! Keeping the tree in step with GitHub, where the phone reads and writes (D-403).
//!
//! Pulling never risks work in progress: with nothing of ours unpushed it is a fast-forward,
//! which git refuses if it would touch a file being edited; with commits on both sides it
//! rebases with the working tree stashed and restored. Nothing here force-pushes, amends or
//! resets (CLAUDE.md §6.10).
//!
//! While Claude Code is at work in the tree, the app never pulls or pushes: a rebase under a
//! run would stash and restore the files it is editing. An answer saved meanwhile is still
//! committed at once; the run's own push carries it, or the sync after the run does.

use super::{claude::Runs, tool, Tree};
use serde::Serialize;
use std::path::{Path, PathBuf};
use std::process::Command;
use tauri::{AppHandle, Emitter, Manager, State};

#[derive(Serialize, Clone, Default)]
pub struct SyncState {
    branch: String,
    ahead: u32,
    behind: u32,
    dirty: u32,
    online: bool,
    error: Option<String>,
}

#[derive(Serialize)]
pub struct Commit {
    hash: String,
    subject: String,
    date: String,
    author: String,
}

fn git(root: &Path, args: &[&str]) -> Result<String, String> {
    let out = Command::new(tool("git"))
        .args(args)
        .current_dir(root)
        .env("GIT_TERMINAL_PROMPT", "0")
        .output()
        .map_err(|e| e.to_string())?;
    if out.status.success() {
        Ok(String::from_utf8_lossy(&out.stdout).trim_end().to_string())
    } else {
        let mut why = String::from_utf8_lossy(&out.stderr).trim().to_string();
        if why.is_empty() {
            why = String::from_utf8_lossy(&out.stdout).trim().to_string();
        }
        Err(why)
    }
}

fn state(root: &Path) -> SyncState {
    let mut s = SyncState { branch: git(root, &["rev-parse", "--abbrev-ref", "HEAD"]).unwrap_or_default(), ..Default::default() };
    if let Ok(counts) = git(root, &["rev-list", "--left-right", "--count", "HEAD...@{u}"]) {
        let mut it = counts.split_whitespace().filter_map(|n| n.parse().ok());
        s.ahead = it.next().unwrap_or(0);
        s.behind = it.next().unwrap_or(0);
    }
    s.dirty = git(root, &["status", "--porcelain"]).map(|o| o.lines().count() as u32).unwrap_or(0);
    s
}

fn pull_and_push(root: &Path) -> SyncState {
    if let Err(e) = git(root, &["fetch", "--quiet", "origin"]) {
        return SyncState { error: Some(e), ..state(root) };
    }
    let mut s = state(root);
    s.online = true;
    let pulled = match (s.ahead, s.behind) {
        (_, 0) => Ok(String::new()),
        (0, _) => git(root, &["merge", "--ff-only", "--quiet", "@{u}"]),
        _ => git(root, &["pull", "--rebase", "--autostash", "--quiet"]),
    };
    let pushed = pulled.and_then(|_| {
        if state(root).ahead > 0 {
            git(root, &["push", "--quiet"])
        } else {
            Ok(String::new())
        }
    });
    SyncState { online: true, error: pushed.err(), ..state(root) }
}

#[tauri::command]
pub async fn sync_state(tree: State<'_, Tree>) -> Result<SyncState, String> {
    let root = tree.root();
    tauri::async_runtime::spawn_blocking(move || state(&root)).await.map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn sync(tree: State<'_, Tree>, runs: State<'_, Runs>) -> Result<SyncState, String> {
    let root = tree.root();
    let hold = runs.live();
    tauri::async_runtime::spawn_blocking(move || if hold { state(&root) } else { pull_and_push(&root) })
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn git_log(tree: State<'_, Tree>, path: Option<String>, n: Option<u32>) -> Result<Vec<Commit>, String> {
    let root = tree.root();
    tauri::async_runtime::spawn_blocking(move || {
        let limit = format!("-{}", n.unwrap_or(20));
        let mut args = vec!["log", limit.as_str(), "--format=%h%x1f%s%x1f%cI%x1f%an"];
        if let Some(p) = path.as_deref() {
            args.extend(["--", p]);
        }
        let out = git(&root, &args)?;
        Ok(out
            .lines()
            .filter_map(|l| {
                let f: Vec<&str> = l.split('\u{1f}').collect();
                (f.len() == 4).then(|| Commit {
                    hash: f[0].into(),
                    subject: f[1].into(),
                    date: f[2].into(),
                    author: f[3].into(),
                })
            })
            .collect())
    })
    .await
    .map_err(|e| e.to_string())?
}

/// Commit one path and nothing else, whatever else is staged. The pre-commit hook still
/// runs: if it refuses, the reason comes back and the file stays saved on disk.
pub fn commit_path(root: &Path, path: &str, message: &str) -> Result<(), String> {
    git(root, &["add", "--", path])?;
    git(root, &["commit", "--quiet", "-m", message, "--only", "--", path]).map(|_| ())
}

/// Push after a commit without holding the window; the app hears how it went.
pub fn push_in_background(app: AppHandle, root: PathBuf) {
    std::thread::spawn(move || {
        let s = if app.state::<Runs>().live() { state(&root) } else { pull_and_push(&root) };
        let _ = app.emit("sync", s);
    });
}
