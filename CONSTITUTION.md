# 📜 StudyMate — Project Constitution

> **Single source of truth** for StudyMate's purpose, principles, architecture,
> constraints, decisions, limitations, and roadmap.
>
> If a future decision conflicts with this document, update this document first.
> Do not silently change the project's direction.

**Version:** 2.0  
**Last updated:** 2026-10-07  
**Current milestone:** Phase 1 — Ingestion Pipeline / M2 Chunking

---

## 1. Project Identity

### 1.1 Name

**StudyMate — AI-Powered Study Planner**

### 1.2 Core idea

StudyMate is not primarily a chatbot or a "chat with PDF" application.

It is a **closed-loop study system**:

> **Retrieve → Quiz → Schedule → Review**

Students provide their study materials and StudyMate helps them:

1. understand the material through grounded Q&A,
2. turn material into flashcards and quizzes,
3. schedule study and review sessions around available time,
4. revisit material using spaced repetition,
5. see what material has and has not been studied.

The system should connect these activities instead of treating them as isolated features.

### 1.3 Product goal

Build a technically defensible study system that demonstrates how:

- document retrieval,
- LLM-assisted generation,
- spaced repetition,
- calendar-aware scheduling,
- study coverage tracking,
- and evaluation

can work together in one coherent application.

The project is also an engineering and learning project. Technical decisions should be explainable in an interview or project presentation.

### 1.4 What makes StudyMate different

StudyMate does **not** attempt to beat general-purpose AI assistants on raw answer quality.

Its value is the integration of several study workflows:

1. **Closed loop** — retrieval leads into studying, scheduling, and review.
2. **Learning science** — reviews use SM-2 rather than arbitrary reminders.
3. **Coverage transparency** — users can see what they have and have not studied.
4. **Evaluation** — retrieval quality is measured instead of judged only by intuition.
5. **Multimodal roadmap** — lecture audio and image-heavy slides can eventually become part of the knowledge base.
6. **Provider-agnostic AI layer** — model providers can be replaced without rewriting application logic.
7. **Privacy/local-data orientation** — study materials are treated as the user's own data.

### 1.5 Competitive position

NotebookLM, ChatGPT, and similar products may provide better raw AI quality.

That is acceptable.

StudyMate is primarily an **engineering project and specialized study workflow**, not an attempt to reproduce or outperform those products at general AI assistance.

Benchmark against them where useful, but do not let competition redefine the project's scope.

---

## 2. Product Principles

These principles are more important than any individual library, framework, or model.

### P1 — Closed-loop learning

Features should contribute to:

> **Retrieve → Quiz → Schedule → Review**

A feature that does not meaningfully support this loop should be questioned before being added.

### P2 — Grounded over confident

When answering questions about uploaded material, StudyMate should prefer:

- retrieved source material,
- page-level provenance,
- explicit uncertainty,
- and refusal when evidence is insufficient

over an unsupported but confident answer.

### P3 — Deterministic where possible

Use deterministic algorithms for things that do not require an LLM.

Examples:

- SM-2 calculations,
- study-slot selection,
- coverage calculations,
- document metadata handling,
- retrieval scoring.

Use probabilistic AI only where it provides real value:

- natural-language answers,
- flashcard generation,
- difficult reasoning,
- vision interpretation,
- speech transcription.

### P4 — Provenance is mandatory

Generated information should remain traceable to its source whenever possible.

Documents, pages, chunks, flashcards, answers, and study activities should maintain enough metadata to explain where information came from.

### P5 — Replaceable AI providers

Provider/model choices are implementation details, not product identity.

The application should route AI tasks by **role/capability**, so providers can be changed through configuration rather than application-wide rewrites.

### P6 — Evaluation over vibes

Important AI functionality must eventually have measurable evaluation.

For retrieval, examples include:

- hit-rate@k,
- MRR,
- refusal/grounding checks,
- golden question/chunk pairs.

A feature is not considered reliable simply because a few manual examples look good.

### P7 — Limitations are documented

Known limitations should be visible and quantified where possible.

Do not hide weaknesses behind vague claims such as "AI may occasionally make mistakes."

### P8 — Build for the actual hardware and budget

The architecture must remain practical for:

- a single developer,
- a 16 GB RAM laptop,
- no local GPU,
- and a $0 development budget.

---

## 3. Scope

### 3.1 Core MVP

The MVP should establish the fundamental loop:

**Upload → Ingest → Retrieve → Ask → Cite → Study → Review**

Core functionality:

- slide-deck PDF ingestion,
- structured parsing,
- chunking,
- local embeddings,
- vector retrieval,
- grounded RAG chat,
- page-level citations,
- basic persistence,
- deployment,
- documentation and evaluation.

### 3.2 Post-MVP

The following extend the closed loop:

- flashcard generation,
- SM-2 review,
- study coverage dashboard,
- exam/mock-test generation,
- calendar-aware scheduling,
- lecture audio transcription,
- OCR for image-only slides,
- vision-based slide understanding.

### 3.3 Explicitly out of scope for now

Do not prematurely build:

- multi-user infrastructure,
- complex authentication,
- local LLM inference,
- a custom vector database,
- a custom calendar engine,
- broad LMS integrations,
- enterprise-scale infrastructure,
- elaborate agent orchestration.

These may be reconsidered only when a concrete requirement justifies them.

---

## 4. Hard Constraints

| ID | Constraint | Consequence |
|---|---|---|
| C1 | **$0 budget** | Prefer free API tiers and local CPU processing |
| C2 | **16 GB RAM, no GPU** | No local chat-LLM inference; embeddings remain local |
| C3 | **Single-user MVP** | No authentication required in v1 |
| C4 | **Slide-deck PDFs are the primary input** | Parsing/chunking must account for sparse slide structure |
| C5 | **Deterministic where possible** | Scheduling and learning-state calculations should not depend on LLM output |
| C6 | **Source provenance matters** | Generated answers/cards should retain document/page/chunk references |
| C7 | **Provider independence** | Provider/model configuration must not be hard-coded throughout the application |
| C8 | **External automation is optional** | Tools such as n8n must not become dependencies of the core study engine |

---

## 5. Architecture

### 5.1 Core architecture

```text
┌──────────────────────┐
│      Next.js         │
│  UI + Study Flow     │
└──────────┬───────────┘
           │ HTTP / streaming
           ▼
┌──────────────────────────────────────┐
│               FastAPI                │
│                                      │
│  ├─ ingestion                        │
│  │    parse → clean → chunk          │
│  │    → embed → store                │
│  │                                    │
│  ├─ retriever                         │
│  │    query → top-k chunks            │
│  │                                    │
│  ├─ llm_client                        │
│  │    role/capability routing         │
│  │                                    │
│  ├─ flashcards                        │
│  │    generation + SM-2               │
│  │                                    │
│  ├─ scheduler                         │
│  │    available slots + study plan    │
│  │                                    │
│  └─ coverage                          │
│       studied / unstudied tracking    │
└──────────┬──────────────┬─────────────┘
           │              │
           ▼              ▼
     ┌───────────┐   ┌─────────────┐
     │ ChromaDB  │   │   SQLite    │
     │ embeddings│   │ application │
     │ + metadata│   │    state    │
     └───────────┘   └─────────────┘
           │
           ▼
   ┌───────────────────┐
   │ External AI APIs  │
   │ chat / reasoning  │
   │ vision / STT      │
   └───────────────────┘
```

### 5.2 Architectural rule

**FastAPI owns the application's core logic.**

The following must remain inside the application rather than being delegated to an external automation platform:

- ingestion,
- chunking,
- embedding,
- retrieval,
- RAG,
- flashcard generation orchestration,
- SM-2 state,
- coverage calculation,
- study scheduling logic,
- persistence,
- evaluation.

External automation may trigger these capabilities, but should not replace them.

---

## 6. External Automation and n8n

### 6.1 Current decision

**n8n is NOT part of the MVP core architecture.**

StudyMate does not currently need n8n.

The core workflows are application logic and are better implemented directly in FastAPI/Python because they need:

- unit tests,
- deterministic behavior,
- direct database access,
- clear version control,
- tight integration with the study domain.

Adding n8n now would increase infrastructure and operational complexity without providing enough value.

### 6.2 When n8n becomes justified

Reconsider n8n when StudyMate needs multiple external services or event-driven workflows, such as:

```text
Google Drive
     │
     ▼
   n8n ──────► StudyMate ingestion API
     │
     ├──────► Email
     ├──────► Telegram/Discord
     └──────► Calendar
```

Potential uses:

- detect new files in Google Drive,
- trigger ingestion through a webhook,
- send scheduled study reminders,
- generate weekly progress summaries,
- react to Google Calendar changes,
- connect StudyMate with services that do not justify custom integrations.

### 6.3 n8n boundary

If introduced, n8n is an **integration/orchestration layer**, not the StudyMate brain.

> **StudyMate owns learning logic.  
> n8n owns external automation.**

This boundary must remain clear.

---

## 7. RAG Pipeline

### 7.1 Ingestion

The current ingestion pipeline is designed around slide decks rather than conventional prose documents.

1. Parse PDF using PyMuPDF.
2. Extract text blocks and positional information.
3. Classify blocks by approximate position:
   - title,
   - body,
   - footer.
4. Remove known footer noise.
5. Detect image-only/empty pages.
6. Preserve PDF page numbers.
7. Produce normalized slide-level content.

Current diagnostic result on the golden deck:

- 68 PDF slides,
- approximately 61 text-bearing slides,
- 7 image-only/empty slides skipped,
- 0 observed footer leaks.

### 7.2 Chunking

Chunking should:

- group consecutive slides,
- target approximately 2,000 characters / ~500 tokens,
- use approximately 400 characters of overlap where appropriate,
- prepend slide titles as contextual anchors,
- preserve `page_start` and `page_end`,
- avoid splitting a slide unnecessarily.

The exact chunk size is an implementation parameter, not a permanent product rule. It may change when evaluation demonstrates a better configuration.

### 7.3 Embedding

Current choice:

`sentence-transformers/all-MiniLM-L6-v2`

Reason:

- small enough for local CPU,
- proven on the development machine,
- avoids API cost,
- suitable for the current MVP.

### 7.4 Storage

ChromaDB stores:

- vectors,
- chunk text,
- retrieval metadata.

Important metadata includes:

```text
doc_id
page_start
page_end
title
text
chunk_index
```

SQLite stores application state.

### 7.5 Retrieval

Initial retrieval strategy:

- cosine similarity,
- top-k approximately 4–6,
- metadata preserved for citations.

Retrieval quality must eventually be evaluated with a golden test set.

### 7.6 Generation

The LLM receives:

- user question,
- retrieved chunks,
- source metadata,
- grounding instructions.

The model must not be treated as the source of truth for uploaded course material.

### 7.7 Low-confidence behavior

If retrieval confidence is insufficient, the system should prefer:

> "I couldn't find this in your uploaded materials."

rather than inventing an answer.

---

## 8. AI Provider Architecture

### 8.1 Role-based routing

AI capabilities are separated by role:

| Role | Responsibility | Current direction |
|---|---|---|
| `CHAT` | RAG answers and general generation | Free-tier provider |
| `REASONING` | Difficult generation/reasoning | Free-tier provider when needed |
| `VISION` | Understanding image-heavy slides | Future |
| `STT` | Lecture transcription | Free-tier speech API |

Provider/model names are configuration, not architecture.

### 8.2 Configuration principle

Providers should be replaceable through environment/configuration:

```env
CHAT_BASE_URL=...
CHAT_API_KEY=...
CHAT_MODEL=...

REASONING_BASE_URL=...
REASONING_API_KEY=...
REASONING_MODEL=...

STT_BASE_URL=...
STT_API_KEY=...
STT_MODEL=...
```

The exact provider/model may change as free-tier availability changes.

### 8.3 Provider failure policy

Free APIs can change, retire models, or impose rate limits.

Therefore:

- never scatter provider-specific logic throughout the application,
- isolate provider calls behind one client layer,
- document the active provider,
- keep a fallback where practical,
- do not make a provider name part of StudyMate's identity.

---

## 9. Data Model

The application will use SQLite for structured state.

Core entities:

- `documents`
- `conversations`
- `messages`
- `flashcards`
- `flashcard_reviews`
- `study_sessions`
- `coverage`

`messages` should retain citation information as a snapshot so historical answers remain traceable even if retrieval configuration changes.

`flashcards` store SM-2 state.

`flashcard_reviews` preserve review history.

`study_sessions` may eventually contain:

```text
external_event_id
```

for Google Calendar integration.

`coverage` tracks which document/chunk material has been studied and when.

Vector embeddings remain in ChromaDB and are referenced through their stored chunk/Chroma identifiers.

Full ERD should live separately at:

```text
docs/erd.mmd
```

---

## 10. Technology Stack

| Layer | Technology | Status |
|---|---|---|
| Backend | FastAPI / Python | Phase 2 |
| Frontend | Next.js + Tailwind | Phase 3 |
| PDF parsing | PyMuPDF (`fitz`) | ✅ Built |
| Embeddings | sentence-transformers / all-MiniLM-L6-v2 | ✅ Proven |
| Vector DB | ChromaDB | Phase 1 |
| SQL | SQLite | Phase 2 |
| Chat | Configurable external LLM provider | ✅ Proven |
| STT | Whisper-compatible API | ✅ Proven / real-audio test pending |
| Packaging | `pyproject.toml` + editable install | ✅ Done |
| Deployment | Vercel + Railway/Render or equivalent | Phase 5 |
| External automation | n8n | **Not currently required** |

Technology choices can change when evaluation or constraints justify the change.

The project constitution should record **why** a technology is chosen, not merely that it is currently popular.

---

## 11. Engineering Conventions

### 11.1 Environment

- Use a project virtual environment.
- Run development commands from the project root.
- Keep secrets in `.env`.
- Never commit API keys.

### 11.2 Dependencies

When adding a dependency:

1. install it in the active environment,
2. update the project's dependency definition,
3. verify the application still runs,
4. avoid unnecessary packages.

Do not treat `pip freeze` as the primary dependency definition. `pyproject.toml` is the source of truth; a generated `requirements.txt` may be maintained when useful.

### 11.3 Project structure

Prefer clear separation by responsibility:

```text
backend/
├── services/
│   ├── ingestion/
│   ├── retriever/
│   ├── llm_client/
│   ├── flashcards/
│   ├── scheduler/
│   └── coverage/
├── tests/
└── ...
```

### 11.4 Secrets and user data

`.gitignore` should cover at minimum:

```text
.env
venv/
__pycache__/
*.db
chroma/
data/
```

Lecture materials may be copyrighted and should not be committed to the repository unless explicitly appropriate.

### 11.5 AI-assisted development

The AI assistant acts as a pair-programming coach.

Default behavior:

1. explain the intended change,
2. give a hint or structure,
3. let the developer implement when the learning value is high,
4. review/debug the implementation,
5. write code directly when the task is mechanical or momentum is more valuable.

### 11.6 Defensible engineering

Every meaningful architectural decision should answer:

> **Why this approach instead of the obvious alternatives?**

If the answer is unclear, the decision is not sufficiently understood.

---

## 12. Decision Log

The decision log is **append-only**.

Do not rewrite history to make old decisions look perfect. If a decision changes, add a new decision explaining what changed and why.

| ID | Decision | Rationale | Status |
|---|---|---|---|
| D1 | Use cloud/free-tier AI instead of local chat LLM | Hardware is limited to 16 GB RAM without a GPU | Active |
| D2 | Use a provider-agnostic AI client | Providers/models can change or disappear | Active |
| D3 | Use role-based AI routing | Different tasks have different capability requirements | Active |
| D4 | Skip empty/image-only pages initially | Prevent unusable pages from polluting the retrieval corpus | Active |
| D5 | Extract slide titles separately | Sparse slides need contextual anchors for retrieval | Active |
| D6 | Use PDF page numbers as canonical page references | Printed slide numbering can differ from PDF numbering | Active |
| D7 | Accept imperfect table extraction initially | Improving table parsing is lower priority than core RAG | Active |
| D8 | Add OCR/vision later | Image recovery is valuable but not required for the initial RAG loop | Active |
| D9 | Use local MiniLM embeddings | Small, free, CPU-friendly, and already proven | Active |
| D10 | Use editable package installation | Avoid CWD-dependent imports and improve project structure | Active |
| D11 | Keep n8n out of the MVP core | External automation does not justify additional infrastructure yet | Active |

### Decision log rules

- New decisions become `D12`, `D13`, etc.
- Do not delete old decisions.
- If a decision is reversed, document the replacement.
- Record the reason, not only the conclusion.

---

## 13. Roadmap

The roadmap represents the intended progression, not an unchangeable contract.

| Phase | Deliverable | Status |
|---|---|---|
| **0** | Setup + feasibility: environment, AI, STT, embeddings | ✅ Done |
| **1** | Ingestion pipeline: parse → chunk → embed → retrieve | 🔨 In progress |
| ├─ M1 | PDF parsing, title extraction, footer cleanup, image-only detection | ✅ Done |
| ├─ M2 | Chunking with slide/title/page metadata | ⬅️ **Current** |
| ├─ M3 | Embedding + ChromaDB storage | ⬜ Next |
| └─ M4 | Retrieval + metadata/citation validation | ⬜ |
| **2** | FastAPI RAG endpoint + grounded streaming answers | ⬜ |
| **3** | Next.js frontend: upload, library, chat, citations | ⬜ |
| **4** | Persistence, errors, guardrails, UX polish | ⬜ |
| **5** | Deployment + README + demo | ⬜ **MVP line** |
| **6** | Lecture audio → notes + OCR fallback | ⬜ |
| **7** | Flashcards + SM-2 review loop | ⬜ |
| **8** | Study scheduling + calendar integration | ⬜ |
| **9** | Coverage dashboard + mock exam + vision recovery | ⬜ |
| **10** | Evaluation harness and retrieval benchmarks | ⬜ |
| **Future** | External automation with n8n, if integration complexity justifies it | 🅿️ Parked |

### Current position

> **Phase 1 / M2 — Chunking**

The next implementation goal is to build the chunking layer on top of the validated parser.

---

## 14. Known Limitations

This section is intentionally honest and should evolve with the project.

### Current

1. **Image-only slides are initially invisible.**  
   The golden deck contains 7/68 slides without useful extracted text.

2. **Table extraction can have poor reading order.**  
   Table content may be present but structurally messy.

3. **Diagram semantics are not fully captured.**  
   Extracted text may reference a diagram without describing its meaning.

4. **Free-tier APIs have rate limits.**  
   The architecture is appropriate for a single-user project, not a public production SLA.

5. **PDF footer thresholds are currently heuristic.**  
   Positional constants may need adaptation for different deck designs.

6. **Model behavior can vary by provider/model.**  
   Grounding and evaluation are required whenever the provider changes.

### Roadmap mitigations

- OCR for text embedded in images,
- vision models for diagram/image understanding,
- improved document-specific layout detection,
- retrieval evaluation,
- stronger refusal/grounding checks,
- provider fallback where practical.

---

## 15. Evaluation Strategy

StudyMate should eventually have a small reproducible evaluation set.

### Retrieval evaluation

Create at least 20 golden:

```text
question → expected relevant chunk/page
```

Measure:

- hit-rate@k,
- MRR,
- retrieval score distribution,
- off-topic retrieval behavior.

### Grounding evaluation

Test:

1. questions directly answered by the document,
2. questions requiring multiple chunks,
3. questions absent from the document,
4. ambiguous questions,
5. page citation correctness.

The desired behavior is not simply "answer everything."

The desired behavior is:

> **Answer when evidence exists, cite it, and refuse when the material does not support the answer.**

### Learning-system evaluation

When flashcards and scheduling exist, evaluate:

- SM-2 state transitions,
- due-date calculations,
- study-slot selection,
- coverage updates,
- calendar synchronization.

Deterministic components should have deterministic tests.

---

## 16. Golden Test Assets

Primary golden deck:

```text
data/DS-Lct01-IntroToDS.pdf
```

Properties:

- TF4507 Distributed Systems,
- 68 slides,
- approximately 61 text-bearing slides.

It is used for:

- ingestion development,
- chunking tests,
- retrieval experiments,
- future evaluation.

Diagnostic tool:

```text
backend/tests/diagnose_pdf.py
```

Use the diagnostic tool when introducing a new document parser behavior or changing layout assumptions.

---

## 17. Parked Items

These ideas are intentionally postponed rather than forgotten:

- n8n integration,
- OCR fallback,
- vision-based slide recovery,
- full Google OAuth/calendar integration,
- advanced table extraction,
- optional tokenization utilities,
- multi-user authentication,
- enterprise deployment,
- advanced agent orchestration.

A parked item should only become active when its value is clear relative to the current milestone.

---

## 18. Constitution Maintenance Rules

This document is a **living engineering constitution**, not a daily task list.

### Update this document when:

- the project's goal changes,
- a hard constraint changes,
- architecture changes,
- an important technical decision is made,
- a limitation is discovered,
- a roadmap phase is completed,
- a previously parked item becomes active.

### Do not update it for:

- every bug fix,
- every small refactor,
- temporary debugging information,
- trivial dependency changes,
- ordinary implementation details.

Those belong in code, issues, commits, or separate documentation.

### Source-of-truth hierarchy

When information conflicts, use this order:

1. **Project Constitution** — product direction and durable architectural decisions
2. **Architecture/design docs** — detailed subsystem decisions
3. **Code/tests** — actual implementation behavior
4. **Issues/tasks** — temporary or planned work
5. **Conversation history** — context, not authoritative project state

If code contradicts the constitution intentionally, update the constitution.

If code contradicts it accidentally, fix the code.

---

## 19. The North Star

StudyMate should remain a **study system, not merely an AI wrapper**.

The long-term experience should feel like:

```text
        ┌──────────────┐
        │ Study Material│
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │   RETRIEVE   │
        │ Understand   │
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │     QUIZ     │
        │ Practice     │
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │   SCHEDULE   │
        │ Plan review  │
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │    REVIEW    │
        │ SM-2 / recall│
        └──────┬───────┘
               │
               └──────────────► back to RETRIEVE
```

Every major feature should strengthen this loop.

If a proposed feature makes StudyMate more complicated without making this loop better, it should probably wait.

---

## Appendix — Current Repository Intent

The repository should remain understandable to a new developer.

At minimum, documentation should make these questions easy to answer:

- What is StudyMate?
- Why does it exist?
- How does the RAG pipeline work?
- Where is the application logic?
- Where are embeddings stored?
- Where is structured state stored?
- How are AI providers configured?
- What has already been proven?
- What is currently being built?
- What is intentionally postponed?
- How is retrieval quality measured?

The answer to those questions should not depend on remembering a previous chat session.
