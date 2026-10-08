"""
Phase 0 feasibility test for StudyMate.
Proves the 4 technical pillars work on a free tier + 16GB laptop:
  1. LLM chat (Groq, OpenAI-compatible)
  2. Streaming (for the typing effect)
  3. Whisper transcription (for lecture audio)
  4. Local embeddings (all-MiniLM-L6-v2, CPU)

Run:  python backend/tests/test_groq.py [optional: path/to/audio.mp3]
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

PASS, FAIL = "✅ PASS", "❌ FAIL"
results = []


def check(name: str, fn):
    print(f"\n{'=' * 60}\n🧪 Testing: {name}\n{'=' * 60}")
    try:
        fn()
        results.append((name, True))
        print(f"\n{PASS}: {name}")
    except Exception as e:
        results.append((name, False))
        print(f"\n{FAIL}: {name} → {type(e).__name__}: {e}")


# ---------------------------------------------------------------
# 1. LLM CHAT — the core generation call
# ---------------------------------------------------------------
def test_chat():
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.environ["LLM_BASE_URL"],
    )
    response = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        messages=[
            {"role": "system", "content": "Answer in one sentence."},
            {"role": "user", "content": "What is retrieval-augmented generation?"},
        ],
        max_tokens=100,
    )
    answer = response.choices[0].message.content
    print(f"Model:  {os.environ['LLM_MODEL']}")
    print(f"Answer: {answer}")
    assert answer, "Empty response"


# ---------------------------------------------------------------
# 2. STREAMING — powers the typing effect in the UI
# ---------------------------------------------------------------
def test_streaming():
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.environ["LLM_BASE_URL"],
    )
    stream = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        messages=[{"role": "user", "content": "Count from 1 to 5."}],
        max_tokens=50,
        stream=True,
    )
    print("Streamed output: ", end="", flush=True)
    chunks = 0
    for event in stream:
        token = event.choices[0].delta.content or ""
        print(token, end="", flush=True)
        chunks += 1
    print()
    assert chunks > 1, "Expected multiple streamed chunks"
    print(f"({chunks} chunks received)")


# ---------------------------------------------------------------
# 3. WHISPER — for the "lecture audio → notes" feature
#    Pass an audio file as argument: python test_groq.py my_audio.mp3
#    Any mp3/m4a/wav works — even a 5-second voice memo.
# ---------------------------------------------------------------
def test_whisper():
    audio_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not audio_path:
        print("⏭️  SKIPPED (no audio file provided).")
        print("   To test: record 5s of yourself talking, then run:")
        print("   python backend/tests/test_groq.py path/to/audio.mp3")
        return "skipped"

    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.environ["LLM_BASE_URL"],
    )
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model=os.environ["WHISPER_MODEL"],
            file=f,
        )
    print(f"Transcript: {transcript.text[:300]}")
    assert transcript.text, "Empty transcript"


# ---------------------------------------------------------------
# 4. LOCAL EMBEDDINGS — runs on YOUR CPU, this is the
#    component that makes RAG possible without any API.
#    First run downloads ~90MB, then it's cached.
# ---------------------------------------------------------------
def test_embeddings():
    from sentence_transformers import SentenceTransformer
    import numpy as np

    print("Loading all-MiniLM-L6-v2 (first run downloads ~90MB)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Two sentences about the same topic, one about something else
    chunks = [
        "Gradient descent updates model weights to minimize the loss function.",
        "SGD is a variant of gradient descent using single samples per update.",
        "The mitochondria is the powerhouse of the cell.",
    ]
    embeddings = model.encode(chunks)
    print(f"Embedding shape: {embeddings.shape}")  # (3, 384)

    # Cosine similarity: first two should be high, third low
    sims = embeddings[:2] @ embeddings[2].T / np.linalg.norm(embeddings[2])
    sim_related = float(embeddings[0] @ embeddings[1])
    sim_unrelated = float(embeddings[0] @ embeddings[2])
    print(f"Similarity (gradient descent vs SGD):     {sim_related:.3f}  ← should be HIGH")
    print(f"Similarity (gradient descent vs mitochondria): {sim_unrelated:.3f}  ← should be LOW")
    assert sim_related > sim_unrelated, "Embeddings are not semantically meaningful!"


# ---------------------------------------------------------------
if __name__ == "__main__":
    check("1. LLM chat (Groq)", test_chat)
    check("2. Streaming (typing effect)", test_streaming)
    check("3. Whisper transcription", test_whisper)
    check("4. Local embeddings (CPU)", test_embeddings)

    print(f"\n{'=' * 60}\n📋 RESULTS\n{'=' * 60}")
    for name, ok in results:
        print(f"  {PASS if ok else FAIL}  {name}")

    n_pass = sum(ok for _, ok in results)
    if n_pass == len(results):
        print("\n🎉 All systems go. StudyMate is fully feasible on your machine.")
        print("   Next step: Phase 1 — the ingestion pipeline.")
    else:
        print("\n🔧 Fix the failing test(s) above before starting Phase 1.")