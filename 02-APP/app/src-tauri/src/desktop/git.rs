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
use std::sync::Mutex;
use tauri::{AppHandle, Emitter, Manager, State};

/// One git operation at a time in this tree (plan P10). Four answers saved in five seconds
/// once ran four commits and four pull-and-push threads against the same index.
static GIT: Mutex<()> = Mutex::new(());

fn hold() -> std::sync::MutexGuard<'static, ()> {
    GIT.lock().unwrap_or_else(|e| e.into_inner())
}

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

/// Fetch, bring the branch up to date, push what is ours. Never over someone's edits: with
/// changes in the tree that are not committed (a terminal session at work), the merge or
/// rebase waits and the state says so; a rebase that fails is aborted, never left half done.
fn pull_and_push(root: &Path) -> SyncState {
    let _g = hold();
    if let Err(e) = git(root, &["fetch", "--quiet", "origin"]) {
        return SyncState { error: Some(e), ..state(root) };
    }
    let s = state(root);
    let pulled = match (s.ahead, s.behind, s.dirty) {
        (_, 0, _) => Ok(String::new()),
        (_, _, d) if d > 0 => Err("The tree has changes that are not committed - someone is working in it. Sync waits.".to_string()),
        (0, _, _) => git(root, &["merge", "--ff-only", "--quiet", "@{u}"]),
        _ => git(root, &["pull", "--rebase", "--quiet"]).map_err(|e| {
            let _ = git(root, &["rebase", "--abort"]);
            e
        }),
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
    let held = runs.live();
    tauri::async_runtime::spawn_blocking(move || {
        if held {
            SyncState { online: true, ..state(&root) }
        } else {
            pull_and_push(&root)
        }
    })
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
    let _g = hold();
    git(root, &["add", "--", path])?;
    git(root, &["commit", "--quiet", "-m", message, "--only", "--", path]).map(|_| ())
}

/// Files changed in the tree and not committed - zero means nobody is mid-edit.
pub fn dirty(root: &Path) -> u32 {
    git(root, &["status", "--porcelain"]).map(|o| o.lines().count() as u32).unwrap_or(0)
}

/// Commit every change under the record's data folders as one commit (what `rx7.py apply`
/// wrote). The hook still runs. Only called when the tree was clean before the apply, so
/// nothing of anyone else's can ride along.
pub fn commit_data(root: &Path, message: &str) -> Result<(), String> {
    let _g = hold();
    git(root, &["add", "-A", "--", "00-CAR/data", "01-REFERENCE/data", "02-APP/data", "02-PROJECTS"])?;
    git(root, &["commit", "--quiet", "-m", message]).map(|_| ())
}

/// Push after a commit without holding the window; the app hears how it went.
pub fn push_in_background(app: AppHandle, root: PathBuf) {
    std::thread::spawn(move || {
        let s = if app.state::<Runs>().live() { SyncState { online: true, ..state(&root) } } else { pull_and_push(&root) };
        let _ = app.emit("sync", s);
    });
}
