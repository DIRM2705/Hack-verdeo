/**
 * empleados.js
 * Módulo de gestión de empleados
 * Dependencias: Tailwind CSS, Font Awesome
 */

/* ═══════════════════════════════════════════
   CONFIGURACIÓN DE BADGES DISPONIBLES
═══════════════════════════════════════════ */
const BADGES_CATALOG = [
  { id: 'lider', label: 'Líder', color: 'bg-violet-50 text-violet-700 border-violet-200', icon: 'fa-star' },
  { id: 'mentor', label: 'Mentor', color: 'bg-amber-50 text-amber-700 border-amber-200', icon: 'fa-graduation-cap' },
  { id: 'fullstack', label: 'Full Stack', color: 'bg-blue-50 text-blue-700 border-blue-200', icon: 'fa-code' },
  { id: 'qa', label: 'QA', color: 'bg-teal-50 text-teal-700 border-teal-200', icon: 'fa-bug' },
  { id: 'agile', label: 'Agile', color: 'bg-emerald-50 text-emerald-700 border-emerald-200', icon: 'fa-arrows-spin' },
  { id: 'cloud', label: 'Cloud', color: 'bg-sky-50 text-sky-700 border-sky-200', icon: 'fa-cloud' },
  { id: 'seguridad', label: 'Seguridad', color: 'bg-rose-50 text-rose-700 border-rose-200', icon: 'fa-shield-halved' },
  { id: 'diseño', label: 'Diseño UX', color: 'bg-pink-50 text-pink-700 border-pink-200', icon: 'fa-pen-ruler' },
  { id: 'ventas', label: 'Top Ventas', color: 'bg-orange-50 text-orange-700 border-orange-200', icon: 'fa-trophy' },
  { id: 'innovador', label: 'Innovador', color: 'bg-indigo-50 text-indigo-700 border-indigo-200', icon: 'fa-lightbulb' },
];

const STATUS_STYLES = {
  'Activo': 'bg-emerald-50 text-emerald-700 border-emerald-200',
  'Inactivo': 'bg-slate-100 text-slate-500 border-slate-200',
  'Licencia': 'bg-amber-50 text-amber-700 border-amber-200',
};

const AVATAR_COLORS = [
  'bg-blue-100 text-blue-700', 'bg-violet-100 text-violet-700',
  'bg-emerald-100 text-emerald-700', 'bg-amber-100 text-amber-700',
  'bg-rose-100 text-rose-700', 'bg-teal-100 text-teal-700',
];

/* ═══════════════════════════════════════════
   ESTADO GLOBAL
═══════════════════════════════════════════ */
let employees = [];
let modalBadges = [];

/* ═══════════════════════════════════════════
   FUNCIONES AUXILIARES
═══════════════════════════════════════════ */
function getBadge(id) {
  return BADGES_CATALOG.find(b => b.id === id);
}

function avatarColor(name) {
  const idx = (name.charCodeAt(0) + (name.charCodeAt(1) || 0)) % AVATAR_COLORS.length;
  return AVATAR_COLORS[idx];
}

function showToast(msg, success = true) {
  const t = document.getElementById('toast');
  const icon = document.getElementById('toast-icon');
  document.getElementById('toast-msg').textContent = msg;
  icon.className = success
    ? 'fa-solid fa-circle-check text-emerald-400'
    : 'fa-solid fa-circle-exclamation text-amber-400';
  t.style.opacity = '1';
  setTimeout(() => t.style.opacity = '0', 2800);
}

/* ═══════════════════════════════════════════
   RENDER TABLA
═══════════════════════════════════════════ */
function renderTable() {
  const q = document.getElementById('search-input').value.toLowerCase();
  const tbody = document.getElementById('employees-tbody');
  const empty = document.getElementById('empty-state');
  const countLbl = document.getElementById('count-label');

  const filtered = employees.filter((e) => {
    const full = `${e.nombre} ${e.apellido} ${e.correo}`.toLowerCase();
    return (!q || full.includes(q));
  });

  tbody.innerHTML = '';

  if (filtered.length === 0) {
    empty.classList.remove('hidden');
    countLbl.textContent = '';
    return;
  }
  empty.classList.add('hidden');

  filtered.forEach((e, fi) => {
    const origIdx = employees.indexOf(e);
    const initials = (e.nombre[0] || '') + (e.apellido[0] || '');
    const avatarCls = avatarColor(e.nombre);
    const badgesHtml = (e.badges || []).slice(0, 3).map(id => {
      const b = getBadge(id);
      if (!b) return '';
      return `<span class="badge-pill ${b.color}"><i class="fa-solid ${b.icon} text-xs"></i>${b.label}</span>`;
    }).join('') + (e.badges.length > 3 ? `<span class="text-xs text-slate-400 font-medium">+${e.badges.length - 3}</span>` : '');

    const tr = document.createElement('tr');
    tr.className = 'employee-row animate-row';
    tr.style.animationDelay = `${fi * 40}ms`;
    tr.innerHTML = `
      <td class="px-5 py-3.5">
        <div class="flex items-center gap-3">
          <div class="avatar ${avatarCls}">${initials}</div>
          <div>
            <p class="font-semibold text-slate-800">${escapeHtml(e.nombre)} ${escapeHtml(e.apellido)}</p>
            <p class="text-xs text-slate-400 mono">${escapeHtml(e.correo)}</p>
          </div>
        </div>
      </td>
      <td class="px-5 py-3.5 hidden md:table-cell">
        <div class="flex flex-wrap gap-1.5">${badgesHtml || '<span class="text-slate-300 text-xs">Sin badges</span>'}</div>
      </td>
      <td class="px-5 py-3.5 text-right">
        <div class="flex items-center justify-end gap-1">
          <button onclick="openModal('edit', ${origIdx})"
            class="w-8 h-8 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-blue-600 transition flex items-center justify-center"
            title="Editar">
            <i class="fa-solid fa-pen text-xs"></i>
          </button>
          <button onclick="openBadgeManager(${origIdx})"
            class="w-8 h-8 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-violet-600 transition flex items-center justify-center"
            title="Gestionar badges">
            <i class="fa-solid fa-tag text-xs"></i>
          </button>
          <button onclick="deleteEmployee(${origIdx})"
            class="w-8 h-8 rounded-lg hover:bg-rose-50 text-slate-400 hover:text-rose-500 transition flex items-center justify-center"
            title="Eliminar">
            <i class="fa-solid fa-trash text-xs"></i>
          </button>
        </div>
      </td>`;
    tbody.appendChild(tr);
  });

  countLbl.textContent = `${filtered.length} empleado${filtered.length !== 1 ? 's' : ''}`;
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>]/g, function (m) {
    if (m === '&') return '&amp;';
    if (m === '<') return '&lt;';
    if (m === '>') return '&gt;';
    return m;
  });
}

/* ═══════════════════════════════════════════
   FILTRO
═══════════════════════════════════════════ */
function filterTable() {
  renderTable();
}

/* ═══════════════════════════════════════════
   MODAL - BADGES
═══════════════════════════════════════════ */
function initBadgeSelect() {
  const sel = document.getElementById('f-badge-select');
  sel.innerHTML = '<option value="">— Agregar badge —</option>';
  BADGES_CATALOG.forEach(b => {
    sel.innerHTML += `<option value="${b.id}">${b.label}</option>`;
  });
}

function renderModalBadges() {
  const container = document.getElementById('f-badges-container');
  container.innerHTML = modalBadges.map(id => {
    const b = getBadge(id);
    if (!b) return '';
    return `<span class="badge-pill ${b.color}">
      <i class="fa-solid ${b.icon} text-xs"></i>${b.label}
      <button type="button" onclick="removeBadge('${id}')" title="Quitar badge">&times;</button>
    </span>`;
  }).join('') || '<span class="text-xs text-slate-400">Sin badges asignados</span>';
}

function addBadgeFromSelect() {
  const sel = document.getElementById('f-badge-select');
  const val = sel.value;
  if (!val) return;
  if (modalBadges.includes(val)) {
    showToast('Badge ya agregado', false);
    sel.value = '';
    return;
  }
  modalBadges.push(val);
  sel.value = '';
  renderModalBadges();
}

function removeBadge(id) {
  modalBadges = modalBadges.filter(b => b !== id);
  renderModalBadges();
}

/* ═══════════════════════════════════════════
   MODAL - CRUD
═══════════════════════════════════════════ */
function openModal(mode, idx = null) {
  const backdrop = document.getElementById('modal-backdrop');
  const title = document.getElementById('modal-title');
  modalBadges = [];

  if (mode === 'edit' && idx !== null) {
    const e = employees[idx];
    title.textContent = 'Editar empleado';
    document.getElementById('edit-index').value = idx;
    document.getElementById('f-nombre').value = e.nombre;
    document.getElementById('f-apellido').value = e.apellido;
    document.getElementById('f-correo').value = e.correo;
    document.getElementById('f-dept').value = e.dept || '';
    document.getElementById('f-estatus').value = e.estatus || 'Activo';
    modalBadges = [...(e.badges || [])];
  } else {
    title.textContent = 'Nuevo empleado';
    document.getElementById('edit-index').value = '';
    ['f-nombre', 'f-apellido', 'f-correo'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('f-dept').value = '';
    document.getElementById('f-estatus').value = 'Activo';
  }

  renderModalBadges();
  backdrop.classList.add('open');
}

function openBadgeManager(idx) {
  openModal('edit', idx);
}

function closeModal() {
  document.getElementById('modal-backdrop').classList.remove('open');
}

function closeModalOutside(e) {
  if (e.target === document.getElementById('modal-backdrop')) closeModal();
}

/* ═══════════════════════════════════════════
   CRUD EMPLEADOS
═══════════════════════════════════════════ */
function saveEmployee() {
  const nombre = document.getElementById('f-nombre').value.trim();
  const apellido = document.getElementById('f-apellido').value.trim();
  const correo = document.getElementById('f-correo').value.trim();
  const dept = document.getElementById('f-dept').value;
  const estatus = document.getElementById('f-estatus').value;
  const idx = document.getElementById('edit-index').value;

  if (!nombre || !apellido || !correo) {
    showToast('Nombre, apellido y correo son obligatorios.', false);
    return;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) {
    showToast('Correo inválido.', false);
    return;
  }

  const emp = { nombre, apellido, correo, dept, estatus, badges: [...modalBadges] };

  if (idx !== '') {
    employees[parseInt(idx)] = emp;
    showToast('Empleado actualizado');
  } else {
    employees.unshift(emp);
    showToast('Empleado registrado');
  }

  closeModal();
  renderTable();
}

function deleteEmployee(idx) {
  if (!confirm(`¿Eliminar a ${employees[idx].nombre} ${employees[idx].apellido}?`)) return;
  employees.splice(idx, 1);
  renderTable();
  showToast('Empleado eliminado', false);
}

/* ═══════════════════════════════════════════
   CARGA INICIAL DE DATOS
═══════════════════════════════════════════ */
function loadEmployeesFromServer(data) {
  if (data && Array.isArray(data)) {
    employees = data;
    renderTable();
  }
}

function initEmployees() {
  initBadgeSelect();

  // Intentar leer variable global inyectada por Jinja
  if (typeof window.empleadosData !== 'undefined' && Array.isArray(window.empleadosData)) {
    employees = window.empleadosData;
    renderTable();
  } else {
    // Fallback: obtener desde endpoint JSON
    fetch('/empleados.json')
      .then(res => res.ok ? res.json() : Promise.reject(res.statusText))
      .then(data => {
        employees = data;
        renderTable();
      })
      .catch(() => {
        renderTable();
      });
  }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initEmployees);