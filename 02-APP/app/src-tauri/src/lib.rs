//! Rx7 — one shell for the desktop and the phone.
//!
//! On the desktop the shell is the app's hands: it runs `tools/rx7.py` to read the record and
//! to save Camden's answers, `git` to keep the tree in step with GitHub, and Claude Code for
//! every run and chat. On the phone it only lends the web view its network and storage: the
//! phone reads the record through the same rx7.py, running inside the app (src/lib/platform).
//! On both it lends Bluetooth LE (tauri-plugin-blec, D-495) and a folder for the logs pulled
//! from the car (logs.rs, BL2/BL3).

#[cfg(desktop)]
mod desktop;
pub mod logs;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let builder = tauri::Builder::default()
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_store::Builder::default().build());
    // A machine with no Bluetooth adapter (or BlueZ not running) still opens the app: the Scan
    // page and Connect and log then say Bluetooth is unavailable.
    let builder = match tauri_plugin_blec::try_init() {
        Ok(plugin) => builder.plugin(plugin),
        Err(e) => {
            eprintln!("Bluetooth unavailable: {e:?}");
            builder
        }
    };
    #[cfg(desktop)]
    let builder = desktop::install(builder);
    #[cfg(mobile)]
    let builder = builder.invoke_handler(tauri::generate_handler![
        logs::logs_root,
        logs::logs_write,
        logs::logs_read,
        logs::logs_size,
        logs::logs_list,
    ]);
    builder
        .run(tauri::generate_context!())
        .expect("Rx7 could not start");
}
