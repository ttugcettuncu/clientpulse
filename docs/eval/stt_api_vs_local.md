# STT: OpenAI API vs local faster-whisper

Generated 2026-10-05 by `python -m dev_tools.stt_api_compare`. Audio: `call_01.mp3` (2.94 min, synthetic gTTS speech). Experiment spend: $0.0265 (approved cap $0.05).

| Engine | Normalized WER | Raw WER | Processing time | Cost | Cost / 1,000 min |
|---|---|---|---|---|---|
| faster-whisper tiny (local, CPU) | 3.1% | 9.2% | 10.3s | $0.0000 | $0.00 |
| faster-whisper base (local, CPU) | 1.7% | 7.5% | 18.0s | $0.0000 | $0.00 |
| faster-whisper small (local, CPU) | 1.2% | 7.1% | 79.8s | $0.0000 | $0.00 |
| OpenAI whisper-1 (API) | 1.7% | 7.8% | 8.8s | $0.0177 | $6.00 |
| OpenAI gpt-4o-mini-transcribe (API) | 1.7% | 7.8% | 4.9s | $0.0088 | $3.00 |

Local latency is CPU time on the dev laptop (no GPU); API latency includes upload and network.
Local cost excludes hardware and electricity.
