from flask import Flask, request, redirect, url_for, render_template
import os
from wisper import transcribe_audio

app = Flask(__name__)

UPLOAD_FOLDER = "models"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def home():
    # Renders templates/index.html
    return render_template("index.html")

@app.route("/add_model", methods=["POST"])
def add_model():
    name = request.form.get("name").lower()
    prompt_text = request.form.get("prompt_text")
    prompt_language = request.form.get("prompt_language")
    ref_audio = request.files.get("ref_audio")
    extra_refs_files = request.files.getlist("extra_refs")

    result = save_model_files(name, ref_audio, extra_refs_files, prompt_text)

    data = {
        "name": name,
        "prompt_text": result["prompt_text"],
        "prompt_language": prompt_language,
        "ref_audio_path": result["ref_audio_path"],
        "extra_refs": result["extra_refs"]
    }

    insert_model_to_db(name, result["prompt_text"], prompt_language, result["ref_audio_path"], result["extra_refs"])

    return {"status": "success", "data": data}

def insert_model_to_db(name, prompt_text, prompt_language, ref_audio_path, extra_refs):
    print("Inserting model to database:")
    print(f"Name: {name}")
    print(f"Prompt Text: {prompt_text}")
    print(f"Prompt Language: {prompt_language}")
    print(f"Reference Audio Path: {ref_audio_path}")
    print(f"Extra References: {extra_refs}")

def save_model_files(model_name, ref_audio, extra_refs_files, prompt_text=None, upload_folder="models"):
    model_folder = os.path.join(upload_folder, model_name.lower())
    os.makedirs(model_folder, exist_ok=True)

    # Save reference audio
    ref_audio_path = None
    if ref_audio:
        ref_audio_path = os.path.join(model_folder, f"{model_name}_ref_audio.wav")
        ref_audio.save(ref_audio_path)

    # Save extra reference audios
    extra_refs_folder = os.path.join(model_folder, "extra_refs")
    extra_refs = []

    for i, f in enumerate(extra_refs_files):
        index = 1 if i == 0 else i
        if f.filename:
            os.makedirs(extra_refs_folder, exist_ok=True)
            f_path = os.path.join(extra_refs_folder, f"{model_name}_extra_ref_{index}_audio.wav")
            f.save(f_path)
            extra_refs.append(f"{model_name}_extra_ref_{index}_audio.wav")

    # Generate prompt text if not provided
    if not prompt_text or prompt_text.strip() == "":
        if ref_audio_path:
            prompt_text = transcribe_audio(ref_audio_path)
        else:
            prompt_text = ""

    return {
        "ref_audio_path": ref_audio_path,
        "extra_refs": extra_refs,
        "prompt_text": prompt_text
    }

if __name__ == "__main__":
    app.run(debug=True)
