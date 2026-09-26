//! The record, through `tools/rx7.py`: `export` to read it, `answer` to save one of Camden's
//! answers, `del … inbox` to withdraw one. Each saved answer is committed on its own and
//! pushed in the background, so his phone sees it too.

use super::{git, tool, Tree};
use serde::Serialize;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::time::{SystemTime, UNIX_EPOCH};
use tauri::{AppHandle, Manager, State};

fn rx7(root: &Path) -> Command {
    let mut c = Command::new(tool("python3"));
    c.arg(root.join("tools/rx7.py")).current_dir(root);
    c
}

fn said(out: &Output) -> String {
    let mut s = String::from_utf8_lossy(&out.stdout).trim().to_string();
    let err = String::from_utf8_lossy(&out.stderr);
    if !err.trim().is_empty() {
        s = format!("{s}\n{}", err.trim()).trim().to_string();
    }
    s
}

async fn blocking<T: Send + 'static>(f: impl FnOnce() -> T + Send + 'static) -> Result<T, String> {
    tauri::async_runtime::spawn_blocking(f).await.map_err(|e| e.to_string())
}

/// A scratch file for text that must reach rx7.py byte for byte (his words never pass
/// through a command line).
struct Scratch(PathBuf);

impl Scratch {
    fn new(text: &str) -> Result<Self, String> {
        let stamp = SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_nanos()).unwrap_or(0);
        let p = std::env::temp_dir().join(format!("rx7-answer-{}-{stamp}.txt", std::process::id()));
        fs::write(&p, text).map_err(|e| e.to_string())?;
        Ok(Scratch(p))
    }
}

impl Drop for Scratch {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.0);
    }
}

#[tauri::command]
pub fn tree_root(tree: State<Tree>) -> String {
    tree.root().display().to_string()
}

#[tauri::command]
pub fn set_tree_root(tree: State<Tree>, path: String) -> Result<String, String> {
    let p = PathBuf::from(&path);
    if !p.join("tools/rx7.py").is_file() {
        return Err(format!("{path} is not an Rx7 tree (no tools/rx7.py)"));
    }
    *tree.0.lock().map_err(|e| e.to_string())? = p;
    Ok(path)
}

/// The whole record as rx7.py exports it. An invalid record (rc 1) is still shown — the
/// app says so; only a crash in the tool (rc 3) is an error here.
#[tauri::command]
pub async fn record_export(app: AppHandle, tree: State<'_, Tree>) -> Result<String, String> {
    let root = tree.root();
    let cache = cache_path(&app);
    blocking(move || {
        let out = rx7(&root).args(["export", "--stdout"]).output().map_err(|e| e.to_string())?;
        match out.status.code() {
            Some(0) | Some(1) => {
                let text = String::from_utf8(out.stdout).map_err(|e| e.to_string())?;
                // The last export is kept in the app's own data folder, so the next launch
                // shows the record at once while the fresh one loads (plan P32). Never in
                // the tree, never a fact of its own: it is a copy of what export said.
                if let Some(p) = cache {
                    if let Some(dir) = p.parent() {
                        let _ = fs::create_dir_all(dir);
                    }
                    let tmp = p.with_extension("json.tmp");
                    if fs::write(&tmp, &text).is_ok() {
                        let _ = fs::rename(&tmp, &p);
                    }
                }
                Ok(text)
            }
            _ => Err(said(&out)),
        }
    })
    .await?
}

fn cache_path(app: &AppHandle) -> Option<PathBuf> {
    app.path().app_data_dir().ok().map(|d| d.join("export.json"))
}

/// The last export this desktop saw, or an empty string when there is none yet.
#[tauri::command]
pub async fn record_cached(app: AppHandle) -> Result<String, String> {
    let p = cache_path(&app);
    blocking(move || Ok(p.and_then(|p| fs::read_to_string(p).ok()).unwrap_or_default())).await?
}

#[derive(Serialize)]
pub struct Saved {
    path: String,
    committed: bool,
    note: String,
}

#[tauri::command]
#[allow(clippy::too_many_arguments)]
pub async fn answer_save(
    app: AppHandle,
    tree: State<'_, Tree>,
    area: String,
    target: String,
    kind: Option<String>,
    choice: String,
    text: String,
    context: String,
    at: String,
) -> Result<Saved, String> {
    let root = tree.root();
    blocking(move || {
        let words = Scratch::new(&text)?;
        let notes = Scratch::new(&context)?;
        let mut c = rx7(&root);
        // --replace: the window only offers Change on a target he already answered, and the
        // tool carries his earlier choice and words into context (R3, plan P18).
        c.args(["answer", &area, &target, "--device", "desktop", "--at", &at, "--replace"]);
        c.arg("--text-file").arg(&words.0).arg("--context-file").arg(&notes.0);
        if !choice.trim().is_empty() {
            c.args(["--choice", choice.trim()]);
        }
        if let Some(k) = kind.filter(|k| !k.is_empty()) {
            c.args(["--kind", &k]);
        }
        let out = c.output().map_err(|e| e.to_string())?;
        if !out.status.success() {
            return Err(said(&out));
        }
        let path = format!("{}/data/inbox/{target}~desktop.csv", area_path(&root, &area)?);
        let message = format!("Camden answered {target} (desktop)");
        commit(app, root, path, message)
    })
    .await?
}

#[derive(Serialize)]
pub struct Applied {
    /// rx7.py apply's exit code: 0 = nothing left in this inbox, 2 = some answers wait for a run.
    rc: i32,
    said: String,
    committed: bool,
}

/// Apply the answers with one right answer by rule (`rx7.py apply -p AREA`, plan P07): work
/// ticks, values and choices with no words, and drives. What it wrote is committed as one
/// commit and pushed. Refuses when the tree has uncommitted changes (someone is working in
/// it), so nothing of theirs is swept into the commit. Branches on the exit code only (R9).
#[tauri::command]
pub async fn record_apply(app: AppHandle, tree: State<'_, Tree>, area: String) -> Result<Applied, String> {
    let root = tree.root();
    blocking(move || {
        if git::dirty(&root) > 0 {
            return Err("The tree has changes that are not committed - someone is working in it. Apply waits.".into());
        }
        let out = rx7(&root).args(["apply", "-p", &area]).output().map_err(|e| e.to_string())?;
        let rc = out.status.code().unwrap_or(3);
        let text = said(&out);
        if rc != 0 && rc != 2 {
            return Err(text);
        }
        let mut committed = false;
        if git::dirty(&root) > 0 {
            let message = format!("Applied his answers by rule (rx7.py apply, {area})");
            committed = git::commit_data(&root, &message).is_ok();
            if committed {
                git::push_in_background(app, root.clone());
            }
        }
        Ok(Applied { rc, said: text, committed })
    })
    .await?
}

#[tauri::command]
pub async fn answer_withdraw(
    app: AppHandle,
    tree: State<'_, Tree>,
    area: String,
    id: String,
) -> Result<Saved, String> {
    let root = tree.root();
    blocking(move || {
        let out = rx7(&root).args(["del", &area, "inbox", &id]).output().map_err(|e| e.to_string())?;
        if !out.status.success() {
            return Err(said(&out));
        }
        let path = format!("{}/data/inbox/{id}.csv", area_path(&root, &area)?);
        let target = id.rsplit_once('~').map(|(t, _)| t).unwrap_or(&id).to_string();
        commit(app, root, path, format!("Camden withdrew his answer to {target} (desktop)"))
    })
    .await?
}

/// Commit exactly one inbox file and push in the background. A refused commit (the hook
/// found the tree invalid, often mid-edit) still leaves his answer saved on disk: it is
/// committed with the next one, and nothing he typed is lost.
fn commit(app: AppHandle, root: PathBuf, path: String, message: String) -> Result<Saved, String> {
    match git::commit_path(&root, &path, &message) {
        Ok(()) => {
            git::push_in_background(app, root);
            Ok(Saved { path, committed: true, note: String::new() })
        }
        Err(why) => Ok(Saved { path, committed: false, note: why }),
    }
}

/// `02-PROJECTS/01-electrical` for `01-electrical`, the way rx7.py names areas.
fn area_path(root: &Path, area: &str) -> Result<String, String> {
    for base in [root.to_path_buf(), root.join("02-PROJECTS")] {
        let p = base.join(area);
        if p.join("data/_tables.csv").is_file() {
            return Ok(p.strip_prefix(root).unwrap_or(&p).display().to_string());
        }
    }
    Err(format!("no area named {area}"))
}
