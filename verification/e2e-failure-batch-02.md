# E2E Failure Batch 02

This record freezes the second exact Studionet revision after live allocation consensus failures. It is evidence for the subsequent batch fix, not passing evidence.

- Frozen contract: `0x5Db7A793FA86629Bf14146C1eE9cb357f3eb9891`
- Frozen deploy transaction: `0x41d7816541f63768cad0ca9d752fa0c17eb8ef9c64ea2f1686b6465da17554eb`
- Frozen candidate before this batch fix: manifest `D36E5A6BB464287135EA50ACAB4721DCE8B76A438693BC8EE05DB3ECB92B7485`
- E2E-04/05/06 main allocation: `0x0b3b876880113773bffea30ecd1412fcff52a9bc07434fec644c1d29440ced6d`, `FINALIZED/SUCCESS` at the transaction layer but `UNDETERMINED` consensus after repeated leader rotation; leader proposed the expected `ALLOCATED` vector, validators disagreed, and no state committed (`hs-001` remained `LOCKED`).
- E2E-07 bad evidence allocation: `0x60d2a3f2f43415b67c9f13ba9ab3e6d1882242a280a63fd970f792612064c616`, `UNDETERMINED` because evidence failure was raised inside the nondeterministic execution; readback remained `LOCKED` with an empty roster.
- E2E-08 first unresolved allocation: `0x7f5762fdc8929f3c0b104397aeefbba8f188e8a06b2add3096b68ac2d4f4a86c`, `UNDETERMINED` after leader rotation; readback remained `LOCKED`.

## Root-cause classification

The valid eight-comment assessment produced the intended leader fields, but model validators disagreed on consequence-bearing fields under the unconstrained semantic prompt. Bad evidence raised before a canonical decision existed, so the consensus wrapper could not finalize an explicit fail-closed result. These are consensus convergence and error-normalization failures, not unauthorized state writes or digest mutation.

## Batch action

The candidate fix adds a fixed mechanical extraction rubric to the prompt so equivalent evidence yields stable fields, and converts bounded evidence transport or prompt-execution failures to a canonical `UNRESOLVED` vector inside the same consensus execution. Malformed structured output remains fail-closed. The existing retry fallback and immutable manifest behavior remain unchanged.
