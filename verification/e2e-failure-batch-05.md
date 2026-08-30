# E2E Failure Batch 05

This record freezes the exact Studionet revision after the first live attempt to exercise retryable `UNRESOLVED` through an unavailable-evidence transport path. It is evidence for the subsequent minimal correction, not passing evidence.

- Frozen contract: `0x9Dfb097F5cb9ad1958ddd058F8a863bA372E67B5`
- Frozen deploy transaction: `0x697b5605c9da4907762caf39d2adf9a61b01ff984759056dc565f14f6a6cb0fe`
- Frozen candidate manifest: `36A4A13BC31348CCEB7A4EB47AED6B58E8E1E4131B998DEFF1A0AAD646251C37`
- Ambiguous unique-evidence allocation: `0x82f8ae8c5dec39569091371ccefcece6a77c2a2e062462e6c6cf2eee086c3cf3`, finalized `ERROR` with `UNDETERMINED`; validator receipts reported `[rollback] allocated comments require a topic` and `[rollback] decision vector order mismatch`.
- Unavailable-evidence allocation: `0x439bbeb609d250e4a3d0946f22e0bed67ba3a6c721735353dcf5e92b53c346f9`, finalized `ERROR` with `UNDETERMINED`; the leader trace shows `genlayer.gl.nondet.NondetException` with `TLD_FORBIDDEN` for `https://example.invalid/hearing-evidence`.

## Root-cause classification

The bounded evidence and prompt failure handlers used `except Exception`. The Studionet nondeterministic web layer raises `NondetException` outside that hierarchy, so the intended canonical `UNRESOLVED` fallback was bypassed and the transaction exited before consensus.

## Batch action

Broaden only the two `_fetch_and_assess` failure boundaries to `except BaseException`, preserving strict malformed-output validation, validator consequence comparison, immutable manifests, and retry/version semantics. Local Direct Mode and all existing regression gates must pass before a new exact revision is eligible for PRE-DEPLOY.
