from typing import Optional, List, Union
from pydantic import BaseModel, Field


class PersonResult(BaseModel):
    id: Optional[str]
    rut: Optional[str]
    dv: Optional[str]
    apellidoPaterno: Optional[str]
    apellidoMaterno: Optional[str]
    nombres: Optional[str]
    pepTitular: Optional[bool]
    categoriaPep: Optional[str]
    categoriaTitular: Optional[str]
    pepPorParentesco: Optional[bool]
    tipoParentesco: Optional[str]
    pepPorAsociacion: Optional[bool]
    razonSocialSociedad: Optional[str]
    rutPepTitularRelacionado: Optional[str]
    dvPepTitularRelacionado: Optional[str]
    nombrePepTitularRelacionado: Optional[str]
    institucionPublica: Optional[str]
    cargo: Optional[str]
    fechaInicio: Optional[str]
    fechaTermino: Optional[str]
    nombreCompleto: Optional[str]
    pais: Optional[str]
    vigente: Optional[Union[str, bool]]  # Could be null, True/False, or empty string
    fecRegistro: Optional[str]
    porcentaje: Optional[int]
    participacion: Optional[Union[str, float, None]]
    participacionTitular: Optional[Union[str, float, None]]
    type: Optional[str]
    formatRut: Optional[str]
    formatRutTitular: Optional[str]
    
    # Optional fields for some result types
    candidato: Optional[str]
    jurisdiccion: Optional[str]
    anoCandidatura: Optional[str]
    nombreRelacionado: Optional[str]
    rutRelacionado: Optional[str]


class Causa(BaseModel):
    id: Optional[str] = None
    fecIngreso: Optional[str] = None
    type: Optional[str] = None
    rolUnico: Optional[str] = None
    tribunal: Optional[str] = None
    rolInterno: Optional[str] = None
    nroInterno: Optional[str] = None
    identificacion: Optional[str] = None
    estado: Optional[str] = None
    estadoAdm: Optional[str] = None
    etapa: Optional[str] = None
    ubicacion: Optional[str] = None
    fecUbicacion: Optional[str] = None
    fecDownload: Optional[str] = None
    materia: Optional[str] = None


class PJUDResult(BaseModel):
    id: str
    rut: Optional[str] = None
    nombre: Optional[str] = None
    estado: Optional[str] = None
    situacion: Optional[str] = None
    delito: Optional[str] = None
    tipoPersona: Optional[str] = None
    causa: Optional[Causa] = None
    rutDte: Optional[str] = None
    nombreDte: Optional[str] = None
    tipoDte: Optional[str] = None
    porcentaje: Optional[float] = None
    fechaCarga: Optional[str] = None
    formatRutDte: Optional[str] = None


# class Results(BaseModel):
#     pepResults: Optional[List[PersonResult]] = []
#     pepHResults: Optional[List[PersonResult]] = []
#     pepCResults: Optional[List[PersonResult]] = []
#     fpResults: Optional[List[PersonResult]] = []
#     pjudResults: Optional[List[PJUDResult]] = []
#     personResults: Optional[List[PersonResult]] = []
#     djResults: Optional[List[PersonResult]] = None
#     negativeResults: Optional[List[PersonResult]] = []
#     vipResults: Optional[List[PersonResult]] = []
#     pepRelacionados: Optional[List[PersonResult]] = []
#     pepHRelacionados: Optional[List[PersonResult]] = []
#     rut: Optional[str] = None
#     name: Optional[str] = None

class Results(BaseModel):
    pepResults: Optional[List[PersonResult]] = Field(default_factory=list)
    pepHResults: Optional[List[PersonResult]] = Field(default_factory=list)
    pepCResults: Optional[List[PersonResult]] = Field(default_factory=list)
    fpResults: Optional[List[PersonResult]] = Field(default_factory=list)
    pjudResults: Optional[List[PJUDResult]] = Field(default_factory=list)
    personResults: Optional[List[PersonResult]] = Field(default_factory=list)
    djResults: Optional[List[PersonResult]] = None
    negativeResults: Optional[List[PersonResult]] = Field(default_factory=list)
    vipResults: Optional[List[PersonResult]] = Field(default_factory=list)
    pepRelacionados: Optional[List[PersonResult]] = Field(default_factory=list)
    pepHRelacionados: Optional[List[PersonResult]] = Field(default_factory=list)
    rut: Optional[str] = None
    name: Optional[str] = None


class AMLResultResponse(BaseModel):
    status: str
    message: Optional[str]
    results: Optional[Results]
