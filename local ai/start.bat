@echo off
REM ── Campus Companion – Llamafile Launcher (Full Context) ──
REM Optimized for Snapdragon X Elite (ARM64, no CUDA)
REM GPU layers set to 0 (no CUDA). If Vulkan works on your Adreno GPU,
REM try increasing -ngl to 10-20 for a speed boost.
llamafile-0.10.6.exe --server --model "qwen2.5-coder-7b-instruct-q4_0.gguf" --host 127.0.0.1 --port 8081 --n-gpu-layers 0 --threads 10 --ctx-size 20000