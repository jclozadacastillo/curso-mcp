# Comparacion Final — Spec a Mano vs Spec Kit
**Sesion:** 4 (Miercoles)  
**Autor:** Juan Carlos Lozada  
**Institucion:** UNIANDES - Dpto. de Desarrollo de Software  

---

## 1. Tabla Comparativa General

| Aspecto | Spec a mano (`clase-sdd`) | Spec Kit (`mi-proyecto-speckit`) |
|---|---|---|
| **¿Cubrio los mismos casos borde?** | Si, cubrio los limites fisicos principales y no numericos basicos. | Cubrio todos los de la spec a mano y agrego protecciones para flotantes no finitos (`inf`, `nan`) y sanitizacion de espacios en blanco. |
| **¿Que genero Spec Kit que tu no habias escrito?** | Enfoque directo en funcion unitaria pura. | Arquitectura en capas (`core`, `service`, `cli`), escenarios formales Given/When/Then, matriz de tareas trazables (`tasks.md`) y suite integral de tests. |
| **¿Que se sintio mas rapido de arrancar?** | Spec a mano. Es directo y toma pocos minutos redactar el markdown basico. | Spec Kit requiere inicializar herramientas, planificar y desglosar fases, lo que toma mas tiempo inicial de arranque. |
| **¿Cual te genero mas confianza en el resultado?** | Confiabilidad moderada (depende de que el programador recuerde todos los casos borde). | Confianza significativamente mayor, debido a la exhaustividad de los escenarios y la separacion de responsabilidades. |

---

## 2. Comparacion de los 3 Casos Lado a Lado

| Caso Evaluado | Entrada | Resultado Spec a Mano | Resultado Spec Kit |
|---|---|---|---|
| **Caso normal** | 100.0 °C a Fahrenheit | `212.0` (Correcto) | `212.0` (Correcto) |
| **Caso borde** | -273.15 °C a Kelvin | `0.0` (Cero absoluto exacto) | `0.0` (Cero absoluto exacto) |
| **Caso no contemplado** | Entrada `float('inf')` | Devuelve `inf` (propagacion silenciosa no fisica) | Lanza `ValueError` ("finite real number") protegiendo la logica |

---

## 3. Frase de Cierre

> *"La proxima vez que tenga un proyecto de tamano **mediano o grande**, elegiria **Spec Kit** porque **establece una arquitectura modular con trazabilidad completa desde los requerimientos funcionales (FR) hasta las pruebas automatizadas, evitando que se omitan casos borde criticos de seguridad y consistencia en el backend**."*
