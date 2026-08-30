# E2E Failure Batch 04

This record freezes the fourth exact Studionet revision after the unresolved-evidence allocation failure. It is evidence for the subsequent batch fix, not passing evidence.

- Frozen contract: `0x25524a58432b83f947B9dF69d834391242c0FbDd`
- Frozen deploy transaction: `0xb9354233764849709743e564c586e08c0d7ae2869fbe078ecc015e87e1837d83`
- Frozen candidate manifest: `55088CCBE774B88C17A98564C92633E5A79454F3045403EF31BEDE55AC690E43`
- E2E-08 unresolved allocation: `0x0b9a361b9e01e9bea08f371fe6b84bc6f5fcc641a97a38e9820ce219147bc264`, finalized `ERROR` with consensus `UNDETERMINED` after leader rotation. Validator receipts reported `[rollback] allocated comments require a topic`; other validator receipts also reported `[rollback] decision vector order mismatch`.
- Authoritative state after failure: `hs-unresolved` remained `LOCKED` (lifecycle `2`), assessment version `1`, empty decision vector and empty selected roster, evidence digest `3617707303ed22d6005aee2da7a3bc62eaaed70db40fe381e56ab202a1a7ac50`.
- Independent safe scenarios on the same frozen revision: main allocation `0x5431960857c486c4139d39bcbbb47735bd0bcc5e3c91919b8731274cd34f8ff2` finalized and read back `ALLOCATED`; main close `0x6aa4003b39a15c03ca3a9ff4c0dc636ff0c2884ad5040c07f33e65828ee18386` finalized and read back `CLOSED`; premature close `0xa4651e8847b302afb5a017ba079c3265fd99b930c837bc072e7858a33a3fe548` finalized as an expected error and `hs-bad` read back `LOCKED`.

## Root-cause classification

For unique evidence whose body did not establish a taxonomy topic, validators sometimes returned a structurally valid `ALLOCATED` vector with `topic_mask=0`. Strict semantic validation raised `allocated comments require a topic` inside consensus, so the transaction could not commit the intended retryable `UNRESOLVED` state. This was an output-normalization gap, not an evidence transport failure.

## Batch action

Canonicalize a structurally valid `ALLOCATED` vector containing any zero-topic comment to `UNRESOLVED` before validator consequence comparison and final storage. Preserve strict outer schema, IDs, types, bounds, duplicate-cluster rules, malformed-output rollback, independent evidence verification, and one consensus execution.
