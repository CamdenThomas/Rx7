//! The pulled logs on this device (02-APP BL2, BL3; electrical log_files LF01-LF05).
//!
//! Connect and log pulls each drive's files from the ICU over Bluetooth; the protocol, the
//! decoding and the pipeline are TypeScript (src/lib/logs). This module is only their disk:
//! `app_data_dir()/logs/<seq>/` with the sequence as eight zero-padded digits, as on the card
//! (LF01). Out of git, out of the tree: the raw logs stay on the device that pulled them until
//! a second home is named (D-478, 02-APP P55).
//!
//! The names are fixed - the three tier files and the pipeline's digest - so nothing written
//! from the web view can leave this folder. A tier file only ever grows by appending at its
//! current end, or is cut back (a CRC that did not match starts the tier again).

use std::fs::{self, OpenOptions};
use std::io::{Seek, SeekFrom, Write};
use std::path::PathBuf;

use tauri::{ipc::Response, AppHandle, Manager};

const NAMES: [&str; 4] = ["summary.bin", "thin.bin", "full.bin", "digest.json"];

fn root(app: &AppHandle) -> Result<PathBuf, String> {
    app.path()
        .app_data_dir()
        .map(|d| d.join("logs"))
        .map_err(|e| format!("no app data folder: {e}"))
}

fn file(app: &AppHandle, seq: u32, name: &str) -> Result<PathBuf, String> {
    if !NAMES.contains(&name) {
        return Err(format!("{name} is not a log file"));
    }
    Ok(root(app)?.join(format!("{seq:08}")).join(name))
}

async fn blocking<T: Send + 'static>(f: impl FnOnce() -> Result<T, String> + Send + 'static) -> Result<T, String> {
    tauri::async_runtime::spawn_blocking(f).await.map_err(|e| e.to_string())?
}

/// Where the logs live on this device, for the screen to say.
#[tauri::command]
pub fn logs_root(app: AppHandle) -> Result<String, String> {
    Ok(root(&app)?.to_string_lossy().into_owned())
}

/// Write `data` at `offset` and cut the file there: an append at the end, or a rewrite from
/// an earlier offset. An offset past the end is refused - the file never has a gap.
#[tauri::command]
pub async fn logs_write(app: AppHandle, seq: u32, name: String, offset: u64, data: Vec<u8>) -> Result<u64, String> {
    let p = file(&app, seq, &name)?;
    blocking(move || {
        if let Some(d) = p.parent() {
            fs::create_dir_all(d).map_err(|e| e.to_string())?;
        }
        let mut f = OpenOptions::new().create(true).truncate(false).read(true).write(true).open(&p).map_err(|e| e.to_string())?;
        let len = f.metadata().map_err(|e| e.to_string())?.len();
        if offset > len {
            return Err(format!("{name} of drive {seq} holds {len} bytes; a write at {offset} would leave a gap"));
        }
        f.set_len(offset).map_err(|e| e.to_string())?;
        f.seek(SeekFrom::Start(offset)).map_err(|e| e.to_string())?;
        f.write_all(&data).map_err(|e| e.to_string())?;
        f.sync_data().map_err(|e| e.to_string())?;
        Ok(offset + data.len() as u64)
    })
    .await
}

/// The whole file, or nothing when it does not exist.
#[tauri::command]
pub async fn logs_read(app: AppHandle, seq: u32, name: String) -> Result<Response, String> {
    let p = file(&app, seq, &name)?;
    blocking(move || Ok(Response::new(fs::read(&p).unwrap_or_default()))).await
}

/// The file's length, 0 when it does not exist.
#[tauri::command]
pub async fn logs_size(app: AppHandle, seq: u32, name: String) -> Result<u64, String> {
    let p = file(&app, seq, &name)?;
    blocking(move || Ok(fs::metadata(&p).map(|m| m.len()).unwrap_or(0))).await
}

/// Every drive folder held, by sequence.
#[tauri::command]
pub async fn logs_list(app: AppHandle) -> Result<Vec<u32>, String> {
    let r = root(&app)?;
    blocking(move || {
        let mut out: Vec<u32> = fs::read_dir(&r)
            .map(|rd| {
                rd.flatten()
                    .filter(|e| e.path().is_dir())
                    .filter_map(|e| {
                        let n = e.file_name().to_string_lossy().into_owned();
                        (n.len() == 8 && n.bytes().all(|b| b.is_ascii_digit())).then(|| n.parse().ok()).flatten()
                    })
                    .collect()
            })
            .unwrap_or_default();
        out.sort_unstable();
        Ok(out)
    })
    .await
}
