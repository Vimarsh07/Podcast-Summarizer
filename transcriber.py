import whisperx
import urllib.error

def transcribe(audio_path):
    # load ASR model
    model = whisperx.load_model("base", device="cpu", compute_type="float32")
    result = model.transcribe(audio_path)

    segments = []
    # attempt diarization + alignment, else fallback
    try:
        # load VAD pipeline
        vad_model = whisperx.load_diarization_pipeline(use_auth_token=None, device="cpu")
        diarization = vad_model(audio_path)
        # align transcription with speakers
        aligned = whisperx.align(
            result, diarization,
            model=model, audio_path=audio_path, device="cpu"
        )
        segments = aligned["segments"]
    except urllib.error.HTTPError as e:
        print("⚠️ VAD download failed, skipping diarization:", e)
        # fallback: plain segments without speaker tags
        segments = [
            {"start": s["start"], "end": s["end"], "text": s["text"], "speaker": None}
            for s in result["segments"]
        ]
    return segments