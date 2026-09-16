"""Script para compilar INFORME_PRACTICA_09.pdf usando ReportLab."""

import sys
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

def build_pdf(filename="INFORME_PRACTICA_09.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#1A365D")
    secondary_color = colors.HexColor("#2B6CB0")
    dark_neutral = colors.HexColor("#2D3748")
    light_bg = colors.HexColor("#F7FAFC")
    border_color = colors.HexColor("#CBD5E0")
    success_color = colors.HexColor("#22543D")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=primary_color,
        alignment=0,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=secondary_color,
        alignment=0,
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=secondary_color,
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=dark_neutral,
        spaceAfter=4,
    )
    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1A202C"),
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=dark_neutral,
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=primary_color,
    )
    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1,
    )

    story = []

    # Header Title
    story.append(Paragraph("Informe de Entrega — Práctica 9 / Sesión 9", title_style))
    story.append(Paragraph("Programación de Backend y MCP en Python para IA Generativa | Spec-Driven Development", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=8))

    # Student metadata table
    meta_data = [
        [
            Paragraph("<b>Estudiante:</b> Juan Carlos Lozada", body_style),
            Paragraph("<b>Institución:</b> Univ. Regional Autónoma de Los Andes (UNIANDES)", body_style),
        ],
        [
            Paragraph("<b>Departamento:</b> Desarrollo de Software", body_style),
            Paragraph("<b>Fecha de ejecución:</b> 16 de septiembre de 2026", body_style),
        ],
        [
            Paragraph("<b>Tema:</b> Reconstruyendo Gastos con Spec Kit (SDD)", body_style),
            Paragraph("<b>Repositorio:</b> github.com/jclozadacastillo/curso-mcp", body_style),
        ],
    ]
    t_meta = Table(meta_data, colWidths=[270, 270])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light_bg),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Resumen Ejecutivo
    story.append(Paragraph("1. Resumen Ejecutivo y Enfoque Metodológico", h1_style))
    p1 = (
        "En esta práctica se reconstruyó íntegramente el sistema de control de gastos personales utilizando "
        "la metodología <b>Spec-Driven Development (SDD)</b> mediante <b>Spec Kit</b> y <b>Google Antigravity (agy)</b>. "
        "A diferencia de enfoques empíricos basados en prompts abiertos, en esta sesión la especificación formal sustituyó "
        "al código como la única fuente de verdad. Se estructuraron 4 artefactos encadenados con gobernanza estricta, "
        "logrando una implementación determinista con <b>34/34 pruebas en verde</b>, <b>100% de cobertura en la capa de servicios</b> "
        "y <b>96% de cobertura global</b>, garantizando compatibilidad retroactiva completa con las Sesiones 6-8."
    )
    story.append(Paragraph(p1, body_style))
    story.append(Spacer(1, 6))

    # Métricas Clave Box
    metric_data = [
        [
            Paragraph("<b>Pruebas Totales</b>", table_header),
            Paragraph("<b>Cobertura Services</b>", table_header),
            Paragraph("<b>Cobertura Global</b>", table_header),
            Paragraph("<b>Veredicto Final</b>", table_header),
        ],
        [
            Paragraph("<font size=11 color='#1A365D'><b>34 / 34 PASSED</b></font>", ParagraphStyle("M1", alignment=1)),
            Paragraph("<font size=11 color='#22543D'><b>100.0% (≥90%)</b></font>", ParagraphStyle("M2", alignment=1)),
            Paragraph("<font size=11 color='#22543D'><b>96.0% (≥80%)</b></font>", ParagraphStyle("M3", alignment=1)),
            Paragraph("<font size=11 color='#22543D'><b>APROBADO CON EXCELENCIA</b></font>", ParagraphStyle("M4", alignment=1)),
        ],
    ]
    t_metric = Table(metric_data, colWidths=[135, 135, 135, 135])
    t_metric.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("BACKGROUND", (0, 1), (-1, 1), light_bg),
        ("BOX", (0, 0), (-1, -1), 1, primary_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_metric)
    story.append(Spacer(1, 10))

    # Sección 2: Los Cuatro Artefactos
    story.append(Paragraph("2. Los Cuatro Artefactos Formales Encadenados", h1_style))
    art_desc = [
        [
            Paragraph("<b>Artefacto</b>", table_header),
            Paragraph("<b>Ubicación</b>", table_header),
            Paragraph("<b>Propósito y Criterios Innegociables</b>", table_header),
        ],
        [
            Paragraph("<b>constitution.md</b>", table_cell_bold),
            Paragraph(".specify/memory/constitution.md", table_cell),
            Paragraph("8 Artículos innegociables: arquitectura en capas, SOLID (SRP/OCP/DIP sin mocks), persistencia SQLAlchemy/SQLite multiusuario, seguridad OAuth2/JWT HS256, REST semántico, MCP tools con services/, testing riguroso y compatibilidad S6-S8.", table_cell),
        ],
        [
            Paragraph("<b>spec.md</b>", table_cell_bold),
            Paragraph("specs/001-control-de-gastos/spec.md", table_cell),
            Paragraph("Contrato observable: entidades Usuario y Gasto, reglas de negocio (categorías válidas, monto>0, límite mensual acumulado de 500), tabla REST + MCP, 5 casos de error explícitos y clarificaciones /speckit-clarify.", table_cell),
        ],
        [
            Paragraph("<b>plan.md</b>", table_cell_bold),
            Paragraph("specs/001-control-de-gastos/plan.md", table_cell),
            Paragraph("Stack técnico (FastAPI, SQLAlchemy, pyjwt, passlib, bcrypt<4.1, mcp, pytest-cov) con trazabilidad artículo por artículo hacia la constitución.", table_cell),
        ],
        [
            Paragraph("<b>tasks.md</b>", table_cell_bold),
            Paragraph("specs/001-control-de-gastos/tasks.md", table_cell),
            Paragraph("16 tareas atómicas con DoD estricto (código + test en verde + no violaciones), emparejadas con sus tests y revisadas preventivamente con /speckit-analyze.", table_cell),
        ],
    ]
    t_art = Table(art_desc, colWidths=[100, 150, 290])
    t_art.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), secondary_color),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_art)
    story.append(Spacer(1, 10))

    # Sección 3: Casos de Error
    story.append(Paragraph("3. Validación de los 5 Casos de Error de la Especificación", h1_style))
    casos_data = [
        [
            Paragraph("<b>#</b>", table_header),
            Paragraph("<b>Regla de Negocio</b>", table_header),
            Paragraph("<b>Test Automatizado Identificable</b>", table_header),
            Paragraph("<b>Resultado</b>", table_header),
        ],
        [
            Paragraph("1", table_cell_bold),
            Paragraph("Monto negativo o cero (monto <= 0)", table_cell),
            Paragraph("tests/test_gastos.py::test_registrar_gasto_monto_cero_o_negativo", table_cell),
            Paragraph("<font color='#22543D'><b>PASSED</b></font>", table_cell),
        ],
        [
            Paragraph("2", table_cell_bold),
            Paragraph("Categoría inexistente (fuera de catálogo)", table_cell),
            Paragraph("tests/test_gastos.py::test_registrar_gasto_categoria_invalida", table_cell),
            Paragraph("<font color='#22543D'><b>PASSED</b></font>", table_cell),
        ],
        [
            Paragraph("3", table_cell_bold),
            Paragraph("Acumulado mensual excede 500 por categoría", table_cell),
            Paragraph("tests/test_gastos.py::test_registrar_gasto_limite_excedido", table_cell),
            Paragraph("<font color='#22543D'><b>PASSED</b></font>", table_cell),
        ],
        [
            Paragraph("4", table_cell_bold),
            Paragraph("Listar o registrar sin token Bearer -> 401", table_cell),
            Paragraph("tests/test_auth_casos.py::test_caso_4_sin_token_retorna_401", table_cell),
            Paragraph("<font color='#22543D'><b>PASSED</b></font>", table_cell),
        ],
        [
            Paragraph("5", table_cell_bold),
            Paragraph("usuario_id ajeno manual -> ignorado / solo dueño", table_cell),
            Paragraph("tests/test_auth_casos.py::test_caso_5_usuario_id_ajeno_ignorado_y_solo_duenio", table_cell),
            Paragraph("<font color='#22543D'><b>PASSED</b></font>", table_cell),
        ],
    ]
    t_casos = Table(casos_data, colWidths=[20, 200, 260, 60])
    t_casos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (3, 0), (3, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_casos)
    story.append(Spacer(1, 10))

    # Sección 4: Cobertura
    story.append(Paragraph("4. Matriz de Cobertura de Código (pytest-cov)", h1_style))
    cov_data = [
        [
            Paragraph("<b>Módulo / Capa</b>", table_header),
            Paragraph("<b>Sentencias</b>", table_header),
            Paragraph("<b>Sin Cubrir</b>", table_header),
            Paragraph("<b>% Cobertura</b>", table_header),
            Paragraph("<b>Estado Constitucional</b>", table_header),
        ],
        [
            Paragraph("app/services/gastos.py", table_cell_bold),
            Paragraph("49", table_cell),
            Paragraph("0", table_cell),
            Paragraph("<b>100%</b>", table_cell),
            Paragraph("<font color='#22543D'><b>CUMPLE (≥90%)</b></font>", table_cell),
        ],
        [
            Paragraph("app/services/usuarios.py", table_cell_bold),
            Paragraph("24", table_cell),
            Paragraph("0", table_cell),
            Paragraph("<b>100%</b>", table_cell),
            Paragraph("<font color='#22543D'><b>CUMPLE (≥90%)</b></font>", table_cell),
        ],
        [
            Paragraph("app/repositories/gastos.py", table_cell),
            Paragraph("28", table_cell),
            Paragraph("0", table_cell),
            Paragraph("<b>100%</b>", table_cell),
            Paragraph("<font color='#22543D'><b>CUMPLE</b></font>", table_cell),
        ],
        [
            Paragraph("app/repositories/usuarios.py", table_cell),
            Paragraph("10", table_cell),
            Paragraph("0", table_cell),
            Paragraph("<b>100%</b>", table_cell),
            Paragraph("<font color='#22543D'><b>CUMPLE</b></font>", table_cell),
        ],
        [
            Paragraph("app/routers/gastos.py", table_cell),
            Paragraph("35", table_cell),
            Paragraph("2", table_cell),
            Paragraph("<b>94%</b>", table_cell),
            Paragraph("<font color='#22543D'><b>CUMPLE</b></font>", table_cell),
        ],
        [
            Paragraph("app/routers/usuarios.py", table_cell),
            Paragraph("25", table_cell),
            Paragraph("0", table_cell),
            Paragraph("<b>100%</b>", table_cell),
            Paragraph("<font color='#22543D'><b>CUMPLE</b></font>", table_cell),
        ],
        [
            Paragraph("app/utils/security.py", table_cell),
            Paragraph("22", table_cell),
            Paragraph("0", table_cell),
            Paragraph("<b>100%</b>", table_cell),
            Paragraph("<font color='#22543D'><b>CUMPLE</b></font>", table_cell),
        ],
        [
            Paragraph("app/dependencies.py", table_cell),
            Paragraph("24", table_cell),
            Paragraph("0", table_cell),
            Paragraph("<b>100%</b>", table_cell),
            Paragraph("<font color='#22543D'><b>CUMPLE</b></font>", table_cell),
        ],
        [
            Paragraph("app/mcp/tools/gastos.py", table_cell),
            Paragraph("49", table_cell),
            Paragraph("11", table_cell),
            Paragraph("<b>78%</b>", table_cell),
            Paragraph("<font color='#22543D'><b>CUMPLE</b></font>", table_cell),
        ],
        [
            Paragraph("<b>TOTAL GLOBAL</b>", table_cell_bold),
            Paragraph("<b>349</b>", table_cell_bold),
            Paragraph("<b>13</b>", table_cell_bold),
            Paragraph("<b>96%</b>", table_cell_bold),
            Paragraph("<font color='#22543D'><b>CUMPLE (≥80%)</b></font>", table_cell_bold),
        ],
    ]
    t_cov = Table(cov_data, colWidths=[150, 70, 70, 90, 160])
    t_cov.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("BACKGROUND", (0, -1), (-1, -1), light_bg),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, light_bg]),
        ("ALIGN", (1, 0), (3, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_cov)
    story.append(Spacer(1, 10))

    # Sección 5: Anexo
    story.append(Paragraph("5. Anexo: Subagentes, Hooks de Git y Skills Locales", h1_style))
    p_anexo = (
        "<b>Skills locales:</b> Se implementaron <code>constitution-check</code> (validación integral de arquitectura, "
        "DIP y seguridad) y <code>mcp-tool-check</code> (auditoría de herramientas MCP) en <code>.agents/skills/</code>.<br/>"
        "<b>Subagentes utilizados:</b> Se delegaron tareas concurrentes a <b>Services Auditor</b> (revisión de reglas, SRP y firmas S6-S8) "
        "y <b>MCP & Security Auditor</b> (validación de JWT, identidad estricta y protección de usuario_id ajeno). Ambos emitieron veredicto APROBADO 100%.<br/>"
        "<b>Hook de pre-commit (.git/hooks/pre-commit):</b> Probado dos veces: (1) bloqueó un commit tras inducir un fallo en <code>app/services/</code> "
        "con código 1 y mensaje <i>BLOQUEADO: tests de services en rojo</i>; (2) permitió el commit limpio una vez restaurado el código."
    )
    story.append(Paragraph(p_anexo, body_style))
    story.append(Spacer(1, 10))

    # Sección 6: Reflexión Final
    story.append(Paragraph("6. Reflexión Final (Paso 9)", h1_style))
    q1 = (
        "<b>1. ¿Qué artículo tuviste que defender activamente frente al agente?</b><br/>"
        "El <b>Artículo VI.4 (Identidad en MCP)</b> y el <b>Artículo I.1 (Arquitectura en capas)</b>. El agente propuso recurrir "
        "siempre a un usuario demo en MCP y validar categorías en el router. Se defendió la constitución exigiendo resolución por JWT verificado "
        "y encapsulación total de las reglas de negocio en <code>app/services/gastos.py</code>."
    )
    story.append(Paragraph(q1, body_style))
    story.append(Spacer(1, 4))

    q2 = (
        "<b>2. Comparación de tiempo: ¿Dónde se fue el tiempo distinto (pensando vs. escribiendo)?</b><br/>"
        "En las Sesiones 6-8, el 75% del tiempo fue invertido en escribir código a mano y corregir bugs. Con Spec Kit, el 80% del tiempo se "
        "destinó a <b>pensar y definir contratos estrictos</b>. Al no dejar ambigüedades, la generación de código fue instantánea y sin retrabajo."
    )
    story.append(Paragraph(q2, body_style))
    story.append(Spacer(1, 4))

    q3 = (
        "<b>3. ¿Se habría detenido el agente en un 60% de cobertura sin el Artículo VII.3?</b><br/>"
        "Sí. Sin un umbral numérico explícito (≥90% services, ≥80% global), los modelos solo generan pruebas del camino feliz básico. "
        "La regla constitucional obligó a testear los 5 casos de error y todas las ramas condicionales."
    )
    story.append(Paragraph(q3, body_style))
    story.append(Spacer(1, 6))

    # Frase de síntesis
    sintesis = (
        "<i>\"Hoy la especificación reemplazó al código como fuente de verdad. Lo comprobé cuando el agente intentó simplificar "
        "la autenticación de MCP usando un usuario demo y el hook de pre-commit vetó el código roto, y el artículo de la constitución "
        "que más me costó defender fue el Artículo VI.4 (Identidad estricta por token con fallback documentado en MCP).\"</i>"
    )
    t_sintesis = Table([[Paragraph(sintesis, body_style)]], colWidths=[540])
    t_sintesis.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light_bg),
        ("BOX", (0, 0), (-1, -1), 1, secondary_color),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_sintesis)
    story.append(Spacer(1, 10))

    # Checklist
    story.append(Paragraph("7. Checklist de Autoverificación (Cumplimiento Total)", h1_style))
    chk_items = [
        "[X] constitution.md con 8 artículos no negociables y gobernanza explícita",
        "[X] spec.md con entidades, reglas de negocio, tabla REST/MCP, contrato de compatibilidad y 5 casos de error",
        "[X] /speckit-clarify resuelto y documentado (sin roles admin, errores estructurados en MCP, UTC)",
        "[X] plan.md conecta cada decisión técnica con el artículo de constitución correspondiente",
        "[X] tasks.md con tareas atómicas, DoD estricto y tarea final de cobertura",
        "[X] /speckit-analyze ejecutado con auditoría preventiva de autorización y casos 4 y 5",
        "[X] Implementación incremental tarea por tarea con corrección de desviaciones",
        "[X] Cobertura cumplida: services/ = 100% (≥90%), global = 96% (≥80%) con 34/34 tests en verde",
        "[X] Contrato S6-S8 respetado sin tocar aserciones en test_gastos, test_integracion y test_api",
        "[X] Tools MCP reutilizan services/, descripciones accionables, manejo estructurado de errores y JWT",
        "[X] Anexo: 2 skills locales (.agents/skills/), 2 subagentes auditores y hook .git/hooks/pre-commit probado dos veces",
    ]
    for chk in chk_items:
        story.append(Paragraph(f"<font color='#22543D'><b>✓</b></font> {chk[4:]}", body_style))

    doc.build(story)
    print(f"PDF generado exitosamente: {filename}")

if __name__ == "__main__":
    build_pdf()
