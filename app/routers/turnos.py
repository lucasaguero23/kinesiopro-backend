from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from datetime import date, timedelta, datetime, time
from typing import Optional, List
from app.database import get_db

# MODELOS
from app.models.turno import Turno
from app.models.paciente import Paciente
from app.models.kinesiologo import Kinesiologo
from app.models.servicio import Servicio

# SCHEMAS
from app.schemas.turno_schema import TurnoCreate, TurnoUpdate, TurnoOut

router = APIRouter(
    prefix="/turnos",
    tags=["Turnos"]
)

# ─────────────────────────────────────────────
# 🛡️ Validaciones Auxiliares
# ─────────────────────────────────────────────

def validar_reglas_horarias(fecha_turno: date, hora_inicio: time):
    """Valida fines de semana, rango de atención y fechas pasadas."""
    if fecha_turno.weekday() >= 5: # 5=Sábado, 6=Domingo
        raise HTTPException(
            status_code=400, 
            detail="No se pueden agendar turnos los fines de semana (Sábados y Domingos)."
        )

    if hora_inicio < time(8, 0) or hora_inicio >= time(22, 0):
        raise HTTPException(
            status_code=400, 
            detail="El horario de atención es de 08:00 a 22:00 hs."
        )

    ahora = datetime.now()
    try:
        turno_datetime = datetime.combine(fecha_turno, hora_inicio)
        if turno_datetime < ahora:
            raise HTTPException(status_code=400, detail="No se pueden agendar turnos en el pasado.")
    except Exception:
        pass 

def validar_superposicion(
    db: Session,
    fecha: date,
    inicio: time,
    fin: time,
    kine_id: Optional[int] = None,
    sala_id: Optional[int] = None,
    paciente_id: Optional[int] = None,
    exclude_id: Optional[int] = None
):
    """
    Valida superposición recibiendo parámetros explícitos.
    Lógica: (NuevoInicio < ViejoFin) Y (NuevoFin > ViejoInicio)
    """
    
    query_base = db.query(Turno).filter(
        Turno.fecha == fecha,
        Turno.estado != "cancelado",
        Turno.hora_inicio < fin,
        Turno.hora_fin > inicio 
    )

    if exclude_id:
        query_base = query_base.filter(Turno.id != exclude_id)

    # 1. Validar Kinesiólogo
    if kine_id:
        if query_base.filter(Turno.kinesiologo_id == kine_id).first():
            raise HTTPException(status_code=400, detail="El kinesiólogo ya tiene un turno en ese horario.")

    # 2. Validar Sala
    if sala_id:
        if query_base.filter(Turno.sala_id == sala_id).first():
            raise HTTPException(status_code=400, detail="La sala seleccionada ya está ocupada en ese horario.")

    # 3. Validar Paciente
    if paciente_id:
        if query_base.filter(Turno.paciente_id == paciente_id).first():
            raise HTTPException(status_code=400, detail="El paciente ya tiene otro turno asignado en este horario.")

# ─────────────────────────────────────────────
# ➕ Crear turno
# ─────────────────────────────────────────────
@router.post("/", response_model=TurnoOut, status_code=201)
def crear_turno(turno: TurnoCreate, db: Session = Depends(get_db)):
    # 1. Validaciones básicas
    validar_reglas_horarias(turno.fecha, turno.hora_inicio)

    # 2. Verificar existencia de FKs
    servicio = db.query(Servicio).filter(Servicio.id == turno.servicio_id).first()
    if not servicio: raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    if not db.query(Paciente).filter(Paciente.id == turno.paciente_id).first():
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    if not db.query(Kinesiologo).filter(Kinesiologo.id == turno.kinesiologo_id).first():
        raise HTTPException(status_code=404, detail="Kinesiólogo no encontrado")

    # 3. Calcular Hora Fin
    dt_inicio = datetime.combine(date.today(), turno.hora_inicio)
    duracion = servicio.duracion_minutos
    hora_fin_calculada = (dt_inicio + timedelta(minutes=duracion)).time()

    # 4. Validar Superposición
    validar_superposicion(
        db=db,
        fecha=turno.fecha,
        inicio=turno.hora_inicio,
        fin=hora_fin_calculada,
        kine_id=turno.kinesiologo_id,
        sala_id=turno.sala_id,
        paciente_id=turno.paciente_id
    )

    # 5. Guardar usando DICCIONARIO para forzar hora_fin
    turno_dict = turno.model_dump()
    turno_dict['hora_fin'] = hora_fin_calculada 
    
    nuevo_turno = Turno(**turno_dict) 
    db.add(nuevo_turno)
    db.commit()
    db.refresh(nuevo_turno)
    return nuevo_turno

# ─────────────────────────────────────────────
# 📋 Listar turnos
# ─────────────────────────────────────────────
@router.get("/", response_model=List[TurnoOut])
def listar_turnos(
    db: Session = Depends(get_db),
    fecha: Optional[date] = Query(None),
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
    estado: Optional[str] = Query(None),
    kinesiologo_id: Optional[int] = Query(None),
    paciente_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    query = db.query(Turno).options(
        joinedload(Turno.paciente).joinedload(Paciente.user),
        joinedload(Turno.kinesiologo).joinedload(Kinesiologo.user),
        joinedload(Turno.servicio),
        joinedload(Turno.sala)
    )

    if fecha: query = query.filter(Turno.fecha == fecha)
    if desde: query = query.filter(Turno.fecha >= desde)
    if hasta: query = query.filter(Turno.fecha <= hasta)
    if estado: query = query.filter(Turno.estado == estado)
    if kinesiologo_id: query = query.filter(Turno.kinesiologo_id == kinesiologo_id)
    if paciente_id: query = query.filter(Turno.paciente_id == paciente_id)

    return query.order_by(Turno.fecha.asc(), Turno.hora_inicio.asc()).offset(skip).limit(limit).all()

# ─────────────────────────────────────────────
# ✏️ Actualizar turno
# ─────────────────────────────────────────────
@router.put("/{turno_id}", response_model=TurnoOut)
def actualizar_turno(turno_id: int, turno_update: TurnoUpdate, db: Session = Depends(get_db)):
    turno_existente = db.query(Turno).filter(Turno.id == turno_id).first()
    if not turno_existente:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    update_dict = turno_update.model_dump(exclude_unset=True)

    if any(k in update_dict for k in ["fecha", "hora_inicio", "kinesiologo_id", "sala_id", "servicio_id"]):
        
        nueva_fecha = update_dict.get("fecha", turno_existente.fecha)
        nueva_hora_ini = update_dict.get("hora_inicio", turno_existente.hora_inicio)
        
        validar_reglas_horarias(nueva_fecha, nueva_hora_ini)

        id_serv = update_dict.get("servicio_id", turno_existente.servicio_id)
        servicio = db.query(Servicio).filter(Servicio.id == id_serv).first()
        duracion = servicio.duracion_minutos if servicio else 30
        
        dt_start = datetime.combine(date.today(), nueva_hora_ini)
        nueva_hora_fin = (dt_start + timedelta(minutes=duracion)).time()

        validar_superposicion(
            db=db,
            fecha=nueva_fecha,
            inicio=nueva_hora_ini,
            fin=nueva_hora_fin,
            kine_id=update_dict.get("kinesiologo_id", turno_existente.kinesiologo_id),
            sala_id=update_dict.get("sala_id", turno_existente.sala_id),
            paciente_id=update_dict.get("paciente_id", turno_existente.paciente_id),
            exclude_id=turno_id
        )
        
        turno_existente.hora_fin = nueva_hora_fin

    for field, value in update_dict.items():
        setattr(turno_existente, field, value)

    db.commit()
    db.refresh(turno_existente)
    return turno_existente

# ─────────────────────────────────────────────
# ⚙️ Otros Endpoints
# ─────────────────────────────────────────────

@router.get("/{turno_id}", response_model=TurnoOut)
def obtener_turno(turno_id: int, db: Session = Depends(get_db)):
    turno = db.query(Turno).filter(Turno.id == turno_id).first()
    if not turno: raise HTTPException(status_code=404, detail="Turno no encontrado")
    return turno

@router.patch("/{turno_id}/estado")
def cambiar_estado(
    turno_id: int, 
    estado: str = Query(...), 
    db: Session = Depends(get_db)
):
    turno = db.query(Turno).filter(Turno.id == turno_id).first()
    if not turno: 
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    # 🛡️ VALIDACIÓN DE CANCELACIÓN TARDÍA
    if estado == "cancelado" and turno.estado != "cancelado":
        ahora = datetime.now()
        fecha_hora_turno = datetime.combine(turno.fecha, turno.hora_inicio)
        
        # Calculamos la diferencia
        tiempo_restante = fecha_hora_turno - ahora
        
        # Si falta menos de 24 horas (y no es una fecha pasada)
        if timedelta(hours=0) < tiempo_restante < timedelta(hours=24):
            raise HTTPException(
                status_code=400, 
                detail="Política de cancelación: No se puede cancelar con menos de 24hs de anticipación. Debe llamar por teléfono."
            )

    turno.estado = estado
    db.commit()
    return {"message": f"Estado del turno #{turno_id} actualizado a '{estado}'."}

@router.delete("/{turno_id}")
def eliminar_turno(turno_id: int, db: Session = Depends(get_db)):
    turno = db.query(Turno).filter(Turno.id == turno_id).first()
    if not turno: raise HTTPException(status_code=404, detail="Turno no encontrado")
    db.delete(turno)
    db.commit()
    return {"message": f"Turno #{turno_id} eliminado correctamente."}

@router.get("/calendario/", response_model=list[TurnoOut])
def obtener_turnos_calendario(
    fecha_inicio: date, fecha_fin: date,
    kinesiologo_id: Optional[int] = None,
    sala_id: Optional[int] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Turno).options(
        joinedload(Turno.paciente).joinedload(Paciente.user),
        joinedload(Turno.kinesiologo).joinedload(Kinesiologo.user),
        joinedload(Turno.servicio),
        joinedload(Turno.sala)
    ).filter(Turno.fecha >= fecha_inicio, Turno.fecha <= fecha_fin)
    
    if kinesiologo_id: query = query.filter(Turno.kinesiologo_id == kinesiologo_id)
    if sala_id: query = query.filter(Turno.sala_id == sala_id)
    if estado: query = query.filter(Turno.estado == estado)
    
    return query.order_by(Turno.fecha, Turno.hora_inicio).all()

@router.put("/{turno_id}/mover", response_model=TurnoOut)
def mover_turno(
    turno_id: int, nueva_fecha: date, nueva_hora_inicio: str, db: Session = Depends(get_db)
):
    turno = db.query(Turno).filter(Turno.id == turno_id).first()
    if not turno: raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    try:
        fmt = "%H:%M" if len(nueva_hora_inicio) == 5 else "%H:%M:%S"
        hora_inicio_obj = datetime.strptime(nueva_hora_inicio, fmt).time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de hora inválido")

    validar_reglas_horarias(nueva_fecha, hora_inicio_obj)

    duracion = datetime.combine(date.min, turno.hora_fin) - datetime.combine(date.min, turno.hora_inicio)
    hora_fin_obj = (datetime.combine(date.today(), hora_inicio_obj) + duracion).time()

    validar_superposicion(
        db=db,
        fecha=nueva_fecha,
        inicio=hora_inicio_obj,
        fin=hora_fin_obj,
        kine_id=turno.kinesiologo_id,
        sala_id=turno.sala_id,
        paciente_id=turno.paciente_id,
        exclude_id=turno_id
    )

    turno.fecha = nueva_fecha
    turno.hora_inicio = hora_inicio_obj
    turno.hora_fin = hora_fin_obj
    
    db.commit()
    db.refresh(turno)
    return turno