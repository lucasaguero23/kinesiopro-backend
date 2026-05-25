"""
Funciones de validación centralizadas para el backend
Contiene validaciones reutilizables y mensajes estandarizados
"""
from typing import Optional
from pydantic import EmailStr, ValidationError, TypeAdapter
from fastapi import HTTPException
import re


# ══════════════════════════════════════════════════════════════════════════
# VALIDADORES DE FORMATO
# ══════════════════════════════════════════════════════════════════════════

def validar_password_fuerte(v: str) -> str:
    """
    Valida reglas de complejidad de contraseña
    - Mínimo 8 caracteres
    - Al menos 1 número
    - Al menos 1 letra mayúscula
    
    Args:
        v: Contraseña a validar
        
    Returns:
        La contraseña validada
        
    Raises:
        ValueError: Si la contraseña no cumple los requisitos
    """
    if len(v) < 8:
        raise ValueError('La contraseña debe tener al menos 8 caracteres.')
    if not re.search(r"\d", v):
        raise ValueError('La contraseña debe contener al menos un número.')
    if not re.search(r"[A-Z]", v):
        raise ValueError('La contraseña debe contener al menos una letra mayúscula.')
    return v


def validar_dni(dni: Optional[str]) -> Optional[str]:
    """
    Valida formato de DNI argentino
    - Solo números
    - Entre 6 y 10 dígitos
    - Limpia puntos y espacios automáticamente
    
    Args:
        dni: DNI a validar
        
    Returns:
        DNI limpio (solo números)
        
    Raises:
        ValueError: Si el DNI no cumple los requisitos
    """
    if dni is None or dni.strip() == '':
        return None
        
    # Limpiar puntos y espacios
    dni_limpio = dni.replace(".", "").replace(" ", "").strip()
    
    # Validar que solo contenga números
    if not dni_limpio.isdigit():
        raise ValueError('El DNI debe contener solo números')
    
    # Validar longitud
    if len(dni_limpio) < 6 or len(dni_limpio) > 10:
        raise ValueError('El DNI debe tener entre 6 y 10 dígitos')
    
    return dni_limpio


def validar_telefono(telefono: Optional[str]) -> Optional[str]:
    """
    Valida formato de teléfono
    - Permite números, +, -, espacios, paréntesis
    - Al menos 6 dígitos
    
    Args:
        telefono: Teléfono a validar
        
    Returns:
        Teléfono validado
        
    Raises:
        ValueError: Si el teléfono no cumple los requisitos
    """
    if telefono is None or telefono.strip() == '':
        return None
    
    # Permitir números, +, -, espacios y paréntesis
    if not re.match(r'^[\d\+\-\s()]+$', telefono):
        raise ValueError('El teléfono contiene caracteres inválidos (solo se permiten números, +, -, (), espacios)')
    
    # Verificar que tenga al menos 6 dígitos
    solo_digitos = re.sub(r'\D', '', telefono)
    if len(solo_digitos) < 6:
        raise ValueError('El teléfono debe tener al menos 6 dígitos')
    
    return telefono.strip()


def validar_email_formato(email: str) -> str:
    """
    Valida formato de email usando Pydantic EmailStr
    
    Args:
        email: Email a validar
        
    Returns:
        Email validado en minúsculas
        
    Raises:
        HTTPException 400: Si el formato del email no es válido
    """
    if not email or not email.strip():
        raise HTTPException(
            status_code=400, 
            detail="El email es obligatorio"
        )
    
    email_limpio = email.strip().lower()
    
    try:
        TypeAdapter(EmailStr).validate_python(email_limpio)
    except ValidationError:
        raise HTTPException(
            status_code=400, 
            detail="El formato del email no es válido (debe contener @ y un dominio válido)"
        )
    
    return email_limpio


def validar_matricula(matricula: Optional[str]) -> Optional[str]:
    """
    Valida matrícula profesional
    - No puede estar vacía en creación
    - Mínimo 3 caracteres
    
    Args:
        matricula: Matrícula a validar
        
    Returns:
        Matrícula validada
        
    Raises:
        ValueError: Si la matrícula no cumple los requisitos
    """
    if matricula is None or matricula.strip() == '':
        return None
    
    matricula_limpia = matricula.strip()
    
    if len(matricula_limpia) < 3:
        raise ValueError('La matrícula profesional debe tener al menos 3 caracteres')
    
    return matricula_limpia


# ══════════════════════════════════════════════════════════════════════════
# VALIDADORES DE TEXTO
# ══════════════════════════════════════════════════════════════════════════

def capitalizar_texto(texto: Optional[str]) -> Optional[str]:
    """
    Capitaliza un texto (primera letra de cada palabra en mayúscula)
    
    Args:
        texto: Texto a capitalizar
        
    Returns:
        Texto capitalizado
    """
    if not texto or texto.strip() == '':
        return None
    return texto.strip().title()


def limpiar_espacios(texto: Optional[str]) -> Optional[str]:
    """
    Limpia espacios innecesarios de un texto
    
    Args:
        texto: Texto a limpiar
        
    Returns:
        Texto sin espacios extras
    """
    if not texto:
        return None
    return ' '.join(texto.split())


# ══════════════════════════════════════════════════════════════════════════
# MENSAJES DE ERROR ESTANDARIZADOS
# ══════════════════════════════════════════════════════════════════════════

class MensajesError:
    """Mensajes de error estandarizados para usar en todo el backend"""
    
    # Errores de autenticación
    CREDENCIALES_INVALIDAS = "Credenciales incorrectas. Verifica tu email y contraseña."
    USUARIO_INACTIVO = "Tu cuenta está inactiva. Contacta al administrador."
    TOKEN_INVALIDO = "Token de autenticación inválido o expirado. Por favor inicia sesión nuevamente."
    
    # Errores de duplicados
    @staticmethod
    def email_duplicado(email: str) -> str:
        return f"El email '{email}' ya está registrado en el sistema."
    
    @staticmethod
    def dni_duplicado(dni: str) -> str:
        return f"El DNI {dni} ya está registrado para otro paciente."
    
    @staticmethod
    def matricula_duplicada(matricula: str) -> str:
        return f"La matrícula '{matricula}' ya está registrada para otro kinesiólogo."
    
    # Errores de no encontrado
    USUARIO_NO_ENCONTRADO = "Usuario no encontrado en el sistema."
    PACIENTE_NO_ENCONTRADO = "Paciente no encontrado."
    KINESIOLOGO_NO_ENCONTRADO = "Kinesiólogo no encontrado."
    
    # Errores de lógica de negocio
    PERFIL_YA_EXISTE = "Este usuario ya tiene un perfil creado."
    KINESIOLOGO_CON_TURNOS = "No se puede eliminar: el kinesiólogo tiene turnos activos. Reasígnalos primero."
    
    @staticmethod
    def kinesiologo_con_n_turnos(cantidad: int) -> str:
        turno_str = "turno" if cantidad == 1 else "turnos"
        return f"No se puede eliminar: el kinesiólogo tiene {cantidad} {turno_str} activo(s) pendiente(s) o confirmado(s)."
    
    # Errores de validación
    CAMPO_REQUERIDO = "Este campo es obligatorio."
    EMAIL_INVALIDO = "El formato del email no es válido."
    PASSWORD_DEBIL = "La contraseña no cumple los requisitos de seguridad."
    DNI_INVALIDO = "El DNI debe contener solo números y tener entre 6 y 10 dígitos."
    TELEFONO_INVALIDO = "El formato del teléfono no es válido."


# ══════════════════════════════════════════════════════════════════════════
# FUNCIONES HELPER
# ══════════════════════════════════════════════════════════════════════════

def crear_error_validacion(campo: str, mensaje: str) -> dict:
    """
    Crea un error de validación en formato estandarizado
    
    Args:
        campo: Nombre del campo con error
        mensaje: Mensaje de error
        
    Returns:
        Dict con formato de error de Pydantic
    """
    return {
        "detail": [
            {
                "loc": ["body", campo],
                "msg": mensaje,
                "type": "value_error"
            }
        ]
    }
