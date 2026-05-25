from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.crud import sala_crud
from app.schemas.sala_schema import SalaCreate, SalaUpdate, SalaOut

router = APIRouter(prefix="/salas", tags=["Salas"])

@router.get("/", response_model=list[SalaOut])
def listar_salas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return sala_crud.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=SalaOut, status_code=201)
def crear_sala(sala: SalaCreate, db: Session = Depends(get_db)):
    return sala_crud.create(db, sala)

@router.get("/{sala_id}", response_model=SalaOut)
def obtener_sala(sala_id: int, db: Session = Depends(get_db)):
    return sala_crud.get_or_404(db, sala_id)

@router.put("/{sala_id}", response_model=SalaOut)
def actualizar_sala(sala_id: int, sala: SalaUpdate, db: Session = Depends(get_db)):
    updated = sala_crud.update(db, sala_id, sala)
    if not updated:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    return updated

@router.delete("/{sala_id}")
def eliminar_sala(sala_id: int, db: Session = Depends(get_db)):
    deleted = sala_crud.delete(db, sala_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    return {"message": "Sala eliminada correctamente"}
