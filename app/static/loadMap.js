window.residentMapInstance = null;

const VIEW_CONFIG = {
    consumo: {
        symbol: 'droplet',
        colorKey: 'consumo_color',
        labelKey: 'consumo_nivel',
        defaultLabel: 'Consumo sin nivel',
        labelPrefix: 'Consumo '
    },
    pago: {
        symbol: 'coins',
        colorKey: 'pago_color',
        labelKey: 'pago_estado',
        defaultLabel: 'Pago sin estado',
        labelPrefix: ''
    },
    morosidad: {
        symbol: 'risk',
        colorKey: 'morosidad_color',
        labelKey: 'morosidad_nivel',
        defaultLabel: 'Riesgo sin clasificar',
        labelPrefix: ''
    }
};

function getResidentMapRoot(rootId) {
    return document.getElementById(rootId);
}

function getResidentMapElements(root) {
    return {
        mapElement: root.querySelector('#map'),
        dataElement: root.querySelector('#puntos-data'),
        viewSelect: root.querySelector('#resident-view-select'),
        legendBody: root.querySelector('#legend-body')
    };
}

function parseResidentPoints(dataElement) {
    return JSON.parse(dataElement?.textContent || '[]');
}

function destroyResidentMap() {
    if (window.residentMapInstance) {
        window.residentMapInstance.remove();
        window.residentMapInstance = null;
    }
}

function normalizeResidentView(view) {
    return VIEW_CONFIG[view] ? view : 'consumo';
}

function getLegendSortPriority(view, label) {
    const normalizedLabel = (label || '').toLowerCase();

    if (view === 'consumo') {
        if (normalizedLabel.includes('alto')) return 1;
        if (normalizedLabel.includes('medio')) return 2;
        if (normalizedLabel.includes('normal')) return 3;
        return 99;
    }

    if (view === 'morosidad') {
        if (normalizedLabel.includes('alto')) return 1;
        if (normalizedLabel.includes('medio')) return 2;
        if (normalizedLabel.includes('bajo')) return 3;
        return 99;
    }

    if (normalizedLabel.includes('pagado')) return 1;
    if (normalizedLabel.includes('no pagado')) return 2;
    return 99;
}

function buildLegendItems(puntos, view) {
    const config = VIEW_CONFIG[normalizeResidentView(view)];
    const itemsByKey = new Map();

    puntos.forEach((punto) => {
        const labelValue = punto?.[config.labelKey] || config.defaultLabel;
        const labelText = `${config.labelPrefix}${labelValue}`.trim();
        const color = punto?.[config.colorKey] || '#64748b';
        const key = `${labelText}::${color}`;

        if (!itemsByKey.has(key)) {
            itemsByKey.set(key, {
                label: labelText,
                color,
                sort: getLegendSortPriority(view, labelText)
            });
        }
    });

    return Array.from(itemsByKey.values()).sort((a, b) => {
        if (a.sort === b.sort) {
            return a.label.localeCompare(b.label, 'es');
        }
        return a.sort - b.sort;
    });
}

function renderLegend(legendBody, puntos, view) {
    if (!legendBody) {
        return;
    }

    const currentView = normalizeResidentView(view);
    const items = buildLegendItems(puntos, currentView);
    if (!items.length) {
        legendBody.innerHTML = `
            <tr>
                <td class="px-3 py-3 text-slate-400" colspan="2">Sin datos para mostrar</td>
            </tr>
        `;
        return;
    }

    legendBody.innerHTML = items
        .map((item) => `
            <tr>
                <td class="px-3 py-2 text-slate-700">${item.label}</td>
                <td class="px-3 py-2">
                    <span class="w-8 h-8 rounded-full bg-white flex items-center justify-center border-2" style="border-color:${item.color}; color:${item.color};">
                        ${currentView === 'morosidad' ? '<span class="w-2.5 h-2.5 rounded-full" style="background:' + item.color + ';"></span>' : '<i class="' + getSymbolIconClass(VIEW_CONFIG[currentView].symbol) + '"></i>'}
                    </span>
                </td>
            </tr>
        `)
        .join('');
}

function createResidentMap(mapElement) {
    return L.map(mapElement).setView([18.975, -98.235], 14);
}

function addResidentTileLayer(map) {
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        minZoom: 0,
        maxZoom: 20,
        maxNativeZoom: 20,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    }).addTo(map);
}

function getSymbolIconClass(simbolo) {
    if (simbolo === 'coins') {
        return 'fa-solid fa-coins';
    }
    return 'fa-solid fa-droplet';
}

function createSymbolMarker(map, options) {
    const iconClass = getSymbolIconClass(options.simbolo);
    const markerHtml = `
        <div style="
            width: 28px;
            height: 28px;
            border-radius: 999px;
            background: #ffffff;
            border: 2px solid ${options.color || '#2563eb'};
            color: ${options.color || '#2563eb'};
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 10px rgba(15, 23, 42, 0.18);
            font-size: 12px;
        ">
            <i class="${iconClass}"></i>
        </div>
    `;

    const customIcon = L.divIcon({
        html: markerHtml,
        className: '',
        iconSize: [28, 28],
        iconAnchor: [14, 14],
        popupAnchor: [0, -12]
    });

    return L.marker([options.lat, options.lng], { icon: customIcon }).addTo(map);
}

function createRiskMarker(map, punto, color) {
    return L.circleMarker([punto.lat, punto.lng], {
        bubblingMouseEvents: true,
        color,
        fillColor: color,
        fillOpacity: 0.8,
        opacity: 1,
        radius: 6,
        stroke: true,
        weight: 3
    }).addTo(map);
}

function buildResidentPopup(punto, view) {
    if (view === 'morosidad') {
        const loteId = punto.lote_id || punto.nombre || 'Lote';
        const probabilidad = Number.isFinite(Number(punto.morosidad_probabilidad))
            ? `${Number(punto.morosidad_probabilidad).toFixed(1)}%`
            : 'n/a';

        return `
            <div style="font-family: Inter, system-ui, sans-serif; font-size: 13px; line-height: 1.45;">
                <strong>Lote ID: ${loteId}</strong><br>
                Riesgo: ${probabilidad}
            </div>
        `;
    }

    return `
        <div style="font-family: Inter, system-ui, sans-serif; font-size: 13px; line-height: 1.45;">
            <strong>${punto.nombre || 'Lote'}</strong><br>
            Consumo: ${punto.consumo_nivel || 'n/a'}<br>
            Pago: ${punto.pago_estado || 'n/a'}
        </div>
    `;
}

function resolveRiskColor(punto) {
    if (punto?.morosidad_color) {
        return punto.morosidad_color;
    }

    const riesgo = Number(punto?.morosidad_probabilidad);
    if (!Number.isFinite(riesgo)) {
        return '#64748b';
    }

    if (riesgo >= 70) {
        return 'red';
    }

    if (riesgo >= 30) {
        return 'orange';
    }

    return '#16a34a';
}

function isValidLatLng(punto) {
    const lat = Number(punto?.lat);
    const lng = Number(punto?.lng);
    return Number.isFinite(lat) && Number.isFinite(lng);
}

function fitResidentMapToPoints(map, puntos) {
    const validPoints = puntos.filter((punto) => isValidLatLng(punto));
    if (!validPoints.length) {
        return;
    }

    const bounds = L.latLngBounds(validPoints.map((punto) => [Number(punto.lat), Number(punto.lng)]));
    map.fitBounds(bounds.pad(0.2));
}

function addResidentMarkers(map, puntos, view) {
    const config = VIEW_CONFIG[normalizeResidentView(view)];

    puntos.forEach((punto) => {
        if (!isValidLatLng(punto)) {
            return;
        }

        const popupHtml = buildResidentPopup(punto, view);

        if (view === 'morosidad') {
            const riskColor = resolveRiskColor(punto);
            const riskMarker = createRiskMarker(map, punto, riskColor);
            riskMarker.bindPopup(popupHtml);
            return;
        }

        if (punto[config.colorKey]) {
            const marker = createSymbolMarker(map, {
                simbolo: config.symbol,
                color: punto[config.colorKey],
                lat: Number(punto.lat),
                lng: Number(punto.lng)
            });

            marker.bindPopup(popupHtml);
            return;
        }

        let marker;
        if (punto.simbolo && punto.color) {
            marker = createSymbolMarker(map, {
                simbolo: punto.simbolo,
                color: punto.color,
                lat: Number(punto.lat),
                lng: Number(punto.lng)
            });
        } else {
            marker = L.circleMarker([Number(punto.lat), Number(punto.lng)], {
                radius: 10,
                fillColor: punto.color,
                color: '#ffffff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map);
        }

        marker.bindPopup(popupHtml);
    });
}

function renderResidentMapView(mapElement, puntos, view) {
    destroyResidentMap();

    const map = createResidentMap(mapElement);
    addResidentTileLayer(map);
    addResidentMarkers(map, puntos, view);
    fitResidentMapToPoints(map, puntos);

    window.residentMapInstance = map;
    refreshResidentMapSize(map);

    return map;
}

function refreshResidentMapSize(map) {
    setTimeout(() => {
        map.invalidateSize();
    }, 0);
}

window.loadResidentMap = function (rootId = 'residentes-content') {
    const root = getResidentMapRoot(rootId);
    if (!root || typeof L === 'undefined') {
        return null;
    }

    const { mapElement, dataElement, viewSelect, legendBody } = getResidentMapElements(root);
    if (!mapElement) {
        return null;
    }

    const puntos = parseResidentPoints(dataElement);
    let activeView = normalizeResidentView(viewSelect?.value);

    const renderCurrentView = () => {
        const map = renderResidentMapView(mapElement, puntos, activeView);
        renderLegend(legendBody, puntos, activeView);
        if (viewSelect && viewSelect.value !== activeView) {
            viewSelect.value = activeView;
        }
        return map;
    };

    const map = renderCurrentView();

    if (viewSelect) {
        viewSelect.addEventListener('change', () => {
            const nextView = normalizeResidentView(viewSelect.value);
            if (nextView === activeView) {
                return;
            }
            activeView = nextView;
            renderCurrentView();
        });
    }

    return map;
};