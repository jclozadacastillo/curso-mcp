---
name: qa-security
description: Revisa el proyecto en busca de secretos expuestos, validacion de entradas insuficiente y manejo de excepciones riesgoso.
---
# Instrucciones
1. Busca claves/contrasenas escritas directamente en el codigo.
2. Revisa validacion de entradas (tipo, formato, longitud, rango).
3. Busca `except:` generico o `except: pass`.
4. Reporta en esta tabla:

| Caso | Lo que se encontro | Correccion sugerida |
|---|---|---|
| 🔑 Secreto expuesto | [hallazgo o "sin hallazgos"] | [sugerencia] |
| 🧪 Validacion de entradas | [hallazgo o "sin hallazgos"] | [sugerencia] |
| 🚪 Manejo de excepciones | [hallazgo o "sin hallazgos"] | [sugerencia] |

5. Sin importar si encontraste un secreto quemado en codigo o no, asegurate de que exista el patron correcto para manejarlos en el futuro. **No confies en leer `.gitignore` como texto — verifica con git directamente**, porque el archivo puede decir cualquier cosa sin que git realmente lo respete, o puede perder una linea entre una corrida y otra sin que se note a simple vista:
   - Si no existe `.env.example`, crealo (con las claves esperadas del proyecto, **sin valores reales** — solo el nombre).
   - Si existe `.env`, corre `git check-ignore -q .env`. Si el codigo de salida no es 0, `.env` NO esta ignorado de verdad — agrega la linea a `.gitignore` y vuelve a verificar, no des por hecho que quedo bien solo por haberla escrito.
   - Si existe `.env`, corre tambien `git ls-files --error-unmatch .env`. Si el codigo de salida es 0, `.env` ya esta trackeado por git — esto es mucho mas grave que solo faltar en `.gitignore`: el secreto puede ya estar en el historial. Reportalo como hallazgo critico aparte, no lo mezcles con "sin hallazgos".
   - Si si encontraste un secreto quemado, la correccion sugerida en la tabla debe ser explicita: moverlo a una variable de entorno leida con `os.environ.get(...)` (o `python-dotenv`), nunca dejarlo como valor literal en el codigo.
6. Debajo de la tabla (no dentro — la tabla se queda en exactamente 3 filas), agrega una seccion `## Acciones de higiene aplicadas` listando cada cosa que hiciste en el punto 5 (ej. "Agregue `.env` a `.gitignore`, no estaba ignorado") o "Ninguna, ya estaba en orden" si no hiciste nada. Una correccion real que no se reporta es tan mala como si no se hubiera hecho.
7. Guarda la tabla completa MAS la seccion de acciones en `hallazgos-seguridad.md` (sobrescribiendo si ya existe) — no te quedes solo con mostrarlo en el chat, el archivo es el entregable.
8. No corrijas el codigo de negocio automaticamente — la unica accion que si tomas por tu cuenta es la del punto 5 (higiene de `.env.example`/`.gitignore`), el resto solo lo diagnosticas.
