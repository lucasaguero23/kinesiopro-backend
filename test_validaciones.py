import requests
import json
from datetime import date, timedelta

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════

BASE_URL = "http://127.0.0.1:8000"
VERDE = "\033[92m"
ROJO = "\033[91m"
RESET = "\033[0m"
AMARILLO = "\033[93m"
AZUL = "\033[94m"
MAGENTA = "\033[95m"

# Credenciales de admin (debes tener este usuario creado)
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin123"

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES HELPER
# ═══════════════════════════════════════════════════════════════════════════

def print_result(test_name, success, message=""):
    """Imprime resultado de un test con colores"""
    estado = f"{VERDE}✅ PASÓ{RESET}" if success else f"{ROJO}❌ FALLÓ{RESET}"
    print(f"{estado} | {test_name}")
    if message:
        print(f"   └─ {message}")

def print_section(title):
    """Imprime título de sección"""
    print(f"\n{AZUL}{'═' * 70}{RESET}")
    print(f"{AZUL}║ {title}{RESET}")
    print(f"{AZUL}{'═' * 70}{RESET}\n")

def get_token(email, password):
    """Obtiene token de autenticación"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login", 
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
    except Exception as e:
        print(f"{ROJO}Error obteniendo token: {e}{RESET}")
    return None

def cleanup_test_data(headers):
    """Limpia datos de prueba (opcional)"""
    # Puedes agregar lógica para limpiar datos de test aquí
    pass

# ═══════════════════════════════════════════════════════════════════════════
# TESTS DE VALIDACIÓN DE CONTRASEÑAS
# ═══════════════════════════════════════════════════════════════════════════

def test_validacion_passwords(headers):
    print_section("GRUPO 1: VALIDACIÓN DE CONTRASEÑAS")
    
    # Test 1.1: Contraseña muy corta (< 8 caracteres)
    payload_short = {
        "nombre": "Test User", 
        "email": "test.short@test.com", 
        "password": "Abc1"  # Solo 4 caracteres
    }
    try:
        res = requests.post(f"{BASE_URL}/auth/register", json=payload_short)
        print_result(
            "Contraseña corta (< 8 chars)",
            res.status_code in [422, 400],
            f"Status: {res.status_code} - {res.json().get('detail', '')[:50]}"
        )
    except Exception as e:
        print_result("Contraseña corta", False, f"Error: {str(e)}")
    
    # Test 1.2: Contraseña sin números
    payload_no_number = {
        "nombre": "Test User", 
        "email": "test.nonumber@test.com", 
        "password": "Abcdefghij"  # Sin números
    }
    try:
        res = requests.post(f"{BASE_URL}/auth/register", json=payload_no_number)
        print_result(
            "Contraseña sin números",
            res.status_code in [422, 400],
            f"Status: {res.status_code}"
        )
    except Exception as e:
        print_result("Contraseña sin números", False, f"Error: {str(e)}")
    
    # Test 1.3: Contraseña sin mayúsculas
    payload_no_upper = {
        "nombre": "Test User", 
        "email": "test.noupper@test.com", 
        "password": "abcdefgh123"  # Sin mayúsculas
    }
    try:
        res = requests.post(f"{BASE_URL}/auth/register", json=payload_no_upper)
        print_result(
            "Contraseña sin mayúsculas",
            res.status_code in [422, 400],
            f"Status: {res.status_code}"
        )
    except Exception as e:
        print_result("Contraseña sin mayúsculas", False, f"Error: {str(e)}")
    
    # Test 1.4: Contraseña válida
    payload_valid = {
        "nombre": "Test User Valid", 
        "email": "test.valid.pwd@test.com", 
        "password": "ValidPass123"  # Contraseña válida
    }
    try:
        res = requests.post(f"{BASE_URL}/auth/register", json=payload_valid)
        print_result(
            "Contraseña válida",
            res.status_code == 200,
            f"Status: {res.status_code}"
        )
    except Exception as e:
        print_result("Contraseña válida", False, f"Error: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════
# TESTS DE VALIDACIÓN DE DNI
# ═══════════════════════════════════════════════════════════════════════════

def test_validacion_dni(headers):
    print_section("GRUPO 2: VALIDACIÓN DE DNI")
    
    # Test 2.1: DNI con letras
    payload_dni_letters = {
        "nombre": "Paciente Test",
        "email": "pac.dnileters@test.com",
        "password": "TestPass123",
        "dni": "ABC12345"  # DNI con letras
    }
    try:
        res = requests.post(f"{BASE_URL}/pacientes/con-usuario", json=payload_dni_letters, headers=headers)
        print_result(
            "DNI con letras",
            res.status_code in [422, 400],
            f"Status: {res.status_code}"
        )
    except Exception as e:
        print_result("DNI con letras", False, f"Error: {str(e)}")
    
    # Test 2.2: DNI muy corto (< 6 dígitos)
    payload_dni_short = {
        "nombre": "Paciente Test",
        "email": "pac.dnishort@test.com",
        "password": "TestPass123",
        "dni": "12345"  # Solo 5 dígitos
    }
    try:
        res = requests.post(f"{BASE_URL}/pacientes/con-usuario", json=payload_dni_short, headers=headers)
        print_result(
            "DNI corto (< 6 dígitos)",
            res.status_code in [422, 400],
            f"Status: {res.status_code}"
        )
    except Exception as e:
        print_result("DNI corto", False, f"Error: {str(e)}")
    
    # Test 2.3: DNI muy largo (> 10 dígitos)
    payload_dni_long = {
        "nombre": "Paciente Test",
        "email": "pac.dnilong@test.com",
        "password": "TestPass123",
        "dni": "12345678901"  # 11 dígitos
    }
    try:
        res = requests.post(f"{BASE_URL}/pacientes/con-usuario", json=payload_dni_long, headers=headers)
        print_result(
            "DNI largo (> 10 dígitos)",
            res.status_code in [422, 400],
            f"Status: {res.status_code}"
        )
    except Exception as e:
        print_result("DNI largo", False, f"Error: {str(e)}")
    
    # Test 2.4: DNI válido
    payload_dni_valid = {
        "nombre": "Paciente DNI Valido",
        "email": "pac.dnivalid@test.com",
        "password": "TestPass123",
        "dni": "12345678"  # DNI válido
    }
    try:
        res = requests.post(f"{BASE_URL}/pacientes/con-usuario", json=payload_dni_valid, headers=headers)
        print_result(
            "DNI válido (8 dígitos)",
            res.status_code == 201,
            f"Status: {res.status_code}"
        )
        
        # Test 2.5: Intentar crear otro paciente con el mismo DNI
        if res.status_code == 201:
            payload_dni_dup = {
                "nombre": "Paciente Duplicado",
                "email": "pac.dnidup@test.com",
                "password": "TestPass123",
                "dni": "12345678"  # Mismo DNI
            }
            res_dup = requests.post(f"{BASE_URL}/pacientes/con-usuario", json=payload_dni_dup, headers=headers)
            print_result(
                "DNI duplicado bloqueado",
                res_dup.status_code == 400,
                f"Status: {res_dup.status_code}"
            )
    except Exception as e:
        print_result("DNI válido", False, f"Error: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════
# TESTS DE VALIDACIÓN DE EMAIL
# ═══════════════════════════════════════════════════════════════════════════

def test_validacion_email(headers):
    print_section("GRUPO 3: VALIDACIÓN DE EMAIL")
    
    # Test 3.1: Email sin @
    payload_no_at = {
        "nombre": "Test User",
        "email": "emailsinprovidercom",
        "password": "TestPass123"
    }
    try:
        res = requests.post(f"{BASE_URL}/auth/register", json=payload_no_at)
        print_result(
            "Email sin @",
            res.status_code in [422, 400],
            f"Status: {res.status_code}"
        )
    except Exception as e:
        print_result("Email sin @", False, f"Error: {str(e)}")
    
    # Test 3.2: Email sin dominio
    payload_no_domain = {
        "nombre": "Test User",
        "email": "email@",
        "password": "TestPass123"
    }
    try:
        res = requests.post(f"{BASE_URL}/auth/register", json=payload_no_domain)
        print_result(
            "Email sin dominio",
            res.status_code in [422, 400],
            f"Status: {res.status_code}"
        )
    except Exception as e:
        print_result("Email sin dominio", False, f"Error: {str(e)}")
    
    # Test 3.3: Email válido
    payload_valid_email = {
        "nombre": "Test User Valid Email",
        "email": "valid.email@test.com",
        "password": "TestPass123"
    }
    try:
        res = requests.post(f"{BASE_URL}/auth/register", json=payload_valid_email)
        print_result(
            "Email válido",
            res.status_code == 200,
            f"Status: {res.status_code}"
        )
        
        # Test 3.4: Intentar registrar mismo email
        if res.status_code == 200:
            res_dup = requests.post(f"{BASE_URL}/auth/register", json=payload_valid_email)
            print_result(
                "Email duplicado bloqueado",
                res_dup.status_code == 400,
                f"Status: {res_dup.status_code}"
            )
    except Exception as e:
        print_result("Email válido", False, f"Error: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════
# TESTS DE VALIDACIÓN DE TELÉFONO
# ═══════════════════════════════════════════════════════════════════════════

def test_validacion_telefono(headers):
    print_section("GRUPO 4: VALIDACIÓN DE TELÉFONO")
    
    # Test 4.1: Teléfono con caracteres inválidos
    payload_tel_invalid = {
        "nombre": "Paciente Tel Test",
        "email": "pac.telinvalid@test.com",
        "password": "TestPass123",
        "dni": "23456789",
        "telefono": "123-456-ABCD"  # Tiene letras
    }
    try:
        res = requests.post(f"{BASE_URL}/pacientes/con-usuario", json=payload_tel_invalid, headers=headers)
        print_result(
            "Teléfono con caracteres inválidos",
            res.status_code in [422, 400],
            f"Status: {res.status_code}"
        )
    except Exception as e:
        print_result("Teléfono inválido", False, f"Error: {str(e)}")
    
    # Test 4.2: Teléfono muy corto
    payload_tel_short = {
        "nombre": "Paciente Tel Test",
        "email": "pac.telshort@test.com",
        "password": "TestPass123",
        "dni": "34567890",
        "telefono": "12345"  # Solo 5 dígitos
    }
    try:
        res = requests.post(f"{BASE_URL}/pacientes/con-usuario", json=payload_tel_short, headers=headers)
        print_result(
            "Teléfono muy corto (< 6 dígitos)",
            res.status_code in [422, 400],
            f"Status: {res.status_code}"
        )
    except Exception as e:
        print_result("Teléfono corto", False, f"Error: {str(e)}")
    
    # Test 4.3: Teléfono válido
    payload_tel_valid = {
        "nombre": "Paciente Tel Valid",
        "email": "pac.telvalid@test.com",
        "password": "TestPass123",
        "dni": "45678901",
        "telefono": "+54 351 1234567"  # Teléfono válido
    }
    try:
        res = requests.post(f"{BASE_URL}/pacientes/con-usuario", json=payload_tel_valid, headers=headers)
        print_result(
            "Teléfono válido con +, espacios",
            res.status_code == 201,
            f"Status: {res.status_code}"
        )
    except Exception as e:
        print_result("Teléfono válido", False, f"Error: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════
# TESTS DE VALIDACIÓN DE MATRÍCULA
# ═══════════════════════════════════════════════════════════════════════════

def test_validacion_matricula(headers):
    print_section("GRUPO 5: VALIDACIÓN DE MATRÍCULA")
    
    # Test 5.1: Matrícula vacía
    payload_mat_empty = {
        "nombre": "Kine Test",
        "email": "kine.matempty@test.com",
        "password": "TestPass123",
        "matricula_profesional": "",  # Vacía
        "especialidad": "Test"
    }
    try:
        res = requests.post(f"{BASE_URL}/kinesiologos/con-usuario", json=payload_mat_empty, headers=headers)
        print_result(
            "Matrícula vacía bloqueada",
            res.status_code in [422, 400],
            f"Status: {res.status_code}"
        )
    except Exception as e:
        print_result("Matrícula vacía", False, f"Error: {str(e)}")
    
    # Test 5.2: Matrícula válida
    payload_mat_valid = {
        "nombre": "Kine Valid",
        "email": "kine.matvalid@test.com",
        "password": "TestPass123",
        "matricula_profesional": "MP-12345",
        "especialidad": "Traumatología"
    }
    try:
        res = requests.post(f"{BASE_URL}/kinesiologos/con-usuario", json=payload_mat_valid, headers=headers)
        print_result(
            "Matrícula válida",
            res.status_code == 201,
            f"Status: {res.status_code}"
        )
        
        # Test 5.3: Intentar crear kine con matrícula duplicada
        if res.status_code == 201:
            payload_mat_dup = {
                "nombre": "Kine Duplicado",
                "email": "kine.matdup@test.com",
                "password": "TestPass123",
                "matricula_profesional": "MP-12345",  # Misma matrícula
                "especialidad": "Otra"
            }
            res_dup = requests.post(f"{BASE_URL}/kinesiologos/con-usuario", json=payload_mat_dup, headers=headers)
            print_result(
                "Matrícula duplicada bloqueada",
                res_dup.status_code == 400,
                f"Status: {res_dup.status_code}"
            )
    except Exception as e:
        print_result("Matrícula válida", False, f"Error: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════
# TESTS DE INTEGRACIÓN
# ═══════════════════════════════════════════════════════════════════════════

def test_integracion(headers):
    print_section("GRUPO 6: TESTS DE INTEGRACIÓN")
    
    # Test 6.1: Crear paciente completo válido
    payload_pac_completo = {
        "nombre": "Juan Pérez",
        "email": "juan.perez.test@test.com",
        "password": "JuanPass123",
        "dni": "98765432",
        "telefono": "351-1234567",
        "obra_social": "OSDE",
        "direccion": "Av. Colón 123",
        "historial_medico": "Sin antecedentes relevantes"
    }
    try:
        res = requests.post(f"{BASE_URL}/pacientes/con-usuario", json=payload_pac_completo, headers=headers)
        paciente_creado = res.status_code == 201
        print_result(
            "Crear paciente completo",
            paciente_creado,
            f"Status: {res.status_code}"
        )
        
        if paciente_creado:
            # Test 6.2: Actualizar paciente
            paciente_id = res.json().get('id')
            if paciente_id:
                update_payload = {
                    "telefono": "351-9876543",
                    "obra_social": "Swiss Medical"
                }
                res_update = requests.put(
                    f"{BASE_URL}/pacientes/{paciente_id}", 
                    json=update_payload, 
                    headers=headers
                )
                print_result(
                    "Actualizar paciente",
                    res_update.status_code == 200,
                    f"Status: {res_update.status_code}"
                )
    except Exception as e:
        print_result("Crear paciente completo", False, f"Error: {str(e)}")
    
    # Test 6.3: Crear kinesiólogo completo válido
    payload_kine_completo = {
        "nombre": "Dr. Carlos Gómez",
        "email": "carlos.gomez.test@test.com",
        "password": "CarlosPass123",
        "matricula_profesional": "MP-99999",
        "especialidad": "Traumatología Deportiva"
    }
    try:
        res = requests.post(f"{BASE_URL}/kinesiologos/con-usuario", json=payload_kine_completo, headers=headers)
        kine_creado = res.status_code == 201
        print_result(
            "Crear kinesiólogo completo",
            kine_creado,
            f"Status: {res.status_code}"
        )
        
        if kine_creado:
            # Test 6.4: Actualizar kinesiólogo
            kine_id = res.json().get('id')
            if kine_id:
                update_payload = {
                    "especialidad": "Rehabilitación Neurológica"
                }
                res_update = requests.put(
                    f"{BASE_URL}/kinesiologos/{kine_id}", 
                    json=update_payload, 
                    headers=headers
                )
                print_result(
                    "Actualizar kinesiólogo",
                    res_update.status_code == 200,
                    f"Status: {res_update.status_code}"
                )
    except Exception as e:
        print_result("Crear kinesiólogo completo", False, f"Error: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def run_tests():
    """Ejecuta todos los tests de validación"""
    print(f"\n{MAGENTA}{'═' * 70}{RESET}")
    print(f"{MAGENTA}║{'AUDITORÍA COMPLETA DE VALIDACIONES - KINESIÓPRO':^68}║{RESET}")
    print(f"{MAGENTA}{'═' * 70}{RESET}\n")
    
    # Obtener token de admin
    print(f"{AMARILLO}🔐 Autenticando como administrador...{RESET}")
    token_admin = get_token(ADMIN_EMAIL, ADMIN_PASSWORD)
    
    if not token_admin:
        print(f"\n{ROJO}{'═' * 70}{RESET}")
        print(f"{ROJO}║ ERROR CRÍTICO: No se pudo autenticar como administrador{RESET}")
        print(f"{ROJO}║ Asegúrate de tener un usuario con:{RESET}")
        print(f"{ROJO}║   - Email: {ADMIN_EMAIL}{RESET}")
        print(f"{ROJO}║   - Password: {ADMIN_PASSWORD}{RESET}")
        print(f"{ROJO}║   - Rol: admin{RESET}")
        print(f"{ROJO}{'═' * 70}{RESET}\n")
        return
    
    print(f"{VERDE}✅ Autenticación exitosa{RESET}\n")
    headers = {"Authorization": f"Bearer {token_admin}"}
    
    # Ejecutar grupos de tests
    try:
        test_validacion_passwords(headers)
        test_validacion_dni(headers)
        test_validacion_email(headers)
        test_validacion_telefono(headers)
        test_validacion_matricula(headers)
        test_integracion(headers)
        
        # Resumen final
        print(f"\n{MAGENTA}{'═' * 70}{RESET}")
        print(f"{MAGENTA}║{'AUDITORÍA COMPLETADA':^68}║{RESET}")
        print(f"{MAGENTA}{'═' * 70}{RESET}\n")
        
        print(f"{VERDE}✅ Auditoría de validaciones finalizada{RESET}")
        print(f"{AMARILLO}📝 Revisa los resultados arriba para ver el estado de cada validación{RESET}\n")
        
    except Exception as e:
        print(f"\n{ROJO}❌ Error durante la ejecución de tests: {str(e)}{RESET}\n")

# ═══════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    run_tests()
