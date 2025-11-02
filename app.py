from flask import Flask, request, redirect, url_for, render_template
import os
from wisper import transcribe_audio

app = Flask(__name__)

# Folder to save uploaded files
UPLOAD_FOLDER = "models"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def home():
    # Renders templates/index.html
    return render_template("index.html")

@app.route("/add_model", methods=["POST"])
def add_model():
    # Get form data
    name = request.form.get("name").lower()
    prompt_text = request.form.get("prompt_text")
    prompt_language = request.form.get("prompt_language")

    model_folder = os.path.join(app.config["UPLOAD_FOLDER"], name)
    os.makedirs(model_folder, exist_ok=True)

    # Get files
    ref_audio = request.files.get("ref_audio")
    extra_refs = request.files.getlist("extra_refs")

    # Save reference audio
    if ref_audio:
      ref_audio_filename = os.path.join(model_folder, name + "_ref_audio.wav")
      ref_audio.save(ref_audio_filename)

    extra_refs_folder = os.path.join(model_folder, "extra_refs")
    
    # Save extra reference audios
    for i, f in enumerate(extra_refs):
        i = 1 if i == 0 else i
        if f.filename:
            os.makedirs(extra_refs_folder, exist_ok=True)
            f_path = os.path.join(extra_refs_folder, f"{name}_extra_ref_{i}_audio.wav")
            f.save(f_path)


    if prompt_text is None or prompt_text.strip() == "":
        prompt_text = transcribe_audio(ref_audio_filename)

    print("Model Name:", name)
    print("Prompt Text:", prompt_text)
    print("Prompt Language:", prompt_language)
    print("Files saved!")

    return "Model added successfully!"

if __name__ == "__main__":
    app.run(debug=True)
