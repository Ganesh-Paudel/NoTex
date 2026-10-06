# Live preview implementation plan

## First milestone

Build a local browser editor that shows notes beside the last successful PDF, reports syntax errors at their original line and column, and refreshes after editing pauses. Start with one document and one local session. Use the existing parser and renderer so CLI output and preview output agree.

The present foundation already provides:

- `convert_source(source)` returning parsed expressions and a LaTeX snapshot without writing files.
- `ParseError.as_dict()` returning structured source diagnostics.
- `compile_pdf(latex, timeout=...)` returning PDF bytes and a log from a temporary build directory.
- Atomic publication and path-alias checks for explicit save/export actions.

No watcher, HTTP service, build scheduler, or preview UI is implemented yet.

## 1. Build the scheduler before the interface

Add `preview/scheduler.py` with a monotonically increasing revision for each source snapshot. Debounce edits for about 300 ms. Allow at most one active PDF build and one pending snapshot; new edits replace the pending snapshot. Parsing is fast and should report diagnostics before starting LaTeX.

Every result must retain its revision. Publish a result only if it matches the current revision, so a slower older build cannot replace a newer preview. The current compiler is synchronous; run it off the HTTP request thread. Initially let an active build finish or hit its timeout and discard stale results. Add explicit process cancellation later if measurements justify it; cancellation must terminate and reap the compiler process and clean temporary files.

Represent states explicitly: `idle`, `debouncing`, `building`, `ready`, and `error`. Keep the last successful PDF available while editing invalid input. Include the PDF's revision so the UI labels it as the last successful build instead of implying it matches the current text.

Test rapid edits, out-of-order completion, syntax errors, compile errors, timeout, session shutdown, and bounded queue size without requiring a browser.

## 2. Add a local transport

Create an optional preview dependency group and a command such as `notex preview notes.txt`. Choose the HTTP framework when implementing this module; the existing converter should remain dependency-free. Bind to `127.0.0.1` by default. The service owns document IDs and build IDs rather than accepting arbitrary filesystem paths from browser requests.

Proposed API:

| Endpoint | Behavior |
| --- | --- |
| `POST /api/sessions/{id}/source` | Submit a source snapshot and return its revision. |
| `GET /api/sessions/{id}/status` | Return current revision, build state, diagnostics, and last successful PDF revision. |
| `GET /api/sessions/{id}/events` | Stream state changes using server-sent events; polling is an initial alternative. |
| `GET /api/sessions/{id}/pdf/{revision}` | Serve an immutable completed PDF for the requested revision. |
| `POST /api/sessions/{id}/save` | Explicitly save the current notes to the already selected document path. |

Use a startup/session token and validate browser origins so unrelated websites cannot control a local service. Bound source size, sessions, queued builds, and retained artifacts. Restrict templates to configured trusted files; accepting arbitrary uploaded TeX requires a separate compiler sandbox with filesystem, network, resource, and process restrictions. A temporary directory and `-no-shell-escape` are useful controls but do not provide that sandbox.

## 3. Build the editor and PDF pane

Start with a textarea, a PDF pane using the browser's PDF viewer, a status indicator, and a diagnostic list. Use revision-specific PDF URLs to avoid serving stale cached content. Preserve the last PDF through syntax errors and show which revision it represents. Keep source saves explicit initially, with a visible unsaved state.

Add a richer code editor, syntax highlighting, and completion after the full edit-to-build flow works. Generate keyword completion from the loaded template registry rather than duplicating box/style names in JavaScript. Translate Python code-point offsets to the browser/editor's UTF-16 positions when highlighting diagnostics.

Add browser tests for typing valid notes, introducing and fixing an error, receiving an older build, saving, and exporting a PDF. Parse diagnostics can point to notes directly; LaTeX errors should show the compiler log until generated-to-source mapping is implemented.

## 4. Add watching and cache invalidation

Watch the selected source and template files when supporting edits from another editor. Include template dependencies in invalidation, normalize file-replacement events from editor saves, and avoid watching the generated outputs. Browser edits and disk edits need a conflict policy; never silently overwrite unsaved browser text when an external edit arrives.

Cache successful PDFs by source content, template contents, converter version, and compiler configuration/version. Bound cache storage and expire artifacts after sessions close. Rebuild on template or compiler changes even when the notes text has not changed. Measure parse time, queue wait, compile time, and total edit-to-preview latency before introducing partial document rendering.

[Latexmk](https://ctan.org/pkg/latexmk) can automate multi-pass compilation and watch LaTeX dependencies. Its watch mode alone does not watch or convert NoteX's `notes.txt`; a NoteX scheduler or source watcher is still required. Consider using it in the compiler backend when adding cross-references, tables of contents, or persistent dependency-aware builds.

## Acceptance criteria for the first release

- Edits produce the same PDF as a CLI conversion of the same source and templates.
- Invalid input reports the original location and retains the last good preview.
- A stale result can never replace the current preview.
- At most one active build and one latest pending snapshot exist per session.
- Compilation hangs reach a timeout and the editor remains responsive.
- Source notes change on disk only through an explicit save action.
- Shutdown cleans build processes and temporary artifacts.
- The local service exposes no arbitrary-file read/write or template-execution API.
- Runtime and build latency are measured and documented on the supported test environment.

Start implementation with scheduler tests, then connect the local transport and browser. This makes the hard concurrency behavior reviewable before UI work.
