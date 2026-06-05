import os
from models.base import Base
from models.empresa import Empresa
from models.empleado import Empleado
from models.usuarios import Usuario
from models.badges import Badge
from models.certificaciones import Certificacion
from models.reseñas import Reseña
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
import csv
import random
import subprocess
import sys

from flask import Flask, jsonify, redirect, render_template, request, session, url_for


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost:3306/VERDEO'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Base.metadata.create_all(db)




@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/api/certificaciones/<uuid_empresa>')
def certificaciones(uuid_empresa):
    with Session(db) as session:
        stm = select(func.count(Certificacion.uuid)).select_from(Certificacion).where(Certificacion.uuid_empresa == uuid_empresa)
        certs = session.execute(stm).scalar()
        return jsonify([{
            "count": certs
        }])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')