# STAGE 1 — Project Intake và GenLayer-Fit Validation

## Objective and trust problem
Construct a symbolic hearing roster that maximizes topic coverage across a small locked comment set.

Trust problem: A unilateral organizer can choose speakers without verifiable representational coverage or duplicate exclusion.

## Intended users and downstream integrations
Organizer, commenters, public observer. Downstream integrations consume deterministic read methods and the `selected_comment_ids` signal only.

## Required scope
One small Intelligent Contract; 3 actors; one bounded assessment transaction; immutable evidence revision binding; explicit lifecycle; deterministic readback; one independently validated consequential field.

## Out of scope
Frontend, payments, tokens, cross-contract calls, hidden databases, external orchestration, real-world actuation, private/sensitive data, legal/medical/scientific truth guarantees, and any mechanism not confirmed by current official GenLayer documentation.

## GenLayer fit
GenLayer is necessary because the core decision requires semantic interpretation of unstructured, revision-bound evidence that deterministic code alone cannot reliably resolve. Ordinary deterministic checks handle identity, bounds, lifecycle, hashes, and post-consensus consequences.

## Why nondeterministic consensus is necessary
A leader must extract topic_mask, citation_present, duplicate_cluster from the evidence; validators independently re-fetch/re-derive those same consequence-bearing fields. Majority acceptance creates a neutral receipt where no single submitter, administrator, or model controls the result.

## Evidence boundary
Maximum eight bounded comments and an organizer-fixed topic taxonomy, all hashed. Evidence is public or public-safe, bounded, immutable by hash/revision after locking, and treated as untrusted data. No hidden account, private document, mutable screenshot, or uncited model knowledge may determine the outcome.

## Reusable primitive
Bounded set-cover roster construction.

## Originality and differentiation
Closest existing material: Public Comment Hearing Allocator and other allocation boards.

Overlap: semantic evidence interpretation, consensus-bound normalized decisions, and persistent lifecycle receipts.

Material difference: Nondeterminism derives incidence fields only; deterministic exhaustive set-cover maximizes topic-union coverage under duplicate-cluster exclusion, not merit or urgency ranking.

## Actors
Organizer, commenters, public observer. Actor count: 3. Authority is limited to submission, locking, acknowledgement/correction, or deterministic downstream reading; no actor can inject the verdict.

## State machine and transitions
OPEN accepts bounded comments and may become LOCKED. LOCKED may become ALLOCATED or UNRESOLVED. ALLOCATED may become CLOSED. UNRESOLVED is terminal for that assessment version and may only be retried as a new version. CLOSED is terminal.

## Contract surface/public methods
create_hearing, add_comment, lock_comments, allocate_slots, close_hearing, read_allocation.

## Storage data
Record owner/authorized actors, lifecycle enum, exact evidence URLs/hashes/revisions, bounded evidence IDs, assessment version, normalized decision fields, bounded reason/references, timestamps/counters where deterministic, and `selected_comment_ids`. Use documented typed storage only.

## Decision and consequential fields
Decision fields: topic_mask, citation_present, duplicate_cluster. Consequential field: `selected_comment_ids`. Explanations are non-authoritative and cannot alter state.

## Validator-state binding feasibility
High. Validators compare a finite schema of enums, booleans, bounded masks/counts/IDs, and evidence digest. Accepted fields map through a fixed deterministic rule to the consequential state. Disagreement or malformed output cannot commit an approving state.

## Nondeterministic/consensus flow
Exactly one nondeterministic consensus execution per assessment write. Fetch/extract/semantic comparison occurs inside the documented leader/validator wrapper. Storage reads needed by the assessment are copied to memory before entry. Contract calls, events, storage writes, and consequential computation occur outside the nondeterministic block.

## Validator-verifiable evidence
Validators can independently retrieve or inspect Maximum eight bounded comments and an organizer-fixed topic taxonomy, all hashed. They verify exact revision identity, substance of each decision field, evidence digest, and boundary compliance; they do not validate only response syntax.

## Workflow
Create hearing → add at most eight comments → lock set → derive incidence fields by consensus → run deterministic set-cover allocation → close only an ALLOCATED hearing.

## Downstream integration/reuse pattern
Any builder can read `selected_comment_ids` plus decision version/evidence digest as a fail-closed gate in an off-chain workflow. No integration must trust explanatory prose.

## Edge cases
Missing/malformed evidence, identity mismatch, duplicate ID, stale or changed revision, unauthorized sender, invalid transition, oversized input, conflicting sources, ambiguous text, timeout, unavailable URL, malformed model output, validator disagreement, duplicate/replay action, correction after terminal state.

## Risks
Primary risks are semantic disagreement, mutable web sources, storage serialization, prompt injection, overclaiming authority, RPC quota, and an incomplete negative matrix. Controls are exact hashes, bounded inputs/outputs, typed storage, independent validator substance checks, one nondeterministic call, fail-closed outcomes, and explicit limitations.

## Complexity and feasibility
One contract; 3 actors; one nondeterministic call per assessment; dependencies limited to current `genlayer-py`/`genlayer-test`. 5 integration tests: bounded intake/lock; optimal set-cover; duplicate exclusion; deterministic tie-break; disagreement yields no roster. Studionet feasibility is high because there is no cross-contract call, payment, browser automation, EVM dependency, graph, or unbounded batch.

## Duplicate/lightweight/learning-exercise risk
The project is acceptable only while preserving the material difference above and the consequential lifecycle. It becomes duplicate/lightweight if reduced to a generic LLM label, if only names/fields change, if the consequential field is not validator-bound, or if removed speculative orchestration is reintroduced.

## Conclusion
**KEEP — research/specification approved baseline.** This conclusion is bound to this exact Stage 1/2 scope and must be re-reviewed if the trust problem, mechanism, evidence pair, decision vector, lifecycle, API, or consequence changes materially.
