import os
from datetime import datetime
from pathlib import Path
import csv
import random
import subprocess
import sys

from flask import Flask, jsonify, redirect, render_template, request, session, url_for


def load_env_file():
    env_path = Path(__file__).resolve().parent.parent / '.env'
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding='utf-8').splitlines():
        text = line.strip()
        if not text or text.startswith('#') or '=' not in text:
            continue

        key, value = text.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip())


load_env_file()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'hackathon-dev-secret')

APP_LOGIN_USER = os.getenv('APP_LOGIN_USER')
APP_LOGIN_PASSWORD = os.getenv('APP_LOGIN_PASSWORD')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOTES_FILE = PROJECT_ROOT / 'lotes.csv'
CONSUMO_FILE = PROJECT_ROOT / 'consumo_de_agua.csv'
VIVIENDAS_COORDS_FILE = PROJECT_ROOT / 'viviendas_limpio_con_coordenadas.csv'
APP_DIR = Path(__file__).resolve().parent
MOROSIDAD_MODEL_FILE = APP_DIR / 'modelo_morosidad_rf.pkl'
MODEL_IMPORTANCE_FILE = PROJECT_ROOT / 'importancia_variables.png'
PREDICTIONS_SCRIPT_FILE = APP_DIR / 'predictions.py'
RISK_CSV_FILE = PROJECT_ROOT / 'lotes_con_probabildad_de_riesgo.csv'
RISK_CSV_ALT_FILE = PROJECT_ROOT / 'lotes_con_probabilidad_riesgo.csv'

MONTH_LABELS = {
    1: 'Ene',
    2: 'Feb',
    3: 'Mar',
    4: 'Abr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Ago',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dic',
}

ANOMALY_STATUSES = [
    'Revisar medidor',
    'Visita programada',
    'En validacion',
    'Pendiente inspeccion',
    'Monitoreo continuo',
]

MOROSIDAD_MODEL_CACHE = None

CONSUMO_STATES = [
    ('alto', '#dc2626'),
    ('medio', '#f59e0b'),
    ('normal', '#16a34a'),
]

PAGO_STATES = [
    ('pagado', '#16a34a'),
    ('no pagado', '#dc2626'),
]

MODEL_FEATURES = ['Monto_Promedio', 'Promedio_Dias', 'Inconsistencia_Dias']


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_lote_key(value):
    text = str(value or '').strip()
    if not text:
        return ''

    try:
        number = float(text)
        if number.is_integer():
            return str(int(number))
    except (TypeError, ValueError):
        pass

    return text


def classify_morosidad(probabilidad):
    risk = max(0.0, min(100.0, float(probabilidad)))

    if risk >= 70:
        return 'Riesgo alto', 'red'
    if risk >= 30:
        return 'Riesgo medio', 'orange'
    return 'Riesgo bajo', '#16a34a'


def load_lotes_rows():
    if not LOTES_FILE.exists():
        return []

    with LOTES_FILE.open('r', encoding='utf-8', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        return [row for row in reader]


def _parse_fpago_value(value):
    if value is None:
        return datetime.min

    text = str(value).strip()
    if not text:
        return datetime.min

    known_formats = (
        '%m/%d/%Y',
        '%Y-%m-%d',
        '%d/%m/%Y',
    )
    for date_format in known_formats:
        try:
            return datetime.strptime(text, date_format)
        except ValueError:
            continue

    return datetime.min


def load_latest_consumo_rows_by_lote():
    if not CONSUMO_FILE.exists():
        return {}

    latest_by_lote = {}
    with CONSUMO_FILE.open('r', encoding='utf-8', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            lote = str(row.get('lote', '')).strip()
            if not lote:
                continue

            fpago_dt = _parse_fpago_value(row.get('Fpago'))
            periodo = safe_int(row.get('PERIODO'))
            score = (fpago_dt, periodo)

            previous = latest_by_lote.get(lote)
            if previous is None or score > previous['score']:
                latest_by_lote[lote] = {
                    'score': score,
                    'row': row,
                }

    return {
        lote: data['row']
        for lote, data in latest_by_lote.items()
    }


def load_viviendas_coordinates_by_lote():
    if not VIVIENDAS_COORDS_FILE.exists():
        return {}

    coordinates_by_lote = {}
    with VIVIENDAS_COORDS_FILE.open('r', encoding='utf-8', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            lote_id = str(row.get('id', '')).strip()
            lat = safe_float(row.get('latitud'), None)
            lng = safe_float(row.get('altitud'), None)

            if not lote_id:
                continue
            if lat is None or lng is None:
                continue
            if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                continue

            coordinates_by_lote[lote_id] = {
                'lat': lat,
                'lng': lng,
                'clave': str(row.get('clave', '')).strip(),
            }

    return coordinates_by_lote

def predict_row_risk(row, model):
    monto_promedio = safe_float(row.get('Monto_Promedio'), safe_float(row.get('TOTAL'), 0.0))
    promedio_dias = safe_float(row.get('Promedio_Dias'), 30.0)
    inconsistencia_dias = safe_float(row.get('Inconsistencia_Dias'), 0.0)

    input_data = [[monto_promedio, promedio_dias, inconsistencia_dias]]
    probabilidad_riesgo = model.predict_proba(input_data)[0][1] * 100
    return {
        'probabilidad_riesgo_pct': round(probabilidad_riesgo, 2),
    }

def _build_stats_points_from_consumo_rows(consumo_rows):
    if not consumo_rows:
        return []

    risk_by_lote = load_or_generate_risk_by_lote()
    coord_by_lote = load_viviendas_coordinates_by_lote()
    points = []

    sorted_rows = sorted(
        consumo_rows.items(),
        key=lambda item: safe_int(item[0], 10**9),
    )

    for index, (lote, row) in enumerate(sorted_rows):
        lote_key = normalize_lote_key(lote)
        coord = coord_by_lote.get(lote_key)
        if not coord:
            continue

        probabilidad = safe_float(risk_by_lote.get(lote_key), 0.0)
        morosidad_nivel, morosidad_color = classify_morosidad(probabilidad)
        consumo_nivel, consumo_color = random.choice(CONSUMO_STATES)
        pago_estado, pago_color = random.choice(PAGO_STATES)
        lat, lng = coord['lat'], coord['lng']

        clave = coord.get('clave')
        display_name = f'Lote {lote}' if not clave else f'Lote {lote} ({clave})'

        points.append({
            'lote_id': lote_key,
            'lat': lat,
            'lng': lng,
            'nombre': display_name,
            'consumo_nivel': consumo_nivel,
            'consumo_color': consumo_color,
            'pago_estado': pago_estado,
            'pago_color': pago_color,
            'morosidad_probabilidad': probabilidad,
            'morosidad_nivel': morosidad_nivel,
            'morosidad_color': morosidad_color,
        })

    return points


def build_period_label(year, period_index):
    start_month = (period_index * 2) - 1
    end_month = period_index * 2
    return f"{MONTH_LABELS[start_month]}-{MONTH_LABELS[end_month]} {year}"


def build_period_options(year, max_period):
    options = []
    for period_index in range(1, max_period + 1):
        period_key = f'{year}-b{period_index}'
        options.append({
            'key': period_key,
            'label': build_period_label(year, period_index),
        })
    return options


def pick_anomalies(lotes_rows, period_index):
    if not lotes_rows:
        return []

    sorted_rows = sorted(
        lotes_rows,
        key=lambda row: (safe_int(row.get('id_lote')) * (period_index + 3)) % 997,
    )

    sample_size = max(1, min(5, len(sorted_rows) // 30))
    selected = sorted_rows[:sample_size]

    anomalies = []
    for idx, row in enumerate(selected):
        variation = 28 + ((safe_int(row.get('id_lote')) + period_index + idx) % 26)
        anomalies.append({
            'lote': row.get('ClaveLote') or f"Lote {row.get('id_lote', '?')}",
            'variacion': f'+{variation}%',
            'estatus': ANOMALY_STATUSES[(period_index + idx) % len(ANOMALY_STATUSES)],
        })

    return anomalies


def build_bimestral_reports(lotes_rows):
    now = datetime.now()
    year = now.year
    current_period = min(6, max(1, ((now.month - 1) // 2) + 1))

    total_lotes = len(lotes_rows)
    cuota_mensual = 550
    cuota_bimestral = cuota_mensual * 2

    reports = {}
    accumulated_income = 0

    for period_index in range(1, current_period + 1):
        lotes_pagaron = total_lotes
        lotes_corriente = total_lotes

        ingresos_bimestre = lotes_corriente * cuota_bimestral
        accumulated_income += ingresos_bimestre

        consumo_medio = round(11.5 + (period_index * 0.42), 1)
        consumo_total = round(consumo_medio * total_lotes, 1)

        anomalies = pick_anomalies(lotes_rows, period_index)
        period_key = f'{year}-b{period_index}'
        reports[period_key] = {
            'ingresosBimestre': ingresos_bimestre,
            'ingresoAcumulado': accumulated_income,
            'consumoMedio': consumo_medio,
            'consumoTotal': consumo_total,
            'lotesPagaron': lotes_pagaron,
            'lotesCorriente': lotes_corriente,
            'anomalias': anomalies,
        }

    return {
        'periods': build_period_options(year, current_period),
        'reports': reports,
        'active_period': f'{year}-b{current_period}',
    }


def get_dashboard_context():
    lotes_rows = load_lotes_rows()
    bimestral_data = build_bimestral_reports(lotes_rows)
    return {
        'current_user': session.get('auth_user'),
        'bimestral_periods': bimestral_data['periods'],
        'bimestral_reports': bimestral_data['reports'],
        'active_bimestral_period': bimestral_data['active_period'],
    }


def _run_predictions_script():
    if not PREDICTIONS_SCRIPT_FILE.exists():
        raise FileNotFoundError(f'No se encontro el script de entrenamiento: {PREDICTIONS_SCRIPT_FILE}')

    subprocess.run(
        [sys.executable, str(PREDICTIONS_SCRIPT_FILE)],
        check=True,
        cwd=str(PROJECT_ROOT),
    )


def _resolve_risk_csv_path():
    if RISK_CSV_FILE.exists():
        return RISK_CSV_FILE

    if RISK_CSV_ALT_FILE.exists():
        return RISK_CSV_ALT_FILE

    _run_predictions_script()

    if RISK_CSV_FILE.exists():
        return RISK_CSV_FILE

    if RISK_CSV_ALT_FILE.exists():
        return RISK_CSV_ALT_FILE

    raise FileNotFoundError(
        'No se encontro lotes_con_probabildad_de_riesgo.csv ni lotes_con_probabilidad_riesgo.csv '
        'despues de ejecutar predictions.py'
    )


def load_or_generate_risk_by_lote():
    csv_path = _resolve_risk_csv_path()
    risk_by_lote = {}

    with csv_path.open('r', encoding='utf-8', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            lote = normalize_lote_key(row.get('lote') or row.get('Unnamed: 0') or '')
            probabilidad = safe_float(row.get('Probabilidad_Riesgo_%'), None)
            if not lote or probabilidad is None:
                continue
            risk_by_lote[lote] = float(probabilidad)

    return risk_by_lote

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if username == APP_LOGIN_USER and password == APP_LOGIN_PASSWORD:
            session['auth_user'] = username
            print(f'Usuario autenticado: {username}')
            return redirect(url_for('dashboard'))

        return render_template('login.html', error='Usuario o contraseña incorrectos.')

    if session.get('auth_user'):
        return redirect(url_for('dashboard'))

    return render_template('login.html', error=None)


@app.route('/dashboard')
def dashboard():
    if not session.get('auth_user'):
        return redirect(url_for('login'))

    return render_template('index.html', **get_dashboard_context())


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/stats')
def stats():
    if not session.get('auth_user'):
        return redirect(url_for('login'))

    consumo_rows = load_latest_consumo_rows_by_lote()
    puntos = _build_stats_points_from_consumo_rows(consumo_rows)

    return render_template(
        'stats.html',
        puntos=puntos
    )


@app.route('/domicilios/nuevo', methods=['GET', 'POST'])
def nuevo_domicilio():
    if not session.get('auth_user'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        numero_lote = str(payload.get('numero_lote', '')).strip()
        titular = str(payload.get('titular', '')).strip()

        if not numero_lote or not titular:
            return jsonify({
                'ok': False,
                'message': 'Numero de lote y titular son obligatorios.'
            }), 400

        return jsonify({
            'ok': True,
            'message': 'Lote recibido. No se agregan puntos temporales al mapa.'
        })

    return render_template('nuevo_domicilio.html')


@app.route('/reportes/bimestrales')
def reportes_bimestrales():
    if not session.get('auth_user'):
        return redirect(url_for('login'))

    context = get_dashboard_context()
    return render_template(
        'reportes_bimestrales.html',
        bimestral_periods=context['bimestral_periods'],
        bimestral_reports=context['bimestral_reports'],
        active_bimestral_period=context['active_bimestral_period'],
    )


@app.route('/api/predicciones/morosidad', methods=['POST'])
def prediccion_morosidad():
    if not session.get('auth_user'):
        return jsonify({'ok': False, 'message': 'No autenticado.'}), 401

    payload = request.get_json(silent=True) or {}
    required_columns = ['lote', 'PERIODO', 'Fpago', 'TOTAL']
    missing_columns = [column for column in required_columns if not str(payload.get(column, '')).strip()]
    if missing_columns:
        return jsonify({
            'ok': False,
            'message': f'Faltan columnas requeridas: {", ".join(missing_columns)}',
        }), 400

    lote_key = normalize_lote_key(payload.get('lote', ''))

    try:
        risk_by_lote = load_or_generate_risk_by_lote()
        probabilidad = risk_by_lote.get(lote_key)
        if probabilidad is None:
            return jsonify({
                'ok': False,
                'message': f'No hay probabilidad de riesgo para el lote {lote_key} en el archivo de riesgo.',
            }), 404

        prediction = {
            'probabilidad_riesgo_pct': round(float(probabilidad), 2),
        }
    except Exception as exc:
        return jsonify({
            'ok': False,
            'message': f'No se pudo generar la predicción: {exc}',
        }), 500

    return jsonify({
        'ok': True,
        'input': {
            'lote': payload.get('lote'),
            'PERIODO': payload.get('PERIODO'),
            'Fpago': payload.get('Fpago'),
            'TOTAL': payload.get('TOTAL'),
        },
        'prediction': prediction,
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')