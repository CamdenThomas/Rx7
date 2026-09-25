//! `photo://localhost/<path>` — his photos of the car, read from the tree's
//! 01-REFERENCE/photos folder and nowhere else.

use super::Tree;
use std::borrow::Cow;
use tauri::http::{Request, Response, StatusCode};
use tauri::{Manager, UriSchemeContext, Wry};

pub fn serve(ctx: UriSchemeContext<'_, Wry>, req: Request<Vec<u8>>) -> Response<Cow<'static, [u8]>> {
    let root = ctx.app_handle().state::<Tree>().root();
    let base = root.join("01-REFERENCE/photos");
    let wanted = percent_decode(req.uri().path().trim_start_matches('/'));
    let file = root.join(&wanted);
    let inside = file.canonicalize().ok().zip(base.canonicalize().ok()).is_some_and(|(f, b)| f.starts_with(b));
    match (inside, std::fs::read(&file)) {
        (true, Ok(bytes)) => {
            let kind = match file.extension().and_then(|e| e.to_str()).map(str::to_ascii_lowercase).as_deref() {
                Some("png") => "image/png",
                Some("webp") => "image/webp",
                _ => "image/jpeg",
            };
            Response::builder().header("Content-Type", kind).body(Cow::Owned(bytes)).unwrap()
        }
        _ => Response::builder().status(StatusCode::NOT_FOUND).body(Cow::Borrowed(&[][..])).unwrap(),
    }
}

fn percent_decode(s: &str) -> String {
    let b = s.as_bytes();
    let mut out = Vec::with_capacity(b.len());
    let mut i = 0;
    while i < b.len() {
        if b[i] == b'%' && i + 2 < b.len() {
            if let Ok(v) = u8::from_str_radix(&s[i + 1..i + 3], 16) {
                out.push(v);
                i += 3;
                continue;
            }
        }
        out.push(b[i]);
        i += 1;
    }
    String::from_utf8_lossy(&out).into_owned()
}
