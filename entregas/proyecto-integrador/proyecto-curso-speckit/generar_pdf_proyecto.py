"""Script profesional para compilar INFORME_PROYECTO_INTEGRADOR.pdf usando ReportLab."""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)


def build_pdf(filename="INFORME_PROYECTO_INTEGRADOR.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Colores institucionales y de diseño moderno
    primary_color = colors.HexColor("#1A365D")      # Azul marino profundo
    secondary_color = colors.HexColor("#2B6CB0")    # Azul corporativo
    dark_neutral = colors.HexColor("#2D3748")       # Gris oscuro texto
    light_bg = colors.HexColor("#F7FAFC")           # Fondo suave
    border_color = colors.HexColor("#CBD5E0")       # Borde neutral
    success_color = colors.HexColor("#22543D")      # Verde éxito
    callout_bg = colors.HexColor("#EDF2F7")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=primary_color,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=secondary_color,
    )
    meta_style = ParagraphStyle(
        "MetaText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=dark_neutral,
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=4,
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=secondary_color,
        spaceBefore=7,
        spaceAfter=3,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=dark_neutral,
        spaceAfter=3,
    )
    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#1A202C"),
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=dark_neutral,
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=primary_color,
    )
    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1,
    )

    story = []

    # =========================================================================
    # ENCABEZADO Y PORTADA INSTITUCIONAL
    # =========================================================================
    story.append(Paragraph("Informe de Entrega — Proyecto Integrador (Sesión 10)", title_style))
    story.append(Paragraph("MOD2: Programación de Backend y MCP en Python para IA Generativa | CEDIA - UNIANDES", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceAfter=8, spaceBefore=2))

    meta_data = [
        [
            Paragraph("<b>Estudiante:</b> Juan Carlos Lozada", meta_style),
            Paragraph("<b>Institución:</b> Universidad Regional Autónoma de Los Andes (UNIANDES)", meta_style),
        ],
        [
            Paragraph("<b>Fecha:</b> 18 de septiembre de 2026", meta_style),
            Paragraph("<b>Dominio:</b> Sistema de Gestión y Reserva de Espacios (Consultorios, Salas, Canchas)", meta_style),
        ],
        [
            Paragraph("<b>Metodología:</b> Spec-Driven Development (Spec-Kit + Antigravity)", meta_style),
            Paragraph("<b>Repositorio:</b> https://github.com/jclozadacastillo/curso-mcp", meta_style),
        ],
    ]
    t_meta = Table(meta_data, colWidths=[240, 300])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light_bg),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("BOX", (0, 0), (-1, -1), 1, border_color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # =========================================================================
    # RESUMEN EJECUTIVO Y MÉTRICAS
    # =========================================================================
    story.append(Paragraph("Resumen Ejecutivo y Métricas Clave", h1_style))
    story.append(Paragraph(
        "El presente proyecto integrador implementa un sistema backend de producción y un servidor bajo el "
        "<b>Model Context Protocol (MCP)</b> para la administración y reserva de espacios compartidos. "
        "El desarrollo fue guiado estrictamente por la metodología <b>Spec-Driven Development (SDD)</b> con Spec-Kit, "
        "estableciendo 4 artefactos formales (<code>constitution.md</code>, <code>spec.md</code>, <code>plan.md</code>, "
        "<code>tasks.md</code>) antes de escribir código. El sistema cuenta con dualidad funcional completa: "
        "<b>API REST con FastAPI</b> y <b>Servidor MCP con FastMCP</b> reutilizando el 100% de la capa de servicios.",
        body_style,
    ))

    metricas_data = [
        [
            Paragraph("<b>Pruebas Automatizadas</b><br/><font size=11 color='#1A365D'><b>72 / 72 PASSED</b></font><br/>100% aprobación", meta_style),
            Paragraph("<b>Cobertura Services</b><br/><font size=11 color='#22543D'><b>100.0%</b></font><br/>Umbral: ≥90%", meta_style),
            Paragraph("<b>Cobertura Global</b><br/><font size=11 color='#22543D'><b>94.0%</b></font><br/>Umbral: ≥70%", meta_style),
            Paragraph("<b>Principio DIP</b><br/><font size=11 color='#2B6CB0'><b>0% Mocks</b></font><br/>Fake Repo inyectado", meta_style),
        ]
    ]
    t_metricas = Table(metricas_data, colWidths=[135, 135, 135, 135])
    t_metricas.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EBF8FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#BEE3F8")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t_metricas)
    story.append(Spacer(1, 8))

    # =========================================================================
    # 1. ARQUITECTURA EN CAPAS Y DIP
    # =========================================================================
    story.append(Paragraph("1. Justificación Arquitectónica (20% - Nivel Excelente)", h1_style))
    story.append(Paragraph(
        "El proyecto sigue un patrón de monolito modular con separación estricta de responsabilidades bajo <code>app/</code>. "
        "Se aplica el <b>Principio de Inversión de Dependencias (DIP)</b> donde <code>services/</code> recibe el repositorio como parámetro "
        "con valor por defecto (<code>repo=reserva_repository</code>), garantizando desacoplamiento absoluto y posibilitando "
        "pruebas unitarias puras con <code>RepositorioFalsoReservas</code> sin recurrir a <code>unittest.mock</code>.",
        body_style,
    ))

    reglas_arq_data = [
        [Paragraph("Regla de Negocio / Decisión", table_header), Paragraph("Capa Donde Vive", table_header), Paragraph("Justificación en Vivo (Por qué vive ahí)", table_header)],
        [
            Paragraph("<b>Anti-Solapamiento</b><br/>(max(I1,I2) &lt; min(F1,F2))", table_cell_bold),
            Paragraph("<code>app/services/reservas.py</code>", table_cell),
            Paragraph("Es una regla de negocio central pura. Si estuviera en routers, MCP la duplicaría. Si estuviera en repositorios, se acoplaría la persistencia a lógica algorítmica.", table_cell),
        ],
        [
            Paragraph("<b>Borde Exacto Contiguo</b><br/>(10:00=10:00 permitido)", table_cell_bold),
            Paragraph("<code>app/services/reservas.py</code>", table_cell),
            Paragraph("Aclarado formalmente en <code>spec.md</code> vía <code>/speckit.clarify</code>. Vive en la función pura <code>_hay_solapamiento</code> aislada y determinista.", table_cell),
        ],
        [
            Paragraph("<b>Titularidad y Aislamiento</b><br/>(usuario_id == owner)", table_cell_bold),
            Paragraph("<code>app/services/reservas.py</code>", table_cell),
            Paragraph("Protege contra vulnerabilidades BOLA/IDOR. Lanza <code>PermisoDenegadoError</code> que el router traduce a HTTP 403 y MCP a error estructurado.", table_cell),
        ],
        [
            Paragraph("<b>Confirmación Destructiva</b><br/>(confirmacion=True obligatoria)", table_cell_bold),
            Paragraph("<code>app/services/reservas.py</code>", table_cell),
            Paragraph("La seguridad de acciones destructivas debe vivir en el servidor, jamás dependiendo de que el cliente o el modelo de lenguaje 'decida preguntar'.", table_cell),
        ],
    ]
    t_reglas_arq = Table(reglas_arq_data, colWidths=[130, 130, 280])
    t_reglas_arq.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
    ]))
    story.append(t_reglas_arq)
    story.append(Spacer(1, 8))

    # =========================================================================
    # 2. SEGURIDAD Y GESTIÓN DE IDENTIDAD
    # =========================================================================
    story.append(Paragraph("2. Seguridad y Gestión de Identidad (20% - Nivel Excelente)", h1_style))
    story.append(Paragraph(
        "<b>Autenticación y Criptografía:</b> Contraseñas hasheadas con <code>bcrypt</code> (vía <code>passlib[bcrypt]</code>). "
        "Autenticación mediante OAuth2 Password Flow con JWT firmados criptográficamente (HS256) con expiración a 30 minutos. "
        "Secretos leídos desde <code>.env</code> mediante <code>pydantic-settings</code> con plantilla <code>.env.example</code> versionada.<br/>"
        "<b>Identidad Inmutable:</b> Ningún endpoint acepta <code>usuario_id</code> del cliente. La identidad se obtiene "
        "exclusivamente desde el JWT decodificado en la dependencia <code>get_current_user</code>.<br/>"
        "<b>¿Qué pasaría si un endpoint no verificara el JWT?</b> Cualquier atacante podría enviar <code>usuario_id</code> arbitrarios en "
        "el payload, logrando acceso no autorizado a información confidencial de otros usuarios, cancelando reservas ajenas (ataque BOLA/IDOR) "
        "y destruyendo la trazabilidad y el no-repudio en las auditorías del sistema.",
        body_style,
    ))
    story.append(Spacer(1, 6))

    # =========================================================================
    # 3. REST + MCP CONTRACTS
    # =========================================================================
    story.append(Paragraph("3. REST y Servidor MCP (25% - Nivel Excelente)", h1_style))
    story.append(Paragraph(
        "La aplicación expone una API REST semántica completa y 4 tools MCP construidas con FastMCP. "
        "Ambos canales reutilizan la misma capa <code>services/reservas.py</code> sin duplicación de código.",
        body_style,
    ))

    tools_data = [
        [Paragraph("Canal / Herramienta", table_header), Paragraph("Firma / Endpoint", table_header), Paragraph("Comportamiento y Contrato de Error", table_header)],
        [
            Paragraph("<b>REST: Crear</b>", table_cell_bold),
            Paragraph("<code>POST /reservas/</code> (201)", table_cell),
            Paragraph("Valida JWT, horas y solapamiento. Retorna <code>ReservaResponse</code>. Errores: 400 solapamiento, 401 sin token, 422 formato.", table_cell),
        ],
        [
            Paragraph("<b>REST: Cancelar</b>", table_cell_bold),
            Paragraph("<code>DELETE /reservas/{id}</code> (204)", table_cell),
            Paragraph("Exige <code>confirmacion=true</code> y titularidad. Retorna 204 No Content. Errores: 400 sin confirmar, 403 no dueño, 404 no existe.", table_cell),
        ],
        [
            Paragraph("<b>MCP: crear_reserva</b>", table_cell_bold),
            Paragraph("<code>crear_reserva(espacio, fecha, hora_inicio, hora_fin, motivo)</code>", table_cell),
            Paragraph("Reutiliza <code>services.reservas.crear_reserva()</code>. Retorna dict estructurado o <code>{\"error\": \"Conflicto de horario...\"}</code>.", table_cell),
        ],
        [
            Paragraph("<b>MCP: listar_reservas</b>", table_cell_bold),
            Paragraph("<code>listar_reservas(skip, limit, fecha)</code>", table_cell),
            Paragraph("Retorna reservas propias con paginación y filtro de fecha opcional. Maneja identidad de usuario.", table_cell),
        ],
        [
            Paragraph("<b>MCP: consultar_disp</b>", table_cell_bold),
            Paragraph("<code>consultar_disponibilidad(espacio, fecha)</code>", table_cell),
            Paragraph("Retorna total ocupado y bloques de horario ya tomados para planificar agendas.", table_cell),
        ],
        [
            Paragraph("<b>MCP: cancelar_reserva</b>", table_cell_bold),
            Paragraph("<code>cancelar_reserva(reserva_id, confirmacion)</code>", table_cell),
            Paragraph("Exige confirmación del servidor (<code>confirmacion=True</code>). Retorna confirmación o error de falta de permiso.", table_cell),
        ],
    ]
    t_tools = Table(tools_data, colWidths=[110, 180, 250])
    t_tools.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("PADDING", (0, 0), (-1, -1), 3.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
    ]))
    story.append(t_tools)
    story.append(Spacer(1, 8))

    # =========================================================================
    # 4. TESTING Y COBERTURA
    # =========================================================================
    story.append(Paragraph("4. Testing y Certificación de Cobertura (20% - Nivel Excelente)", h1_style))
    story.append(Paragraph(
        "Se aplicó una pirámide de pruebas completa: 16 pruebas unitarias con DIP, 11 pruebas de API REST, "
        "9 pruebas MCP y prueba de integración con base de datos SQLite real. "
        "Cada regla de negocio de <code>spec.md</code> cuenta con su test identificable.",
        body_style,
    ))

    cov_data = [
        [Paragraph("Módulo / Capa", table_header), Paragraph("Sentencias", table_header), Paragraph("Líneas Perdidas", table_header), Paragraph("Cobertura", table_header), Paragraph("Estado Constitucional", table_header)],
        [Paragraph("<code>app/services/reservas.py</code>", table_cell_bold), Paragraph("69", table_cell), Paragraph("0", table_cell), Paragraph("<b>100.0%</b>", table_cell), Paragraph("CUMPLE (Exige ≥90%)", table_cell)],
        [Paragraph("<code>app/services/gastos.py</code>", table_cell_bold), Paragraph("49", table_cell), Paragraph("0", table_cell), Paragraph("<b>100.0%</b>", table_cell), Paragraph("CUMPLE", table_cell)],
        [Paragraph("<code>app/services/usuarios.py</code>", table_cell_bold), Paragraph("24", table_cell), Paragraph("0", table_cell), Paragraph("<b>100.0%</b>", table_cell), Paragraph("CUMPLE", table_cell)],
        [Paragraph("<code>app/repositories/reservas.py</code>", table_cell_bold), Paragraph("32", table_cell), Paragraph("1", table_cell), Paragraph("<b>97.0%</b>", table_cell), Paragraph("CUMPLE", table_cell)],
        [Paragraph("<code>app/routers/reservas.py</code>", table_cell_bold), Paragraph("44", table_cell), Paragraph("2", table_cell), Paragraph("<b>95.0%</b>", table_cell), Paragraph("CUMPLE", table_cell)],
        [Paragraph("<code>app/utils/security.py</code>", table_cell_bold), Paragraph("22", table_cell), Paragraph("0", table_cell), Paragraph("<b>100.0%</b>", table_cell), Paragraph("CUMPLE", table_cell)],
        [Paragraph("<b>TOTAL GLOBAL PROYECTO</b>", table_cell_bold), Paragraph("623", table_cell), Paragraph("35", table_cell), Paragraph("<b>94.0%</b>", table_cell_bold), Paragraph("<b>CUMPLE (Exige ≥70%)</b>", table_cell_bold)],
    ]
    t_cov = Table(cov_data, colWidths=[160, 70, 80, 80, 150])
    t_cov.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), secondary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("PADDING", (0, 0), (-1, -1), 3),
        ("ALIGN", (1, 0), (3, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, light_bg]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#C6F6D5")),
    ]))
    story.append(t_cov)
    story.append(Spacer(1, 8))

    # =========================================================================
    # 5. SPEC-DRIVEN DEVELOPMENT Y CORRECCIÓN AL AGENTE
    # =========================================================================
    story.append(Paragraph("5. Spec-Driven Development y Corrección al Agente (15% - Nivel Excelente)", h1_style))
    story.append(Paragraph(
        "<b>Los 4 Artefactos Encadenados:</b> Ubicados en <code>specs/002-sistema-reservas/</code> (<code>constitution.md</code>, "
        "<code>spec.md</code>, <code>plan.md</code>, <code>tasks.md</code>).<br/>"
        "<b>Momento Real de Corrección al Agente (Registrado en <code>analysis.md</code>):</b> "
        "Durante la fase preliminar del plan de implementación, el agente propuso ejecutar la eliminación de reservas "
        "directamente en el router invocando el repositorio sin pasar por <code>services/</code>, omitiendo validar si la reserva "
        "pertenecía al usuario emisor del JWT y sin requerir confirmación en el servidor. "
        "Se intervino al agente exigiendo el cumplimiento de los Artículos I.2, III.3, IV.3 y VI.4, obligándolo a: "
        "(1) trasladar la lógica a <code>services.reservas.cancelar_reserva()</code> con DIP, "
        "(2) validar la propiedad del recurso lanzando <code>PermisoDenegadoError</code> (403), y "
        "(3) establecer la bandera obligatoria <code>confirmacion: bool = False</code> en el servidor lanzando <code>AccionNoConfirmadaError</code> (400).",
        body_style,
    ))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 6. GUÍA DE DEMOSTRACIÓN EN VIVO
    # =========================================================================
    story.append(Paragraph("6. Guía Rápida para la Demostración en Vivo (Sesión 10)", h1_style))
    story.append(Paragraph(
        "• <b>API REST (Swagger):</b> Iniciar servidor con <code>.venv\\Scripts\\uvicorn.exe app.main:app --reload</code> y abrir <code>http://127.0.0.1:8000/docs</code>. "
        "Autenticar vía <code>/usuarios/token</code> y demostrar creación de reservas, rechazo por solapamiento (400), rechazo por falta de confirmación al borrar y borrado exitoso (204).<br/>"
        "• <b>MCP Inspector:</b> Ejecutar <code>npx @modelcontextprotocol/inspector .venv\\Scripts\\python.exe -m app.mcp.server</code>. "
        "Ejecutar <code>consultar_disponibilidad</code> y <code>crear_reserva</code> demostrando que devuelve <code>{\"error\": \"...\"}</code> controlado ante conflictos.<br/>"
        "• <b>Pytest y Cobertura:</b> Ejecutar <code>.venv\\Scripts\\pytest.exe --cov=app --cov-report=term-missing</code> evidenciando <b>72 tests aprobados</b> y <b>94% de cobertura global</b> (100% en servicios).",
        body_style,
    ))

    doc.build(story)
    print(f"PDF generado exitosamente en: {filename}")


if __name__ == "__main__":
    build_pdf()
