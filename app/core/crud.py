from app.core.crud_base import CRUDBase
from app.models.paciente import Paciente
from app.models.kinesiologo import Kinesiologo
from app.models.sala import Sala
from app.models.servicio import Servicio
from app.models.user import User
from app.models.role import Role
from app.schemas.paciente_schema import PacienteCreate, PacienteUpdate
from app.schemas.kinesiologo_schema import KinesiologoCreate, KinesiologoUpdate
from app.schemas.sala_schema import SalaCreate, SalaUpdate
from app.schemas.servicio_schema import ServicioCreate, ServicioUpdate
from app.schemas.user_schema import UserCreate, UserUpdate
from app.schemas.role_schema import RoleCreate, RoleUpdate

# Instancias CRUD para cada modelo
paciente_crud = CRUDBase[Paciente, PacienteCreate, PacienteUpdate](Paciente)
kinesiologo_crud = CRUDBase[Kinesiologo, KinesiologoCreate, KinesiologoUpdate](Kinesiologo)
sala_crud = CRUDBase[Sala, SalaCreate, SalaUpdate](Sala)
servicio_crud = CRUDBase[Servicio, ServicioCreate, ServicioUpdate](Servicio)
user_crud = CRUDBase[User, UserCreate, UserUpdate](User)
role_crud = CRUDBase[Role, RoleCreate, RoleUpdate](Role)
