# E2E Failure Batch 01

This record freezes the first exact Studionet revision after the live retry failure. It is evidence for the subsequent batch fix, not a passing scenario.

- Frozen manifest: `FD865F6EB7FBF52416EF6C9FB0195441646B628BE45A168A32AC31B014027F94`
- Contract: `0xD31B5A21037189Da928534BCA64dc7AAfcEd2BA4`
- Scenario: E2E-08 retry of an accepted `UNRESOLVED` assessment for `hs-unresolved`
- First allocation: `0x4711a9dde60b0826ae44653ce7c8f8abd4c2b197dfc4dc47d04d5b354be14b9d`, `FINALIZED/SUCCESS`, accepted `UNRESOLVED`
- Retry: `0x1d45348be05231b2429ba85bb832be079aa704adb972eca8d6d1c9150a256224`, `UNDETERMINED`, repeated validator disagreement and leader rotation
- Readback after retry: `lifecycle=4`, `assessment_version=1`, empty selected roster, locked evidence digest unchanged at `037655549aaec3b7962ed7f1f1d3aef82dede5f210eb9b3aa8f32f22557400e4`

## Root-cause classification

The retry re-fetched the same hash-bound public evidence independently for the leader and validators. The first assessment reached consensus, but the retry did not reach validator quorum after repeated leader rotation. No accepted retry state was written and the locked manifest remained unchanged. This is a consensus/re-fetch variance failure, not a lifecycle or digest-integrity failure.

## Batch action

The candidate fix retains the previously accepted `UNRESOLVED` decision vector and empty roster when a retry consensus call raises, while recording the new assessment version. Initial `LOCKED` assessments still propagate consensus, evidence, schema, and transport failures without fallback.
