from tokenize import Double3
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from starlette.datastructures import MutableHeaders
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from sqlalchemy.orm import sessionmaker
from sqlalchemy import Float, String, Integer, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
import time
from fastapi.responses import FileResponse
import boto3

session = boto3.Session(aws_access_key_id='',
aws_secret_access_key='',
 aws_session_token='')

s3 = session.resource('s3')

class Profesor(BaseModel):
    #id: int #= 1
    nombres: str #= "Prueba Profesor"
    apellidos: str #= "Ferraez"
    numeroEmpleado: int #= 1
    horasClase: int# = 4

class Alumno(BaseModel):
    #id: int #= 1
    nombres: str #= "Prueba Profesor"
    apellidos: str #= "Ferraez"
    matricula: str #= 1
    promedio: float #= 9

Base = declarative_base()
class ProfesorDB(Base):
    __tablename__ = 'profesores'
    id = Column(Integer, primary_key=True)
    nombres = Column(String(200))
    apellidos = Column(String(200))
    numeroEmpleado = Column(Integer)
    horasClase = Column(Integer)
class AlumnoDB(Base):
    __tablename__ = 'alumnos'
    id = Column(Integer, primary_key=True)
    nombres = Column(String(200))
    apellidos = Column(String(200))
    matricula = Column(String(200))
    promedio = Column(Float)
    fotoPerfilUrl = Column(String(1000)) 

app = FastAPI()
engine = create_engine(
    "mysql+pymysql://admin:9999886410@database-1.cjijrujhklho.us-east-1.rds.amazonaws.com/sicei",echo=True
)
sessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = sessionMaker()

Base.metadata.create_all(engine)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["Process-Time"] = str(process_time)
    return response

@app.get("/")
async def docs_redirect():
    response = RedirectResponse(url='/docs')
    return response    

profesores_dict: Dict[str, Profesor] = dict()
alumnos_dict: Dict[str, Alumno] = dict()

@app.get("/alumnos")
async def get_alumnos():
    return session.query(AlumnoDB).all()

from fastapi import FastAPI, File, UploadFile

@app.post("/alumnos/{id}/fotoPerfil")
async def create_upload_file( id:int, file: UploadFile = File(...),):

    contents = await file.read() 
    object = s3.Object('aws-sicei2', f'{id}.jpg')
    result = object.put(Body= (contents), ACL='public-read')
    print(result)
    alumno = session.query(AlumnoDB).get(id)
    alumno.fotoPerfilUrl = f"https://aws-sicei2.s3.amazonaws.com/{id}.jpg"
    session.commit()
    return {"filename": f"https://aws-sicei2.s3.amazonaws.com/{id}.jpg"}
    
@app.get("/alumnos/{id}")
async def get_alumno(id:int):

    alumno = session.query(AlumnoDB).get(id)

    if alumno is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return alumno


@app.post("/alumnos", status_code=201)
async def crear_alumno(alumno:Alumno):
    session.add(AlumnoDB(nombres=alumno.nombres, apellidos=alumno.apellidos, matricula=alumno.matricula, promedio=alumno.promedio, fotoPerfilUrl=""))
    session.commit()
    return alumno

@app.put("/alumnos/{id}")
async def actualizar_alumno(alumno:Alumno, id:int):

    alumnoDB = session.query(AlumnoDB).get(id)

    if alumnoDB is None:
        raise HTTPException(status_code=404, detail="Item not found")

    alumnoDB.nombres = alumno.nombres
    alumnoDB.apellidos = alumno.apellidos
    alumnoDB.matricula = alumno.matricula
    alumnoDB.promedio = alumno.promedio
    session.commit()
    return alumno

@app.delete("/alumnos/{id}")
async def get_alumno(id:int):

    alumnoDB = session.query(AlumnoDB).get(id)

    if alumnoDB is None:
        raise HTTPException(status_code=404, detail="Item not found")

    session.delete(alumnoDB)
    session.commit()
    
    return {
        "message": f"deleted {id}"
    }

@app.get("/profesores")
async def get_profesores():
    return session.query(ProfesorDB).all() 

@app.get("/profesores/{id}")
async def get_profesor(id:int):

    profesor = session.query(ProfesorDB).get(id)

    if profesor is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return profesor


@app.post("/profesores", status_code=201)
async def crear_profesor(profesor:Profesor):
    session.add(ProfesorDB(nombres=profesor.nombres, apellidos=profesor.apellidos, 
    numeroEmpleado=profesor.numeroEmpleado, horasClase = profesor.horasClase))
    session.commit()
    return profesor

@app.put("/profesores/{id}")
async def actualizar_profesor(profesor:Profesor, id:int):

    profesorDB = session.query(ProfesorDB).get(id)

    if profesorDB is None:
        raise HTTPException(status_code=404, detail="Item not found")

    profesorDB.nombres = profesor.nombres
    profesorDB.apellidos = profesor.apellidos
    profesorDB.numeroEmpleado = profesor.numeroEmpleado
    profesorDB.horasClase = profesor.horasClase
    session.commit()
    return profesor

@app.delete("/profesores/{id}")
async def delete_profesor(id:int):


    profesorDB = session.query(ProfesorDB).get(id)

    if profesorDB is None:
        raise HTTPException(status_code=404, detail="Item not found")

    session.delete(profesorDB)
    session.commit()
    
    return {
        "message": f"deleted {id}"
    }
















