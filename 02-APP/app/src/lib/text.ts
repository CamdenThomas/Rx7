// Turning the record's prose into something readable: decision bodies are written with a
// little Markdown (bold, lists, tables), and every D-### becomes a link to that decision.
// Everything is escaped first, so nothing in a cell can ever run as code in the app.

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/** One line of the record's prose as safe HTML: every id the record uses becomes a link
 *  (D-### to its decision, PT### to the part's row, S-### to the source, `block X.NN` to a
 *  search for it), so a row never has to be typed to be followed (plan P30). */
export function inlineMd(s: string): string {
  const codes: string[] = [];
  let out = esc(s).replace(/`([^`]+)`/g, (_, c: string) => `\u0000${codes.push(`<code>${c}</code>`) - 1}\u0000`);
  out = out
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" data-external>$1</a>')
    .replace(/&lt;(https?:\/\/[^\s&]+)&gt;/g, '<a href="$1" data-external>$1</a>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*\w])\*([^*\s][^*]*?)\*(?!\w)/g, '$1<em>$2</em>')
    .replace(/(^|[\s(])_([^_\s][^_]*?)_(?=[\s).,;:]|$)/g, '$1<em>$2</em>')
    .replace(/\b(D-\d{3})\b/g, '<a href="#/d/$1" class="cite">$1</a>')
    .replace(/\b(PT\d{3,4})\b/g, '<a href="#/row/00-CAR/parts/$1" class="cite">$1</a>')
    .replace(/\b(S-\d{3})\b/g, '<a href="#/row/01-REFERENCE/sources/$1" class="cite">$1</a>')
    .replace(/\bblock ((?:\d{2}|CAR|REF|APP|VER)\.\d{2,3})\b/g, 'block <a href="#/search?q=$1" class="cite">$1</a>');
  return out.replace(/\u0000(\d+)\u0000/g, (_, i: string) => codes[Number(i)]);
}

const inline = inlineMd;

function table(rows: string[]): string {
  const cells = (r: string) => r.trim().replace(/^\||\|$/g, '').split(/(?<!\\)\|/).map((c) => c.trim().replace(/\\\|/g, '|'));
  const [head, , ...body] = rows;
  return `<div class="table-wrap"><table><thead><tr>${cells(head).map((c) => `<th>${inline(c)}</th>`).join('')}</tr></thead><tbody>${body
    .map((r) => `<tr>${cells(r).map((c) => `<td>${inline(c)}</td>`).join('')}</tr>`)
    .join('')}</tbody></table></div>`;
}

/** Markdown-light to safe HTML. */
export function md(text: string): string {
  const lines = (text ?? '').replace(/\r/g, '').split('\n');
  const out: string[] = [];
  let i = 0;
  while (i < lines.length) {
    const l = lines[i];
    if (!l.trim()) {
      i++;
      continue;
    }
    const h = l.match(/^(#{1,4})\s+(.*)$/);
    if (h) {
      const level = Math.min(h[1].length + 2, 6);
      out.push(`<h${level}>${inline(h[2])}</h${level}>`);
      i++;
      continue;
    }
    if (/^\s*\|.*\|\s*$/.test(l) && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i + 1] ?? '') && (lines[i + 1] ?? '').includes('-')) {
      const rows: string[] = [];
      while (i < lines.length && /^\s*\|/.test(lines[i])) rows.push(lines[i++]);
      out.push(table(rows));
      continue;
    }
    if (/^\s*(?:[-*]|\d+[.)])\s+/.test(l)) {
      const ordered = /^\s*\d+[.)]/.test(l);
      const items: { depth: number; text: string }[] = [];
      while (i < lines.length && (/^\s*(?:[-*]|\d+[.)])\s+/.test(lines[i]) || (/^\s{2,}\S/.test(lines[i]) && items.length))) {
        const m = lines[i].match(/^(\s*)(?:[-*]|\d+[.)])\s+(.*)$/);
        if (m) items.push({ depth: m[1].length >= 2 ? 1 : 0, text: m[2] });
        else items[items.length - 1].text += ' ' + lines[i].trim();
        i++;
      }
      const tag = ordered ? 'ol' : 'ul';
      let html = `<${tag}>`;
      let open = false;
      for (const it of items) {
        if (it.depth === 1 && !open) {
          html = html.replace(/<\/li>$/, '') + '<ul>';
          open = true;
        } else if (it.depth === 0 && open) {
          html += '</ul></li>';
          open = false;
        }
        html += `<li>${inline(it.text)}</li>`;
      }
      if (open) html += '</ul></li>';
      out.push(html + `</${tag}>`);
      continue;
    }
    if (/^\s*```/.test(l)) {
      const code: string[] = [];
      i++;
      while (i < lines.length && !/^\s*```/.test(lines[i])) code.push(lines[i++]);
      i++;
      out.push(`<pre>${esc(code.join('\n'))}</pre>`);
      continue;
    }
    const para: string[] = [];
    while (i < lines.length && lines[i].trim() && !/^(#{1,4}\s|\s*(?:[-*]|\d+[.)])\s|\s*\||\s*```)/.test(lines[i])) para.push(lines[i++].trim());
    if (!para.length) para.push(lines[i++].trim());
    out.push(`<p>${inline(para.join(' '))}</p>`);
  }
  return out.join('\n');
}

/** Plain text of a Markdown-ish string, for previews and search. */
export function plain(text: string): string {
  return (text ?? '')
    .replace(/[*_`#>|]/g, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/\s+/g, ' ')
    .trim();
}

export function daysAgo(iso: string): number | null {
  const t = Date.parse(iso);
  return Number.isNaN(t) ? null : Math.floor((Date.now() - t) / 86_400_000);
}

export function ago(iso: string): string {
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (m) {
    const d = Math.round((new Date().setHours(0, 0, 0, 0) - new Date(+m[1], +m[2] - 1, +m[3]).getTime()) / 86_400_000);
    return d <= 0 ? 'today' : d === 1 ? 'yesterday' : d < 30 ? `${d} days ago` : day(iso);
  }
  const t = Date.parse(iso);
  if (Number.isNaN(t)) return iso;
  const s = Math.max(0, (Date.now() - t) / 1000);
  if (s < 60) return 'just now';
  if (s < 3600) return `${Math.floor(s / 60)} min ago`;
  if (s < 86_400) return `${Math.floor(s / 3600)} h ago`;
  const d = Math.floor(s / 86_400);
  if (d === 1) return 'yesterday';
  if (d < 30) return `${d} days ago`;
  return new Date(t).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

export function day(iso: string): string {
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  const t = m ? new Date(+m[1], +m[2] - 1, +m[3]).getTime() : Date.parse(iso);
  return Number.isNaN(t) ? iso : new Date(t).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

export function money(usd: string, qty = ''): string {
  const n = Number(usd);
  if (!usd || Number.isNaN(n)) return 'price unconfirmed';
  const each = n.toLocaleString(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: n < 100 ? 2 : 0 });
  return qty && qty !== '1' ? `${each} × ${qty}` : each;
}

export const plural = (n: number, one: string, many = `${one}s`) => `${n} ${n === 1 ? one : many}`;
