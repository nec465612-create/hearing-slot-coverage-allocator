# E2E Failure Batch 03

This record freezes the third exact Studionet revision after the live allocation consensus failure. It is evidence for the subsequent batch fix, not passing evidence.

- Frozen contract: `0x644eFd07AEe5E27182103f2c8017B7777667F037`
- Frozen deploy transaction: `0x6a47f656e8daab7aa500ffed67ac118d4f1ba2e97903ff565f865d2122ee3adc`
- Frozen candidate before this batch fix: manifest `34373B682A090CF956D70136ACCDB4D7E92137673022BDCF74DD341C666337CF`
- E2E-04/05/06 main allocation: `0xd863dbb1df84bc9eafb8892c9973d94f19752c2c2787c3e38938dc7f06cf9911`, transaction `UNDETERMINED` after repeated leader rotation; the leader produced the expected fields, but validator disagreement remained.
- Authoritative state after failure: `hs-001` remained `LOCKED`, assessment version 1, empty decision vector and empty selected roster, locked digest `4396478eae004987467c80f89e96aaa75db626132848db102d18306afd90cf9a`.

## Root-cause classification

The prompt-only mechanical rubric did not guarantee identical validator outputs. The live receipt showed an `ALLOCATED` leader proposal with repeated validator `Disagree` outcomes, so the consensus wrapper correctly refused to commit a consequential roster.

## Batch action

The candidate fix retains strict schema validation and the one consensus execution, but for evidence sets containing repeated SHA-256 bodies it canonicalizes topic masks, citation flags, and duplicate clusters from the independently fetched, hash-verified bodies. Unique-evidence assessments continue using the validated model fields. This targets the exact repeated-evidence set-cover case without weakening malformed-output or disagreement fail-closed behavior.
