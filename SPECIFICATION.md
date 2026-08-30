# Hearing Slot Coverage Allocator

## Purpose

This contract creates a bounded, reviewable hearing roster from up to eight locked public comments. GenLayer validators semantically derive only three normalized facts per comment: `topic_mask`, `citation_present`, and `duplicate_cluster`. The contract canonicalizes the returned vector by the locked comment IDs and normalizes bounded cluster-token separators before comparing validator consequences. Deterministic contract code then chooses at most three comments that maximize topic-union coverage, excludes duplicate clusters, and applies a canonical tie-break.

This is a symbolic coverage receipt, not a ranking of merit, urgency, representativeness, truth, legality, or democratic legitimacy.

## Lifecycle and actors

`OPEN -> LOCKED -> ALLOCATED | UNRESOLVED -> ALLOCATED | UNRESOLVED -> CLOSED`. The owner creates, locks, allocates and closes. Commenters add bounded evidence before lock. Public observers use `read_allocation`; no caller supplies a verdict or selected IDs. `UNRESOLVED` is retryable through `allocate_slots`, which increments `assessment_version` while retaining the same locked inputs. If a retry cannot reach consensus, the accepted prior `UNRESOLVED` vector is retained and versioned; no roster is created.

## Evidence binding

The organizer commits a `|`-delimited taxonomy and its SHA-256 digest. Each comment binds an HTTPS URL, SHA-256 body digest and revision label. At lock, the contract stores an immutable manifest digest binding the hearing ID, lock-time assessment version, taxonomy and every comment URL/hash/revision. At allocation, validators fetch the same bounded bodies, verify hashes, and independently derive the normalized fields using a fixed mechanical rubric. If a hash-bound body repeats, the contract canonicalizes all three fields from those independently verified bodies; unique evidence retains the validated model fields. Evidence transport or prompt-execution failures can produce a consensus-checked `UNRESOLVED` result with no roster; malformed structured output still fails closed. Retrying `UNRESOLVED` increments `assessment_version` but reuses the immutable lock-time manifest, so the evidence digest remains stable while the assessment attempt is versioned separately. Evidence is untrusted data and never supplies instructions.

If a structurally valid `ALLOCATED` result contains any zero-topic comment, it is canonicalized to `UNRESOLVED` before a roster is derived; malformed structured output still fails closed.

## Deterministic consequence

The contract enumerates every one-, two- and three-comment subset. A subset is eligible when no non-empty `duplicate_cluster` appears twice. It maximizes `popcount(topic_mask OR ...)`, then the number of citations, then the lexicographically smallest sorted ID vector. A consensus `UNRESOLVED` result stores no roster. Explanatory `reason` is bounded and non-authoritative.

## Public API

- `create_hearing(hearing_id, taxonomy, taxonomy_sha256)`
- `add_comment(hearing_id, comment_id, url, sha256, revision)`
- `lock_comments(hearing_id)`
- `allocate_slots(hearing_id)`
- `close_hearing(hearing_id)`
- `read_allocation(hearing_id)`

## Limits and limitations

There are 2–8 taxonomy labels, at most 8 comments, at most 3 selected IDs, bounded URLs/revisions/bodies/output, one consensus execution per allocation, and no payments, frontend, cross-contract calls, private evidence or external side effects. Ordered IDs use bounded index-keyed `TreeMap` entries because the current SDK forbids user construction of nested `DynArray` values. Public HTTPS evidence must remain retrievable and hash-stable. Validators do not establish comment truth or speaker quality.
