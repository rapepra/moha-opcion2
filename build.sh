#!/usr/bin/env bash
# Build para Cloudflare Pages
#   Build command:          bash build.sh
#   Build output directory: dist
# Copia solo lo que la web necesita: no publica documentación, scripts ni fotos originales sin optimizar.
set -euo pipefail

rm -rf dist
mkdir -p dist/images

cp index.html 404.html robots.txt sitemap.xml llms.txt llms-full.txt site.webmanifest favicon.ico _headers dist/
cp -R fonts dist/
cp -R images/opt dist/images/

# Comprobación: toda ruta local referenciada en las páginas debe existir en dist/
missing=0
for page in dist/index.html dist/404.html; do
  for ref in $(grep -oE '(src|href|srcset|imagesrcset)="[^"]+"' "$page" | sed -E 's/^[a-z]+="//; s/"$//' | tr ',' '\n' | awk '{print $1}' | grep -E '^(\./|/)[^/]' || true); do
    path="dist/${ref#./}"
    path="${path/dist\/\//dist/}"
    if [ ! -e "$path" ]; then echo "FALTA: $ref (en $page)"; missing=1; fi
  done
done
[ "$missing" -eq 0 ] || exit 1

echo "Build OK: $(find dist -type f | wc -l | tr -d ' ') archivos, $(du -sh dist | cut -f1)"
