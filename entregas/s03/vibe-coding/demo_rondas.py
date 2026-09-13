"""
Script de pruebas para registrar las salidas de la Practica 2.
Ejecuta los casos planteados en la guia para cada ronda.
"""

from validador import (
    GestorConAdminRoto,
    GestorUsuarios,
    validar_email,
    validar_password,
)


def ejecutar_ronda_1():
    print("=== RONDA 1: Validador de contrasenas ===")
    casos = ["12345", "password", ""]
    for caso in casos:
        valido, msg = validar_password(caso)
        print(f"Entrada: '{caso}' -> Valido: {valido} | Mensaje: {msg}")
    print()


def ejecutar_ronda_2():
    print("=== RONDA 2: Validacion de email ===")
    casos = ["ana@correo.com", "ana@", ""]
    for caso in casos:
        valido, msg = validar_email(caso)
        print(f"Entrada: '{caso}' -> Valido: {valido} | Mensaje: {msg}")
    print()


def ejecutar_ronda_3():
    print("=== RONDA 3: Lista de varios usuarios ===")
    gestor = GestorUsuarios()
    r1 = gestor.agregar_usuario("carlos@uniandes.edu.ec", "Clave123")
    r2 = gestor.agregar_usuario("maria@uniandes.edu.ec", "Pass456")
    print(f"Registro 1: {r1}")
    print(f"Registro 2: {r2}")
    print(f"Lista completa ({len(gestor.listar())} usuarios): {gestor.listar()}")
    print()


def ejecutar_bloque_cierre():
    print("=== BLOQUE DE CIERRE: Falla provocada ===")
    gestor_roto = GestorConAdminRoto()
    # Se agrega admin sin contrasena (permitido por el prompt ambiguo)
    res_admin = gestor_roto.agregar_usuario("admin@uniandes.edu.ec", None, es_admin=True)
    print(f"Admin registrado sin clave: {res_admin}")

    # Intento de autenticacion posterior: revienta en runtime
    try:
        print("Intentando autenticar al administrador con contrasena 'admin123'...")
        gestor_roto.autenticar("admin@uniandes.edu.ec", "admin123")
    except TypeError as err:
        print(f"ERROR CAPTURADO (Inconsistencia en runtime): {err}")
    print()


if __name__ == "__main__":
    ejecutar_ronda_1()
    ejecutar_ronda_2()
    ejecutar_ronda_3()
    ejecutar_bloque_cierre()
