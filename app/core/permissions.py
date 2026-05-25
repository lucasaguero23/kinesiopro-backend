from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user 
from app.models.user import User

def role_required(*allowed_roles: str):
    """
    Permite el acceso si el usuario tiene AL MENOS UNO de los roles permitidos.
    El rol 'admin' siempre tiene acceso implícito (superusuario).
    Uso: role_required("kinesiologo", "recepcionista")
    """
    def wrapper(current_user: User = Depends(get_current_user)):
        user_roles = [r.name for r in current_user.roles]
        
        # Si es admin, pasa siempre
        if "admin" in user_roles:
            return current_user

        # Verificar si tiene alguno de los roles requeridos
        has_permission = any(role in user_roles for role in allowed_roles)
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de los siguientes roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return wrapper