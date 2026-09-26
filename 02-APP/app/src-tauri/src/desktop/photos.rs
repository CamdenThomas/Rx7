//! `photo://localhost/<path>` — his photos of the car, read from the tree's
//! 01-REFERENCE/photos folder, and the 3D model built in 01-REFERENCE/model (D-415) — nowhere else.

use super::Tree;
use std::borrow::Cow;
use tauri::http::{Request, Response, StatusCode};
use tauri::{Manager, UriSchemeContext, Wry};

pub fn serve(ctx: UriSchemeContext<'_, Wry>, req: Request<Vec<u8>>) -> Response<Cow<'static, [u8]>> {
    let root = ctx.app_handle().state::<Tree>().root();
    let wanted = percent_decode(req.uri().path().trim_start_matches('/'));
    let file = root.join(&wanted);
    // His photos, the 3D model, and the generated harness drawings (D-385) - nowhere else.
    let inside = file.canonicalize().is_ok_and(|f| {
        ["01-REFERENCE/photos", "01-REFERENCE/model", "02-PROJECTS/01-electrical/00-design/diagrams"]
            .iter()
            .filter_map(|b| root.join(b).canonicalize().ok())
            .any(|b| f.starts_with(b))
    });
    let kind = match file.extension().and_then(|e| e.to_str()).map(str::to_ascii_lowercase).as_deref() {
        Some("png") => Some("image/png"),
        Some("webp") => Some("image/webp"),
        Some("jpg") | Some("jpeg") => Some("image/jpeg"),
        Some("svg") => Some("image/svg+xml"),
        Some("glb") => Some("model/gltf-binary"),
        _ => None,
    };
    if req.method() == tauri::http::Method::HEAD {
        // Home asks only whether the model exists; answer without reading 8 MB.
        return match (inside && file.is_file(), kind) {
            (true, Some(k)) => Response::builder().header("Content-Type", k).body(Cow::Borrowed(&[][..])).unwrap(),
            _ => Response::builder().status(StatusCode::NOT_FOUND).body(Cow::Borrowed(&[][..])).unwrap(),
        };
    }
    match (inside, kind, std::fs::read(&file)) {
        (true, Some(k), Ok(bytes)) => Response::builder().header("Content-Type", k).body(Cow::Owned(bytes)).unwrap(),
        _ => Response::builder().status(StatusCode::NOT_FOUND).body(Cow::Borrowed(&[][..])).unwrap(),
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn percent_decode_keeps_his_characters() {
        assert_eq!(super::percent_decode("a%20b"), "a b");
        assert_eq!(super::percent_decode("%E2%80%9Cquoted%E2%80%9D"), "\u{201c}quoted\u{201d}");
        assert_eq!(super::percent_decode("plain/path.jpg"), "plain/path.jpg");
        assert_eq!(super::percent_decode("bad%zz"), "bad%zz");
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
