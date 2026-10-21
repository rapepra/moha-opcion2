# 🛠️ MO-HOUSE | Web Oficial & Documentación

Sitio web oficial de alta conversión (CRO), SEO Local y GEO (Generative Engine Optimization) para **MO-HOUSE** — *Instalaciones, soluciones y confianza*.

Especialistas en **Fontanería general · Climatización · Aerotermia · Calefacción**, con servicio en **San Sebastián, Mondragón, Vitoria-Gasteiz y radio de 40 km a la redonda** (Gipuzkoa y Álava).

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
├── index.html              # Página principal (HTML5, CSS inline, Schema.org JSON-LD)
├── 404.html                # Página de error (noindex) con botones de contacto
├── images/opt/             # Imágenes optimizadas que sirve la web (AVIF/WebP/JPG)
├── images/                 # Fotos originales (no se publican) + optimizar_imagenes.py
├── fonts/                  # Plus Jakarta Sans autoalojada (woff2)
├── llms.txt / llms-full.txt# Información estructurada para IAs (ChatGPT, Claude, Perplexity, Gemini)
├── sitemap.xml / robots.txt# Indexación para buscadores e IAs
├── _headers                # Cabeceras de Cloudflare Pages (caché, seguridad, noindex en *.pages.dev)
├── site.webmanifest, favicon.ico
├── build.sh                # Genera dist/ solo con lo publicable
└── README.md, DOCUMENTACION.md
```

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

**5. Conversiones (SEM)** — cada clic en llamar/WhatsApp envía `lead_click` al `dataLayer`. Para medirlo en Google Ads/GA4, añadir el contenedor de Google Tag Manager y crear un activador de evento personalizado `lead_click`.

---

## 🖼️ Añadir o cambiar fotos

1. Copia la foto a `images/` con un nombre descriptivo (`instalacion-aerotermia-bergara.jpg`).
2. Ejecuta `python3 images/optimizar_imagenes.py .` (genera las versiones en `images/opt/`).
3. Usa en `index.html` el mismo bloque `<picture>` que las demás fotos.

---

## 📞 Datos de Contacto y Facturación

- **Nombre Comercial:** MO-HOUSE
- **NIF Oficial:** Z0617960R
- **Teléfono / WhatsApp:** [602 38 32 37](tel:602383237)
- **Email:** [mohamed.akhrif2016@gmail.com](mailto:mohamed.akhrif2016@gmail.com)
- **Área de Cobertura:** San Sebastián · Mondragón · Vitoria-Gasteiz (Radio 40 km)
