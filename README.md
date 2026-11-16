# 🛠️ MO-HOUSE | Web Oficial & Documentación

Sitio web oficial de alta conversión (CRO), SEO Local y GEO (Generative Engine Optimization) para **MO-HOUSE** — *Instalaciones, soluciones y confianza*.

Especialistas en **Fontanería general · Climatización · Aerotermia · Calefacción**, empresa de **Ermua** con servicio en **Ermua, Eibar y 47 pueblos a menos de 25 km** (Debabarrena, Durangaldea, Debagoiena, Lea-Artibai, Urola y Aramaio). Urgencias 24 h.

---

## 🎯 Mensaje Corporativo

> *"En MO-HOUSE ofrecemos soluciones profesionales en fontanería, climatización, aerotermia y calefacción.*  
> *Desde una pequeña reparación hasta una instalación completa, nos encargamos de buscar la solución más adecuada para cada necesidad.*  
> *También gestionamos trabajos especializados, como la sustitución de bajantes de fibrocemento mediante empresas autorizadas, y coordinamos proyectos de renovación de baños y cocinas.*  
> ***MO-HOUSE — Instalaciones, soluciones y confianza.***"

---

## 🏗️ Jerarquía de Servicios y Especialidades

### 1. FONTANERÍA GENERAL (Actividad Principal)
- Instalaciones completas de fontanería y saneamiento.
- Montaje y renovación de instalaciones.
- Localización y reparación de fugas.
- Desatascos y problemas de evacuación.
- Reparaciones generales de fontanería.
- Sustitución de tuberías, grifería y sanitarios.
- Mantenimiento de instalaciones.

### 2. CLIMATIZACIÓN, AEROTERMIA Y CALEFACCIÓN (Actividad Principal)
- Instalación de aire acondicionado.
- Instalaciones de aerotermia.
- Instalación y renovación de calefacción.
- Montaje de radiadores y circuitos.
- Adaptación y mejora de instalaciones existentes.

### 3. BAJANTES Y SANEAMIENTO (Especialidad Técnica)
- Sustitución y renovación de bajantes.
- Reparación de tuberías y redes de evacuación.
- Gestión de retirada de bajantes de fibrocemento con amianto mediante empresa autorizada.
- Coordinación de los trabajos de retirada y gestión de residuos.
- Instalación de nuevas bajantes y conexiones de saneamiento.

### 4. RENOVACIÓN DE BAÑOS Y COCINAS (Servicio Complementario)
- Renovación de instalaciones de agua y desagües.
- Adaptación y redistribución de instalaciones.
- Gestión y coordinación de gremios.
- Renovaciones completas de baños y cocinas, según las necesidades del cliente.

---

## 📁 Estructura del Proyecto

```text
moha-opcion2/
├── tools/generar_web.py      # GENERA todas las páginas, el sitemap y optimiza fotos nuevas (editar el contenido aquí)
├── tools/minify.py           # Usado por build.sh: mete el CSS en línea y minifica
├── css/site.css              # Estilos comunes
├── js/site.js                # Menú móvil, galería, avisos legales y medición de clics
├── index.html                # Inicio                      ┐
├── fontanero-ermua/          # Fontanero en Ermua          │
├── fontanero-eibar/          # Fontanero en Eibar          │ generados por
├── urgencias-24h/            # Fontanero urgente 24 h      │ tools/generar_web.py
├── aerotermia-climatizacion/ # Aerotermia, clima, calef.   │ (no editar a mano)
├── bajantes-fibrocemento/    # Bajantes de uralita         │
├── reparaciones-obras-ermua/ # Reparaciones y obras Ermua  │
├── zona-de-servicio/         # Los 47 pueblos por comarca  │
├── 404.html, sitemap.xml     #                             ┘
├── images/opt/               # Fotos optimizadas que sirve la web (AVIF/WebP/JPG)
├── images/                   # Fotos originales (no se publican)
├── fonts/                    # Plus Jakarta Sans autoalojada
├── llms.txt / llms-full.txt  # Información para IAs (ChatGPT, Claude, Perplexity, Gemini)
├── robots.txt, _headers, site.webmanifest, favicon.ico
└── build.sh                  # Genera dist/ con lo publicable
```

### Cambiar contenido
1. Edita `tools/generar_web.py` (teléfono, pueblos en `ZONAS`, textos, preguntas frecuentes…).
2. Ejecuta `python3 tools/generar_web.py` (necesita Pillow) y luego `bash build.sh` para comprobar.
3. Sube los cambios a git: Cloudflare Pages publica solo.

---

## 🚀 Despliegue en Cloudflare Pages

**1. Crear el proyecto** — Workers & Pages → Create → Pages → *Connect to Git* → repo `moha-opcion2`:
- Production branch: la rama que se publique (p. ej. `main` tras fusionar `mo-house-seo-optimization`)
- Framework preset: **None**
- Build command: `bash build.sh`
- Build output directory: `dist`

**2. Dominio** — Custom domains → añadir `mo-house.es` y `www.mo-house.es`.
Después, en el dominio: Rules → Redirect Rules → *Redirect from WWW to root* (301) para que solo exista `https://mo-house.es/`.

**3. Ajustes del dominio en Cloudflare (importantes para SEO/GEO):**
- SSL/TLS → Edge Certificates → **Always Use HTTPS: On**
- Security → Bots → **Block AI bots / AI Scrapers and Crawlers: Off** (si está activo, ChatGPT, Claude o Perplexity no podrán leer la web)
- AI Crawl Control / *Manage robots.txt*: **desactivado** (si no, Cloudflare reescribe nuestro robots.txt)
- Caching → Configuration → **Crawler Hints: On** (avisa a Bing y otros vía IndexNow)
- Speed → **Rocket Loader: Off** (puede romper el menú y la galería)
- Scrape Shield → **Email Obfuscation: Off** (puede alterar el email en la página)

**4. Buscadores** (una vez publicada):
- Google Search Console → añadir propiedad de **dominio** `mo-house.es` (verificación por DNS, Cloudflare la añade sola) → enviar `https://mo-house.es/sitemap.xml`
- Bing Webmaster Tools → *Importar desde Google Search Console* (Bing alimenta a ChatGPT Search y Copilot)
- Probar los datos estructurados: https://search.google.com/test/rich-results
- Search Console → Inspección de URLs → pedir indexación de `/`, `/fontanero-ermua/` y `/fontanero-eibar/`

**5. Conversiones (SEM)** — cada clic en llamar/WhatsApp envía `lead_click` al `dataLayer`. Para medirlo en Google Ads/GA4, añadir el contenedor de Google Tag Manager y crear un activador de evento personalizado `lead_click`.

---

## 🖼️ Añadir o cambiar fotos

1. Copia la foto a `images/` con un nombre descriptivo (`instalacion-aerotermia-ermua.jpg`).
2. Úsala en `tools/generar_web.py` con `pic("instalacion-aerotermia-ermua", "texto alternativo")`.
3. Al ejecutar el generador se crean solas las versiones optimizadas en `images/opt/`.

---

## 📞 Datos de Contacto y Facturación

- **Nombre Comercial:** MO-HOUSE
- **NIF Oficial:** Z0617960R
- **Teléfono / WhatsApp:** [602 38 32 37](tel:602383237)
- **Email:** [mohamed.akhrif2016@gmail.com](mailto:mohamed.akhrif2016@gmail.com)
- **Área de Cobertura:** Ermua · Eibar · alrededores (25 km) · 24 h
- **Ficha de Google:** https://share.google/MHQ0pvipF8k27Tr6L
