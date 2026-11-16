#!/usr/bin/env python3
"""Minificado conservador de las páginas HTML de dist/ (solo espacios y comentarios).

- CSS de <style>: quita comentarios y espacios sobrantes.
- JSON-LD: lo compacta con json (valida que sea JSON correcto).
- HTML: quita comentarios y la sangría de cada línea (no une líneas, así no rompe JS).
"""
import json, re, sys

def css_min(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([{};])\s*', r'\1', css)
    css = re.sub(r',\s+', ',', css)
    return css.replace(';}', '}').strip()

def html_min(h):
    h = re.sub(r'(<style>)(.*?)(</style>)', lambda m: m.group(1) + css_min(m.group(2)) + m.group(3), h, flags=re.S)
    h = re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)',
               lambda m: m.group(1) + json.dumps(json.loads(m.group(2)), ensure_ascii=False, separators=(',', ':')) + m.group(3),
               h, flags=re.S)
    h = re.sub(r'<!--(?!\[).*?-->', '', h, flags=re.S)
    h = '\n'.join(line.strip() for line in h.splitlines() if line.strip())
    return h + '\n'

for path in sys.argv[1:]:
    src = open(path, encoding='utf-8').read()
    out = html_min(src)
    open(path, 'w', encoding='utf-8').write(out)
    print(f"minify {path}: {len(src.encode())//1024} KB -> {len(out.encode())//1024} KB")
