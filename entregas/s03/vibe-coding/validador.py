"""
Practica 2 - Vibe Coding: El Experimento Guiado
Sesion 3 - Backend y MCP en Python
Estudiante: Juan Carlos Lozada (UNIANDES)
"""

import re


# Ronda 1: Validador de contrasenas generado sin spec
def validar_password(password: str) -> tuple[bool, str]:
    """
    Validacion generada a partir del prompt: 'hazme un validador de contrasenas'
    El modelo asumio por su cuenta:
    - Longitud minima de 6 caracteres
    - Al menos un numero
    """
    if not password:
        return False, "La contrasena no puede estar vacia."
    if len(password) < 6:
        return False, "La contrasena debe tener al menos 6 caracteres."
    if not any(c.isdigit() for c in password):
        return False, "La contrasena debe contener al menos un digito numerico."
    return True, "Contrasena valida."


# Ronda 2: Se agrega validacion de email
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def validar_email(email: str) -> tuple[bool, str]:
    """
    Validacion generada para: 'agregale que tambien valide un formato de email'
    """
    if not email:
        return False, "El email no puede estar vacio."
    if not EMAIL_REGEX.match(email):
        return False, f"Formato de correo no valido: '{email}'"
    return True, "Email valido."


# Ronda 3: Gestion de lista de usuarios
class GestorUsuarios:
    """
    Manejo de coleccion de usuarios tras el pedido:
    'ahora que maneje una lista de varios usuarios, cada uno con su contrasena y su email'
    """

    def __init__(self):
        self.usuarios = []

    def agregar_usuario(self, email: str, password: str) -> dict:
        val_email, msg_email = validar_email(email)
        if not val_email:
            return {"resultado": "error", "detalle": msg_email}

        val_pass, msg_pass = validar_password(password)
        if not val_pass:
            return {"resultado": "error", "detalle": msg_pass}

        usuario = {"email": email, "password": password, "rol": "usuario"}
        self.usuarios.append(usuario)
        return {"resultado": "ok", "usuario": usuario}

    def listar(self) -> list:
        return self.usuarios


# Bloque de Cierre: Falla provocada por prompt ambiguo
# Pedido: 'ahora que la validacion de contrasena sea opcional para usuarios administradores'
class GestorConAdminRoto(GestorUsuarios):
    """
    Version donde se aplico el cambio de admin sin contrasena obligatoria.
    Provoca inconsistencia de tipos y vulnerabilidad logica.
    """

    def agregar_usuario(
        self, email: str, password: str | None = None, es_admin: bool = False
    ) -> dict:
        val_email, msg_email = validar_email(email)
        if not val_email:
            return {"resultado": "error", "detalle": msg_email}

        # Cambio sin spec: si es admin, password no se valida y puede venir None o vacio
        if not es_admin:
            val_pass, msg_pass = validar_password(password or "")
            if not val_pass:
                return {"resultado": "error", "detalle": msg_pass}

        usuario = {
            "email": email,
            "password": password,
            "rol": "admin" if es_admin else "usuario",
        }
        self.usuarios.append(usuario)
        return {"resultado": "ok", "usuario": usuario}

    def autenticar(self, email: str, password_intento: str) -> bool:
        """
        Metodo que asume que password siempre es str y usa .strip()
        Rompe en runtime con TypeError si un admin se creo con password=None.
        """
        for u in self.usuarios:
            if u["email"] == email:
                stored = u["password"]
                # Bug provocado: TypeError si stored es None
                if stored is None:
                    raise TypeError(
                        f"Fallo de integridad: El usuario admin '{email}' no tiene contrasena asignada."
                    )
                return stored.strip() == password_intento.strip()
        return False
