#!/usr/bin/env python3
"""Genera todas las páginas de mo-house.es desde un único sitio.

Uso:  python3 tools/generar_web.py        (desde la raíz del proyecto)

- Contenido, cabecera, pie, datos estructurados (schema.org) y sitemap salen de aquí:
  cambia un dato (teléfono, pueblos, horario…) y se actualiza en todas las páginas.
- Si una foto de images/ todavía no tiene versión optimizada en images/opt/, la crea.
"""
import hashlib, html, json, os, re
from datetime import date
from urllib.parse import quote

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://mo-house.es"
TODAY = date.today().isoformat()

PHONE = "602 38 32 37"
TEL = "+34602383237"
EMAIL = "mohamed.akhrif2016@gmail.com"
NIF = "Z0617960R"
GBP = "https://share.google/MHQ0pvipF8k27Tr6L"
KG = "https://www.google.com/search?kgmid=/g/11p27mvmxk"
BIZ_ID = f"{SITE}/#business"
LAT, LON = 43.1873, -2.5015  # Ermua (sin calle: la ficha de Google no muestra dirección exacta)
RATING = 5.0                  # valoración de la ficha de Google

# Pueblos a menos de 25 km de Ermua/Eibar, por comarca
ZONAS = [
    ("ermua-eibar", "Ermua, Eibar y alrededor", "Bizkaia y Gipuzkoa",
     ["Ermua", "Eibar", "Mallabia", "Soraluze"],
     "Es donde más trabajamos: estamos en cualquier punto en 20 a 30 minutos, también de noche."),
    ("debabarrena", "Bajo Deba (Debabarrena)", "Gipuzkoa",
     ["Elgoibar", "Mendaro", "Deba", "Mutriku"],
     "Valle abajo, hasta la costa. Urgencias y trabajos programados."),
    ("durangaldea", "Durangaldea", "Bizkaia",
     ["Zaldibar", "Berriz", "Durango", "Iurreta", "Abadiño", "Elorrio", "Atxondo", "Garai", "Izurtza", "Mañaria", "Amorebieta-Etxano"],
     "Desde Ermua, Zaldibar y Berriz están a un paso; Durango y Amorebieta, a pocos minutos por la autopista."),
    ("debagoiena", "Alto Deba (Debagoiena)", "Gipuzkoa",
     ["Bergara", "Elgeta", "Antzuola", "Arrasate-Mondragón", "Aretxabaleta", "Eskoriatza", "Oñati", "Leintz-Gatzaga"],
     "Bergara y Elgeta quedan muy cerca; Arrasate, Aretxabaleta y Oñati, valle arriba."),
    ("lea-artibai", "Lea-Artibai", "Bizkaia",
     ["Markina-Xemein", "Etxebarria", "Ziortza-Bolibar", "Munitibar", "Aulesti", "Berriatua", "Ondarroa", "Mendexa", "Lekeitio", "Amoroto", "Ispaster"],
     "Por el puerto de Areitio o por la costa, de Markina a Ondarroa y Lekeitio."),
    ("urola", "Urola (Kosta, Erdia y Goiena)", "Gipuzkoa",
     ["Azkoitia", "Azpeitia", "Zestoa", "Aizarnazabal", "Zumaia", "Zumarraga", "Urretxu", "Legazpi"],
     "Pueblos del valle del Urola a los que llegamos por Elgoibar o Bergara."),
    ("aramaio", "Aramaio", "Álava",
     ["Aramaio"],
     "El valle alavés vecino de Arrasate y Elorrio."),
]
ALL_TOWNS = [t for z in ZONAS for t in z[3]]

# --------------------------------------------------------------------------- imágenes
OPT = os.path.join(ROOT, "images", "opt")


def ensure_opt(base):
    """Crea las versiones optimizadas de images/<base>.jpg si faltan; devuelve (ancho, alto) de la de 800."""
    jpg = os.path.join(OPT, f"{base}-800.jpg")
    if not os.path.exists(jpg):
        src = os.path.join(ROOT, "images", base + ".jpg")
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        for w in (480, 800, 1200):
            r = im.copy() if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            r.save(f"{OPT}/{base}-{w}.webp", "WEBP", quality=72, method=6)
            if w in (480, 800):
                r.save(f"{OPT}/{base}-{w}.avif", "AVIF", quality=55, speed=4)
            if w == 800:
                r.save(jpg, "JPEG", quality=76, optimize=True, progressive=True)
        print("  optimizada:", base)
    with Image.open(jpg) as im:
        return im.size


def pic(base, alt, sizes="(max-width: 680px) 100vw, 50vw", eager=False, pos=None):
    w, h = ensure_opt(base)
    o = f"/images/opt/{base}"
    style = f' style="object-position: {pos};"' if pos else ""
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture><source type="image/avif" srcset="{o}-480.avif 480w, {o}-800.avif 800w" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{o}-480.webp 480w, {o}-800.webp 800w" sizes="{sizes}">'
            f'<img src="{o}-800.jpg" alt="{html.escape(alt)}" width="{w}" height="{h}" {load} decoding="async"{style}></picture>')


def preload(base, sizes):
    o = f"/images/opt/{base}"
    return (f'<link rel="preload" as="image" type="image/avif" imagesrcset="{o}-480.avif 480w, {o}-800.avif 800w" '
            f'imagesizes="{sizes}" fetchpriority="high">')


# --------------------------------------------------------------------------- piezas comunes
SVG_PHONE = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>'
SVG_WA = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M.06 24l1.69-6.16a11.87 11.87 0 0 1-1.59-5.95C.16 5.34 5.5 0 12.05 0a11.82 11.82 0 0 1 8.41 3.49 11.82 11.82 0 0 1 3.48 8.41c0 6.56-5.34 11.89-11.89 11.89a11.9 11.9 0 0 1-5.69-1.45zm6.6-3.81c1.67 1 3.28 1.59 5.39 1.59 5.45 0 9.89-4.43 9.89-9.88 0-5.46-4.42-9.89-9.88-9.89-5.45 0-9.89 4.43-9.89 9.88 0 2.23.65 3.89 1.75 5.64l-1 3.64zm11.38-5.46c-.07-.12-.27-.2-.57-.35-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.64.07-.3-.15-1.26-.46-2.39-1.47-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.61-.92-2.21-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.07c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.23 1.36.19 1.87.12.57-.09 1.76-.72 2.01-1.41.25-.7.25-1.29.17-1.41z"/></svg>'


def rating(conv="maps-rating"):
    return (f'<a class="rating" href="{GBP}" target="_blank" rel="noopener" data-conversion="{conv}">'
            f'<span class="stars" aria-hidden="true">★★★★★</span><strong>{str(RATING).replace(".", ",")}</strong>'
            f'<span>en Google · Ver opiniones</span></a>')


def wa(text):
    return f"https://wa.me/34602383237?text={quote(text)}"


def btn_call(conv, label=None, cls="btn btn-primary"):
    return f'<a href="tel:{TEL}" class="{cls}" data-conversion="{conv}">{SVG_PHONE}<span>{label or "Llamar al " + PHONE}</span></a>'


def btn_wa(conv, msg, label="WhatsApp", cls="btn btn-wa"):
    return f'<a href="{wa(msg)}" class="{cls}" target="_blank" rel="noopener" data-conversion="{conv}">{SVG_WA}<span>{label}</span></a>'


NAV = [
    ("/#servicios", "Servicios"),
    ("/#trabajos", "Trabajos"),
    ("/fontanero-ermua/", "Ermua"),
    ("/fontanero-eibar/", "Eibar"),
    ("/urgencias-24h/", "Urgencias 24 h"),
    ("/zona-de-servicio/", "Zona"),
    ("/#contacto", "Contacto"),
]


def header(path):
    links = "".join(
        f'<a href="{u}"{" aria-current=\"page\"" if u == path else ""}>{t}</a>' for u, t in NAV)
    return f'''<div class="topbar"><div class="container">
<span><span class="dot"></span>Urgencias 24 h en Ermua, Eibar y alrededores</span>
<a href="tel:{TEL}" data-conversion="call-topbar">Llamar: {PHONE}</a>
</div></div>
<header class="header">
<div class="container">
<a href="/" class="brand" aria-label="MO-HOUSE, inicio">
<picture><source type="image/webp" srcset="/images/opt/logo-mo-house-96.webp"><img src="/images/opt/logo-mo-house-96.png" alt="" width="44" height="44"></picture>
<span><span class="brand-name">MO-<span>HOUSE</span></span><span class="brand-sub">Fontanería y climatización</span></span>
</a>
<nav class="nav" aria-label="Principal">{links}</nav>
<div class="header-actions">
<a href="tel:{TEL}" class="btn btn-primary btn-sm" data-conversion="call-header">{SVG_PHONE}<span class="btn-call-text">{PHONE}</span></a>
<button class="menu-btn" id="menuBtn" aria-label="Abrir menú" aria-expanded="false" aria-controls="drawer"><span></span></button>
</div>
</div>
<nav class="drawer" id="drawer" aria-label="Menú móvil">{links}
{btn_wa("wa-drawer", "Hola MO-HOUSE, te escribo desde la web.", "Escribir por WhatsApp")}
</nav>
</header>'''


def footer():
    zonas_links = "".join(f'<li><a href="/zona-de-servicio/#{z[0]}">{z[1]}</a></li>' for z in ZONAS[1:6])
    return f'''<footer class="footer below">
<div class="container">
<div class="footer-grid">
<div>
<a href="/" class="brand"><picture><source type="image/webp" srcset="/images/opt/logo-mo-house-96.webp"><img src="/images/opt/logo-mo-house-96.png" alt="" width="44" height="44" loading="lazy"></picture><span class="brand-name">MO-<span>HOUSE</span></span></a>
<p>Fontanería, climatización, aerotermia y calefacción en Ermua, Eibar y alrededores. Urgencias 24 horas.</p>
<p style="margin-top:0.75rem"><a href="tel:{TEL}" data-conversion="call-footer"><strong>{PHONE}</strong></a><br>{EMAIL}<br>NIF {NIF}</p>
</div>
<div>
<h3>Servicios</h3>
<ul>
<li><a href="/urgencias-24h/">Fontanero urgente 24 h</a></li>
<li><a href="/#servicios">Fontanería y fugas</a></li>
<li><a href="/aerotermia-climatizacion/">Aerotermia y aire acondicionado</a></li>
<li><a href="/aerotermia-climatizacion/#calefaccion">Calefacción y radiadores</a></li>
<li><a href="/bajantes-fibrocemento/">Bajantes de fibrocemento</a></li>
<li><a href="/reparaciones-obras-ermua/">Reparaciones y obras</a></li>
</ul>
</div>
<div>
<h3>Dónde trabajamos</h3>
<ul>
<li><a href="/fontanero-ermua/">Fontanero en Ermua</a></li>
<li><a href="/fontanero-eibar/">Fontanero en Eibar</a></li>
{zonas_links}
</ul>
</div>
<div>
<h3>Contacto</h3>
<ul>
<li><a href="tel:{TEL}" data-conversion="call-footer2">Llamar: {PHONE}</a></li>
<li><a href="{wa("Hola MO-HOUSE, te escribo desde la web.")}" target="_blank" rel="noopener" data-conversion="wa-footer">WhatsApp</a></li>
<li><a href="mailto:{EMAIL}">Correo electrónico</a></li>
<li><a href="{GBP}" target="_blank" rel="noopener" data-conversion="maps-footer">MO-HOUSE en Google</a></li>
</ul>
</div>
</div>
<div class="footer-bottom">
<span>&copy; <span id="year">{date.today().year}</span> MO-HOUSE · Ermua y Eibar</span>
<span><button type="button" data-legal="aviso">Aviso legal</button><button type="button" data-legal="privacidad">Privacidad</button><button type="button" data-legal="cookies">Cookies</button></span>
</div>
<p class="credit">Web y SEO local: <a href="https://estudios.presupuesta.net/?utm_source=mo-house&amp;utm_medium=footer-credit&amp;utm_campaign=client-referral" target="_blank" rel="noopener">Presupuesta Estudios</a></p>
</div>
</footer>
<div class="dock">
{btn_wa("wa-dock", "Hola MO-HOUSE, necesito un fontanero.")}
{btn_call("call-dock", PHONE)}
</div>
<div class="modal" id="legal" role="dialog" aria-modal="true" aria-labelledby="legalTitle">
<div class="modal-box"><div class="modal-top"><strong id="legalTitle" data-legal-title>Aviso legal</strong><button class="modal-close" aria-label="Cerrar">&times;</button></div><div class="modal-body"></div></div>
</div>'''


def js_tag():
    h = hashlib.md5(open(os.path.join(ROOT, "js", "site.js"), "rb").read()).hexdigest()[:8]
    return f'<script src="/js/site.js?v={h}" defer></script>'


def business(full=False):
    b = {
        "@type": ["LocalBusiness", "Plumber", "HVACBusiness"],
        "@id": BIZ_ID,
        "name": "MO-HOUSE",
        "url": f"{SITE}/",
        "telephone": TEL,
        "email": EMAIL,
        "image": f"{SITE}/images/opt/og-mo-house-1200x630.jpg",
        "logo": f"{SITE}/images/opt/logo-mo-house-512.png",
        "priceRange": "€€",
        "address": {"@type": "PostalAddress", "addressLocality": "Ermua", "postalCode": "48260",
                    "addressRegion": "Bizkaia", "addressCountry": "ES"},
        "geo": {"@type": "GeoCoordinates", "latitude": LAT, "longitude": LON},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                       "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                       "opens": "00:00", "closes": "23:59"}],
        "hasMap": GBP,
        "sameAs": [GBP, KG],
    }
    if full:
        b.update({
            "alternateName": ["MO HOUSE", "MO-HOUSE Fontanería", "MO-HOUSE fontanero Ermua", "MO-HOUSE fontanero Eibar"],
            "slogan": "Instalaciones, soluciones y confianza",
            "description": ("MO-HOUSE es una empresa de fontanería, climatización, aerotermia y calefacción de Ermua que trabaja en "
                            "Ermua, Eibar y los pueblos a menos de 25 km (Debabarrena, Durangaldea, Debagoiena, Lea-Artibai y Urola). "
                            "Urgencias 24 horas todos los días, reparaciones, instalaciones completas, cambio de bajantes de "
                            "fibrocemento mediante empresa autorizada y renovación de baños y cocinas."),
            "taxID": NIF,
            "currenciesAccepted": "EUR",
            "paymentAccepted": "Efectivo, tarjeta, Bizum, transferencia bancaria",
            "founder": {"@type": "Person", "name": "Mohammed Akhrif", "jobTitle": "Fontanero e instalador de climatización"},
            "areaServed": [{"@type": "City", "name": "Ermua", "sameAs": "https://es.wikipedia.org/wiki/Ermua"},
                           {"@type": "City", "name": "Eibar", "sameAs": "https://es.wikipedia.org/wiki/Eibar"}]
                          + [{"@type": "City", "name": t} for t in ALL_TOWNS if t not in ("Ermua", "Eibar")]
                          + [{"@type": "AdministrativeArea", "name": n} for n in
                             ["Debabarrena", "Durangaldea", "Debagoiena", "Lea-Artibai", "Bizkaia", "Gipuzkoa"]],
            "serviceArea": {"@type": "GeoCircle",
                            "geoMidpoint": {"@type": "GeoCoordinates", "latitude": LAT, "longitude": LON},
                            "geoRadius": "25000"},
            "contactPoint": [{"@type": "ContactPoint", "telephone": TEL, "contactType": "customer service",
                              "areaServed": ["Ermua", "Eibar", "Bizkaia", "Gipuzkoa"], "availableLanguage": ["es"],
                              "hoursAvailable": {"@type": "OpeningHoursSpecification",
                                                 "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                                 "opens": "00:00", "closes": "23:59"}}],
            "knowsAbout": ["Fontanería", "Urgencias de fontanería", "Detección de fugas", "Desatascos", "Aerotermia",
                           "Aire acondicionado", "Calefacción", "Radiadores", "Bajantes de fibrocemento", "Saneamiento",
                           "Reforma de baños"],
            "makesOffer": [{"@type": "Offer", "itemOffered": {"@id": f"{SITE}{p}#servicio"}} for p in
                           ["/urgencias-24h/", "/aerotermia-climatizacion/", "/bajantes-fibrocemento/", "/reparaciones-obras-ermua/"]],
        })
    return b


def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def faq_html(faqs):
    return '<div class="faq">' + "".join(
        f'<details><summary>{q}</summary><div><p>{a}</p></div></details>' for q, a in faqs) + "</div>"


def faq_schema(url, faqs):
    return {"@type": "FAQPage", "@id": f"{url}#preguntas",
            "mainEntity": [{"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
                           for q, a in faqs]}


def breadcrumb(url, name):
    return {"@type": "BreadcrumbList", "@id": f"{url}#migas", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": name, "item": url}]}


def cta_band(conv, msg, title="¿Tienes una avería o quieres presupuesto?",
             text=f"Llama o manda fotos por WhatsApp. Te contesta el instalador, no una centralita."):
    return f'''<div class="cta-band">
<div><h2>{title}</h2><p>{text}</p></div>
<div class="cta-row">{btn_call("call-" + conv)}{btn_wa("wa-" + conv, msg)}</div>
</div>'''


def page(path, title, desc, body, graph, lcp=None, og_image=None, robots="index, follow, max-image-preview:large, max-snippet:-1"):
    url = SITE + path
    og = og_image or f"{SITE}/images/opt/og-mo-house-1200x630.jpg"
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="format-detection" content="telephone=no">
<meta name="geo.region" content="ES-BI">
<meta name="geo.placename" content="Ermua; Eibar">
<meta name="geo.position" content="{LAT};{LON}">
<meta name="ICBM" content="{LAT}, {LON}">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="MO-HOUSE">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0e1520">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/images/opt/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/images/opt/apple-touch-icon-180.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/fonts/plus-jakarta-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
{lcp or ""}
<link rel="stylesheet" href="/css/site.css">
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
{header(path)}
<main>
{body}
</main>
{footer()}
{js_tag()}
</body>
</html>
'''


def write(path, content):
    out = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/" else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(content)
    print("  página:", path)


PAGES = []  # (path, [imágenes]) para el sitemap


def webpage(path, name, desc, img, about=None):
    url = SITE + path
    d = {"@type": "WebPage", "@id": f"{url}#webpage", "url": url, "name": name, "description": desc,
         "inLanguage": "es-ES", "isPartOf": {"@id": f"{SITE}/#website"}, "about": {"@id": about or BIZ_ID},
         "primaryImageOfPage": f"{SITE}/images/opt/{img}-1200.webp", "dateModified": TODAY}
    if path != "/":
        d["breadcrumb"] = {"@id": f"{url}#migas"}
    return d


def service(path, name, stype, desc, towns):
    return {"@type": "Service", "@id": f"{SITE}{path}#servicio", "name": name, "serviceType": stype,
            "description": desc, "provider": {"@id": BIZ_ID}, "url": SITE + path,
            "areaServed": [{"@type": "City", "name": t} for t in towns],
            "hoursAvailable": {"@type": "OpeningHoursSpecification",
                               "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                               "opens": "00:00", "closes": "23:59"}}


def photo_row(items):
    return '<div class="photo-row">' + "".join(
        f'<figure>{pic(b, alt, "(max-width: 560px) 50vw, 250px", pos=pos)}<figcaption>{cap}</figcaption></figure>'
        for b, alt, cap, pos in items) + "</div>"


def aside(conv, msg, links):
    li = "".join(f'<li><a href="{u}">{t}</a></li>' for u, t in links)
    return f'''<aside class="aside">
<div class="aside-box">
<h3>Urgencias 24 horas</h3>
<p>Llama a cualquier hora o manda fotos de la avería por WhatsApp.</p>
{btn_call("call-" + conv)}
{btn_wa("wa-" + conv, msg, "Enviar fotos por WhatsApp")}
</div>
<div class="aside-box"><h3>Opiniones</h3><p>Nuestros clientes nos valoran con 5 estrellas en Google.</p>{rating("maps-aside-" + conv)}</div>
<div class="aside-box"><h3>También te puede interesar</h3><ul style="margin-top:0.6rem">{li}</ul></div>
</aside>'''


def inner(path, crumb, h1, sub, lead, hero_img, hero_alt, hero_cap, hero_pos, conv, msg, content, faqs, links):
    return f'''<div class="container"><nav aria-label="Migas de pan"><ol class="breadcrumb"><li><a href="/">Inicio</a></li><li aria-current="page">{crumb}</li></ol></nav></div>
<section class="page-hero">
<div class="container hero-grid">
<div>
<h1>{h1}<span class="sub" style="display:block;font-size:0.5em">{sub}</span></h1>
<p class="lead">{lead}</p>
<div class="cta-row">{btn_call("call-hero-" + conv)}{btn_wa("wa-hero-" + conv, msg)}</div>
{rating("maps-hero-" + conv)}
</div>
<figure class="hero-photo">{pic(hero_img, hero_alt, "(max-width: 900px) 100vw, 520px", eager=True, pos=hero_pos)}<figcaption>{hero_cap}</figcaption></figure>
</div>
</section>
<section class="section alt below">
<div class="container layout">
<article class="prose">
{content}
</article>
{aside(conv, msg, links)}
</div>
</section>
<section class="section below" id="preguntas">
<div class="container">
<div class="section-head center"><h2>Preguntas frecuentes</h2></div>
{faq_html(faqs)}
<div style="margin-top:3rem">{cta_band(conv + "-final", msg)}</div>
</div>
</section>'''


def zone_text(z, link_main=True):
    towns = ", ".join(z[3])
    return f'<div class="zone" id="{z[0]}"><h3>{z[1]} <small>· {z[2]}</small></h3><p>{towns}.</p></div>'


# =========================================================================== INICIO
def build_home():
    path = "/"
    hero = "instalacion-tuberias-multicapa-bano-eibar"
    faqs = [
        ("¿Qué trabajos hacéis?",
         "Fontanería (averías, fugas, desatascos, tuberías, grifería, sanitarios y contadores), aerotermia, aire acondicionado y "
         "calefacción. También cambiamos bajantes comunitarias, incluidas las de fibrocemento a través de una empresa autorizada, y "
         "renovamos baños y cocinas."),
        ("¿Sois de la zona?",
         "Sí. MO-HOUSE es de Ermua y casi todo nuestro trabajo está entre Ermua y Eibar. Por eso en estos dos pueblos llegamos en "
         "20 a 30 minutos cuando hay una urgencia."),
        ("¿En qué pueblos trabajáis?",
         "En Ermua, Eibar y los pueblos a menos de 25 km: Mallabia, Soraluze, Elgoibar, Deba, Mutriku, Zaldibar, Berriz, Durango, "
         "Elorrio, Amorebieta, Bergara, Arrasate, Oñati, Markina, Ondarroa, Lekeitio, Azkoitia, Azpeitia y Zumaia, entre otros. "
         'Tienes la lista completa en <a href="/zona-de-servicio/">zona de servicio</a>.'),
        ("¿Atendéis urgencias de noche y en fin de semana?",
         f"Sí, las 24 horas y todos los días del año, en el {PHONE}. Fugas, roturas de tubería, atascos, filtraciones al vecino o "
         "calefacción sin funcionar."),
        ("¿Cuánto cuesta y cómo hacéis el presupuesto?",
         "Te damos un precio cerrado antes de empezar. Para muchas averías basta con que nos mandes fotos o un vídeo por WhatsApp; "
         "si hace falta, pasamos a verlo sin compromiso."),
        ("¿Dais factura para el seguro o la comunidad?",
         f"Sí, siempre factura oficial con NIF {NIF} e IVA desglosado. Sirve para el seguro del hogar, comunidades de vecinos y "
         "administradores de fincas."),
        ("¿Cómo cambiáis una bajante de fibrocemento (uralita)?",
         "La retirada del fibrocemento la hace una empresa autorizada inscrita en el RERA, con su plan de trabajo aprobado. "
         "Nosotros coordinamos la obra e instalamos la bajante nueva de PVC insonorizado. "
         '<a href="/bajantes-fibrocemento/">Más información sobre bajantes</a>.'),
        ("¿Instaláis aerotermia en pisos?",
         "Sí, en pisos y casas. Antes miramos si tus radiadores y el espacio para la unidad exterior permiten aerotermia o si "
         'te conviene otra solución. <a href="/aerotermia-climatizacion/">Aerotermia y climatización</a>.'),
    ]

    services = [
        ("reparacion-tuberia-plomo-cobre-eibar", "Cambio de tubería de plomo por multicapa en Ermua", "Fontanería y urgencias",
         "Averías, fugas y renovación de instalaciones en pisos, locales y comunidades.",
         ["Fugas y roturas de tubería", "Desatascos de fregadero, baño y bajante", "Cambio de tuberías de plomo y cobre",
          "Grifería, sanitarios, contadores y llaves de paso"], "/urgencias-24h/", "Urgencias 24 h", "50% 40%"),
        ("tomas-lavadora-climatizacion-terraza-eibar", "Unidad exterior de bomba de calor en una terraza de Ermua",
         "Aerotermia, clima y calefacción", "Instalamos y renovamos equipos de frío y calor pensando en lo que vas a gastar después.",
         ["Aerotermia para calefacción y agua caliente", "Aire acondicionado split, multisplit y conductos",
          "Calefacción y radiadores", "Mejora de instalaciones existentes"], "/aerotermia-climatizacion/", "Ver aerotermia y clima", "50% 12%"),
        ("reparacion-bajante-comunitaria-pvc-eibar", "Bajante comunitaria nueva de PVC en Eibar", "Bajantes y saneamiento",
         "Cambio de bajantes en comunidades, con la retirada del fibrocemento a cargo de una empresa autorizada.",
         ["Bajantes de fecales y pluviales", "Colectores y arquetas", "Fibrocemento (uralita) con empresa RERA",
          "PVC insonorizado y documentación para la ITE"], "/bajantes-fibrocemento/", "Ver bajantes", "50% 45%"),
        ("reforma-bano-ducha-calacatta-eibar", "Baño reformado con ducha de obra en Eibar", "Baños y cocinas",
         "Cuando la reforma toca agua y desagües, nos encargamos de la instalación y coordinamos al resto de gremios.",
         ["Cambio de bañera por plato de ducha", "Nueva distribución de agua y desagües",
          "Coordinación de albañil, electricista y alicatado", "Cocinas: fregadero, lavavajillas y tomas"], "/reparaciones-obras-ermua/", "Ver reparaciones y obras", "50% 60%"),
    ]
    svc_html = "".join(f'''<article class="card">{pic(b, alt, "(max-width: 680px) 100vw, 560px", pos=pos)}
<div class="card-body"><h3>{t}</h3><p>{d}</p><ul>{"".join(f"<li>{x}</li>" for x in pts)}</ul>
<a class="card-link" href="{u}">{lt} →</a></div></article>''' for b, alt, t, d, pts, u, lt, pos in services)

    cases = [
        ("reparacion-bajante-comunitaria-pvc-eibar", "Bajante comunitaria sustituida por PVC en Eibar", "Comunidad de vecinos · Eibar",
         "Cambio de bajante comunitaria", "La bajante de fibrocemento tenía fisuras y filtraba a los pisos de abajo. La retirada la hizo una empresa autorizada y montamos una columna nueva de PVC serie B insonorizado.",
         [("Retirada", "empresa autorizada RERA"), ("Tubería nueva", "PVC serie B insonorizado"), ("Documentación", "factura y certificado para la ITE y el seguro")]),
        ("reforma-bano-ducha-griferia-negra-eibar", "Plato de ducha y grifería negra en un baño de Ermua", "Vivienda · Ermua",
         "Bañera cambiada por plato de ducha", "Quitamos la bañera, adaptamos las tomas con multicapa, impermeabilizamos y montamos plato de resina con mampara.",
         [("Grifería", "termostática empotrada"), ("Plazo", "48 horas"), ("Resultado", "ducha a ras de suelo, más segura")]),
        ("limpieza-colector-comunitario-garaje-eibar", "Colector de saneamiento en el garaje de una comunidad de Ermua", "Garaje comunitario · Ermua",
         "Atasco en el colector general", "Tapón de grasa y sedimentos en el colector colgado del garaje. Lo limpiamos con máquina de espiral sin romper la tubería.",
         [("Técnica", "máquina rotativa con cabezal cortador"), ("Tiempo", "2 horas, aviso urgente"), ("Resultado", "evacuación normal sin obra")]),
        ("sustitucion-contador-agua-digital-eibar", "Contador de agua nuevo y llave de corte en Eibar", "Vivienda · Eibar",
         "Fuga en el contador y la llave de paso", "Los racores de cobre estaban sulfatados dentro de la hornacina del contador. Cambiamos racores, llave de corte y dejamos el contador nuevo.",
         [("Material", "latón y racores estancos"), ("Tiempo", "1 hora"), ("Resultado", "sin fugas y con corte de agua fiable")]),
    ]
    case_html = "".join(f'''<article class="card case">{pic(b, alt, "(max-width: 1000px) 100vw, 220px")}
<div class="card-body"><span class="tag">{tag}</span><h3>{t}</h3><p>{d}</p>
<dl>{"".join(f"<dt>{k}:</dt> <dd>{v}</dd>" for k, v in spec)}</dl></div></article>''' for b, alt, tag, t, d, spec in cases)

    gallery = [
        ("banos", "reforma-bano-ducha-calacatta-eibar", "Baño con porcelánico tipo Calacatta", "Eibar", "Revestimiento porcelánico efecto mármol, grifería empotrada dorada y plato extraplano."),
        ("banos", "reforma-bano-lavabo-piedra-dorado-eibar", "Columna de ducha termostática", "Ermua", "Rociador de techo y teleducha sobre porcelánico efecto mármol."),
        ("banos", "reforma-bano-mampara-negra-eibar", "Lavabo doble y espejo con luz", "Elgoibar", "Mueble suspendido con lavabo doble, grifería monomando, espejo LED e inodoro nuevo."),
        ("banos", "montaje-plato-ducha-resina-blanco-eibar", "Plato de ducha de resina", "Ermua", "Plato de resina antideslizante clase 3 con válvula sifónica de gran caudal."),
        ("banos", "nivelacion-solera-valvula-sifonica-ducha-eibar", "Solera y desagüe de ducha", "Ermua", "Base nivelada con mortero y válvula de desagüe conectada antes de montar el plato."),
        ("banos", "retirada-banera-herramientas-albanileria-eibar", "Retirada de bañera", "Durango", "Picado del murete y retirada de la bañera antigua para poner ducha."),
        ("bajantes", "reparacion-bajante-comunitaria-pvc-eibar", "Bajante comunitaria de PVC", "Eibar", "Columna nueva de PVC serie B insonorizado tras la retirada autorizada de la antigua."),
        ("fontaneria", "sustitucion-contador-agua-digital-eibar", "Contador de agua", "Eibar", "Contador nuevo y racores de latón en lugar de los oxidados."),
        ("fontaneria", "contador-agua-nuevo-llave-mariposa-eibar", "Llave de paso general", "Ermua", "Llave de corte nueva y uniones estancas en la batería de contadores."),
        ("fontaneria", "regulador-presion-bateria-contadores-eibar", "Regulador de presión", "Eibar", "Reductor de presión con manómetro y latiguillos de acero inoxidable."),
        ("fontaneria", "reparacion-tuberia-plomo-cobre-eibar", "Tubería de plomo a multicapa", "Ermua", "Cambio urgente de tubería de plomo picada por multicapa prensado."),
        ("desatascos", "limpieza-colector-comunitario-garaje-eibar", "Colector en garaje", "Ermua", "Limpieza y retirada de tapón en la tubería colgada del garaje."),
        ("desatascos", "atasco-tapon-grasa-colector-bajante-eibar", "Tapón de grasa en bajante", "Soraluze", "Limpieza interior de un conducto obstruido por grasa y sedimentos."),
        ("clima", "instalacion-radiador-calefaccion-aluminio-eibar", "Radiador de aluminio", "Eibar", "Radiador de aluminio con válvulas termostáticas bajo la ventana."),
        ("clima", "instalacion-climatizador-terraza-eibar", "Bomba de calor en terraza", "Ermua", "Tomas de agua, desagüe y línea eléctrica para la unidad exterior y la lavadora."),
    ]
    filt = [("all", "Todos"), ("fontaneria", "Fontanería"), ("clima", "Clima y calefacción"), ("bajantes", "Bajantes"),
            ("desatascos", "Desatascos"), ("banos", "Baños")]
    gal_html = '<div class="filters" role="group" aria-label="Filtrar trabajos">' + "".join(
        f'<button type="button" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{t}</button>' for k, t in filt) + "</div>"
    gal_html += '<div class="gallery">' + "".join(
        f'''<button type="button" class="gallery-item" data-category="{c}" data-full="/images/opt/{b}-1200.webp" data-title="{t}" data-place="{p}" data-desc="{d}">{pic(b, f"{t} en {p}, trabajo de MO-HOUSE", "(max-width: 680px) 50vw, 280px")}<span>{t}<small>{p}</small></span></button>'''
        for c, b, t, p, d in gallery) + "</div>"

    zones_short = "".join(zone_text(z) for z in ZONAS[1:])
    body = f'''<section class="hero">
<div class="container hero-grid">
<div>
<h1><span class="hl">Fontanero en Eibar y Ermua</span><span class="sub">Fontanería, climatización, aerotermia y calefacción. Urgencias 24 horas.</span></h1>
<p class="lead">Somos MO-HOUSE, de Ermua. Reparamos averías y hacemos instalaciones en pisos, comunidades y locales de Ermua, Eibar y los pueblos de alrededor. Hablas directamente con el instalador y sabes el precio antes de empezar.</p>
<div class="cta-row">{btn_call("call-hero")}{btn_wa("wa-hero", "Hola MO-HOUSE, necesito presupuesto o ayuda con una avería.", "Escribir por WhatsApp")}</div>
{rating("maps-hero")}
<ul class="checks">
<li>Urgencias 24 horas, también fines de semana y festivos</li>
<li>Presupuesto cerrado y sin compromiso, incluso por fotos</li>
<li>Factura oficial válida para el seguro y la comunidad</li>
</ul>
</div>
<figure class="hero-photo">{pic(hero, "Tuberías multicapa nuevas en el baño de un piso de Eibar", "(max-width: 900px) 100vw, 520px", eager=True)}
<figcaption><strong>Renovación de tuberías en un baño de Eibar</strong>Trabajo real de MO-HOUSE</figcaption></figure>
</div>
</section>

<section class="section alt below" id="servicios">
<div class="container">
<div class="section-head"><span class="eyebrow">Servicios</span><h2>Qué hacemos en Ermua, Eibar y alrededores</h2>
<p>Lo principal es la fontanería y la climatización. Además cambiamos bajantes en comunidades y renovamos baños y cocinas.</p></div>
<div class="grid-2">{svc_html}</div>
</div>
</section>

<section class="section below" id="trabajos">
<div class="container">
<div class="section-head"><span class="eyebrow">Trabajos recientes</span><h2>Algunos trabajos en Ermua y Eibar</h2>
<p>Qué problema había y cómo lo resolvimos.</p></div>
<div class="grid-2">{case_html}</div>
<div class="section-head" style="margin-top:4rem"><h2>Galería de trabajos</h2><p>Fotos de obras reales. Pulsa una para verla en grande.</p></div>
{gal_html}
</div>
</section>

<section class="section alt below" id="nosotros">
<div class="container about">
<div class="about-photo">{pic("instalacion-valvula-desague-ducha-eibar", "Instalación de desagüe de ducha por MO-HOUSE", "(max-width: 900px) 100vw, 440px")}</div>
<div>
<span class="eyebrow">Sobre MO-HOUSE</span>
<h2>Un fontanero de Ermua para Ermua y Eibar</h2>
<p>MO-HOUSE es el negocio de Mohammed Akhrif, fontanero e instalador de climatización. Somos de Ermua y la mayoría de nuestros clientes están entre Ermua y Eibar, así que conocemos bien los edificios de la zona: muchos pisos de los años 50 a 70 que todavía tienen tuberías de plomo o cobre antiguo, bajantes de fibrocemento y calefacciones que piden una revisión.</p>
<p>Desde una reparación pequeña hasta una instalación completa, buscamos la solución que de verdad te conviene y te explicamos el precio antes de empezar.</p>
<dl class="facts">
<div><dt>Horario</dt><dd>24 horas, todos los días</dd></div>
<div><dt>Zona</dt><dd>Ermua, Eibar y 25 km</dd></div>
<div><dt>Teléfono y WhatsApp</dt><dd>{PHONE}</dd></div>
<div><dt>Opiniones en Google</dt><dd><a href="{GBP}" target="_blank" rel="noopener">5 estrellas</a></dd></div>
</dl>
</div>
</div>
</section>

<section class="section below" id="zona">
<div class="container">
<div class="section-head"><span class="eyebrow">Zona de servicio</span><h2>Ermua, Eibar y los pueblos de alrededor</h2>
<p>Trabajamos sobre todo en Ermua y Eibar, y vamos a cualquier pueblo a menos de 25 km.</p></div>
<div class="place-cards">
<a class="place" href="/fontanero-ermua/"><h3>Fontanero en Ermua</h3><p>Somos de aquí. Urgencias en 20 a 30 minutos, Mallabia y Zaldibar incluidos.</p><span class="card-link">Ver Ermua →</span></a>
<a class="place" href="/fontanero-eibar/"><h3>Fontanero en Eibar</h3><p>Todos los barrios, de Amaña a Urki e Ipurua. Urgencias en 20 a 30 minutos.</p><span class="card-link">Ver Eibar →</span></a>
<a class="place" href="/reparaciones-obras-ermua/"><h3>Reparaciones y obras en Ermua</h3><p>Baños, cocinas, cambio de bañera por ducha y arreglos tras una fuga.</p><span class="card-link">Ver obras →</span></a>
<a class="place" href="/zona-de-servicio/"><h3>47 pueblos a 25 km</h3><p>Durangaldea, Bajo y Alto Deba, Lea-Artibai y Urola.</p><span class="card-link">Ver la zona →</span></a>
</div>
<div class="zones">{zones_short}</div>
<p class="note">¿Tu pueblo no aparece? Si está a menos de 25 km de Ermua o Eibar, también vamos. <a href="/zona-de-servicio/">Ver la zona completa</a> o <a href="tel:{TEL}" data-conversion="call-zona">llama al {PHONE}</a>.</p>
<p class="eu" lang="eu">Iturgintza, klimatizazioa, aerotermia eta berogailuak Ermuan, Eibarren eta inguruetan. Larrialdiak 24 orduz: {PHONE}.</p>
</div>
</section>

<section class="section alt below" id="preguntas">
<div class="container">
<div class="section-head center"><span class="eyebrow">Preguntas frecuentes</span><h2>Lo que más nos preguntan</h2></div>
{faq_html(faqs)}
</div>
</section>

<section class="section below" id="contacto">
<div class="container">
{cta_band("contacto", "Hola MO-HOUSE, necesito presupuesto o ayuda con una avería.", "¿Tienes una avería o quieres presupuesto?", "Llama o manda fotos por WhatsApp y te decimos qué hay que hacer y cuánto cuesta.")}
<div class="contact-grid">
<a class="contact-item" href="tel:{TEL}" data-conversion="call-contact"><small>Teléfono 24 h</small><strong>{PHONE}</strong><span>Urgencias y presupuestos</span></a>
<a class="contact-item" href="{wa("Hola MO-HOUSE, te escribo desde la web.")}" target="_blank" rel="noopener" data-conversion="wa-contact"><small>WhatsApp</small><strong>{PHONE}</strong><span>Mándanos fotos o vídeo de la avería</span></a>
<a class="contact-item" href="mailto:{EMAIL}"><small>Correo</small><strong>{EMAIL}</strong><span>Presupuestos y comunidades</span></a>
<a class="contact-item" href="{GBP}" target="_blank" rel="noopener" data-conversion="maps-contact"><small>Google</small><strong>MO-HOUSE en Google</strong><span>Opiniones, fotos y cómo llegar</span></a>
</div>
</div>
</section>

<div class="modal" id="lightbox" role="dialog" aria-modal="true" aria-label="Foto del trabajo">
<div class="modal-box wide">
<div class="modal-top"><div><strong data-lb="title"></strong><small data-lb="place"></small></div><button class="modal-close" aria-label="Cerrar">&times;</button></div>
<img class="lightbox-img" alt="" width="1200" height="900">
<div class="modal-body"><p data-lb="desc"></p>
<a class="btn btn-wa" data-lb="wa" href="#" target="_blank" rel="noopener" data-conversion="wa-lightbox" style="margin-top:1rem;width:100%">{SVG_WA}<span>Pedir un trabajo parecido</span></a></div>
</div>
</div>'''

    title = "Fontanero en Eibar y Ermua 24 h · Clima y Aerotermia | MO-HOUSE"
    desc = f"Fontanero de Ermua para Eibar, Ermua y alrededores: urgencias 24 h, fugas, desatascos, aerotermia, aire acondicionado y calefacción. ☎ {PHONE}"
    graph = [business(full=True),
             {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": "MO-HOUSE", "inLanguage": "es-ES",
              "publisher": {"@id": BIZ_ID},
              "creator": {"@type": "Organization", "@id": "https://estudios.presupuesta.net/#agency", "name": "Presupuesta Estudios",
                          "url": "https://estudios.presupuesta.net/"}},
             webpage(path, title, desc, hero), faq_schema(SITE + "/", faqs)]
    write(path, page(path, title, desc, body, graph, preload(hero, "(max-width: 900px) 100vw, 520px")))
    PAGES.append((path, [hero] + [g[1] for g in gallery]))


# =========================================================================== PÁGINAS INTERIORES
def build_ermua():
    path = "/fontanero-ermua/"
    hero = "cambio-banera-por-plato-ducha-eibar"
    msg = "Hola MO-HOUSE, necesito un fontanero en Ermua."
    faqs = [
        ("¿Tenéis fontanero urgente en Ermua por la noche o en fin de semana?",
         f"Sí. Atendemos urgencias en Ermua las 24 horas, todos los días, en el {PHONE}. Como somos de aquí, normalmente llegamos en 20 a 30 minutos."),
        ("¿Vais también a Mallabia y Zaldibar?",
         "Sí, son pueblos vecinos y vamos igual que a Ermua. También a Eibar, Berriz, Durango y el resto de Durangaldea."),
        ("¿Hacéis presupuesto sin compromiso en Ermua?",
         "Sí. Con fotos o un vídeo por WhatsApp muchas veces ya podemos darte precio. Si hace falta verlo, pasamos por tu casa sin compromiso."),
        ("¿Trabajáis con comunidades y administradores de fincas de Ermua?",
         "Sí: bajantes, colectores, contadores, atascos en garajes y averías en zonas comunes. Damos factura oficial y la documentación que pida la comunidad o el seguro."),
        ("¿Instaláis aerotermia o aire acondicionado en Ermua?",
         'Sí, en pisos y casas de Ermua. Primero miramos si tu vivienda es buena candidata para aerotermia. <a href="/aerotermia-climatizacion/">Más sobre aerotermia</a>.'),
    ]
    content = f'''<h2>Fontanería en Ermua, hecha por gente de Ermua</h2>
<p>MO-HOUSE es de Ermua. Cuando nos llamas desde Ermua no viene alguien de fuera que no conoce la zona: venimos nosotros, que estamos a pocos minutos y conocemos cómo están hechos los edificios del pueblo.</p>
<p>Atendemos a particulares, comunidades de vecinos, comercios y talleres de Ermua, y también de Mallabia, Zaldibar y Eibar, que está pegado.</p>

<h2>Qué hacemos en Ermua</h2>
<ul>
<li><strong>Urgencias:</strong> fugas, roturas de tubería, filtraciones al piso de abajo y atascos, a cualquier hora.</li>
<li><strong>Fontanería:</strong> cambio de tuberías de plomo, hierro o cobre antiguo por multicapa, grifos, cisternas, termos y calentadores.</li>
<li><strong>Calefacción y aerotermia:</strong> radiadores, purgado y equilibrado, cambio a bomba de calor, aire acondicionado.</li>
<li><strong>Comunidades:</strong> bajantes (también de fibrocemento, con empresa autorizada), colectores de garaje y contadores.</li>
<li><strong>Baños y cocinas:</strong> cambio de bañera por plato de ducha, nuevas tomas y desagües. Mira <a href="/reparaciones-obras-ermua/">reparaciones y obras en Ermua</a>.</li>
</ul>

<h2>Los pisos de Ermua y sus instalaciones</h2>
<p>Ermua creció muchísimo entre los años 50 y 70, y gran parte de los pisos de esa época conservan la instalación original: tuberías que se pican, llaves de paso que ya no cierran, bajantes de fibrocemento con fisuras y radiadores que no calientan igual. Son averías que vemos cada semana.</p>
<p>Si vas a reformar el baño o la cocina, es buen momento para cambiar las tuberías que quedan detrás de los azulejos. Te decimos qué merece la pena cambiar y qué no.</p>

<h2>Cómo trabajamos</h2>
<ol>
<li>Nos llamas o nos mandas fotos por WhatsApp al {PHONE}.</li>
<li>Te damos un precio cerrado antes de empezar. Si hay que verlo, vamos sin compromiso.</li>
<li>Hacemos el trabajo y dejamos todo limpio.</li>
<li>Te damos factura oficial, válida para el seguro o la comunidad.</li>
</ol>
{photo_row([
    ("instalacion-contador-agua-manometro-eibar", "Contador de agua con reductor de presión y manómetro en Ermua", "Contador y reductor de presión, Ermua", None),
    ("reforma-bano-revestimiento-marmol-eibar", "Baño reformado con lavabo doble en Ermua", "Baño renovado, Ermua", None),
    ("montaje-plato-ducha-resina-blanco-eibar", "Plato de ducha de resina instalado en Ermua", "Plato de ducha, Ermua", None),
])}

<h2>Cerca de Ermua</h2>
<p>Desde Ermua llegamos enseguida a <a href="/fontanero-eibar/">Eibar</a>, Mallabia, Zaldibar y Berriz, y en pocos minutos a Durango, Elorrio y Abadiño. Mira todos los pueblos en <a href="/zona-de-servicio/">zona de servicio</a>.</p>
<p class="eu" lang="eu">Iturgina Ermuan: larrialdiak 24 orduz, ura, berogailua eta aerotermia. Deitu {PHONE} zenbakira.</p>'''
    body = inner(path, "Fontanero en Ermua", "Fontanero en Ermua",
                 "Urgencias 24 h, reparaciones e instalaciones. Somos de Ermua.",
                 f"Fugas, atascos, calefacción, aerotermia y bajantes en Ermua, Mallabia y Zaldibar. Llegamos en 20 a 30 minutos y te damos el precio antes de empezar.",
                 hero, "Ducha nueva en lugar de bañera en un piso de Ermua", "<strong>Cambio de bañera por ducha</strong>Vivienda en Ermua", "50% 70%",
                 "ermua", msg, content, faqs,
                 [("/reparaciones-obras-ermua/", "Reparaciones y obras en Ermua"), ("/fontanero-eibar/", "Fontanero en Eibar"),
                  ("/urgencias-24h/", "Urgencias 24 h"), ("/aerotermia-climatizacion/", "Aerotermia y climatización"),
                  ("/bajantes-fibrocemento/", "Bajantes de fibrocemento")])
    title = "Fontanero en Ermua 24 h · Urgencias y Calefacción | MO-HOUSE"
    desc = f"Fontanero de Ermua: urgencias 24 h, fugas, atascos, calefacción, aerotermia y bajantes en Ermua, Mallabia y Zaldibar. Llegamos en 20-30 min. ☎ {PHONE}"
    url = SITE + path
    graph = [business(), webpage(path, title, desc, hero), breadcrumb(url, "Fontanero en Ermua"),
             service(path, "Fontanero en Ermua", "Plumbing",
                     "Fontanería, urgencias 24 horas, calefacción, aerotermia y bajantes en Ermua, Mallabia y Zaldibar.",
                     ["Ermua", "Mallabia", "Zaldibar", "Eibar"]),
             faq_schema(url, faqs)]
    write(path, page(path, title, desc, body, graph, preload(hero, "(max-width: 900px) 100vw, 520px")))
    PAGES.append((path, [hero, "instalacion-contador-agua-manometro-eibar", "reforma-bano-revestimiento-marmol-eibar", "montaje-plato-ducha-resina-blanco-eibar"]))


def build_eibar():
    path = "/fontanero-eibar/"
    hero = "fontaneria-cocina-fregadero-griferia-eibar"
    msg = "Hola MO-HOUSE, necesito un fontanero en Eibar."
    faqs = [
        ("¿Atendéis en todos los barrios de Eibar?",
         "Sí: centro, Amaña, Urki, Ipurua, Txonta, Legarre, Azitain, Barrena, Arrate y el resto. Estamos al lado, en Ermua."),
        ("¿Cuánto tardáis en llegar a una urgencia en Eibar?",
         f"Normalmente entre 20 y 30 minutos, a cualquier hora del día o de la noche. Llama al {PHONE}."),
        ("¿Cambiáis tuberías de plomo en pisos de Eibar?",
         "Sí. Es uno de los trabajos que más hacemos: cambiamos el plomo o el cobre antiguo por multicapa, por tramos o la instalación completa del piso."),
        ("¿Hacéis el cambio de bañera por plato de ducha?",
         "Sí, normalmente en uno o dos días: quitamos la bañera, adaptamos agua y desagüe, impermeabilizamos y montamos plato y mampara."),
        ("¿Dais factura para el seguro?",
         f"Sí, factura oficial con NIF {NIF}. Si la avería la cubre el seguro, te damos la factura y las fotos que te pidan."),
    ]
    content = f'''<h2>Tu fontanero en Eibar, a cinco minutos</h2>
<p>MO-HOUSE es de Ermua, pegado a Eibar, y buena parte de nuestro trabajo está en Eibar: pisos, comunidades, bajos comerciales y talleres. Atendemos cualquier barrio, del centro a Amaña, Urki, Ipurua, Txonta, Legarre, Azitain, Barrena o Arrate.</p>

<h2>Servicios en Eibar</h2>
<ul>
<li><strong>Urgencias 24 h:</strong> fugas, tuberías reventadas, agua que baja al vecino, atascos y calefacción parada.</li>
<li><strong>Tuberías:</strong> cambio de plomo y cobre antiguo por multicapa, llaves de paso, contadores y reductores de presión.</li>
<li><strong>Calefacción y clima:</strong> radiadores, aerotermia, aire acondicionado y mejora de instalaciones existentes.</li>
<li><strong>Comunidades:</strong> bajantes (también de fibrocemento con empresa autorizada), colectores y arquetas.</li>
<li><strong>Baños y cocinas:</strong> cambio de bañera por ducha, fregaderos, lavavajillas y nuevas tomas.</li>
</ul>

<h2>Edificios de Eibar: lo que solemos encontrar</h2>
<p>En Eibar hay muchos edificios de los años 50, 60 y 70, levantados cuando la ciudad creció con la industria. En esos pisos es habitual encontrar tuberías de plomo o cobre muy gastadas, hornacinas de contador con racores oxidados, bajantes comunitarias de fibrocemento y presiones de agua altas que acaban rompiendo latiguillos y grifos.</p>
<p>Muchas veces una fuga pequeña es el aviso de que el tramo entero está mal. Te lo explicamos y te damos las dos opciones: reparar el punto o cambiar el tramo.</p>

<h2>Cómo trabajamos</h2>
<ol>
<li>Llamas o mandas fotos por WhatsApp al {PHONE}.</li>
<li>Precio cerrado antes de empezar, sin sorpresas.</li>
<li>Trabajo hecho y zona limpia.</li>
<li>Factura oficial para ti, el seguro o la comunidad.</li>
</ol>
{photo_row([
    ("hornacina-contador-agua-llave-paso-eibar", "Contador de agua y llave de paso con racores oxidados en Eibar", "Hornacina de contador antes de cambiarla, Eibar", None),
    ("reparacion-bajante-comunitaria-pvc-eibar", "Bajante comunitaria de PVC en un edificio de Eibar", "Bajante comunitaria nueva, Eibar", None),
    ("instalacion-radiador-calefaccion-aluminio-eibar", "Radiador de aluminio instalado en un piso de Eibar", "Radiador nuevo, Eibar", None),
])}

<h2>Alrededor de Eibar</h2>
<p>Desde Eibar vamos a <a href="/fontanero-ermua/">Ermua</a>, Soraluze, Elgoibar, Mendaro, Deba, Bergara y Elgeta. Tienes la lista completa en <a href="/zona-de-servicio/">zona de servicio</a>.</p>
<p class="eu" lang="eu">Iturgina Eibarren: larrialdiak 24 orduz, ur-ihesak, buxadurak, berogailua eta aerotermia. Deitu {PHONE} zenbakira.</p>'''
    body = inner(path, "Fontanero en Eibar", "Fontanero en Eibar",
                 "Urgencias 24 h en todos los barrios. Fontanería, calefacción y aerotermia.",
                 "Estamos al lado, en Ermua: llegamos a cualquier barrio de Eibar en 20 a 30 minutos. Precio cerrado antes de empezar y factura oficial.",
                 hero, "Fregadero y grifería instalados en una cocina de Eibar", "<strong>Fregadero y grifería nuevos</strong>Cocina en Eibar", "50% 40%",
                 "eibar", msg, content, faqs,
                 [("/fontanero-ermua/", "Fontanero en Ermua"), ("/urgencias-24h/", "Urgencias 24 h"),
                  ("/aerotermia-climatizacion/", "Aerotermia y climatización"), ("/bajantes-fibrocemento/", "Bajantes de fibrocemento"),
                  ("/zona-de-servicio/#debabarrena", "Bajo Deba")])
    title = "Fontanero en Eibar 24 h · Urgencias y Calefacción | MO-HOUSE"
    desc = f"Fontanero en Eibar las 24 h: fugas, atascos, tuberías de plomo, calefacción y aerotermia en todos los barrios. Llegamos en 20-30 min. ☎ {PHONE}"
    url = SITE + path
    graph = [business(), webpage(path, title, desc, hero), breadcrumb(url, "Fontanero en Eibar"),
             service(path, "Fontanero en Eibar", "Plumbing",
                     "Fontanería, urgencias 24 horas, calefacción, aerotermia y bajantes en todos los barrios de Eibar.",
                     ["Eibar", "Soraluze", "Ermua"]),
             faq_schema(url, faqs)]
    write(path, page(path, title, desc, body, graph, preload(hero, "(max-width: 900px) 100vw, 520px")))
    PAGES.append((path, [hero, "hornacina-contador-agua-llave-paso-eibar", "reparacion-bajante-comunitaria-pvc-eibar", "instalacion-radiador-calefaccion-aluminio-eibar"]))


def build_urgencias():
    path = "/urgencias-24h/"
    hero = "tuberias-cobre-oxidadas-contador-agua-eibar"
    msg = "Hola MO-HOUSE, tengo una urgencia de fontanería."
    faqs = [
        ("¿De verdad atendéis a las 3 de la mañana?",
         f"Sí. El {PHONE} está operativo las 24 horas, también domingos y festivos. Si no podemos coger en ese momento, te devolvemos la llamada enseguida."),
        ("¿Cuánto cuesta una urgencia?",
         "Depende de la hora y del trabajo. Te decimos el precio por teléfono antes de salir, para que decidas con calma."),
        ("¿Cuánto tardáis?",
         "En Ermua y Eibar, 20 a 30 minutos. En el resto de la zona, según la distancia; te lo decimos al llamar."),
        ("¿Lo paga el seguro?",
         "Muchas pólizas cubren los daños por agua. Te damos factura oficial y fotos del antes y el después para que lo presentes."),
    ]
    content = f'''<h2>Urgencias que atendemos</h2>
<ul>
<li><strong>Fugas y tuberías rotas:</strong> agua que sale de la pared o del suelo, latiguillos reventados, llaves de paso que gotean.</li>
<li><strong>Filtraciones al vecino:</strong> localizamos de dónde sale el agua y la cortamos.</li>
<li><strong>Atascos:</strong> fregadero, inodoro, ducha, bajante o colector del garaje.</li>
<li><strong>Sin agua caliente o sin calefacción:</strong> termos, calentadores, radiadores y aerotermia.</li>
<li><strong>Contador y acometida:</strong> fugas en la hornacina del contador o en la llave general.</li>
</ul>

<h2>Qué hacer mientras llegamos</h2>
<ol>
<li><strong>Cierra la llave de paso</strong> de la vivienda. Suele estar en la cocina, en el baño o junto al contador.</li>
<li>Si el agua está cerca de enchufes o del cuadro eléctrico, <strong>corta la luz</strong> de esa zona.</li>
<li>Recoge el agua que puedas y aparta lo que se pueda mojar.</li>
<li><strong>Haz fotos</strong> de la avería y de los daños: te harán falta para el seguro.</li>
<li>Si el agua baja a otro piso, avisa al vecino de abajo.</li>
</ol>
<p>Si no encuentras la llave de paso o no cierra, llámanos y te guiamos por teléfono.</p>

<h2>Dónde atendemos urgencias</h2>
<p>En <a href="/fontanero-ermua/">Ermua</a> y <a href="/fontanero-eibar/">Eibar</a> llegamos en 20 a 30 minutos. También vamos a Mallabia, Soraluze, Elgoibar, Zaldibar, Berriz, Durango, Bergara y el resto de pueblos de nuestra <a href="/zona-de-servicio/">zona de servicio</a>.</p>
{photo_row([
    ("plato-ducha-roto-agrietado-filtracion-eibar", "Plato de ducha roto que filtraba al piso de abajo", "Plato roto con filtración al vecino", None),
    ("atasco-tapon-grasa-colector-bajante-eibar", "Tapón de grasa dentro de una bajante atascada", "Tapón de grasa en bajante", "50% 50%"),
    ("reparacion-tuberia-plomo-cobre-eibar", "Tubería de plomo picada sustituida por multicapa", "Tubería de plomo picada", None),
])}'''
    body = inner(path, "Urgencias 24 h", "Fontanero urgente 24 horas",
                 "Ermua, Eibar y alrededores. Todos los días del año.",
                 f"Fugas, tuberías rotas, atascos y filtraciones al vecino. Llama al {PHONE}: te atiende el instalador y te decimos el precio antes de salir.",
                 hero, "Tuberías de cobre oxidadas con fuga junto al contador de agua", "<strong>Fuga en tuberías de cobre</strong>Aviso urgente en Eibar", "50% 40%",
                 "urgencias", msg, content, faqs,
                 [("/fontanero-ermua/", "Fontanero en Ermua"), ("/fontanero-eibar/", "Fontanero en Eibar"),
                  ("/bajantes-fibrocemento/", "Bajantes de fibrocemento"), ("/zona-de-servicio/", "Zona de servicio")])
    title = "Fontanero Urgente 24 h en Ermua y Eibar | MO-HOUSE"
    desc = f"Fontanero urgente 24 horas en Ermua, Eibar y alrededores: fugas, tuberías rotas, atascos y filtraciones. Llegamos en 20-30 min. ☎ {PHONE}"
    url = SITE + path
    graph = [business(), webpage(path, title, desc, hero), breadcrumb(url, "Urgencias 24 h"),
             service(path, "Fontanero urgente 24 horas", "Emergency plumbing",
                     "Urgencias de fontanería 24 horas: fugas, roturas, atascos, filtraciones y averías de agua caliente y calefacción.",
                     ["Ermua", "Eibar", "Mallabia", "Soraluze", "Elgoibar", "Zaldibar", "Berriz", "Durango", "Bergara"]),
             faq_schema(url, faqs)]
    write(path, page(path, title, desc, body, graph, preload(hero, "(max-width: 900px) 100vw, 520px")))
    PAGES.append((path, [hero, "plato-ducha-roto-agrietado-filtracion-eibar", "atasco-tapon-grasa-colector-bajante-eibar", "reparacion-tuberia-plomo-cobre-eibar"]))


def build_aerotermia():
    path = "/aerotermia-climatizacion/"
    hero = "tomas-lavadora-climatizacion-terraza-eibar"
    msg = "Hola MO-HOUSE, quiero información sobre aerotermia / aire acondicionado / calefacción."
    faqs = [
        ("¿La aerotermia funciona en Ermua y Eibar?",
         "Sí. Los inviernos del valle son húmedos pero no extremos, y una bomba de calor aire-agua bien dimensionada rinde bien. Lo importante es elegir la potencia adecuada y revisar los emisores."),
        ("¿Puedo poner aerotermia con mis radiadores?",
         "Depende. Algunos radiadores sirven tal cual, otros hay que ampliarlos o cambiarlos por modelos de baja temperatura. Lo revisamos en la visita antes de darte presupuesto."),
        ("¿Dónde va la unidad exterior en un piso?",
         "Normalmente en la terraza, el tendedero o la fachada si la comunidad lo permite. Comprobamos el espacio, el ruido y el desagüe antes de proponerlo."),
        ("¿Hacéis mantenimiento de equipos ya instalados?",
         "Sí: revisión de aire acondicionado, purgado y equilibrado de radiadores y revisión de instalaciones de aerotermia."),
    ]
    content = f'''<h2>Aerotermia</h2>
<p>La aerotermia es una bomba de calor que saca energía del aire exterior para dar calefacción y agua caliente, y en muchos casos también frío en verano. Gasta electricidad, pero bastante menos de la que consume un termo o una calefacción eléctrica para dar el mismo calor.</p>
<p>No a todas las casas les conviene igual. Antes de darte precio miramos:</p>
<ul>
<li>Qué calefacción tienes ahora y cuánto consume.</li>
<li>Si tus radiadores sirven para trabajar a menor temperatura o conviene cambiar alguno.</li>
<li>Dónde se puede colocar la unidad exterior y el depósito de agua caliente.</li>
<li>Cuántas personas viven en casa y cuánta agua caliente usáis.</li>
</ul>

<h2>Aire acondicionado</h2>
<p>Instalamos equipos split para una habitación, multisplit para varias con una sola unidad exterior y climatización por conductos cuando hay falso techo. Hacemos la instalación completa: soportes, línea frigorífica, desagüe y puesta en marcha.</p>

<h2 id="calefaccion">Calefacción y radiadores</h2>
<ul>
<li>Instalación y renovación de calefacción, circuito completo o por tramos.</li>
<li>Radiadores nuevos, válvulas termostáticas y purgado y equilibrado de la instalación.</li>
<li>Radiadores que no calientan, ruidos en la instalación o pérdidas de presión.</li>
<li>Cambio de calefacción antigua a aerotermia.</li>
</ul>

<h2>Dónde instalamos</h2>
<p>En <a href="/fontanero-ermua/">Ermua</a>, <a href="/fontanero-eibar/">Eibar</a> y los pueblos de alrededor: Elgoibar, Soraluze, Durango, Elorrio, Bergara, Arrasate y el resto de nuestra <a href="/zona-de-servicio/">zona de servicio</a>.</p>
{photo_row([
    ("instalacion-climatizador-terraza-eibar", "Unidad exterior de bomba de calor en la terraza de un piso de Ermua", "Unidad exterior en terraza, Ermua", "50% 25%"),
    ("instalacion-radiador-calefaccion-aluminio-eibar", "Radiador de aluminio con válvula termostática en Eibar", "Radiador de aluminio, Eibar", None),
    ("instalacion-tuberias-multicapa-bano-eibar", "Circuito de tuberías multicapa de agua caliente y fría", "Circuitos de agua caliente", None),
])}'''
    body = inner(path, "Aerotermia y climatización", "Aerotermia, aire acondicionado y calefacción",
                 "En Ermua, Eibar y alrededores.",
                 "Instalamos aerotermia, aire acondicionado y calefacción en pisos y casas. Primero vemos qué te conviene; luego te damos un presupuesto cerrado.",
                 hero, "Unidad exterior de bomba de calor sobre la lavadora en una terraza", "<strong>Bomba de calor en terraza</strong>Instalación en Ermua", "50% 10%",
                 "aerotermia", msg, content, faqs,
                 [("/fontanero-ermua/", "Fontanero en Ermua"), ("/fontanero-eibar/", "Fontanero en Eibar"),
                  ("/urgencias-24h/", "Urgencias 24 h"), ("/zona-de-servicio/", "Zona de servicio")])
    title = "Aerotermia y Aire Acondicionado en Eibar y Ermua | MO-HOUSE"
    desc = "Instalación de aerotermia, aire acondicionado y calefacción en Ermua, Eibar y alrededores. Estudio previo y presupuesto cerrado sin compromiso."
    url = SITE + path
    graph = [business(), webpage(path, title, desc, hero), breadcrumb(url, "Aerotermia y climatización"),
             service(path, "Aerotermia, aire acondicionado y calefacción", "HVAC",
                     "Instalación y renovación de aerotermia, aire acondicionado (split, multisplit, conductos) y calefacción con radiadores.",
                     ["Ermua", "Eibar", "Elgoibar", "Soraluze", "Durango", "Elorrio", "Bergara", "Arrasate-Mondragón"]),
             faq_schema(url, faqs)]
    write(path, page(path, title, desc, body, graph, preload(hero, "(max-width: 900px) 100vw, 520px")))
    PAGES.append((path, [hero, "instalacion-climatizador-terraza-eibar", "instalacion-radiador-calefaccion-aluminio-eibar", "instalacion-tuberias-multicapa-bano-eibar"]))


def build_bajantes():
    path = "/bajantes-fibrocemento/"
    hero = "sustitucion-bajante-general-edificio-eibar"
    msg = "Hola MO-HOUSE, somos una comunidad y queremos presupuesto para cambiar la bajante."
    faqs = [
        ("¿Es obligatorio quitar la bajante de uralita?",
         "Mientras esté en buen estado no hay que tocarla. Pero la Ley 7/2022 de residuos obliga a los ayuntamientos a censar las instalaciones con amianto y a planificar su retirada, y una bajante con fisuras o filtraciones conviene cambiarla cuanto antes."),
        ("¿Quién retira el fibrocemento?",
         "Una empresa autorizada inscrita en el RERA, con su plan de trabajo aprobado por la autoridad laboral (OSALAN en Euskadi). Nosotros coordinamos la obra e instalamos la bajante nueva."),
        ("¿Los vecinos tienen que salir de casa?",
         "Normalmente no. Os avisamos con antelación de los ratos en los que no se podrá usar el baño o la cocina de cada piso."),
        ("¿Qué documentación dais a la comunidad?",
         "Presupuesto detallado para la junta, factura oficial y el certificado de gestión de residuos de la empresa autorizada, útil para la ITE y el seguro."),
    ]
    content = f'''<h2>Cuándo hay que cambiar la bajante</h2>
<ul>
<li>Manchas de humedad o filtraciones en los patinillos o en los baños de los pisos de abajo.</li>
<li>Malos olores en el baño o la cocina que no se van.</li>
<li>Atascos que se repiten en la misma columna.</li>
<li>La ITE señala la bajante como deficiente.</li>
<li>La bajante es de fibrocemento (uralita) y está agrietada o rota.</li>
</ul>
<p>En Ermua y Eibar hay muchos edificios de los años 50 a 70 que todavía tienen las bajantes originales de fibrocemento.</p>

<h2>Cómo lo hacemos</h2>
<ol>
<li><strong>Visita y presupuesto</strong> para la comunidad, con lo que hay que hacer en cada piso.</li>
<li><strong>Retirada del fibrocemento</strong> por una empresa autorizada inscrita en el RERA, con plan de trabajo aprobado por OSALAN y gestión de los residuos.</li>
<li><strong>Bajante nueva</strong> de PVC serie B insonorizado, con abrazaderas antivibración y manguitos de dilatación, y conexión de los desagües de cada vivienda.</li>
<li><strong>Prueba</strong> de funcionamiento y cierre de los registros.</li>
<li><strong>Documentación:</strong> factura oficial y certificado de residuos para la ITE y el seguro.</li>
</ol>

<h2>Otros trabajos de saneamiento</h2>
<ul>
<li>Reparación de tramos de bajante de PVC o hierro.</li>
<li>Colectores colgados en garajes y arquetas.</li>
<li>Desatascos de bajantes y colectores con máquina.</li>
</ul>
{photo_row([
    ("bajante-averiada-muro-bano-eibar", "Bajante antigua de fibrocemento al abrir el muro de un baño", "Bajante antigua de fibrocemento", None),
    ("bajante-comunitaria-rota-antes-eibar", "Bajante comunitaria rota antes de sustituirla", "Bajante rota, antes del cambio", None),
    ("reparacion-bajante-comunitaria-pvc-eibar", "Bajante comunitaria nueva de PVC insonorizado", "Bajante nueva de PVC", None),
])}
<p>Trabajamos con comunidades y administradores de fincas de <a href="/fontanero-ermua/">Ermua</a>, <a href="/fontanero-eibar/">Eibar</a>, Elgoibar, Durango, Bergara y el resto de la <a href="/zona-de-servicio/">zona</a>.</p>'''
    body = inner(path, "Bajantes de fibrocemento", "Cambio de bajantes de fibrocemento (uralita)",
                 "Para comunidades de Ermua, Eibar y alrededores.",
                 "Coordinamos la retirada del fibrocemento con una empresa autorizada e instalamos la bajante nueva de PVC insonorizado. Presupuesto claro para la junta de vecinos.",
                 hero, "Sustitución de la bajante general de un edificio", "<strong>Bajante general en obra</strong>Comunidad de vecinos", "50% 40%",
                 "bajantes", msg, content, faqs,
                 [("/fontanero-ermua/", "Fontanero en Ermua"), ("/fontanero-eibar/", "Fontanero en Eibar"),
                  ("/urgencias-24h/", "Urgencias 24 h"), ("/zona-de-servicio/", "Zona de servicio")])
    title = "Cambio de Bajantes de Uralita en Eibar y Ermua | MO-HOUSE"
    desc = "Cambio de bajantes comunitarias de fibrocemento en Ermua, Eibar y alrededores: retirada por empresa autorizada RERA y bajante nueva de PVC insonorizado."
    url = SITE + path
    graph = [business(), webpage(path, title, desc, hero), breadcrumb(url, "Bajantes de fibrocemento"),
             service(path, "Cambio de bajantes de fibrocemento", "Plumbing",
                     "Sustitución de bajantes comunitarias: retirada del fibrocemento por empresa autorizada RERA e instalación de PVC serie B insonorizado.",
                     ["Ermua", "Eibar", "Elgoibar", "Soraluze", "Durango", "Bergara"]),
             faq_schema(url, faqs)]
    write(path, page(path, title, desc, body, graph, preload(hero, "(max-width: 900px) 100vw, 520px")))
    PAGES.append((path, [hero, "bajante-averiada-muro-bano-eibar", "bajante-comunitaria-rota-antes-eibar", "reparacion-bajante-comunitaria-pvc-eibar"]))


def build_zona():
    path = "/zona-de-servicio/"
    zones = "".join(f'''<div class="zone" id="{z[0]}"><h3>{z[1]} <small>· {z[2]}</small></h3><p>{", ".join(z[3])}.</p><p style="margin-top:0.35rem">{z[4]}</p></div>''' for z in ZONAS)
    body = f'''<div class="container"><nav aria-label="Migas de pan"><ol class="breadcrumb"><li><a href="/">Inicio</a></li><li aria-current="page">Zona de servicio</li></ol></nav></div>
<section class="page-hero">
<div class="container">
<div class="section-head" style="margin-bottom:1.5rem">
<h1>Zona de servicio<span class="sub" style="display:block;font-size:0.5em;margin-top:0.6rem;color:#cfd8e3">Ermua, Eibar y los pueblos a menos de 25 km</span></h1>
<p class="lead">Somos de Ermua y trabajamos sobre todo en Ermua y Eibar. Desde aquí vamos a {len(ALL_TOWNS)} pueblos de Bizkaia, Gipuzkoa y Álava, con urgencias las 24 horas.</p>
<div class="cta-row">{btn_call("call-hero-zona")}{btn_wa("wa-hero-zona", "Hola MO-HOUSE, ¿venís a mi pueblo?", "Preguntar por WhatsApp")}</div>
</div>
<div class="place-cards">
<a class="place" href="/fontanero-ermua/"><h3>Fontanero en Ermua</h3><p>Nuestro pueblo. Urgencias en 20 a 30 minutos.</p><span class="card-link">Ver Ermua →</span></a>
<a class="place" href="/fontanero-eibar/"><h3>Fontanero en Eibar</h3><p>Todos los barrios. Urgencias en 20 a 30 minutos.</p><span class="card-link">Ver Eibar →</span></a>
</div>
</div>
</section>
<section class="section alt below">
<div class="container">
<div class="section-head"><h2>Pueblos que atendemos, por comarca</h2><p>Fontanería, urgencias, aerotermia, aire acondicionado, calefacción y bajantes en todos ellos.</p></div>
<div class="zones">{zones}</div>
<p class="note">¿No ves tu pueblo? Si está a menos de 25 km de Ermua, <a href="tel:{TEL}" data-conversion="call-zona-note">llámanos al {PHONE}</a> y te confirmamos.</p>
</div>
</section>
<section class="section below">
<div class="container">{cta_band("zona", "Hola MO-HOUSE, ¿venís a mi pueblo?")}</div>
</section>'''
    title = "Fontanero en Durango, Elgoibar, Soraluze y Bergara | MO-HOUSE"
    desc = "Fontanero en Ermua, Eibar, Elgoibar, Soraluze, Durango, Bergara, Arrasate, Markina, Ondarroa, Azpeitia y pueblos a 25 km. Urgencias 24 h."
    url = SITE + path
    graph = [business(), webpage(path, title, desc, "instalacion-tuberias-multicapa-bano-eibar"), breadcrumb(url, "Zona de servicio"),
             service(path, "Fontanería y climatización en Ermua, Eibar y alrededores", "Plumbing",
                     "Fontanería, urgencias 24 horas, aerotermia, aire acondicionado, calefacción y bajantes a menos de 25 km de Ermua.",
                     ALL_TOWNS)]
    write(path, page(path, title, desc, body, graph))
    PAGES.append((path, []))


def build_obras():
    path = "/reparaciones-obras-ermua/"
    hero = "reforma-bano-atico-vigas-eibar"
    msg = "Hola MO-HOUSE, quiero presupuesto para una reparación u obra en Ermua."
    faqs = [
        ("¿Hacéis obras pequeñas o solo reformas completas?",
         "Las dos cosas. Desde cerrar y alicatar el hueco que queda tras reparar una fuga hasta reformar el baño o la cocina entera."),
        ("¿Cuánto se tarda en cambiar la bañera por un plato de ducha?",
         "Normalmente uno o dos días: quitar la bañera, adaptar agua y desagüe, impermeabilizar, montar el plato y la mampara, y rematar el alicatado."),
        ("¿Tengo que buscar yo al albañil o al electricista?",
         "No. Nosotros hacemos la fontanería y coordinamos al resto de oficios que haga falta, así tratas con una sola persona y un solo presupuesto."),
        ("¿Hace falta permiso del Ayuntamiento de Ermua?",
         "Para obras interiores pequeñas suele bastar con comunicarlo al Ayuntamiento. Según la obra, te decimos qué hace falta antes de empezar."),
        ("¿Os lleváis el escombro?",
         "Sí. Retiramos el escombro y dejamos la vivienda limpia al terminar."),
    ]
    content = f'''<h2>Reparaciones en casa</h2>
<p>Muchas reparaciones empiezan por el agua: una fuga detrás del azulejo, un plato de ducha que filtra al vecino, una bajante que hay que abrir. Nosotros no nos quedamos en arreglar la tubería: cerramos el hueco, reponemos el alicatado y dejamos la pared o el suelo como estaban.</p>
<ul>
<li>Fugas y humedades: localizar, reparar y rematar la obra.</li>
<li>Platos de ducha rotos o que filtran.</li>
<li>Cambio de sanitarios, grifería, cisternas y termos.</li>
<li>Apertura y cierre de patinillos y registros.</li>
<li>Tuberías viejas que conviene cambiar antes de que den problemas.</li>
</ul>

<h2>Obras y reformas en Ermua</h2>
<ul>
<li><strong>Cambio de bañera por plato de ducha</strong>, en uno o dos días.</li>
<li><strong>Reforma de baño completa:</strong> instalación nueva de agua y desagües, plato o bañera, mueble, sanitarios y alicatado.</li>
<li><strong>Cocinas:</strong> nueva distribución de tomas, fregadero, lavavajillas y lavadora.</li>
<li><strong>Calefacción y radiadores</strong> aprovechando la obra.</li>
</ul>

<h2>Cómo organizamos una obra</h2>
<ol>
<li>Vamos a verla y te damos un presupuesto cerrado, por partidas.</li>
<li>Hacemos la fontanería y coordinamos al albañil, al electricista y al alicatador cuando hacen falta. Hablas con una sola persona.</li>
<li>Te decimos cuántos días va a durar y qué partes de la casa no podrás usar.</li>
<li>Al terminar retiramos el escombro, limpiamos y te damos factura oficial.</li>
</ol>

<h2>Baños de los pisos de Ermua</h2>
<p>En muchos pisos de Ermua de los años 60 y 70 el baño todavía tiene la bañera original y las tuberías de entonces. Si vas a reformarlo, es el momento de cambiar también las tuberías que quedan detrás de los azulejos: luego ya no se ven y es cuando más caro sale abrir.</p>
{photo_row([
    ("demolicion-murete-banera-antigua-eibar", "Demolición del murete de una bañera antigua", "Quitando la bañera antigua", None),
    ("obra-reforma-plato-ducha-proceso-eibar", "Obra de cambio de bañera por plato de ducha en proceso", "Plato de ducha durante la obra", None),
    ("cambio-banera-por-plato-ducha-eibar", "Ducha terminada con grifería negra tras la reforma", "Ducha terminada", "50% 70%"),
    ("adaptacion-desague-ducha-mortero-eibar", "Adaptación del desagüe de la ducha antes de la solera", "Nuevo desagüe de ducha", None),
    ("reforma-bano-mueble-lavabo-led-eibar", "Baño reformado con mueble de madera y espejo con luz", "Baño reformado", None),
    ("instalacion-inodoro-sanitario-eibar", "Inodoro nuevo instalado en un baño reformado", "Inodoro nuevo", None),
])}

<h2>También cerca de Ermua</h2>
<p>Hacemos reparaciones y obras en Mallabia, Zaldibar, <a href="/fontanero-eibar/">Eibar</a> y el resto de pueblos de nuestra <a href="/zona-de-servicio/">zona de servicio</a>. Para averías urgentes, mira <a href="/urgencias-24h/">urgencias 24 h</a>.</p>'''
    body = inner(path, "Reparaciones y obras en Ermua", "Reparaciones y obras en Ermua",
                 "Baños, cocinas y arreglos de casa, con presupuesto cerrado.",
                 "Somos de Ermua. Hacemos reparaciones del hogar y pequeñas obras: cambio de bañera por ducha, reformas de baño y cocina, y el remate de obra después de una fuga.",
                 hero, "Baño reformado con lavabos sobre encimera en un ático de Ermua", "<strong>Reforma de baño</strong>Ático en Ermua", "50% 55%",
                 "obras", msg, content, faqs,
                 [("/fontanero-ermua/", "Fontanero en Ermua"), ("/urgencias-24h/", "Urgencias 24 h"),
                  ("/aerotermia-climatizacion/", "Aerotermia y calefacción"), ("/bajantes-fibrocemento/", "Bajantes de fibrocemento"),
                  ("/fontanero-eibar/", "Fontanero en Eibar")])
    title = "Reparaciones y Obras en Ermua · Reformas de Baño | MO-HOUSE"
    desc = f"Reparaciones y pequeñas obras en Ermua: reformas de baño y cocina, cambio de bañera por ducha y arreglos tras fugas. Presupuesto cerrado. ☎ {PHONE}"
    url = SITE + path
    graph = [business(), webpage(path, title, desc, hero), breadcrumb(url, "Reparaciones y obras en Ermua"),
             service(path, "Reparaciones y obras en Ermua", "Home repair and renovation",
                     "Reparaciones del hogar y pequeñas obras: reformas de baño y cocina, cambio de bañera por plato de ducha y reparación de daños por agua.",
                     ["Ermua", "Mallabia", "Zaldibar", "Eibar"]),
             faq_schema(url, faqs)]
    write(path, page(path, title, desc, body, graph, preload(hero, "(max-width: 900px) 100vw, 520px")))
    PAGES.append((path, [hero, "demolicion-murete-banera-antigua-eibar", "obra-reforma-plato-ducha-proceso-eibar",
                         "cambio-banera-por-plato-ducha-eibar", "reforma-bano-mueble-lavabo-led-eibar", "instalacion-inodoro-sanitario-eibar"]))


def build_404():
    body = f'''<section class="section"><div class="container" style="max-width:640px;text-align:center">
<h1>Esta página no existe</h1>
<p class="lead" style="margin-left:auto;margin-right:auto">Puede que el enlace esté mal escrito o que la página se haya movido. Si tienes una avería, te atendemos directamente.</p>
<div class="cta-row" style="justify-content:center"><a class="btn btn-ghost" href="/">Ir al inicio</a>{btn_call("call-404")}{btn_wa("wa-404", "Hola MO-HOUSE, te escribo desde la web.")}</div>
</div></section>'''
    out = page("/404", "Página no encontrada | MO-HOUSE", "Página no encontrada.", body, [business()], robots="noindex, follow")
    out = out.replace(f'<link rel="canonical" href="{SITE}/404">\n', "")
    open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(out)
    print("  página: /404.html")


def build_sitemap():
    urls = []
    for path, imgs in PAGES:
        im = "".join(f"\n    <image:image><image:loc>{SITE}/images/opt/{b}-1200.webp</image:loc></image:image>" for b in imgs)
        urls.append(f"  <url>\n    <loc>{SITE}{path}</loc>\n    <lastmod>{TODAY}</lastmod>{im}\n  </url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + "\n".join(urls) + "\n</urlset>\n")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(xml)
    print("  sitemap.xml:", len(PAGES), "URLs")


if __name__ == "__main__":
    build_home()
    build_ermua()
    build_eibar()
    build_urgencias()
    build_aerotermia()
    build_bajantes()
    build_obras()
    build_zona()
    build_404()
    build_sitemap()
