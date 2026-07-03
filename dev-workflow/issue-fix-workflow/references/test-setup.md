# Bootstrap de pruebas — Vitest + Playwright (solo primera vez)

> **Ejemplo concreto** para un stack Next.js + Firebase/Firestore en monorepo
> pnpm/Turbo. No es prescriptivo: adapta paquete, comandos y rutas a tu repo (lo
> que detectaste en el Paso 0 del SKILL.md). Si tu stack es otro (Jest, Cypress,
> pytest, `go test`…), conserva la **forma** (unit + e2e con video antes/después)
> y cambia las herramientas.

El repo aún no tiene infraestructura de pruebas: `pnpm test` es un no-op y no hay
`vitest.config` ni `playwright.config`. Como la regla es **1 PR por issue**, este
setup se monta **una sola vez** dentro del **PR del primer fix que lo necesita**
(no en un PR aparte). Déjalo explícito en el cuerpo de ese PR como excepción de
una sola vez; los PR siguientes ya solo traen su fix + su test.

CI (`.github/workflows/ci.yml`) corre `pnpm build`, `pnpm typecheck`, `pnpm test`
en cada PR a `main`/`develop`. El objetivo es que `pnpm test` ejecute Vitest vía
Turbo, y que los E2E de Playwright se corran aparte (no en el `test` de CI por
defecto, para no requerir navegadores en el runner salvo que se decida).

## 1. Vitest (unit / lógica de server actions)

```bash
pnpm --filter @<scope>/web add -D vitest @vitest/coverage-v8
```

`apps/web/vitest.config.ts`:
```ts
import { defineConfig } from 'vitest/config'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  test: { environment: 'node', include: ['src/**/*.test.ts'] },
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
})
```

`apps/web/package.json` → scripts:
```json
"test": "vitest run",
"test:watch": "vitest"
```

Turbo ya define la task `test` (`turbo.json`), así que `pnpm test` en la raíz la
toma automáticamente. La lógica pura (p. ej. helpers en `src/lib`, paquetes
`shared`) se testea directo. Para código de servidor que toca la base de datos,
abstrae el acceso o usa un **emulador** (p. ej. el de Firestore, ver `firebase.json`,
puerto 8080) en vez de pegarle a tu proyecto real.

## 2. Playwright (E2E + video antes/después)

```bash
pnpm --filter @<scope>/web add -D @playwright/test
pnpm --filter @<scope>/web exec playwright install chromium
```

`apps/web/playwright.config.ts`:
```ts
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:3000',
    video: 'on',          // graba SIEMPRE — es la evidencia antes/después
    trace: 'retain-on-failure',
  },
  outputDir: './test-results',
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
    reuseExistingServer: true,
  },
})
```

`apps/web/package.json` → script:
```json
"test:e2e": "playwright test"
```

Specs en `apps/web/e2e/<issue>.spec.ts`. Los videos salen a
`apps/web/test-results/`.

## 3. .gitignore

Agrega (si no están) para no commitear artefactos de prueba:
```
test-results/
playwright-report/
coverage/
```

Los videos de evidencia se adjuntan al PR manualmente (arrastrándolos a la
descripción) o se convierten a GIF; **no** se commitean al repo, para mantener el
PR "solo el fix".

## 4. Emulador para tests que escriben

Para no tocar datos reales en pruebas, apunta el Admin SDK al emulador:
```bash
FIRESTORE_EMULATOR_HOST=127.0.0.1:8080 pnpm test
```
y levanta `pnpm emulators` aparte (requiere Java). Considéralo al diseñar tests de
server actions que tocan Firestore/Auth.

## 5. Evidencia visual en CI (repo PRIVADO)

En repo privado no se puede embeber evidencia inline por API (ver SKILL.md). La vía
automatizable es un **artefacto de CI**: un workflow que corre el E2E (con
emuladores) y sube `test-results/` (videos) como artefacto descargable del PR.

`.github/workflows/e2e.yml` (resumen, ~2 min en CI):
```yaml
on: { pull_request: { branches: [main, develop] } }
jobs:
  e2e:
    runs-on: ubuntu-latest
    permissions: { contents: read, pull-requests: write }   # para comentar el link
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - uses: actions/setup-java@v4          # los emuladores corren sobre la JVM
        with: { distribution: temurin, java-version: '21' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm --filter <web> exec playwright install --with-deps chromium
      - run: npm install -g firebase-tools
      - run: firebase emulators:exec --only auth,firestore --project demo-<proj> "pnpm --filter <web> test:e2e"
      # Manifiesto autoexplicativo DENTRO del artefacto (header auto + texto redactado):
      - if: always()
        run: |
          mkdir -p <web>/test-results
          { echo "PR #${{ github.event.pull_request.number }} — ${{ github.head_ref }} @ ${{ github.sha }}";
            echo; cat <web>/e2e/EVIDENCIA.txt; } > <web>/test-results/EVIDENCIA.txt
      - id: artifact
        if: always()
        uses: actions/upload-artifact@v4
        with: { name: e2e-evidencia, path: <web>/test-results/, retention-days: 14 }
      # Link clickeable del artefacto en el PR (un comentario que se actualiza):
      - if: always() && steps.artifact.outputs.artifact-url != ''
        uses: actions/github-script@v7
        with:
          script: |
            const marker='<!-- e2e-evidencia -->', url='${{ steps.artifact.outputs.artifact-url }}'
            const body=`${marker}\n🎥 [descargar evidencia E2E](${url})`
            const {data:cs}=await github.rest.issues.listComments({...context.repo, issue_number:context.issue.number})
            const ex=cs.find(c=>c.body?.includes(marker))
            ex ? await github.rest.issues.updateComment({...context.repo, comment_id:ex.id, body})
               : await github.rest.issues.createComment({...context.repo, issue_number:context.issue.number, body})
```
El revisor llega al artefacto por el **comentario con link** (auto) o por Checks →
e2e → Artifacts. No es inline, pero es automático y no expone nada públicamente.

**El artefacto DEBE incluir `EVIDENCIA.txt`** que diga: **qué issue** resuelve, **qué
se espera ver** en los videos/capturas, y **por qué eso demuestra** que quedó
resuelto. El texto base va versionado en `<web>/e2e/EVIDENCIA.txt` (lo edita cada
fix); CI le antepone el header (PR/rama/commit/run). Así el bundle se explica solo
sin contexto del PR.
