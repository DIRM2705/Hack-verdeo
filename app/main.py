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
from uuid import UUID
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
def home():
    return render_template('index.html')

@app.route('/empresa/<uuid_empresa>')
def dashboard(uuid_empresa: str):
    # ejemplo de UUID de empresa — reemplazar por UUID real según sesión/usuario
    ejemplo_uuid = 'a0c48199a44a4f22be0c43ade5ddd630'
    return render_template('empresa.html', empresa_uuid=ejemplo_uuid)


@app.route('/normativas/<uuid_empresa>')
def normativas_page(uuid_empresa : str):
    """Renderiza la plantilla de normativas usando los datos obtenidos desde la BD."""
    return render_template('normativas.html', empresa_uuid=uuid_empresa)

@app.route('/empleados/<uuid_empresa>')
def empleados_page(uuid_empresa : str):
    """Renderiza la plantilla de empleados usando los datos obtenidos desde la BD."""
    with Session(db) as session:
        uuid_empresa = UUID(uuid_empresa)
        stm = select(Empleado.uuid, Empleado.nombres, Empleado.apellidos, Badge.icono_url).join(Badge, Badge.empleados_uuid == Empleado.uuid).where(Empleado.empresa_uuid == uuid_empresa)
        rows = session.execute(stm).all()
        empleados_list = []
        for r in rows:
            empleados_list.append({
                'uuid': r[0],
                'nombres': r[1],
                'apellidos': r[2],
                'correo': r[3] if len(r) > 3 else '',
                'icono_url': r[4] if len(r) > 4 else None,
                'badges': []
            })
    return render_template('empleados.html', empresa_uuid=uuid_empresa, empleados=empleados_list)

@app.route('/api/empresa/<uuid_empresa>')
def empresa(uuid_empresa : str):
    with Session(db) as session:
        uuid_empresa = UUID(uuid_empresa)
        stm = select(Empresa.nombre).where(Empresa.uuid == uuid_empresa)
        empresa = session.execute(stm).first()
        if not empresa:
            return jsonify({"error": "Empresa no encontrada"}), 404
        return jsonify({
            "nombre": empresa[0]
        })

@app.route('/api/certificaciones/<uuid_empresa>')
def certificaciones(uuid_empresa : str):
    with Session(db) as session:
        uuid_empresa = UUID(uuid_empresa)
        stm = select(Certificacion.nombre, Certificacion.fecha_vencimiento).where(Certificacion.empresa_uuid == uuid_empresa)
        certs = session.execute(stm).all()
        return jsonify([{
            "count": len(certs),
            "certificaciones": [{"nombre": c.nombre, "fecha_vencimiento": c.fecha_vencimiento} for c in certs]
        }])
        
@app.route('/api/empleados/<uuid_empresa>')
def empleados(uuid_empresa : str):
    with Session(db) as session:
        uuid_empresa = UUID(uuid_empresa)
        stm = select(Empleado.uuid, Empleado.nombres, Empleado.apellidos, Badge.icono_url).join(Badge, Badge.empleados_uuid == Empleado.uuid).where(Empleado.empresa_uuid == uuid_empresa)
        emp = session.execute(stm).scalars().all()
        return jsonify([{
            "count": len(emp),
            "empleados": [{"uuid": e.uuid, "nombres": e.nombres, "apellidos": e.apellidos, "icono_url": e.icono_url} for e in emp]
        }])
        
@app.route('/api/reseñas/<uuid_empresa>')
def reseñas(uuid_empresa : str):
    with Session(db) as session:
        uuid_empresa = UUID(uuid_empresa)
        stm = select(Reseña.calificacion, Reseña.comentario).select_from(Reseña).where(Reseña.uuid_empresa == uuid_empresa)
        res = session.execute(stm).all()
        return jsonify([{
            "count": len(res),
            "reseñas": [{"calificacion": r[0], "comentario": r[1]} for r in res]
        }])

def clasificar_empresa(uuid_empresa: UUID) -> str:
    """
    Clasifica una empresa como 'mala', 'regular' o 'excelente' basándose en:
    - La cantidad de certificaciones vigentes
    - El tiempo que han estado activas las certificaciones
    - La proporción de certificaciones vencidas
    
    Args:
        uuid_empresa: UUID de la empresa a clasificar
        
    Returns:
        str: 'mala', 'regular' o 'excelente'
    """
    with Session(db) as session:
        # Obtener todas las certificaciones de la empresa
        stm = select(Certificacion.fecha_expedicion, Certificacion.fecha_vencimiento).where(
            Certificacion.empresa_uuid == uuid_empresa
        )
        certificaciones = session.execute(stm).all()
        
        if not certificaciones:
            return "mala"
        
        ahora = datetime.now()
        vigentes = 0
        vencidas = 0
        tiempo_total_vigencia = 0
        
        for fecha_exp, fecha_venc in certificaciones:
            # Calcular si está vigente
            if fecha_venc > ahora:
                vigentes += 1
            else:
                vencidas += 1
            
            # Calcular tiempo de vigencia en días
            if fecha_venc > ahora:
                # Si está vigente, calcular desde expedición hasta ahora
                tiempo_vigencia = (ahora - fecha_exp).days
            else:
                # Si está vencida, calcular desde expedición hasta vencimiento
                tiempo_vigencia = (fecha_venc - fecha_exp).days
            
            tiempo_total_vigencia += tiempo_vigencia
        
        total_certs = len(certificaciones)
        tiempo_promedio = tiempo_total_vigencia // total_certs if total_certs > 0 else 0
        porcentaje_vigentes = (vigentes / total_certs) * 100
        
        # Lógica de clasificación
        if vigentes == 0:
            return "mala"
        elif vigentes == 1 and total_certs > 1:
            return "mala"
        elif vigentes <= 2 or (porcentaje_vigentes < 50 and total_certs > 2):
            return "regular"
        elif vigentes >= 4 and porcentaje_vigentes >= 80 and tiempo_promedio >= 365:
            return "excelente"
        elif vigentes >= 3 and porcentaje_vigentes >= 60 and tiempo_promedio >= 180:
            return "regular"
        else:
            return "regular"


@app.route('/api/clasificacion/<uuid_empresa>')
def get_clasificacion(uuid_empresa: str):
    """
    Endpoint que retorna la clasificación de una empresa
    """
    try:
        uuid_empresa_obj = UUID(uuid_empresa)
        clasificacion = clasificar_empresa(uuid_empresa_obj)
        return jsonify({"clasificacion": clasificacion})
    except ValueError:
        return jsonify({"error": "UUID inválido"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')