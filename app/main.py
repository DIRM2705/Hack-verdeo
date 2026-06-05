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
        stm = select(Certificacion.nombre, Certificacion.fecha_vencimiento).where(Certificacion.uuid_empresa == uuid_empresa)
        certs = session.execute(stm).scalars().all()
        return jsonify([{
            "count": len(certs),
            "certificaciones": [{"nombre": c.nombre} for c in certs]
        }])
        
@app.route('/api/empleados/<uuid_empresa>')
def empleados(uuid_empresa):
    with Session(db) as session:
        stm = select(Empleado.uuid, Empleado.nombre, Empleado.apellidos, Badge.icono_url).join(Badge, Empleado.badge_uuid == Badge.uuid).where(Empleado.uuid_empresa == uuid_empresa)
        emp = session.execute(stm).scalars().all()
        return jsonify([{
            "count": len(emp),
            "empleados": [{"uuid": e.uuid, "nombre": e.nombre, "apellidos": e.apellidos, "icono_url": e.icono_url} for e in emp]
        }])
        
@app.route('/api/reseñas/<uuid_empresa>')
def reseñas(uuid_empresa):
    with Session(db) as session:
        stm = select(func.count(Reseña.uuid)).select_from(Reseña).where(Reseña.uuid_empresa == uuid_empresa)
        res = session.execute(stm).scalar()
        return jsonify([{
            "count": res
        }])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


@app.route('/empleados/<uuid_empresa>')
def empleados_page(uuid_empresa):
    """Renderiza la plantilla de empleados usando los datos obtenidos desde la BD."""
    with Session(db) as session:
        stm = select(Empleado.uuid, Empleado.nombre, Empleado.apellidos, Empleado.correo, Badge.icono_url).join(Badge, Empleado.badge_uuid == Badge.uuid).where(Empleado.uuid_empresa == uuid_empresa)
        rows = session.execute(stm).all()
        empleados_list = []
        for r in rows:
            empleados_list.append({
                'uuid': r[0],
                'nombre': r[1],
                'apellido': r[2],
                'correo': r[3] if len(r) > 3 else '',
                'icono_url': r[4] if len(r) > 4 else None,
                'badges': []
            })
    return render_template('empleados.html', empleados=empleados_list)