# Phase 0 Research: Log Job Applications

## Decision: Direct REST call via `httpx`, not the official Gemini SDK

**Rationale**: `httpx` is already a required dependency (FastAPI's `TestClient` is httpx-based), so calling Gemini's REST endpoint directly with it is a net-zero new runtime dependency. The official `google-genai` SDK brings a much larger surface (chat sessions, streaming, files API, embeddings) than the single "text in, JSON out" call this feature needs, and Google has already renamed the SDK once (`google-generativeai` → `google-genai`), which is real maintenance-churn risk for a solo-maintained hobby project. `httpx.MockTransport` (built into httpx) also gives a clean, dependency-free way to mock exactly the network boundary in tests. This is a direct application of the constitution's Simplicity & YAGNI principle: use the simplest tool, not a general-purpose SDK, for a narrow single-call need.

**Alternatives considered**:
- `google-genai` official SDK — rejected: over-provisioned surface, extra dependency, past API churn, harder to mock cleanly.
- stdlib `urllib` — rejected: `httpx` is already required for testing anyway, so `urllib` buys no real simplicity win while losing `httpx`'s JSON helpers, timeout handling, and `MockTransport`.

## Decision: Gemini REST endpoint, request/response shape, and auth (verified live, July 2026)

- **Endpoint**: `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
- **Model**: `gemini-2.5-flash` — the current free-tier flash model as of Q2 2026 (~10 RPM / 500 RPD on the free tier). Model names change over time; this should be a single named constant in `gemini_client.py` so it's trivial to bump later.
- **Auth**: API key passed via the `x-goog-api-key` HTTP header (current standard; the older `?key=` query param still works but the header is preferred going forward).
- **Request body**:
  ```json
  {
    "contents": [{"parts": [{"text": "<prompt including the user's free-text sentence>"}]}],
    "generationConfig": {
      "response_mime_type": "application/json",
      "response_schema": {
        "type": "object",
        "properties": {
          "company": {"type": "string"},
          "role": {"type": "string"}
        },
        "required": ["company", "role"]
      }
    }
  }
  ```
- **Response shape**: generated text lives at `candidates[0].content.parts[0].text`.

**Rationale for using `generationConfig.response_mime_type: "application/json"` with a `response_schema`**: this makes Gemini return raw JSON (no markdown code fences, no prose wrapping), which simplifies `_parse_response` to a plain `json.loads` plus a check that `company`/`role` are present and non-empty — no fence-stripping heuristics needed. This is a stronger, more Simplicity-aligned choice than parsing free-form text output.

**Alternatives considered**: prompting for JSON without `response_schema` — rejected, since without a schema the model can (and does, in practice) wrap output in markdown fences or add explanatory prose, requiring fragile string-stripping logic in `_parse_response` that the schema-constrained approach avoids entirely.

## Decision: Synchronous FastAPI routes and synchronous `httpx.Client`

**Rationale**: single-user, local, personal tool — there is no concurrency requirement that `async def` + `httpx.AsyncClient` would address. Sync code is simpler to write, read, test, and mock. This is a direct Simplicity/YAGNI call: async is infrastructure for a scale this app will never reach.

**Alternatives considered**: async FastAPI routes — rejected as premature; nothing in the spec's success criteria implies concurrent load.

## Decision: Project type — single-project server-rendered web app (Option 1)

**Rationale**: FastAPI + Jinja2 templates, no separate frontend build/SPA. This is a personal tool with simple CRUD-style screens (a list view, a two-step add-application flow); a separate frontend project would be speculative complexity with no current need.

**Alternatives considered**: Option 2 (separate `backend/`/`frontend/` projects) — rejected, no requirement calls for a decoupled frontend; would add a build step and API-contract overhead for no current benefit.

## Decision: Constitution Check — Complexity Tracking required for LLM dependency

**Rationale**: introducing an external network dependency (Gemini API), a secret to manage, and non-deterministic output is a real increase in complexity relative to a pure-Python parser, so Simplicity & YAGNI requires it be explicitly justified rather than silently accepted. See `plan.md`'s Complexity Tracking table.

**Alternatives considered**: fixed-pattern regex/keyword extraction — evaluated and rejected per the feature spec itself (FR-002 requires identifying company/role "regardless of the exact phrasing or word order used"), since a fixed pattern cannot generalize across arbitrary phrasing, and approximating LLM-level flexibility with an ever-growing hand-maintained pattern library would itself be a larger, more brittle Simplicity violation than one isolated, well-tested API call behind a single function.

## Decision: `pytest` + FastAPI `TestClient` + `httpx.MockTransport` for testing

**Rationale**: satisfies the constitution's NON-NEGOTIABLE Test-First principle with an entirely offline, deterministic test suite — no real Gemini API key needed to run tests, no network flakiness. `TestClient` is httpx-based, so the same mocking primitive (`httpx.MockTransport`) covers both the Gemini boundary and route-level integration tests.

**Alternatives considered**: mocking at the SDK level — moot, since the REST-call approach avoids the SDK entirely; recording/replaying real API responses (VCR-style) — rejected as unnecessary extra tooling for a small, stable JSON contract that's easy to hand-write fixtures for.
