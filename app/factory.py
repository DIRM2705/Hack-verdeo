from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models.empleado import Empleado
from models.usuarios import Usuario
from models.reseñas import Reseña
from models.empresa import Empresa
from models.certificaciones import Certificacion

EMPRESAS = [
    {
        "nombre": "CARPE DIEM",
        "calle": "CALLE 5 DE MAYO",
        "numero": 123,
        "numero_interior": None,
        "colonia": "SAN JERÓNIMO LÍDICE",
        "ciudad": "PUEBLA",
        "estado": "PUEBLA" ,
        "latitud": 19.0379,
        "longitud": -98.2062
    }
]

CERTIFICACIONES = [
    {
        "nombre": "Distintivo H",
        "empresa": "CARPE DIEM",
        "fecha_vencimiento": "2025-12-31",
        "url_certificado": "https://www.gob.mx/cms/uploads/attachment/file/123456/distintivo_h.pdf"
    }
]

RESEÑAS = [
    {
        "empresa": "CARPE DIEM",
        "usuario": "Juan Pérez",
        "calificacion": 4,
        "comentario": "Excelente lugar para comer, muy limpio y con buena atención."
    },
]

USUARIOS = [
    {
        "nombres": "Juan",
        "apellidos": "Pérez",
        "correo": "juan.perez@example.com",
        "contraseña": "password123",
        "fecha_nacimiento": "1990-01-01"
    }
]

EMPLEADOS = [
    {
        "empresa": "CARPE DIEM",
        "nombres": "María",
        "apellidos": "Gómez"
    }
]

def seed_empleados(session: Session):
    empleados = []
    for empleado in EMPLEADOS:
        stmt = select(Empresa).where(Empresa.nombre == empleado["empresa"]).limit(1)
        empresa = session.execute(stmt).scalar_one()
        empleado = Empleado(
            empresa_uuid=empresa.uuid,
            nombres=empleado["nombres"],
            apellidos=empleado["apellidos"]
        )
        empleados.append(empleado)
    session.add_all(empleados)

def seed_empresas(session: Session):
    empresas = []
    for empresa in EMPRESAS:
        empresa = Empresa(
            nombre=empresa["nombre"],
            calle=empresa["calle"],
            numero=empresa["numero"],
            numero_interior=empresa["numero_interior"],
            colonia=empresa["colonia"],
            ciudad=empresa["ciudad"],
            estado=empresa["estado"],
            latitud=empresa["latitud"],
            longitud=empresa["longitud"]
        )
        empresas.append(empresa)
    session.add_all(empresas)
    
def clear_data(session: Session):
    session.query(Certificacion).delete()
    session.query(Empleado).delete()
    session.query(Empresa).delete()
    session.query(Reseña).delete()
    session.query(Usuario).delete()

def seed_certificaciones(session: Session):
    certificaciones = []
    for certificacion in CERTIFICACIONES:
        stmt = select(Empresa).where(Empresa.nombre == certificacion["empresa"]).limit(1)
        empresa = session.execute(stmt).scalar_one()
        certificacion = Certificacion(
            nombre=certificacion["nombre"],
            fecha_vencimiento=certificacion["fecha_vencimiento"],
            url_certificado=certificacion["url_certificado"],
            empresa_uuid=empresa.uuid
        )
        certificaciones.append(certificacion)
    session.add_all(certificaciones)
    
def seed_usuarios(session: Session):
    usuarios = []
    for usuario in USUARIOS:
        usuario = Usuario(
            nombres=usuario["nombres"],
            apellidos=usuario["apellidos"],
            correo=usuario["correo"],
            contraseña=usuario["contraseña"],
            fecha_nacimiento=usuario["fecha_nacimiento"]
        )
        usuarios.append(usuario)
    session.add_all(usuarios)
    
def seed_reseñas(session: Session):
    reseñas = []
    for reseña in RESEÑAS:
        stmt1 = select(Empresa).where(Empresa.nombre == reseña["empresa"]).limit(1)
        stmt2 = select(Usuario).where(Usuario.nombres + " " + Usuario.apellidos == reseña["usuario"]).limit(1)
        empresa = session.execute(stmt1).scalar_one()
        usuario = session.execute(stmt2).scalar_one()
        reseña = Reseña(
            calificacion=reseña["calificacion"],
            comentario=reseña["comentario"],
            uuid_empresa=empresa.uuid,
            uuid_usuario=usuario.uuid
        )
        reseñas.append(reseña)
    session.add_all(reseñas)

def seed():
    engine = create_engine('mysql+pymysql://root:1234@localhost:3306/VERDEO')
    with Session(engine) as session:
        print("Sembrando datos...")
        
        #Sembrado de datos   
        clear_data(session) 
        seed_empresas(session)
        seed_usuarios(session)
        seed_certificaciones(session)
        seed_reseñas(session)
        seed_empleados(session)
        
        #Guardar cambios en la base de datos
        session.commit()
        
if __name__ == "__main__":
    seed()
    