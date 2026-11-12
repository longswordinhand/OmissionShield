# Hardware and software environment — UISAI1

Recorded: 2026-11-10/11 before Phase-1 overhead re-timing.

- Host: `uisai1`
- OS: Ubuntu 24.04.3 LTS, Linux kernel `6.8.0-138-generic`, x86_64
- CPU: Intel Xeon Gold 6526Y; 1 socket; 16 physical cores; 32 hardware threads
- RAM: 251 GiB total
- GPU: NVIDIA H100 NVL, 95,830 MiB reported memory
- NVIDIA driver: 580.105.08
- Python: 3.12.10
- torch: 2.14.1
- transformers: 5.12.1
- accelerate: 1.15.0
- pytest: 9.1.0
- Ollama client: 0.7.0; server was not running at capture time

These versions describe the environment used for the Phase-1 re-timing, not necessarily the historical LLM inference environment; the latter was not fully logged and must not be inferred from this file.
