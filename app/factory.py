from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
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
        "estado": "PUEBLA"  
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
            estado=empresa["estado"]
        )
        empresas.append(empresa)
    session.add_all(empresas)
    
def clear_data(session: Session):
    session.query(Certificacion).delete()
    session.query(Empresa).delete()
    
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

def seed():
    engine = create_engine('mysql+pymysql://root:1234@localhost:3306/VERDEO')
    with Session(engine) as session:
        print("Sembrando datos...")
        
        #Sembrado de datos   
        clear_data(session) 
        seed_empresas(session)
        seed_certificaciones(session)
        
        #Guardar cambios en la base de datos
        session.commit()
        
if __name__ == "__main__":
    seed()
    