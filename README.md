# Hearing Slot Coverage Allocator

Deterministically allocates up to three non-duplicate hearing comments by validator-agreed topic coverage.

## Live Deployment

- Network: GenLayer Studionet
- Chain ID: `61999`
- Contract: [`0xAb2E21C06B74C55659a7f58C45050058C99EFBF5`](https://explorer-studio.genlayer.com/address/0xAb2E21C06B74C55659a7f58C45050058C99EFBF5)
- Deployer: [`0xeF5D2119416A2f5afa35dCFA209766EFC1BE5902`](https://explorer-studio.genlayer.com/address/0xeF5D2119416A2f5afa35dCFA209766EFC1BE5902)
- Deployment transaction: [`0x39f1c31b40b0b93d36af81f673719035ff4c71391677dc8865efad9e7e2d352d`](https://explorer-studio.genlayer.com/tx/0x39f1c31b40b0b93d36af81f673719035ff4c71391677dc8865efad9e7e2d352d)
- Source revision: `CAF05E41FE856F1C2BB7767689E9677E6D6268BEA8CF21EECAF74EF94253260A`
- Full [Studionet E2E matrix](verification/e2e-matrix.md)

Evidence includes a successful consensus allocation ([receipt](https://explorer-studio.genlayer.com/tx/0x710b13fd7f9fc596a01e7ed4c3dbe91daef8134a9095641f4d88d0ce96905ea5)) and negative scenarios: ninth-comment rejection, invalid evidence producing `UNRESOLVED` ([receipt](https://explorer-studio.genlayer.com/tx/0x063a0fdc91d7aba88ab9b4faf754269d1194f2d6053c7f20ca8585cad2cde755)), retry versioning ([receipt](https://explorer-studio.genlayer.com/tx/0x03dbc8b377561a2c3ba4bd346f7abddf3c257f6ed6c138b03247368ca9e951b1)), and premature-close rollback.

## Problem and GenLayer Fit

Public-hearing organizers need a bounded, auditable coverage signal when evidence is public but semantic interpretation is not safely reducible to a single trusted backend. Validators independently retrieve hash-bound evidence and agree on the consequence-bearing fields before state changes.

GenLayer is useful here because independent validator execution makes the evidence interpretation reviewable and consensus-bound. A conventional backend is sufficient when one operator is trusted, evidence is already structured, or no independent semantic verification is needed. This contract does not rank merit, urgency, truth, legality, or representativeness.

## How It Works

`create_hearing -> add_comment (1..8) -> lock_comments -> allocate_slots -> read_allocation -> close_hearing`

The owner commits the taxonomy; any sender may submit bounded comments while the hearing is open. Each validator independently fetches HTTPS evidence, checks its SHA-256 digest, and derives `topic_mask`, `citation_present`, and `duplicate_cluster` using the fixed rubric. One `run_nondet_unsafe` call compares leader and validator consequence fields. The deterministic contract then excludes duplicate clusters and selects the roster by maximum topic coverage, then citation count, then lexicographic ID vector.

## State and Invariants

Lifecycle values are `OPEN`, `LOCKED`, `ALLOCATED`, `UNRESOLVED`, and `CLOSED`. The lock manifest is immutable. Allocation is permitted only once comments are locked; close is permitted only after `ALLOCATED`. `UNRESOLVED` always stores an empty roster and is not directly closable. A retry increments `assessment_version` without changing the locked manifest and preserves a previously accepted unresolved vector if the retry cannot reach consensus.

## Public API

- `create_hearing(hearing_id, taxonomy, taxonomy_sha256)` — owner-only initialization.
- `add_comment(hearing_id, comment_id, url, sha256, revision)` — bounded pre-lock intake; any sender may submit while open.
- `lock_comments(hearing_id)` — freezes the manifest.
- `allocate_slots(hearing_id)` — consensus-bound assessment and deterministic selection.
- `read_allocation(hearing_id)` — oracle view for observers and downstream integrations.
- `close_hearing(hearing_id)` — terminalizes the hearing after assessment.

Integrators should use `read_allocation` as the oracle view and treat `UNRESOLVED`, empty rosters, and non-finalized transactions as non-allocations.

## Consensus Design and Failure Behavior

The leader and validators independently fetch bounded HTTPS bodies and verify hashes. Fetched text is untrusted data; embedded instructions do not control contract behavior. The raw outer schema and field types are validated first; repeated-evidence fields are then canonicalized from the verified body before validator comparison and final storage. Unique evidence retains strict structured-output validation. Transport or prompt failures become consensus-checked `UNRESOLVED`; malformed output, zero-topic `ALLOCATED` output, and validator disagreement fail closed. No external side effect is performed.

### Consensus Binding Matrix

| Consequence field | Leader | Validators | State binding |
|---|---|---|---|
| `status` | Produces fixed-schema result | Independently re-fetch, derive, and compare | Determines `ALLOCATED` vs `UNRESOLVED` |
| `comment_id`, `topic_mask` | Reports each locked ID | Re-derives and compares normalized vector | Drives topic union |
| `citation_present` | Reports rubric result | Re-derives and compares | Citation tie-break |
| `duplicate_cluster` | Reports normalized token | Re-derives and compares | Duplicate exclusion |
| roster | Not trusted from model | Not trusted from model | Deterministically selected by contract |

## Security and Edge Cases

Authorization, ID/type/range checks, eight-comment intake bounds, HTTPS-only evidence, bounded bodies, SHA-256 binding, immutable manifests, strict output validation, and fail-closed disagreement handling are enforced. Empty, separator-only, whitespace-only, malformed, unavailable, duplicate, and mutated evidence paths are covered by tests or the live E2E matrix.

## Verification

```powershell
$env:PYTHONIOENCODING='utf-8'
genvm-lint check contracts/hearing_slot_coverage_allocator.py
pytest -q -W error tests
python -m pip check
python -m py_compile contracts/hearing_slot_coverage_allocator.py
```

The exact local result is `21 passed`; lint/validation, dependency checks, and compilation also pass. The matrix records finalized Studionet receipts and authoritative readbacks for E2E-01 through E2E-10.

## Consensus Engineering Lessons

- Bind every fetched body to an expected digest before semantic interpretation.
- Treat validator output as untrusted until the contract normalizes and compares every consequence-bearing field.
- Keep roster selection deterministic and inside the contract; never accept an LLM-generated roster.
- Model transport failure as an explicit unresolved state instead of a false allocation.
- Keep `ACCEPTED` distinct from `FINALIZED` when downstream systems consume evidence.

## Reusable Integrations

1. Public-comment intake dashboards can display the `read_allocation` oracle view without owning consensus logic.
2. Evidence registries can reuse the lock-manifest, digest-bound retrieval pattern for bounded public records.
3. Hearing or grant workflows can adapt the deterministic set-cover selector while preserving an organizer-controlled taxonomy.

## Limitations

This is a coverage signal, not a judgment of importance or representation. Taxonomy quality remains organizer-controlled. Evidence must be public-safe, bounded, retrievable, and hash-stable. There is no frontend, payment, notification, or real-world actuation layer.

## Repository Structure

```text
contracts/hearing_slot_coverage_allocator.py   contract
tests/direct/                                  Direct Mode tests
tests/integration/                            integration checks
verification/e2e-matrix.md                    live evidence matrix
verification/e2e-failure-batch-01..05.md      frozen failure records
STAGE1.md / STAGE2.md                          approved design baseline
SPECIFICATION.md                               storage and state specification
requirements.txt                               dependencies
LICENSE                                        MIT license
```

## License

MIT; see [LICENSE](LICENSE).
