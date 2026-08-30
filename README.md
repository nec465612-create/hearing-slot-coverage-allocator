# Hearing Slot Coverage Allocator

## Purpose

`HearingSlotCoverageAllocator` is a small GenLayer Intelligent Contract for a bounded symbolic hearing roster. It converts locked public comments into validator-agreed topic incidence, citation presence and duplicate-cluster fields, then deterministically selects up to three non-duplicate comments with maximum topic coverage. It is a coverage signal only; it does not rank merit, urgency, truth, legality or representativeness.

## Workflow

`create_hearing -> add_comment (1..8) -> lock_comments -> allocate_slots -> read_allocation -> close_hearing`.

Only the owner controls the lifecycle. Commenters submit evidence before lock. A public observer or downstream integration reads only the deterministic result. Consensus `UNRESOLVED` keeps the roster empty; calling `allocate_slots` again creates a new assessment version over the same locked inputs.

## Consensus engineering

One allocation write performs one `run_nondet_unsafe` execution. The leader and each validator independently fetch every bounded HTTPS body, verify its SHA-256 digest, and derive the exact structured fields `topic_mask`, `citation_present` and `duplicate_cluster` with a fixed mechanical rubric. The contract canonicalizes returned comment vectors by the locked comment IDs and normalizes bounded cluster-token separators before comparing validator consequences. When hash-bound evidence bodies repeat, the contract derives the three fields from those independently verified bodies so duplicate evidence cannot create model-specific consequence variance; unique evidence retains the validated model fields. The deterministic contract computes `selected_comment_ids` only after accepted consensus. Evidence transport or prompt-execution failures become a consensus-checked `UNRESOLVED` vector with no roster; malformed structured output and validator disagreement fail closed. The lock-time evidence manifest is immutable across `UNRESOLVED` retries; retries version the assessment separately. A retry that cannot reach consensus retains the prior accepted `UNRESOLVED` vector while still recording the new assessment version.

An otherwise well-formed `ALLOCATED` result with a zero-topic comment is canonicalized to `UNRESOLVED`; malformed structured output and validator disagreement still fail closed.

## Local verification

```powershell
genvm-lint check contracts/hearing_slot_coverage_allocator.py
pytest -q
```

## Limitations

The contract records a reviewable symbolic allocation, not a claim that selected comments are the most important or representative. Taxonomy design remains an organizer-controlled input and is therefore committed, hash-bound and publicly readable. Evidence must be public-safe, bounded and retrievable by validators. No frontend or real-world actuation is included.

See [SPECIFICATION.md](SPECIFICATION.md) for storage, state, validation and deterministic selection details.
