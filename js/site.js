/* MO-HOUSE · JS común (menú móvil, galería, avisos legales y medición de conversiones) */
(function () {
  'use strict';

  // Menú móvil
  var btn = document.getElementById('menuBtn');
  var drawer = document.getElementById('drawer');
  function closeMenu() {
    if (!btn) return;
    drawer.classList.remove('open');
    btn.setAttribute('aria-expanded', 'false');
  }
  if (btn && drawer) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = drawer.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    drawer.addEventListener('click', function (e) { if (e.target.closest('a')) closeMenu(); });
    document.addEventListener('click', function (e) { if (!drawer.contains(e.target)) closeMenu(); });
  }

  // Modales
  function openModal(m) { m.classList.add('open'); document.body.style.overflow = 'hidden'; }
  function closeModals() {
    document.querySelectorAll('.modal.open').forEach(function (m) { m.classList.remove('open'); });
    document.body.style.overflow = '';
  }
  document.addEventListener('click', function (e) {
    if (e.target.classList.contains('modal') || e.target.closest('.modal-close')) closeModals();
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closeModals(); closeMenu(); } });

  // Galería: filtros y visor
  var filters = document.querySelectorAll('.filters button');
  var items = document.querySelectorAll('.gallery-item');
  filters.forEach(function (f) {
    f.addEventListener('click', function () {
      filters.forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
      f.setAttribute('aria-pressed', 'true');
      var cat = f.dataset.filter;
      items.forEach(function (it) { it.hidden = !(cat === 'all' || it.dataset.category === cat); });
    });
  });
  var lb = document.getElementById('lightbox');
  if (lb) {
    items.forEach(function (it) {
      it.addEventListener('click', function () {
        var title = it.dataset.title, place = it.dataset.place;
        lb.querySelector('img').src = it.dataset.full;
        lb.querySelector('img').alt = it.querySelector('img').alt;
        lb.querySelector('[data-lb="title"]').textContent = title;
        lb.querySelector('[data-lb="place"]').textContent = place;
        lb.querySelector('[data-lb="desc"]').textContent = it.dataset.desc;
        var msg = 'Hola MO-HOUSE, he visto en vuestra web el trabajo "' + title + '" (' + place + ') y quería pedir presupuesto.';
        lb.querySelector('[data-lb="wa"]').href = 'https://wa.me/34602383237?text=' + encodeURIComponent(msg);
        openModal(lb);
      });
    });
  }

  // Avisos legales
  var legal = document.getElementById('legal');
  var LEGAL = {
    aviso: ['Aviso legal', '<p>En cumplimiento del artículo 10 de la Ley 34/2002 (LSSI-CE):</p><ul><li><strong>Titular:</strong> MO-HOUSE</li><li><strong>NIF:</strong> Z0617960R</li><li><strong>Actividad:</strong> fontanería, climatización, aerotermia y calefacción; bajantes y saneamiento; renovación de baños y cocinas.</li><li><strong>Zona de servicio:</strong> Ermua, Eibar y alrededores (25 km).</li><li><strong>Teléfono:</strong> 602 38 32 37</li><li><strong>Email:</strong> mohamed.akhrif2016@gmail.com</li></ul>'],
    privacidad: ['Privacidad', '<p>Conforme al RGPD (UE) 2016/679 y la LOPDGDD 3/2018, los datos que nos facilitas por teléfono, WhatsApp o correo los trata MO-HOUSE (NIF Z0617960R) solo para atender tu solicitud, preparar presupuestos y emitir facturas.</p><p>No se ceden a terceros salvo obligación legal. Puedes ejercer tus derechos de acceso, rectificación y supresión escribiendo a mohamed.akhrif2016@gmail.com.</p>'],
    cookies: ['Cookies', '<p>Esta web solo usa cookies técnicas necesarias para funcionar. No usa cookies publicitarias ni de seguimiento de terceros.</p>']
  };
  document.querySelectorAll('[data-legal]').forEach(function (b) {
    b.addEventListener('click', function () {
      var d = LEGAL[b.dataset.legal];
      if (!d || !legal) return;
      legal.querySelector('[data-legal-title]').textContent = d[0];
      legal.querySelector('.modal-body').innerHTML = d[1];
      openModal(legal);
    });
  });

  // Año del pie
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // Conversiones (Google Ads / GA4 vía GTM): evento lead_click en cada CTA
  window.dataLayer = window.dataLayer || [];
  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-conversion]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    window.dataLayer.push({
      event: 'lead_click',
      lead_channel: href.indexOf('tel:') === 0 ? 'phone' : href.indexOf('wa.me') > -1 ? 'whatsapp' : href.indexOf('google') > -1 || href.indexOf('share.google') > -1 ? 'google_maps' : 'other',
      lead_location: a.dataset.conversion,
      page: location.pathname
    });
  });
})();
