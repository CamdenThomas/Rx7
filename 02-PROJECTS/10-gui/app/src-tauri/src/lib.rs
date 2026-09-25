//! Rx7 — one shell for the desktop and the phone.
//!
//! On the desktop the shell is the app's hands: it runs `tools/rx7.py` to read the record and
//! to save Camden's answers, `git` to keep the tree in step with GitHub, and Claude Code for
//! every run and chat. On the phone it only lends the web view its network and storage: the
//! phone reads the record through the same rx7.py, running inside the app (src/lib/platform).

#[cfg(desktop)]
mod desktop;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let builder = tauri::Builder::default()
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_store::Builder::default().build());
    #[cfg(desktop)]
    let builder = desktop::install(builder);
    builder
        .run(tauri::generate_context!())
        .expect("Rx7 could not start");
}
