# Proyecto Integrador — Sistema de Gestión y Reserva de Espacios

**Curso:** MOD2: Programación de Backend y MCP en Python para IA Generativa (08-26)  
**Estudiante:** Juan Carlos Lozada  
**Institución:** Universidad Regional Autónoma de Los Andes (UNIANDES) / CEDIA  
**Metodología:** Spec-Driven Development (SDD) con GitHub Spec-Kit y Google Antigravity (`agy`)  

---

## 1. Descripción del Proyecto
Sistema backend monolítico modular con soporte para API REST y servidor Model Context Protocol (MCP) para la administración y reserva de espacios compartidos (consultorios médicos, salas de reuniones y canchas deportivas).

El proyecto fue desarrollado y gobernado mediante **Spec-Driven Development (SDD)**, encadenando cuatro artefactos formales de especificación antes de la codificación, garantizando una cobertura global del **94%** y del **100% en la capa de servicios**.

---

## 2. Los 4 Artefactos de Spec-Kit
Los artefactos formales residen en el directorio `specs/002-sistema-reservas/` y `.specify/memory/`:

1. **`constitution.md`**: Marco normativo con 7 artículos no negociables (Arquitectura en capas, Principio de Inversión de Dependencias sin mocks, Persistencia y aislamiento, Seguridad OAuth2+JWT sin IDOR, Convenciones REST, Contratos MCP con confirmación en servidor, Estándar de testing ≥90% services y ≥70% global).
2. **`spec.md`**: Especificación funcional completa con entidades, reglas de negocio (RN-01 a RN-04), clarificación formal de bordes horarios y contratos de endpoints y tools MCP.
3. **`plan.md`**: Stack tecnológico y matriz de trazabilidad: decisión técnica → artículo constitucional.
4. **`tasks.md`**: Tareas atómicas ordenadas por capas con *Definition of Done (DoD)*.
5. **`analysis.md`**: Auditoría preventiva y registro del momento real donde se corrigió al agente por intentar saltarse capas y omitir validación de titularidad.

---

## 3. Arquitectura y Principio de Inversión de Dependencias (DIP)

El código se organiza bajo el directorio `app/`:
* `models/`: Entidades ORM SQLAlchemy (`Usuario`, `Reserva`).
* `schemas/`: Esquemas Pydantic para entrada y salida (`ReservaCreate`, `ReservaResponse`, etc.).
* `repositories/`: Persistencia desacoplada con transacciones SQLAlchemy.
* `services/`: Lógica de dominio pura. Aplica **DIP** recibiendo `repo=reservas_repository` por defecto. No importa SQLAlchemy ni maneja sesiones directamente.
* `routers/`: Endpoints FastAPI protegidos con OAuth2 Bearer JWT. Traduce excepciones de dominio a códigos HTTP semánticos (201, 200, 204, 400, 401, 403, 404, 422).
* `mcp/`: Servidor FastMCP con 4 tools (`crear_reserva`, `listar_reservas`, `consultar_disponibilidad`, `cancelar_reserva`) reutilizando `services/`.
* `utils/`: Hashing `bcrypt` y codificación/decodificación segura de JWT (HS256).

---

## 4. Instalación y Puesta en Marcha

### Prerrequisitos
* Python 3.11 o superior.
* Gestor de paquetes `uv` o `pip` estándar.

### Paso 1: Clonar y configurar entorno
```powershell
# Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar dependencias
pip install -e .
pip install pytest pytest-cov httpx reportlab
```

### Paso 2: Configuración de variables de entorno
```powershell
Copy-Item .env.example .env
```

### Paso 3: Iniciar la API REST
```powershell
uvicorn app.main:app --reload --port 8000
```
La documentación interactiva Swagger estará disponible en:  
👉 **http://127.0.0.1:8000/docs**

---

## 5. Ejecución del Servidor MCP

El servidor implementa FastMCP y puede ejecutarse sobre `stdio`:
```powershell
python -m app.mcp.server
```

Para probarlo interactivamente con **MCP Inspector**:
```powershell
npx @modelcontextprotocol/inspector python -m app.mcp.server
```

---

## 6. Pruebas Automatizadas y Cobertura

Para correr la suite completa de 72 pruebas y generar el reporte de cobertura:
```powershell
pytest -v --cov=app --cov-report=term-missing
```

### Resumen de Cobertura Obtenida:
* **`app/services/reservas.py`**: **100.0%** (Meta: $\ge 90\%$)
* **`app/services/gastos.py`**: **100.0%**
* **`app/services/usuarios.py`**: **100.0%**
* **`app/repositories/reservas.py`**: **97.0%**
* **`app/routers/reservas.py`**: **95.0%**
* **Total Global**: **94.0%** (Meta: $\ge 70\%$)
* **Total de Pruebas**: **72 aprobadas / 0 fallidas (100%)**

---

## 7. Entregables del Proyecto
* **`INFORME_PROYECTO_INTEGRADOR.md`**: Informe técnico completo según la plantilla oficial.
* **`INFORME_PROYECTO_INTEGRADOR.pdf`**: Documento compilado con diseño editorial listo para cargar en el AVAC / Moodle.
* **`proyecto-integrador.zip`**: Archivo comprimido con la solución completa.
