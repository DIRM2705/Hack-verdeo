from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.empresa import Empresa

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

def seed():
    engine = create_engine('mysql+pymysql://root:1234@localhost:3306/VERDEO')
    with Session(engine) as session:
        print("Sembrando datos...")
        
        #Sembrado de datos    
        seed_empresas(session)
        
        #Guardar cambios en la base de datos
        session.commit()
        
if __name__ == "__main__":
    seed()
    