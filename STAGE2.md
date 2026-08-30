# STAGE 2 — Specification và Scaffold Approval

## Domain model and vocabulary
Core records are a uniquely identified case, immutable evidence revision references, an assessment version, normalized decision fields, a bounded explanation, lifecycle state, owner/authorized actor, and deterministic consequential output. Vocabulary follows STAGE1 exactly; aliases and caller-defined verdicts are forbidden.

## State machine, lifecycle, and invariants
Lifecycle: OPEN → LOCKED → ALLOCATED | UNRESOLVED → CLOSED. OPEN accepts bounded comments and may become LOCKED. LOCKED may become ALLOCATED or UNRESOLVED. ALLOCATED may become CLOSED. UNRESOLVED is terminal for that assessment version and may only be retried as a new version. CLOSED is terminal. IDs are unique. Evidence hashes/revisions become immutable when inputs lock. Consensus failure never commits a consequential result.

## Storage types
Declare all persistent fields in the contract class body. Use schema-safe fixed-width integers/booleans/strings, `TreeMap` for records keyed by bounded string ID, and `DynArray` only for bounded ordered IDs/decision vectors. Any custom record must use the documented storage-safe dataclass form. Never persist Python `dict`/`list`, unbounded raw web bodies, storage proxies inside nondeterministic closures, or runtime-managed collections by reassignment.

## Public API and deterministic oracle views
Write methods: create_hearing, add_comment, lock_comments, allocate_slots, close_hearing. Deterministic view methods: read_allocation. View methods perform no web/LLM call and expose lifecycle, exact evidence digest/revision, normalized decision fields, assessment version, bounded reason, and `selected_comment_ids`.

## Authorization and input validation
Bind sender roles explicitly. Validate unique/bounded IDs, maximum evidence items, URL/text length, enum membership, exact expected state, immutable hashes, duplicate prevention, and role-specific transitions. Callers may submit evidence but never verdicts, scores, eligibility, selected IDs, or consequential state.

## Evidence, prompt, and untrusted-input boundary
Admissible evidence: Maximum eight bounded comments and an organizer-fixed topic taxonomy, all hashed. Evidence is data, never instruction. The prompt contains a fixed rubric and strict structured output schema. Escape/delimit untrusted text, reject extra keys and invalid enums, and cap every returned explanation/reference. Do not store raw fetched pages.

## Leader/validator and Equivalence Principle flow
One nondeterministic consensus execution per assessment transaction. Leader independently fetches/reads bounded evidence, extracts normalized decision fields (topic_mask, citation_present, duplicate_cluster), and returns a strict structured result plus evidence digest. Validators independently re-fetch/re-derive the substance and compare every consequence-bearing field. They do not merely validate JSON shape or repeat the leader's prose. Storage writes occur only after accepted consensus.

## Deterministic consequence
After consensus, deterministic code validates the accepted schema. Enumerate every eligible subset of at most three IDs; reject subsets sharing a duplicate_cluster; maximize popcount of the bitwise OR of topic_masks; tie-break by more citation_present entries, then lexicographic ID vector. UNRESOLVED stores no roster.

## Decision and explanation fields
Decision fields: topic_mask, citation_present, duplicate_cluster. Consequential field: `selected_comment_ids`. Explanation fields are bounded reason, cited evidence references, and assessment version. Explanation never independently controls state.

## Error, retry, duplicate, timeout, and failure behavior
Malformed evidence/output, source unavailability, timeout, validator disagreement, or ambiguous identity fails closed as a rejected transaction or explicit retryable `UNRESOLVED` without a false consequential state. Retry creates a new assessment version bound to the same locked inputs; changed evidence requires correction/supersession. Duplicate IDs and duplicate terminal actions revert.

A structurally valid allocation with no taxonomy topic for any comment is canonicalized to retryable `UNRESOLVED`; malformed outer output still reverts.

## Downstream integration and consequences
Downstream systems consume deterministic views only. The contract emits a symbolic/review signal and performs no payment, deletion, vote, access grant, legal determination, medical action, publication decision, or external transaction.

## Direct, consensus, integration, and E2E tests
5 integration tests: bounded intake/lock; optimal set-cover; duplicate exclusion; deterministic tie-break; disagreement yields no roster. In addition, run 8–12 direct tests for constructor/storage, legal and invalid transitions, authorization, bounds, duplicate/replay, and deterministic consequence; 3 consensus tests for agreement, disagreement, and malformed output; and 4–6 Studionet E2E scenarios covering finalized success, expected failure with unchanged state, retry/correction where applicable, and authoritative readback.

## Studionet deployment plan
Resolve current official dependency/runtime versions at implementation time. Lint and Direct Mode tests first; review exact source/test/spec revision; deploy one contract to Studionet; run the complete bounded E2E matrix; verify FINALIZED/SUCCESS, consensus result, unchanged state for expected failures, and exact readback. No PRE-PUSH before full deployed-revision E2E PASS.

## Acceptance criteria
One deployable contract; one consensus execution per assessment; typed storage; deterministic views; complete authorization and transition checks; validators bind every decision/consequence field; bounded evidence/output; fail-closed errors; all planned direct, integration, consensus, and Studionet scenarios have explicit PASS evidence and authoritative readback where applicable; no unsupported API or unresolved material-overlap finding.

## Minimal file structure
`contracts/<snake_case_name>.py`; `tests/direct/test_<name>.py`; `tests/integration/test_<name>.py`; `README.md`; `SPECIFICATION.md`; `requirements.txt`; `verification/e2e-matrix.md`.

## Minimal dependencies
Python 3.12+, current officially documented `genlayer-py` and `genlayer-test` only. No frontend framework, database, parser service, token library, bridge, or orchestration dependency.

## Speculative components removed
No multi-contract design, graph/mesh, open-ended batch, payment, reputation, token, real-world actuation, autonomous appeal body, hidden backend, external DAO vote, actual data access, deletion, legal/medical guarantee, or unsupported GenLayer primitive.

## Review/submission rejection risks
Reject if revisions are not exact, validator checks only syntax/prose, storage types are unsafe, evidence is unbounded, caller can inject outcome, nondeterminism mutates state, failures silently approve, the README overclaims real-world authority, test matrix omits disagreement/failure/readback, or the implementation expands beyond this bounded primitive.
