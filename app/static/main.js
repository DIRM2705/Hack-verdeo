// Obtener el UUID de la empresa desde el meta tag
const empresaUUID = document.querySelector('meta[name="empresa-uuid"]').getAttribute('content');

/**
 * Función para obtener las reseñas desde la API de Flask
 * @returns {Promise<Array>} Lista de reseñas
 */
async function obtenerReseñas() {
    try {
        const response = await fetch(`/api/reseñas/${empresaUUID}`);

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();
        console.log('Reseñas recibidas:', data);
        return data;
    } catch (error) {
        console.error('Error al obtener reseñas:', error);
        throw error;
    }
}

/**
 * Función para obtener los datos de la empresa desde la API de Flask
 * @returns {Promise<Object>} Datos de la empresa
 */
async function obtenerEmpresa() {
    try {
        const response = await fetch(`/api/empresa/${empresaUUID}`);
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        const data = await response.json();
        console.log('Datos de la empresa recibidos:', data);
        return data;
    } catch (error) {
        console.error('Error al obtener datos de la empresa:', error);
        throw error;
    }
}

/**
 * Función para obtener las certificaciones desde la API de Flask
 * @returns {Promise<Array>} Lista de certificaciones
 */
async function obtenerCertificaciones() {
    try {
        const response = await fetch(`/api/certificaciones/${empresaUUID}`);

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();
        console.log('Certificaciones recibidas:', data);
        return data;
    } catch (error) {
        console.error('Error al obtener certificaciones:', error);
        throw error;
    }
}

/**
 * Función para calcular el promedio de calificaciones
 * @param {Array} reseñas - Lista de reseñas
 * @returns {Object} Promedio y total de reseñas
 */
function calcularPromedio(reseñas) {
    if (!reseñas || reseñas.length === 0) {
        return { promedio: 0, total: 0 };
    }

    let suma = 0;
    let count = 0;

    reseñas.forEach(reseña => {
        if (reseña.calificacion) {
            suma += reseña.calificacion;
            count++;
        }
    });

    const promedio = count > 0 ? (suma / count).toFixed(1) : 0;
    return { promedio, total: count };
}

/**
 * Función para renderizar las estrellas según calificación
 * @param {number} rating - Calificación (1-5)
 * @returns {string} HTML de estrellas
 */
function renderStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - Math.ceil(rating);

    let starsHtml = '';

    // Estrellas llenas
    for (let i = 0; i < fullStars; i++) {
        starsHtml += '<i class="fa-solid fa-star"></i>';
    }

    // Media estrella
    if (hasHalfStar) {
        starsHtml += '<i class="fa-solid fa-star-half-alt"></i>';
    }

    // Estrellas vacías
    for (let i = 0; i < emptyStars; i++) {
        starsHtml += '<i class="fa-regular fa-star"></i>';
    }

    return starsHtml;
}

/**
 * Función para renderizar el nombre de la empresa en el DOM
 * @param {Object} empresa - Datos de la empresa
 */
function renderEmpresa(empresa) {
    const nombreElement = document.getElementById('empresa-nombre');
    if (nombreElement) {
        nombreElement.innerHTML = `<strong>Nombre:</strong> ${escapeHtml(empresa.nombre)}`;
    }
}
/**
 * Función para renderizar las reseñas en el DOM
 * @param {Array} reseñas - Lista de reseñas
 */
function renderReseñas(reseñas) {
    const container = document.getElementById('reseñas-list');
    const loadingDiv = document.getElementById('reseñas-loading');
    const errorDiv = document.getElementById('reseñas-error');

    // Ocultar loading
    if (loadingDiv) loadingDiv.style.display = 'none';
    errorDiv.style.display = 'none';

    if (!reseñas || reseñas.length === 0) {
        container.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: #94a3b8;">
                        <i class="fa-regular fa-comment-dots" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
                        <p>No hay reseñas disponibles</p>
                        <p style="font-size: 0.75rem;">Sé el primero en calificar este local</p>
                    </div>
                `;
        return;
    }

    // Calcular promedio
    const { promedio, total } = calcularPromedio(reseñas);

    // Generar HTML
    let html = `
                <div class="rating-average">
                    <span class="rating-number">${promedio}</span>
                    <div class="stars">${renderStars(parseFloat(promedio))}</div>
                    <span class="review-count">(${total} reseñas)</span>
                </div>
            `;

    reseñas.forEach(reseña => {
        const fecha = reseña.fecha ? new Date(reseña.fecha).toLocaleDateString('es-MX') : '';
        const estrellas = reseña.calificacion ? renderStars(reseña.calificacion) : '★★★★★';

        html += `
                    <div class="review">
                        <div class="stars" style="margin-bottom: 0.25rem;">${estrellas}</div>
                        <p style="margin: 0.25rem 0; color: #334155;">"${escapeHtml(reseña.comentario || 'Sin comentario')}"</p>
                        <p style="font-size: 0.7rem; color: #94a3b8; margin-top: 0.25rem;">
                            <em>${escapeHtml(reseña.nombre_cliente || 'Cliente Anónimo')}</em>
                            ${fecha ? ` - ${fecha}` : ''}
                        </p>
                    </div>
                `;
    });

    container.innerHTML = html;
}

/**
 * Función para renderizar las certificaciones en el DOM
 * @param {Array} certificaciones - Lista de certificaciones
 */
function renderCertificaciones(certificaciones) {
    const container = document.getElementById('certificaciones-list');
    const loadingDiv = document.getElementById('certificaciones-loading');
    const errorDiv = document.getElementById('cert-error');

    // Ocultar loading
    if (loadingDiv) loadingDiv.style.display = 'none';
    errorDiv.style.display = 'none';

    if (!certificaciones || certificaciones.length === 0) {
        container.innerHTML = `
                    <div style="text-align: center; padding: 1rem; color: #94a3b8;">
                        <i class="fa-regular fa-file"></i>
                        <p>No hay certificaciones registradas</p>
                    </div>
                `;
        return;
    }

    let html = `<p style="margin-bottom: 0.5rem;"><strong>Total:</strong> ${certificaciones.length} certificaciones</p>`;

    certificaciones.forEach(cert => {
        const fechaVencimiento = cert.fecha_vencimiento ? new Date(cert.fecha_vencimiento) : null;
        const hoy = new Date();
        const estaVigente = fechaVencimiento && fechaVencimiento > hoy;
        const expiryClass = estaVigente ? 'valid' : '';
        const expiryText = fechaVencimiento ? `Vence: ${fechaVencimiento.toLocaleDateString('es-MX')}` : 'Sin fecha de vencimiento';

        html += `
                    <div class="cert-item">
                        <div>
                            <div class="cert-name">${escapeHtml(cert.nombre)}</div>
                            <div class="cert-expiry ${expiryClass}">${expiryText}</div>
                        </div>
                        ${!estaVigente && fechaVencimiento ? '<i class="fa-solid fa-triangle-exclamation" style="color: #ef4444;"></i>' : '<i class="fa-solid fa-check-circle" style="color: #10b981;"></i>'}
                    </div>
                `;
    });

    container.innerHTML = html;
}

/**
 * Función de escape para evitar XSS
 */
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, function (m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

/**
 * Función principal para cargar todos los datos
 */
async function cargarDatos() {
    // Cargar datos de la empresa
    try {
        const empresaData = await obtenerEmpresa();
        if (empresaData) {
            renderEmpresa(empresaData);
        }
    } catch (error) {
        console.error('Error cargando datos de la empresa:', error);
        const nombreElement = document.getElementById('empresa-nombre');
        if (nombreElement) {
            nombreElement.innerHTML = `<span style="color: #ef4444;">Error al cargar datos de la empresa</span>`;
        }
    }
    
    // Cargar certificaciones
    try {
        const certData = await obtenerCertificaciones();
        if (certData && certData.length > 0) {
            renderCertificaciones(certData[0].certificaciones || []);
        } else {
            renderCertificaciones([]);
        }
    } catch (error) {
        console.error('Error cargando certificaciones:', error);
        const loadingDiv = document.getElementById('certificaciones-loading');
        const errorDiv = document.getElementById('cert-error');
        if (loadingDiv) loadingDiv.style.display = 'none';
        errorDiv.style.display = 'block';
        errorDiv.textContent = 'Error al cargar certificaciones. Intenta nuevamente.';
        document.getElementById('certificaciones-list').innerHTML = '';
    }

    // Cargar reseñas
    try {
        const reseñasData = await obtenerReseñas();
        if (reseñasData && reseñasData.length > 0 && reseñasData[0].reseñas) {
            renderReseñas(reseñasData[0].reseñas);
        } else {
            renderReseñas([]);
        }
    } catch (error) {
        console.error('Error cargando reseñas:', error);
        const loadingDiv = document.getElementById('reseñas-loading');
        const errorDiv = document.getElementById('reseñas-error');
        if (loadingDiv) loadingDiv.style.display = 'none';
        errorDiv.style.display = 'block';
        errorDiv.textContent = 'Error al cargar reseñas. Intenta nuevamente.';
        document.getElementById('reseñas-list').innerHTML = '';
    }
}

/**
 * Función para mostrar secciones (normativas)
 */
function showSection(sectionId, btnElement) {
    // Ocultar todas las secciones
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });

    // Mostrar la sección seleccionada
    document.getElementById(sectionId).classList.add('active');

    // Actualizar botón activo
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    btnElement.classList.add('active');
}

// Cargar datos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', cargarDatos);