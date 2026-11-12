# Reference verification — 2026-11-10/11 revision

Scope: all references in `OmissionShield_TDSC_REV_2026-11-10.tex` after Phase-2 additions. This supersedes the stale Sep-28 note that reported 16 references / 11 pages.

Status meanings: VERIFIED = current public record found and title/author/venue or arXiv identifier matched; VERIFIED-ARTIFACT = public artifact rather than formal publication; VERIFIED-SPRINT = explicitly a sprint/hackathon project, not a publication.

| Key | Record | Status | Verification basis / correction |
|---|---|---|---|
| costa2025fides | Costa et al., *Securing AI Agents with Information-Flow Control*, arXiv:2505.23643 | VERIFIED | Current arXiv record matches title/authors. |
| rajagopalan2026authenticated | Rajagopalan & Rao, *Authenticated Workflows: A Systems Approach to Protecting Agentic AI*, arXiv:2602.10465 | VERIFIED | Current arXiv record matches. |
| wang2026traces | Wang et al., *From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents*, arXiv:2606.04990 | VERIFIED | Current full arXiv page heading includes “A Survey of”; revised manuscript corrected the title. |
| santos2026cxi | Santos-Grueiro, *Context-to-Execution Integrity for LLM Agents*, arXiv:2607.06000 | VERIFIED | Current arXiv record matches. |
| rajan2026missing | Santhiya Rajan, Samuel Mugel, Roman Orus, *Where Facts Go Missing...*, arXiv:2607.22448v3 | VERIFIED-RESTORED | Live arXiv record checked 2026-11-11 shows v3 (submitted 24 Jul 2026; revised 19 Aug 2026) and explicitly lists `Santhiya Rajan, Samuel Mugel, Roman Orus` / `by Santhiya Rajan and 2 other authors`. The prior sole-author correction came from a secondary mirror and was wrong; the original three-author manuscript form is restored. |
| kemeklis2026omission | Kemeklis & Vemuri, *Omission Attacks: When Doing Nothing Is the Attack* | VERIFIED-SPRINT | Apart project page explicitly says “Submitted to AI Control Hackathon 2026” and “Sprint projects ... not Apart Research publications.” The official hackathon page gives the event dates as Mar. 20–22, 2026; bibliography corrected from Mar. 23 to Mar. 20–22. |
| zhang2026agate | Zhang et al., AGATE, arXiv:2609.30830 | VERIFIED | Current arXiv abstract confirms authorization/data-provenance gate, observed-source registration, three harness adapters, and observation coverage as a limit. |
| salas2026governed | Salas, *Correct Is Not Governed: Provenance Integrity in Agentic Workflows*, arXiv:2608.12761 | VERIFIED | Current arXiv abstract confirms Matrix causal-state layer, completion evidence, and completeness-contract transfer failure. |
| tracegrant2026 | Liao et al., TraceGrant, arXiv:2608.21126 | VERIFIED | Current arXiv abstract confirms trusted-user Contract, admitted evidence constrained by prior authority, and completion verified against tool results. |
| aidguard2026 | Tong, Dai, Guo, AID-Guard, arXiv:2608.21159 | VERIFIED | Current arXiv record matches. |
| koyuncu2023missingness | Koyuncu et al., KDD 2023, pp. 1164–1175 | VERIFIED | DBLP record confirms KDD 2023 pages; DOI retained from prior verification. |
| koyuncu2024tist | Koyuncu et al., *Adversarial Missingness Attacks on Causal Structure Learning*, TIST 15(6), Art. 119, 2024 | VERIFIED | DBLP confirms TIST 15(6):119:1–119:60. Added in Phase 2. |
| koyuncu2026remediation | Koyuncu et al., *Exploiting Missing Data Remediation Strategies Using Adversarial Missingness Attacks*, AAAI-26 | VERIFIED | Pages 22671–22678 were already confirmed from the live AAAI-26 issue page. Muse independently confirmed the DOI via the live Crossref record for `10.1609/aaai.v40i27.39428`, which matches the title, authors Deniz Koyuncu, Alex Gittens, Bülent Yener, and Moti Yung, Proceedings of the AAAI Conference on Artificial Intelligence, volume 40, pages 22671–22678, publication date 2026-03-14, and publisher Association for the Advancement of Artificial Intelligence. DOI restored in the manuscript; arXiv:2409.04407 remains cited as the extended version. |
| harikumar2026robust | Harikumar et al., *Robust Bayesian Decision Making under Adversarial Uncertainty*, UAI 2026, PMLR 337:1983–2007 | VERIFIED | PMLR record matches authors/title/pages. |
| guo2015necm | Guo & Sengur, NECM, Neural Computing and Applications 26(3):561–571 | VERIFIED | DBLP/Springer-indexed record matches. |
| chen2026enumerating | Chen et al., *Judging Is Not Enumerating...*, arXiv:2608.01000 | VERIFIED | Current arXiv record matches. |
| lee2017whynot | Lee, Koehler, Ludaescher, Glavic, ICDE 2017:485–496 | VERIFIED | Current DBLP record confirms title/authors/pages. DOI retained from prior verification. |
| lee2018pug | Lee, Ludaescher, Glavic, PUG, VLDB Journal 28(1):47–71 (2019) | VERIFIED | Current DBLP volume/author records match. Bib key remains historical-only; publication year in citation is 2019. |
| reis2021tqrg | Reis & Abreu, *A Ground-Truth Dataset of Real Security Patches*, arXiv:2110.09635 | VERIFIED | Current arXiv record matches title/authors and dataset counts. |
| secalertbench2026 | SecAlertBench public artifact | VERIFIED-ARTIFACT | Fresh clone HEAD `42a84889fda912ca432c994924a1ccd4b9df6274`; upstream data file SHA-256 equals local `33f95305d1c42f8e615e4f94066119570859dee7eb086dff7c2273536c932ea3`; no LICENSE/COPYING file found. No formal paper/arXiv/DOI is claimed. |
| debenedetti2024agentdojo | Debenedetti et al., AgentDojo, NeurIPS 2024 Datasets and Benchmarks Track, arXiv:2406.13352 | VERIFIED | NeurIPS proceedings and arXiv record match. |

## Count and manuscript status

- Revised bibliography entries: **21**.
- The prior Sep-28 verification note is stale and must not be used for this revision.
- SecAlertBench remains cited as a **public artifact**, not as a formal paper.
- No TIST DOI was added because the current verification established the journal record without requiring an unverified DOI.
