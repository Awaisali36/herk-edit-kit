#!/usr/bin/env python3
"""Transcribe a recording locally with WhisperX and write the kit's word-level format.

Usage:
  python3 scripts/transcribe-whisperx.py <media> <out.json> [--model large-v3] [--language en]

Output matches examples/editing/source.json:
  { language_code, audio_duration_secs, text, words: [{text, start, end, type}] }
Needs the WhisperX and alignment models (downloaded from huggingface.co on first run).
"""
import argparse
import json

import whisperx


def main():
    p = argparse.ArgumentParser()
    p.add_argument("media")
    p.add_argument("out")
    p.add_argument("--model", default="large-v3")
    p.add_argument("--language", default=None)
    p.add_argument("--batch-size", type=int, default=8)
    a = p.parse_args()

    audio = whisperx.load_audio(a.media)
    model = whisperx.load_model(a.model, "cpu", compute_type="int8", language=a.language)
    result = model.transcribe(audio, batch_size=a.batch_size)
    lang = result["language"]

    align_model, meta = whisperx.load_align_model(language_code=lang, device="cpu")
    aligned = whisperx.align(result["segments"], align_model, meta, audio, "cpu")

    words = []
    for seg in aligned["segments"]:
        for w in seg.get("words", []):
            # Words the aligner could not place (numbers, symbols) inherit the previous end.
            start = w.get("start", words[-1]["end"] if words else seg["start"])
            end = w.get("end", start)
            words.append({"text": w["word"].strip(), "start": round(start, 3),
                          "end": round(end, 3), "type": "word"})

    out = {
        "language_code": lang,
        "audio_duration_secs": round(len(audio) / 16000, 3),
        "text": " ".join(w["text"] for w in words),
        "words": words,
    }
    with open(a.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"{len(words)} words -> {a.out}")


if __name__ == "__main__":
    main()
