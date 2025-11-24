import os
import uuid
from datetime import datetime

import soundfile as sf
from flask import Flask, jsonify, render_template, request, send_file

from helper import load_text_to_speech, load_voice_style, sanitize_filename, timer

app = Flask(__name__)

# Global variables for TTS model
text_to_speech = None
available_voice_styles = []


def initialize_tts_model():
    """Initialize the TTS model and load available voice styles"""
    global text_to_speech, available_voice_styles

    # Load TTS model
    text_to_speech = load_text_to_speech("assets/onnx", use_gpu=False)

    # Load available voice styles
    voice_style_dir = "assets/voice_styles"
    if os.path.exists(voice_style_dir):
        available_voice_styles = [
            f for f in os.listdir(voice_style_dir) if f.endswith(".json")
        ]

    print(f"TTS model initialized with {len(available_voice_styles)} voice styles")


@app.route("/")
def index():
    """Main page with TTS interface"""
    return render_template("index.html", voice_styles=available_voice_styles)


@app.route("/synthesize", methods=["POST"])
def synthesize():
    """TTS synthesis endpoint"""
    try:
        data = request.get_json()

        # Get parameters
        text = data.get("text", "")
        voice_style = data.get("voice_style", "F2.json")
        total_step = max(1, min(int(data.get("total_step", 5)), 20))
        speed = float(data.get("speed", 1.05))
        n_test = int(data.get("n_test", 1))

        if not text:
            return jsonify({"error": "Text is required"}), 400

        # Validate voice style
        if voice_style not in available_voice_styles:
            return jsonify({"error": f"Voice style {voice_style} not available"}), 400

        # Create output directory
        output_dir = "static/results"
        os.makedirs(output_dir, exist_ok=True)

        # Load voice style
        voice_style_path = f"assets/voice_styles/{voice_style}"
        style = load_voice_style([voice_style_path], verbose=False)

        # Synthesize speech
        results = []
        for n in range(n_test):
            with timer(f"Generating speech {n + 1}/{n_test}"):
                wav, duration = text_to_speech(text, style, total_step, speed)

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = (
                f"{sanitize_filename(text, 20)}_{timestamp}_{unique_id}_{n + 1}.wav"
            )
            filepath = os.path.join(output_dir, filename)

            # Save audio file
            w = wav[0, : int(text_to_speech.sample_rate * duration[0].item())]
            sf.write(filepath, w, text_to_speech.sample_rate)

            results.append(
                {
                    "filename": filename,
                    "url": f"/static/results/{filename}",
                    "duration": float(duration[0].item()),
                }
            )

        return jsonify(
            {
                "success": True,
                "results": results,
                "parameters": {
                    "text": text,
                    "voice_style": voice_style,
                    "total_step": total_step,
                    "speed": speed,
                    "n_test": n_test,
                },
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/voice_styles")
def get_voice_styles():
    """Get list of available voice styles"""
    return jsonify({"voice_styles": available_voice_styles})


if __name__ == "__main__":
    print("=== TTS Web Interface ===")
    initialize_tts_model()
    app.run(debug=True, host="0.0.0.0", port=5001)
