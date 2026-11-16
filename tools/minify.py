#!/usr/bin/env python3
"""Uso: minify.py css/site.css pagina1.html pagina2.html ...

- Sustituye <link rel="stylesheet" href="/css/site.css"> por el CSS minificado en línea
  (sin petición extra: mejor LCP/FCP).
- Compacta el JSON-LD (y comprueba que es JSON válido).
- Quita comentarios HTML y la sangría de cada línea (no une líneas, así no rompe el JS).
"""
import json, re, sys

def css_min(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([{};])\s*', r'\1', css)
    css = re.sub(r',\s+', ',', css)
    return css.replace(';}', '}').strip()

css = css_min(open(sys.argv[1], encoding='utf-8').read())
LINK = '<link rel="stylesheet" href="/css/site.css">'

for path in sys.argv[2:]:
    src = open(path, encoding='utf-8').read()
    h = src.replace(LINK, '<style>' + css + '</style>')
    h = re.sub(r'(<style>)(.*?)(</style>)', lambda m: m.group(1) + css_min(m.group(2)) + m.group(3), h, flags=re.S)
    h = re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)',
               lambda m: m.group(1) + json.dumps(json.loads(m.group(2)), ensure_ascii=False, separators=(',', ':')) + m.group(3),
               h, flags=re.S)
    h = re.sub(r'<!--(?!\[).*?-->', '', h, flags=re.S)
    h = '\n'.join(line.strip() for line in h.splitlines() if line.strip()) + '\n'
    open(path, 'w', encoding='utf-8').write(h)
    print(f"minify {path}: {len(src.encode())//1024} KB -> {len(h.encode())//1024} KB")
