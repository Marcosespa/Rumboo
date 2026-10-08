"""Única parte de core que conoce FastAPI: sesión de BD por petición y traducción de errores de negocio."""
from typing import Annotated
from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.errores import Conflicto, ErrorDominio, Invalido, NoAutorizado, NoEncontrado

HTTP_STATUS = {NoEncontrado: 404, Conflicto: 409, Invalido: 422, NoAutorizado: 401}


def get_db(request: Request):
    with request.app.state.sessions() as session:
        yield session


DB = Annotated[Session, Depends(get_db)]


async def domain_error(request, exc: ErrorDominio):
    return JSONResponse(status_code=HTTP_STATUS.get(type(exc), 400), content={"detail": exc.mensaje})
