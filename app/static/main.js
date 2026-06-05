const titles = {
    negocios: {
        title: 'Mi Local',
        subtitle: 'Gestiona tus certificaciones, historial y reseñas de clientes.',
    },
    clientes: {
        title: 'Mapa Interactivo',
        subtitle: 'Visualiza la distribución y opiniones de tus clientes.',
    },
    normativas: {
        title: 'Normativas y Prevención',
        subtitle: 'Información vital sobre NOMs, sanidad y control de plagas.',
    },
};

function showSection(sectionId, element) {
    const buttons = document.querySelectorAll('.nav-btn');
    buttons.forEach((btn) => btn.classList.remove('active'));

    if (element) {
        element.classList.add('active');
    }

    const sections = document.querySelectorAll('.content-section');
    sections.forEach((sec) => sec.classList.remove('active'));

    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    const titleElement = document.getElementById('page-title');
    const subtitleElement = document.getElementById('page-subtitle');
    if (titleElement && subtitleElement && titles[sectionId]) {
        titleElement.innerText = titles[sectionId].title;
        subtitleElement.innerText = titles[sectionId].subtitle;
    }
}

window.showSection = showSection;

// ---- Certificaciones: fetch + render ----
async function loadCertificaciones(uuid) {
    if (!uuid) return;
    const errEl = document.getElementById('cert-error');
    try {
        const res = await fetch(`/api/certificaciones/${encodeURIComponent(uuid)}`);
        if (!res.ok) throw new Error('network');
        const data = await res.json();
        const info = Array.isArray(data) ? data[0] : data;
        const count = info && (info.count ?? (info.certificaciones ? info.certificaciones.length : 0));
        const certs = info && info.certificaciones ? info.certificaciones : [];

        const histEl = document.getElementById('historial-count');
        if (histEl) histEl.innerText = `Historial: ${count ?? 0} certificaciones`;

        const list = document.getElementById('certificaciones-list');
        if (!list) return;
        list.innerHTML = '';

        if (!certs || certs.length === 0) {
            list.innerHTML = '<p>No hay certificaciones registradas.</p>';
            return;
        }

        certs.forEach(c => {
            const nombre = c.nombre ?? c.name ?? 'Sin nombre';
            const fecha = c.fecha_vencimiento ?? c.fecha_vencimiento_iso ?? c.fecha ?? null;

            const card = document.createElement('div');
            card.className = 'cert-card card';

            const title = document.createElement('div');
            title.style.fontWeight = '700';
            title.innerText = nombre;
            card.appendChild(title);

            if (fecha) {
                const dateP = document.createElement('div');
                dateP.innerText = `Vencimiento: ${fecha}`;
                card.appendChild(dateP);

                // try parse date
                const venc = new Date(fecha);
                const now = new Date();
                const isValidDate = !isNaN(venc.getTime());
                const badge = document.createElement('span');
                badge.style.marginTop = '6px';
                if (isValidDate && venc > now) {
                    badge.className = 'admin-badge';
                    badge.innerText = 'Activa';
                } else if (isValidDate) {
                    badge.className = 'badge-expired';
                    badge.innerText = 'Vencida';
                } else {
                    badge.className = 'badge-unknown';
                    badge.innerText = 'Estado desconocido';
                }
                card.appendChild(badge);
            } else {
                const badge = document.createElement('span');
                badge.className = 'badge-unknown';
                badge.innerText = 'Estado desconocido';
                card.appendChild(badge);
            }

            list.appendChild(card);
        });
    } catch (e) {
        if (errEl) {
            errEl.style.display = 'block';
            errEl.innerText = 'Error al obtener certificaciones.';
        }
        console.error(e);
    }
}

// auto-load when negocios shown (and when an empresa UUID is provided via meta or global)
function tryLoadCertsIfNeeded(sectionId) {
    if (sectionId !== 'negocios') return;
    if (window._certsLoaded) return;
    const meta = document.querySelector('meta[name="empresa-uuid"]');
    const uuid = (meta && meta.content) || window.EMPRESA_UUID || '';
    if (!uuid) return; // nothing to load
    loadCertificaciones(uuid);
    window._certsLoaded = true;
}

// wrap original showSection to trigger cert load
const _origShow = showSection;
window.showSection = function(sectionId, element) {
    _origShow(sectionId, element);
    tryLoadCertsIfNeeded(sectionId);
};

// on load, if negocios is active, attempt to load
document.addEventListener('DOMContentLoaded', () => {
    const active = document.querySelector('.content-section.active');
    if (active && active.id === 'negocios') tryLoadCertsIfNeeded('negocios');
});