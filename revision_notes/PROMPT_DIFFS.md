# Prompt and decoding protocol differences

All prompt text below is transcribed from the executed source files; braces such as `{filename}`, `{patch}`, `{case.task}`, and `{body}` denote runtime substitutions performed by the code.

## Protocol table

| Script / experiment | Exact prompt construction | Backend / decoding | Batch |
|---|---|---|---:|
| `src/tqrg_llm_eval.py` (Qwen3/Ollama, Git) | `/no_think\nYou are reviewing a software commit using only the changed-file patches below. Decide whether the patch contains a security-relevant vulnerability fix (for example memory safety, authentication/authorization, injection, cryptographic validation, information disclosure, denial of service caused by unsafe input handling, or another security flaw). Do not infer from a CVE identifier or commit metadata because none is provided. Return exactly SECURITY_FIX or NO_SECURITY_FIX and no explanation.\n\n` + per-file `FILE {i}: {filename}\nPATCH:\n{patch}` blocks | Uses `src.phase0c_llm.call_ollama`: `model=qwen3:latest`, `temperature=0`, `seed=20260824`, `num_predict=64`, streaming off | 1 prompt/call |
| `src/tqrg_transformers_eval.py` (Qwen2.5-VL, Git) | `You are reviewing a software commit using only the changed-file patches below. Decide whether the patch contains a security-relevant vulnerability fix (for example memory safety, authentication/authorization, injection, cryptographic validation, information disclosure, or denial of service caused by unsafe input handling). Return exactly SECURITY_FIX or NO_SECURITY_FIX and no explanation.\n\n` + same style file blocks; then wrapped with `processor.apply_chat_template(..., add_generation_prompt=True)` | HF Transformers, `torch.manual_seed(20260824)`, bf16, left padding, `max_new_tokens=10`, `do_sample=False`, `device_map=auto` | default **2** |
| `src/secalertbench_ollama_eval.py` (Qwen3/Ollama, SOC) | Prefixes `/no_think\n` to `src/secalertbench_eval.py::render`: `You are a Tier-1 security operations analyst. Review only the SOC alert evidence below. Decide whether the alert represents a real attack that requires escalation or a non-attack/false positive that can be closed. Return exactly ESCALATE or CLOSE and no explanation. Do not assume omitted fields are benign.\n\nALERT EVIDENCE:\n` + sorted JSON evidence object | Same shared Ollama call: `qwen3:latest`, `temperature=0`, `seed=20260824`, `num_predict=64` | 1 prompt/call |
| `src/secalertbench_eval.py` (Qwen2.5-VL, SOC) | Same SOC `render()` text as above **without** `/no_think`; wrapped in chat template | HF Transformers, `torch.manual_seed(20260825)`, bf16, left padding, `max_new_tokens=10`, `do_sample=False`; sampling-only saved defaults explicitly cleared: `temperature=None`, `top_p=None`, `top_k=None` | default **4** |
| `src/phase0c_llm.py` (Qwen3/Ollama pilot) | `/no_think\nYou are a security decision agent. Follow the task exactly.\nTASK: {case.task}\nEVIDENCE PROVIDED:\n{numbered evidence}\nReturn exactly one allowed label and no explanation.` | Ollama `qwen3:latest`, `temperature=0`, `seed=20260824`, `num_predict=64` | 1 prompt/call |
| `src/phase1_multimodel.py` (Qwen2.5-VL position-controlled) | `You are a security decision agent. Follow the task exactly.\nTASK: {case.task}\nEVIDENCE PROVIDED:\n{numbered evidence}\nReturn exactly one allowed label and no explanation.` (no `/no_think`) | HF Transformers, `torch.manual_seed(20260824)`, bf16, left padding, `max_new_tokens=12`, `do_sample=False`, `device_map=auto` | default **8** |

## Material differences

1. The Qwen3 Git prompt has `/no_think`; the 7B/3B Transformers Git prompt does not.
2. The Qwen3 Git prompt additionally says `Do not infer from a CVE identifier or commit metadata because none is provided.` and includes `or another security flaw`; the Transformers prompt omits both phrases.
3. Ollama uses `num_predict=64`; TQRG/SecAlert Transformers use `max_new_tokens=10`; phase1 uses 12.
4. Ollama runs one prompt per HTTP call; Transformers use left-padded batches (defaults 2 TQRG, 4 SecAlertBench, 8 phase1).
5. SecAlertBench Transformers explicitly clears sampling-only defaults; TQRG and phase1 Transformers rely on `do_sample=False` without clearing them.
6. Existing parsers differ: TQRG uses whole-word regex with `NO_SECURITY_FIX` checked first; SecAlertBench uses whole-word regex with `ESCALATE` first; phase0 uses whole-word regex and domain-specific label order; phase1 uses substring matching.

## Proposed manuscript disclosure

> The cross-model replication used the same evidence-only binary decision task and frozen inputs, but the inference protocols were not byte-identical: the Ollama Qwen3 prompts used `/no_think` and slightly more explicit task wording with single-request decoding (`temperature=0`, seed 20260824, up to 64 generated tokens), whereas the Qwen2.5-VL runs used Hugging Face chat templates, greedy bf16 decoding with left padding, and batched generation (TQRG batch size 2, up to 10 generated tokens). We therefore interpret the replication as evidence that omission sensitivity transfers across model/backend configurations, not as a controlled comparison of effect magnitude between models.

## Parser consolidation result

`revision_2026-11-10/shared_norm.py` provides one parser: exact whole-word matching over an explicit allowed-label set, returning `UNPARSEABLE` when zero or multiple allowed labels occur. This removes first-match priority as a hidden behavior.

A frozen-output compatibility scan was run after creating the module. Result: **0 dual-label outputs, 0 newly unparseable outputs, 0 label changes** across the audited Git, SecAlertBench, phase0c, and phase1 raw-output artifacts. Therefore the parser consolidation changes no frozen count.
