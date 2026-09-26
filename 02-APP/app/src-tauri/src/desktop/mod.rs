//! The desktop's hands. Every fact comes from the tree through `tools/rx7.py`; this module
//! only runs programs and passes their output on. It never parses the record itself (R9).

mod claude;
mod git;
mod photos;
mod record;

use std::env;
use std::path::PathBuf;
use std::sync::Mutex;

/// The tree the app works on — `~/docs/storage/Rx7` unless the app is pointed elsewhere.
pub struct Tree(pub Mutex<PathBuf>);

impl Default for Tree {
    fn default() -> Self {
        let home = env::var_os("HOME").map(PathBuf::from).unwrap_or_default();
        Tree(Mutex::new(home.join("docs/storage/Rx7")))
    }
}

impl Tree {
    pub fn root(&self) -> PathBuf {
        self.0.lock().expect("tree lock").clone()
    }
}

/// A program by name, found even when the app was started from a launcher whose PATH
/// does not include `~/.local/bin` (where Claude Code lives).
pub fn tool(name: &str) -> PathBuf {
    let home = env::var_os("HOME").map(PathBuf::from).unwrap_or_default();
    let mut dirs: Vec<PathBuf> = env::var_os("PATH")
        .map(|p| env::split_paths(&p).collect())
        .unwrap_or_default();
    dirs.extend([home.join(".local/bin"), "/usr/local/bin".into(), "/usr/bin".into()]);
    dirs.into_iter()
        .map(|d| d.join(name))
        .find(|p| p.is_file())
        .unwrap_or_else(|| PathBuf::from(name))
}

pub fn install(builder: tauri::Builder<tauri::Wry>) -> tauri::Builder<tauri::Wry> {
    builder
        .manage(Tree::default())
        .manage(claude::Runs::default())
        .register_uri_scheme_protocol("photo", photos::serve)
        .invoke_handler(tauri::generate_handler![
            record::tree_root,
            record::set_tree_root,
            record::record_export,
            record::record_cached,
            record::record_fingerprint,
            record::answer_save,
            record::answer_withdraw,
            record::record_apply,
            git::sync_state,
            git::sync,
            git::git_log,
            claude::claude_start,
            claude::claude_stop,
        ])
}
