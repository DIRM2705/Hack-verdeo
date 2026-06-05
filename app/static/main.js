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