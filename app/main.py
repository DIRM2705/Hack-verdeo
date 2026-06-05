import os
from datetime import datetime
from pathlib import Path
import csv
import random
import subprocess
import sys

from flask import Flask, jsonify, redirect, render_template, request, session, url_for


app = Flask(__name__)



@app.route('/')
def dashboard():
    return render_template('index.html')


@app.route('/stats')
def stats():

    return render_template(
        'stats.html'
    )


@app.route('/domicilios/nuevo', methods=['GET', 'POST'])
def nuevo_domicilio():
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')