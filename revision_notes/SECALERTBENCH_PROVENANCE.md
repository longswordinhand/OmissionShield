# SecAlertBench provenance pin

## Local artifact

Local file:
`data/public/secalertbench/secalertbench.json`

`data/public/secalertbench/SHA256SUMS.txt` records:
`33f95305d1c42f8e615e4f94066119570859dee7eb086dff7c2273536c932ea3`

Independent `sha256sum` of the local file on 2026-11-10/11:
`33f95305d1c42f8e615e4f94066119570859dee7eb086dff7c2273536c932ea3`

Result: **MATCH**.

## Upstream pin and fresh-clone verification

Upstream repository:
`https://github.com/Dxsssu/SecAlertBench.git`

Fresh clone performed to `/tmp/secalertbench_phase1` on 2026-11-10/11.

Fresh-clone HEAD:
`42a84889fda912ca432c994924a1ccd4b9df6274`

Fresh-clone data file:
`0x02. Processed SecAlertBench Dataset/secalertbench.json`

Fresh-clone data SHA-256:
`33f95305d1c42f8e615e4f94066119570859dee7eb086dff7c2273536c932ea3`

Therefore the local experiment file is byte-identical to the data file at the current upstream HEAD `42a84889fda912ca432c994924a1ccd4b9df6274`.

## Retrieval/download date

Exact historical download date: **UNRECOVERABLE** from a provenance record.

The local file mtime is `2026-08-25 13:17:42 -0500`, and `SHA256SUMS.txt` has nearly the same mtime. This is consistent with local acquisition/checksum creation on Aug. 25, 2026, but mtime is not treated as proof of the download date.

## License status

A fresh-clone search found **no `LICENSE*` or `COPYING*` file** in the repository. Therefore no redistribution license is assumed. The final reproducibility package should pin the upstream URL/commit/hash and should not redistribute the dataset unless permission/license status is resolved.
