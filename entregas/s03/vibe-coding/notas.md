# Bitacora y Notas de Laboratorio — Practica 2 (Vibe Coding)

**Curso:** Programacion de Backend y MCP en Python para IA Generativa  
**Sesion:** 3 (Lunes)  
**Estudiante:** Juan Carlos Lozada  
**Fecha:** 31 de agosto de 2026 (Lunes)  
**Institucion:** UNIANDES - Dpto. de Desarrollo de Software  

---

## Ronda 1 — Validador de contrasenas

### 1. Prediccion (antes de ejecutar)
* **Prompt del instructor:** `hazme un validador de contrasenas`
* **Longitud minima esperada:** Pense que por defecto pediria 8 caracteres, que es el estandar mas comun en librerias web.
* **Exigencia de caracteres:** Predije que exigiria mayuscula, minuscula y al menos un numero.
* **Caso vacio:** Esperaba que lanzara una excepcion tipo `ValueError` o devolviera `False`.

### 2. Ejecucion real en mi maquina
Casos probados:
* `'12345'`: Rechazado por longitud (el modelo definio un minimo arbitrario de 6 caracteres).
* `'password'`: Rechazado porque no contiene numeros (no exigio mayusculas ni simbolos especiales, solo digitos).
* `''`: Retorno `(False, "La contrasena no puede estar vacia.")`.

### 3. Tabla comparativa

| Pregunta | Mi prediccion | Mi resultado real | Coincide con el instructor |
|---|---|---|---|
| Longitud minima exigida | 8 caracteres | 6 caracteres | No (el instructor obtuvo 8 con regex) |
| Exigio simbolo / mayuscula / numero | Mayuscula + numero | Solo numero | No (al instructor le pidio simbolo obligatorio) |
| Comportamiento con clave vacia | ValueError o False | Retorno booleano False con mensaje explicativo | Si, ambos devolvieron False |

---

## Ronda 2 — Agregar validacion de email

### 1. Prediccion (antes de ejecutar)
* **Prompt:** `agregale que tambien valide un formato de email`
* **Estilo de respuesta:** Predije que mantendria la firma retornando una tupla `(bool, str)`.
* **Caso `ana@`:** Predije que la regex lo detectaria como invalido por faltar el dominio y TLD.

### 2. Ejecucion real
Casos probados:
* `'ana@correo.com'` -> Valido (`True`).
* `'ana@'` -> Invalido (`False`), mensaje: `Formato de correo no valido: 'ana@'`.
* `''` -> Invalido (`False`), mensaje: `El email no puede estar vacio.`.

### 3. Tabla comparativa

| Pregunta | Mi prediccion | Mi resultado real |
|---|---|---|
| Mantuvo el formato de respuesta | Si, tupla (bool, str) | Si, pero en el chat agrego un bloque de ejemplo no solicitado |
| Comportamiento con email mal formado (`ana@`) | Retornar False por regex | Retorno False correctamente con mensaje |

*Observacion:* En mi caso no reescribio la funcion de contrasena, pero en el codigo del instructor el modelo decidio unificar ambas validaciones en una sola clase sin que nadie se lo pidiera.

---

## Ronda 3 — Lista de varios usuarios

### 1. Prediccion (antes de ejecutar)
* **Prompt:** `ahora que maneje una lista de varios usuarios, cada uno con su contrasena y su email`
* **Riesgo de rotura:** Sospeche que al pasar a lista dejaria de exponer las funciones de validacion sueltas y obligaria a pasar ambos datos juntos.
* **Estructura de datos:** Predije una lista simple de diccionarios en memoria `[{'email': ..., 'password': ...}]`.

### 2. Ejecucion real
* Implemento la clase `GestorUsuarios` con un arreglo interno `self.usuarios`.
* Si falla el correo o la clave, retorna un diccionario con status de error.
* Se probaron dos altas de usuarios de UNIANDES:
  * `carlos@uniandes.edu.ec` (valido)
  * `maria@uniandes.edu.ec` (valido)
* La lista se genera correctamente, pero no valida duplicados de email.

### 3. Tabla comparativa

| Pregunta | Mi prediccion | Mi resultado real |
|---|---|---|
| Se rompio algo que ya funcionaba | Si, se acoplaron las validaciones y no hay validacion de unicidad | El flujo cambio de tupla a diccionario de respuesta |
| Estructura de la lista | Lista de diccionarios en memoria | Lista de diccionarios dentro de una clase |

---

## Bloque de Cierre — Provocar la falla en vivo

### 1. Hipotesis previa
* **Prompt:** `ahora que la validacion de contrasena sea opcional para usuarios administradores`
* **Que puede salir mal:** Si un administrador se crea sin contrasena (valor `None` o string vacio), cualquier funcion posterior de autenticacion, hash o comparacion que espere una cadena va a explotar con `TypeError` o `AttributeError`, o peor aun, permitira acceso irrestricto sin credenciales.

### 2. Ejecucion y evidencia del fallo
* Se registro el usuario `admin@uniandes.edu.ec` con `password=None` y `es_admin=True`.
* El registro paso en verde.
* Al llamar a `autenticar("admin@uniandes.edu.ec", "admin123")`, el sistema intento evaluar el valor almacenado y detono la excepcion:
  ```text
  TypeError: Fallo de integridad: El usuario admin 'admin@uniandes.edu.ec' no tiene contrasena asignada.
  ```
* **Diagnostico:** El cambio solicitado sin especificacion resolvio el "registro" pero destruyo la coherencia del modelo de autenticacion.

---

## Reflexion Final

1. **¿En que ronda tu prediccion se alejo mas de lo que realmente paso? ¿Por que crees que fallaste esa prediccion?**  
   En la Ronda 1 y en el Bloque de Cierre. En la Ronda 1 asumi que el modelo aplicaria estandares modernos de seguridad (minimo 8 caracteres, caracteres alfanumericos y simbolos), pero decidio por su cuenta un umbral bajo de 6 caracteres solo con numeros. Fallo porque cuando no hay una especificacion explicita, la IA "completa los vacios" con su propio sesgo estadistico del entrenamiento, el cual es variable y no determinista.

2. **¿Tu resultado fue exactamente igual al del instructor en todas las rondas, o hubo diferencias con el mismo pedido? ¿Que te dice eso sobre pedir cosas sin spec?**  
   Hubo diferencias notables desde la primera ronda: mientras en mi entorno exigio 6 caracteres y retorno tuplas, al instructor le genero una regex con simbolos obligatorios de 8 caracteres y estructuro el codigo de otra forma. Esto demuestra de forma directa que "vibe coding" (programar por intuicion o prompts sueltos) no es reproducible ni confiable para entornos de produccion, ya que el mismo prompt genera arquitecturas y contratos incompatibles entre distintas corridas.

3. **Frase completada:**  
   *"Si yo tuviera que darle este codigo a otra persona manana, tendria que explicarle **que criterios exactos determinan una contrasena valida, por que no se verifican correos duplicados y como debe autenticarse un administrador sin contrasena**, porque eso no esta escrito en ningun lado."*
