---
name: issue-fix-workflow
description: >-
  Flujo de trabajo para llevar UN issue de GitHub desde que se elige hasta un PR
  probado y con evidencia, en CUALQUIER repo. Úsalo SIEMPRE que el usuario decida
  trabajar en un issue, pida crear una rama para un hallazgo, o vaya a abrir un PR
  de una corrección — aunque no nombre el flujo explícitamente. Se dispara con
  frases como "trabajemos el issue #N", "vamos con el #1", "arreglemos el hallazgo",
  "crea la rama para", "hagamos el PR del issue", "let's work on issue #",
  "fix this issue", "open a PR for". Cubre: detectar y recordar las convenciones del
  repo (rama de integración, gestor de paquetes, stack de pruebas, CI), crear la
  rama con convención de nombres, reproducir antes de arreglar, implementar SOLO el
  fix, pruebas con evidencia antes/después, y PR con evidencia.
---

# Flujo: de issue a PR con evidencia

Este es el contrato de trabajo. La meta no es solo "arreglar el bug", sino
**dejar prueba reproducible de que el problema existía y de que quedó resuelto**,
en un PR que contenga **únicamente** ese arreglo. Un PR sin evidencia o con
cambios mezclados no está listo, por bien que se vea el código.

> **Agnóstico del repo.** Este flujo no asume un stack ni una rama concreta. La
> primera vez que lo usas en un repo, el **Paso 0** detecta sus convenciones
> (rama de integración, gestor de paquetes, stack de pruebas, CI) y las guarda en
> un archivo local; de ahí en adelante las relee. Todos los `<placeholders>` de
> abajo salen de ese archivo. `gh` ya detecta el repo actual, así que no hace
> falta `--repo` salvo que quieras forzarlo.

## Modelo y esfuerzo
| Fase | Modelo | Esfuerzo | Por qué |
|---|---|---|---|
| Paso 0 — detectar convenciones del repo | haiku | bajo | lectura mecánica de lockfiles/workflows |
| Reproducir + fix + tests (pasos 2–5) | sonnet | medio–alto | el rigor rojo→verde no se negocia |
| Diagnóstico difícil (bug esquivo, arquitectura) | opus | alto | entender primero, tocar después |

Sesión por debajo del pico que pide el issue → avísale al usuario antes de implementar. Por encima → delega el Paso 0 a un subagente con `model: haiku` explícito.

## Principios (el "por qué")

- **Un issue = una rama = un PR.** El revisor debe poder razonar sobre un cambio
  acotado. Si al arreglar descubres otro problema, **no lo arregles aquí**: abre
  un issue nuevo y sigue enfocado. Mezclar arreglos esconde regresiones.
- **Reproduce antes de arreglar.** Primero escribe la prueba/escena que falla por
  el bug. Eso te da el "antes", evita arreglar lo que no era, y convierte la
  evidencia en un subproducto natural (rojo → verde) en vez de un trámite final.
- **No hay PR sin test.** El entregable mínimo es una prueba que **falla por el
  bug y pasa con el fix** — esa es la evidencia que CI vuelve a correr sola.
  Asegurar que el issue quede cubierto por un test no es opcional; es la
  definición de "hecho". Si un issue de verdad no es testeable de forma evidente,
  **no lo asumas**: propón cómo demostrarlo y acuérdalo con el usuario.
- **La evidencia visual es parte del entregable.** Además del test, un artefacto
  que muestra el comportamiento antes y después (video/gif para UI, salida
  rojo→verde para lógica/seguridad). Si no es obvio qué mostrar, **propón la
  evidencia y confírmala con el usuario antes de seguir** — no inventes un video
  que no demuestra nada.
- **Base = la rama de integración del repo.** Las ramas salen de esa rama
  actualizada y los PR apuntan a ella (la detectas en el Paso 0; suele ser
  `develop` en Gitflow o `main`). CI corre su compuerta en cada PR.

## Cuándo NO usar este flujo

Cambios triviales pactados con el usuario fuera del tablero (un typo, ajustar un
texto) no necesitan rama/issue/PR formal si el usuario lo dice. Ante la duda,
sigue el flujo: es barato y deja trazabilidad.

---

## Paso 0 — Convenciones del repo (la primera vez en este repo)

Este flujo se adapta al repo, no al revés. Antes de tocar nada, asegúrate de tener
las convenciones registradas en un archivo local: **`.claude/issue-fix-workflow.local.md`**.

1. **Si ya existe**, léelo y úsalo — no vuelvas a detectar.
2. **Si no existe**, detéctalas (tabla abajo), **confirma con el usuario** lo que no
   sea obvio, y escríbelo en ese archivo. Mantenlo **fuera de git sin tocar archivos
   versionados**: agrega su ruta a `.git/info/exclude` (el exclude local del repo,
   que nunca se commitea). No uses `.gitignore` salvo que el usuario lo prefiera.

Detección (usa lo que el repo te diga; pregunta solo los huecos):

| Convención | Cómo detectarla |
|---|---|
| Rama de integración | `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`; si existe una rama `develop`, suele ser la base de los PR. Confirma si hay duda. |
| Gestor de paquetes | lockfile: `pnpm-lock.yaml`→pnpm · `package-lock.json`→npm · `yarn.lock`→yarn · `bun.lockb`→bun |
| Monorepo / paquete objetivo | `pnpm-workspace.yaml` / `turbo.json` / `nx.json`; lista los workspaces y pregunta cuál es el paquete que se prueba (o "(paquete único)" si no hay monorepo) |
| Stack de pruebas | deps en `package.json`: `vitest`/`jest` (unit), `@playwright/test`/`cypress` (e2e). Otro lenguaje → su runner (pytest, `go test`, etc.) |
| Compuerta de CI | lee `.github/workflows/*.yml`: qué corre en cada PR (build/typecheck/test/lint) |
| Visibilidad del repo | `gh repo view --json isPrivate -q .isPrivate` (define cómo se adjunta la evidencia, ver Paso 7) |
| Convención de commits/ramas | mira `git log --oneline -20` (¿Conventional Commits? ¿idioma?); pregunta el idioma si no es claro |

Plantilla del archivo (rellena con lo detectado):

```markdown
# issue-fix-workflow — convenciones de este repo (local, no versionado)
- Rama de integración: develop                 # o main
- Gestor de paquetes: pnpm                      # npm | yarn | bun
- Workspace/paquete objetivo: @scope/web        # o "(paquete único)"
- Unit tests: vitest        → comando: pnpm test
- E2E: playwright           → comando: pnpm --filter @scope/web test:e2e
- Compuerta de CI: build, typecheck, test
- Visibilidad: público                          # privado
- Commits: Conventional Commits, español; `Refs #N` en commits, `Closes #N` en el PR
- Artefactos de prueba: <paquete>/test-results/ (gitignored)
```

Excluirlo localmente (sin tocar archivos versionados):

```bash
mkdir -p .claude
grep -qxF '.claude/issue-fix-workflow.local.md' .git/info/exclude 2>/dev/null \
  || echo '.claude/issue-fix-workflow.local.md' >> .git/info/exclude
```

> De aquí en adelante, **cada `<placeholder>`** (rama de integración, `<pm>`,
> `<paquete>`, comandos de test/CI) sale de ese archivo.

---

## Paso 1 — Crear la rama desde la rama de integración

El usuario decide qué issue se trabaja; este flujo arranca **después** de esa
decisión. Primero:

1. Lee el issue completo y su severidad/labels: `gh issue view <N>`.
2. Resume en una frase **qué** se arregla y **cómo sabremos** que quedó (criterio
   de aceptación). Si el issue no lo dice, acuérdalo con el usuario ahora — es la
   base de la evidencia.

Convención de rama: **`<tipo>/<N>-<nombre-corto-kebab>`** (idioma del nombre según
el Paso 0).

| tipo | cuándo |
|------|--------|
| `security/` | vulnerabilidad / control de acceso |
| `fix/` | bug de lógica o comportamiento incorrecto |
| `feat/` | funcionalidad nueva |
| `refactor/` | reestructura sin cambiar comportamiento |
| `perf/` | rendimiento |
| `chore/` | tooling, dependencias, CI, config |
| `docs/` | documentación |
| `test/` | solo pruebas o infraestructura de pruebas |

```bash
git checkout <rama-integración> && git pull origin <rama-integración>
git checkout -b security/1-rechazar-acceso-ajeno
```

Nombre corto: 2–4 palabras, describe el **arreglo**, no el síntoma
(`security/2-cifrar-dato-sensible`, no `security/2-dato-en-texto-plano`).

> **1 PR por issue** es la regla. La primera vez que el repo no tiene
> infraestructura de pruebas, el setup (ver `references/test-setup.md`) **viaja
> dentro del PR del primer fix que lo necesita** — excepción de una sola vez,
> déjala explícita en el cuerpo del PR. De ahí en adelante, cada PR es solo su
> fix + su test.

---

## Paso 2 — Reproducir (capturar el "antes")

Escribe la prueba que **falla por el bug**, según el tipo de issue:

| Tipo de hallazgo | Reproducción / evidencia |
|---|---|
| Comportamiento de UI (flujo, estado, navegación) | Test e2e que actúa como el usuario; con grabación de video activa captura el "antes" (falla) |
| Seguridad / control de acceso / IDOR | Test que ejerce el abuso — p. ej. invocar una acción/endpoint con un identificador ajeno — y **espera ser rechazado**. Falla hoy, pasa con el fix |
| Lógica pura / cálculo | Test **unitario** con el caso que da el resultado incorrecto |
| Datos en texto plano / fuga al cliente | Test que inspecciona el payload/persistencia y **asserta** que el dato sensible no aparece en claro |
| Visual / estilos | Captura "antes" (screenshot del test e2e) |

Corre la prueba y **confirma que falla por la razón correcta**. Guarda la salida:
ese rojo es la mitad de tu evidencia.

Si para este issue ningún artefacto evidente aplica (o el video no demostraría
nada), dilo y **acuerda con el usuario qué mostrar** antes de implementar.

---

## Paso 3 — Implementar SOLO el fix

- Cambia lo mínimo necesario para que la prueba pase. Resiste arreglar de paso.
- Respeta el estilo del código vecino (mismos patrones, nombres, densidad de
  comentarios).
- Si el arreglo destapa trabajo grande fuera de alcance, **abre issue nuevo** y
  enlázalo en el PR como seguimiento.

---

## Paso 4 — Verde + evidencia "después"

1. La prueba de reproducción ahora **pasa**.
2. Captura el "después". Elige el formato según el cambio: un **video** si hay flujo
   o movimiento; una **captura/screenshot** si es estático (un estado, estilos, una
   tabla, un error) — no fuerces un video cuando una imagen lo muestra mejor. Para
   video antes/después limpio (comandos según el Paso 0):
   ```bash
   # ANTES: corre el spec contra el estado pre-fix (stash del fix o checkout de la rama de integración)
   git stash && <pm> <cmd-e2e> <spec>   # graba "antes"
   git stash pop
   # DESPUÉS: con el fix aplicado
   <pm> <cmd-e2e> <spec>                 # graba "después"
   ```
   Los videos quedan en el directorio de resultados del Paso 0 (p. ej.
   `<paquete>/test-results/`, gitignored). Renómbralos a
   `proof/issue-<N>/antes.<ext>` y `después.<ext>` para adjuntarlos al PR.

---

## Paso 5 — Compuerta local (espejo de CI)

No abras el PR hasta que esto pase entero — es exactamente lo que correrá CI (los
comandos exactos están en el Paso 0):

```bash
# compuerta de CI, p. ej.:
<pm> build && <pm> typecheck && <pm> test
<pm> <cmd-e2e>      # E2E + videos, si aplica
```

Muestra la salida real al usuario (no afirmes "pasa" sin pegar el resultado).
Aplica la disciplina de evidencia: **probar antes de declarar hecho**.

---

## Paso 6 — Commit

Conventional Commits, en el idioma del Paso 0, con scope y referencia al issue.
Usa **`Refs #N`** en commits (no `Closes`, para no cerrar el issue al pushear la
rama; el cierre lo hace el PR al mergear).

```
security(api): derivar la identidad desde la sesión, no del cliente

La acción confiaba en un identificador enviado por el cliente y corría con
privilegios elevados, saltándose las reglas de acceso. Ahora la identidad
sale de la sesión verificada en el servidor.

Refs #1
Co-Authored-By: Claude <noreply@anthropic.com>
```

Antes de commitear, **revisa el alcance**: `git diff <rama-integración>...HEAD --stat`.
Cada archivo debe pertenecer al issue. Saca cualquier cosa ajena (formateos
sueltos, reportes, scripts de exploración, `.env*`, artefactos). Recuerda que
reportes y scripts auxiliares de auditoría viven **fuera del repo** a propósito.

---

## Paso 7 — Abrir el PR (solo el fix + evidencia)

PR hacia la rama de integración. Título: **`[<tipo>] #<N> · <resumen corto>`**.
Cuerpo según la plantilla `assets/pr-body.md` (Closes #N, qué/por qué, evidencia
antes/después, checklist).

```bash
git push -u origin security/1-rechazar-acceso-ajeno
gh pr create --base <rama-integración> \
  --title "[security] #1 · Identidad desde la sesión verificada" \
  --body-file <(...)   # usa assets/pr-body.md como base
```

### Adjuntar la evidencia visual (imágenes o videos)

La evidencia no siempre es un video: muchas veces basta una **captura** (un estado,
un antes/después de UI, una tabla, un error). El script incluido en este skill
acepta **imágenes** (.png/.jpg/.gif/.webp) y **videos** (.webm/.mp4 → los convierte
a gif):

```bash
scripts/publicar-evidencia.sh <N> \
  antes.png despues.png            # o videos: .../antes.webm .../despues.webm
```

(Ruta del script: la carpeta `scripts/` de este skill. Si lo invocas desde otro
directorio, usa la ruta absoluta a ese archivo.)

Para verse **inline**, GitHub necesita una URL accesible sin auth — y ahí está el
quiebre público vs privado (la visibilidad la fijaste en el Paso 0):
- **Repo PÚBLICO:** el script publica los assets en una rama `media/issue-N` y los
  comenta vía `raw.githubusercontent` → inline. Automático.
- **Repo PRIVADO:** las URLs `raw` dan **404 al proxy** y **subir adjuntos por API
  no se puede** (el endpoint `user-attachments` del drag-drop exige sesión de
  navegador, no token — verificado: 422). El script lo detecta y deja los archivos
  en `evidencia-issue-N/` para que los **arrastres** al PR (imágenes inline; `.webm`
  con reproductor nativo) — o súbelos como **artefacto de CI** para descarga.
- La evidencia principal igual son los tests rojo→verde, que CI ejecuta solos.

> Espera la aprobación del usuario antes de pushear y abrir el PR — es una acción
> de cara al exterior. El merge lo decide el equipo con CI en verde y review.

---

## Guardarraíles de alcance ("solo el fix")

Antes de marcar listo, verifica:
- [ ] `git diff <rama-integración>...HEAD --stat` — todo pertenece al issue #N.
- [ ] La prueba de reproducción fallaba antes y pasa ahora.
- [ ] La compuerta de CI (build + typecheck + test, + e2e si aplica) en verde, con salida mostrada.
- [ ] Evidencia antes/después lista y enlazada/adjunta.
- [ ] El PR cierra el issue (`Closes #N`) y no toca nada fuera de alcance.

## Ejemplos issue → rama → evidencia (genéricos)

- **#1** control de acceso → `security/1-rechazar-acceso-ajeno` → test que invoca
  la acción con un identificador ajeno y **espera rechazo** (rojo→verde) + e2e del
  login real.
- **#2** dato sensible en texto plano → `security/2-cifrar-dato-sensible` → test que
  asserta que el payload al cliente no contiene el dato en claro.
- **#3** cálculo dependiente de la fecha → `fix/3-calculo-estable` → unit test que
  fija la fecha y prueba que el resultado no cambia entre días.
- **#4** división por cero → `fix/4-evitar-division-cero` → unit test con la entrada
  `0` esperando un resultado vacío, no `NaN`.

## Archivos de apoyo
- `references/test-setup.md` — **ejemplo** de bootstrap de pruebas (Vitest +
  Playwright sobre un monorepo pnpm/Turbo con Firestore). Adáptalo a tu stack; las
  rutas y comandos salen del Paso 0.
- `assets/pr-body.md` — plantilla del cuerpo del PR.
- `scripts/publicar-evidencia.sh` — publica evidencia (imágenes o videos→gif)
  inline en el PR vía rama `media/issue-N` en repo **público**, o la deja lista para
  arrastrar en repo **privado**. Requiere `gh` (+ `ffmpeg` solo para videos).
