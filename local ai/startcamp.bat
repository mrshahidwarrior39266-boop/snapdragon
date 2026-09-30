@echo off
REM ── Campus Companion – Llamafile Launcher (Compact) ──
REM Optimized for Snapdragon X Elite (ARM64, no CUDA)
REM Lower context size for faster startup / less RAM usage.
llamafile-0.10.6.exe --server -m "qwen2.5-coder-7b-instruct-q4_0.gguf" --host 127.0.0.1 --port 8081 -ngl 0 -t 10 -c 16384