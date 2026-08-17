from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from CORE.config import settings

'''crea una conexion a la base de datos utilizando la URL de la base de datos especificada en el archivo .env'''
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

'''session maker es una clase que crea una nueva sesión de base de datos cada vez que se llama. Se utiliza para interactuar con la base de datos, por lo que se necesita una sesión para realizar cualquier operación en la base de datos.'''
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
'''indica que cada sesion creada debe de usar ese engine, el cual corresponde a la conexion a la base de datos especificada en el archivo .env'''

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    '''hasta este punto es donde se crea una sesion de base de datos, que se utilizará para interactuar con la base de datos,almacena y deja cambios pendientes, los sincroniza con la base de datos cuando corresponde, y cierra la sesion cuando ya no se necesita'''

    try:
        yield db

    finally:
        db.close()
'''el yield db entrega temporalmente la sesion de base de datos para que se pueda utilizar en otras partes del proyecto, como en los endpoints de la API, y cuando ya no se necesita, se cierra la sesion'''
