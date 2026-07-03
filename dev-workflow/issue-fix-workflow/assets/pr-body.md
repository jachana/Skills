<!-- Plantilla del cuerpo del PR. Reemplaza los <…>. Borra estos comentarios. -->

Closes #<N>

## Qué arregla
<Una o dos frases: el problema y el comportamiento corregido.>

## Por qué / causa raíz
<Qué lo causaba. Si es seguridad, el impacto que se cierra.>

## Cómo se arregló
<El enfoque, acotado. Archivos clave tocados.>

## Evidencia

**Reproducción (antes):**
<Salida del test en rojo, o `antes.webm` — el bug ocurriendo.>

**Resuelto (después):**
<El mismo test en verde, o `después.webm` — el comportamiento correcto.>

<!-- Arrastra aquí proof/issue-<N>/antes.webm y después.webm si aplica. -->

## Checklist
- [ ] Rama desde la rama de integración, nombre `<tipo>/<N>-<nombre-corto>`.
- [ ] Solo este fix — `git diff <rama-integración>...HEAD --stat` sin cambios ajenos.
- [ ] Prueba que fallaba por el bug y ahora pasa.
- [ ] Compuerta de CI (build + typecheck + test) en verde.
- [ ] Evidencia antes/después adjunta o enlazada.
- [ ] Sin secretos, `.env*`, ni artefactos en el diff.

## Seguimiento (si aplica)
<Issues nuevos abiertos por trabajo fuera de alcance detectado acá: #…>
