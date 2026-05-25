from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.crud import servicio_crud
from app.schemas.servicio_schema import ServicioCreate, ServicioUpdate, ServicioOut

router = APIRouter(prefix="/servicios", tags=["Servicios"])

@router.get("/", response_model=list[ServicioOut])
def listar_servicios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return servicio_crud.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=ServicioOut, status_code=201)
def crear_servicio(servicio: ServicioCreate, db: Session = Depends(get_db)):
    return servicio_crud.create(db, servicio)

@router.get("/{servicio_id}", response_model=ServicioOut)
def obtener_servicio(servicio_id: int, db: Session = Depends(get_db)):
    return servicio_crud.get_or_404(db, servicio_id)

@router.put("/{servicio_id}", response_model=ServicioOut)
def actualizar_servicio(servicio_id: int, servicio: ServicioUpdate, db: Session = Depends(get_db)):
    updated = servicio_crud.update(db, servicio_id, servicio)
    if not updated:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return updated

@router.delete("/{servicio_id}")
def eliminar_servicio(servicio_id: int, db: Session = Depends(get_db)):
    deleted = servicio_crud.delete(db, servicio_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return {"message": "Servicio eliminado correctamente"}
