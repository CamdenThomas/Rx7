import { describe, expect, it } from 'vitest';
import { md, money, plain } from '../src/lib/text';

describe('md — the record prose, rendered safely', () => {
  it('escapes everything before formatting', () => {
    expect(md('<script>alert(1)</script> **bold**')).toBe('<p>&lt;script&gt;alert(1)&lt;/script&gt; <strong>bold</strong></p>');
  });
  it('turns every D-### into a link, and nothing shorter', () => {
    const h = md('See D-405 and D-01, B-12.');
    expect(h).toContain('<a href="#/d/D-405" class="cite">D-405</a>');
    expect(h).not.toContain('#/d/D-01');
  });
  it('links a part and a source to their 00-CAR rows (D-519)', () => {
    const h = md('PT014 per S-002 p.14');
    expect(h).toContain('<a href="#/row/00-CAR/parts/PT014" class="cite">PT014</a>');
    expect(h).toContain('<a href="#/row/00-CAR/sources/S-002" class="cite">S-002</a>');
  });
  it('leaves code spans alone', () => {
    expect(md('`D-405 **x**`')).toBe('<p><code>D-405 **x**</code></p>');
  });
  it('renders lists with nested items and tables', () => {
    expect(md('- one\n  - inner\n- two')).toBe('<ul><li>one<ul><li>inner</li></ul></li><li>two</li></ul>');
    const t = md('| a | b |\n| --- | --- |\n| 1 | x \\| y |');
    expect(t).toContain('<th>a</th>');
    expect(t).toContain('<td>x | y</td>');
  });
  it('opens only http links, marked external', () => {
    expect(md('[site](https://example.com) [bad](javascript:alert(1))')).toContain('<a href="https://example.com" data-external>site</a>');
    expect(md('[bad](javascript:alert(1))')).not.toContain('href="javascript');
  });
});

describe('small helpers', () => {
  it('plain strips markup', () => expect(plain('**a** `b` [c](http://x)')).toBe('a b c'));
  it('money says when a price is unconfirmed', () => {
    expect(money('')).toBe('price unconfirmed');
    expect(money('8', '2')).toBe('$8.00 × 2');
  });
});
