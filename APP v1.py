# ...existing code...
try:
    from flask import Flask, render_template_string, request, jsonify, url_for
    from werkzeug.utils import secure_filename
    from PIL import Image, ImageEnhance, ImageFilter
except Exception:
    print("Dependency error: failed to import required packages. Install with:")
    print("  python -m pip install Flask Pillow Werkzeug")
    raise

import os
import io
import time

BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
GENERATED_DIR = os.path.join(BASE_DIR, "static", "generated")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

app = Flask(__name__, static_folder='static')

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

INDEX_HTML = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rediseña tu Casa</title>
<style>
:root{--accent:#007bff;--bg:#f8f8f8}
*{box-sizing:border-box}body{font-family:Arial,Helvetica,sans-serif;margin:0;color:#222;background:white}
.hero{background-image:linear-gradient(rgba(0,0,0,0.35),rgba(0,0,0,0.3)), url('https://picsum.photos/seed/room/1600/900');background-size:cover;background-position:center;min-height:60vh;display:flex;flex-direction:column;align-items:center;justify-content:center;color:white;text-align:center;padding:40px}
.hero h1{font-size:clamp(1.6rem,3.5vw,3rem);margin:0}
.upload-form{display:flex;gap:10px;flex-wrap:wrap;align-items:center;justify-content:center;margin-top:12px}
.file-label{background:rgba(255,255,255,0.12);padding:8px 12px;border-radius:6px;cursor:pointer}
.file-label input{display:none}
select{padding:8px;border-radius:6px;border:1px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.08);color:white}
button{background:var(--accent);border:none;color:white;padding:10px 16px;border-radius:6px;cursor:pointer}
.preview{margin-top:14px}
.preview-img{max-width:90vw;max-height:45vh;border-radius:8px;box-shadow:0 6px 20px rgba(0,0,0,0.3)}
.steps{max-width:1100px;margin:40px auto;padding:20px;text-align:center}
.logos{background:var(--bg);overflow:hidden;padding:18px 0}
.logos-track{display:inline-block;white-space:nowrap;animation:scroll 20s linear infinite;padding-left:2%}
.logos img{height:60px;margin:0 18px;vertical-align:middle;border-radius:6px;object-fit:cover}
@keyframes scroll{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
@media (max-width:600px){.upload-form{flex-direction:column}.logos img{height:44px;margin:0 12px}}
</style>
</head>
<body>
<section class="hero" role="banner" aria-label="Presentación">
    <h1>Rediseña tu casa con un solo click</h1>
    <h2>Powered by AI</h2>

    <form id="upload-form" class="upload-form" onsubmit="return false;">
        <label class="file-label">
            <input id="image-input" type="file" name="image" accept="image/*" required>
            <span>Seleccionar imagen</span>
        </label>

        <select id="style-select" aria-label="Seleccionar estilo">
            <option>Modern</option>
            <option>Classic</option>
            <option>Nordic</option>
            <option>Japanese</option>
        </select>

        <button id="generate-btn" type="button">Generar</button>
    </form>

    <div id="preview" class="preview" aria-live="polite"></div>
</section>

<section class="steps" aria-labelledby="steps-title">
    <h2 id="steps-title">Pasos para rediseñar tu habitación</h2>
    <ol>
        <li>Sube imagen de la habitación que quieres redecorar</li>
        <li>Selecciona tu diseño</li>
        <li>Visualiza el resultado con un precio estimado y links</li>
        <li>Personaliza tu diseño</li>
    </ol>
</section>

<section class="logos" aria-hidden="false" aria-label="Marquesinas de marcas">
    <div class="logos-track">
        <img src="https://picsum.photos/seed/1/200/80" alt="Marca 1" loading="lazy">
        <img src="https://picsum.photos/seed/2/200/80" alt="Marca 2" loading="lazy">
        <img src="https://picsum.photos/seed/3/200/80" alt="Marca 3" loading="lazy">
        <img src="https://picsum.photos/seed/4/200/80" alt="Marca 4" loading="lazy">
        <img src="https://picsum.photos/seed/5/200/80" alt="Marca 5" loading="lazy">
        <img src="https://picsum.photos/seed/1/200/80" alt="Marca 1" loading="lazy">
        <img src="https://picsum.photos/seed/2/200/80" alt="Marca 2" loading="lazy">
        <img src="https://picsum.photos/seed/3/200/80" alt="Marca 3" loading="lazy">
        <img src="https://picsum.photos/seed/4/200/80" alt="Marca 4" loading="lazy">
        <img src="https://picsum.photos/seed/5/200/80" alt="Marca 5" loading="lazy">
    </div>
</section>

<script>
const uploadInput = document.getElementById('image-input');
const generateBtn = document.getElementById('generate-btn');
const preview = document.getElementById('preview');
const styleSelect = document.getElementById('style-select');

let uploadedFilename = null;

async function uploadFile(file){
    const form = new FormData();
    form.append('image', file);
    const res = await fetch('/upload', { method: 'POST', body: form });
    return res.json();
}

async function generateDesign(filename, style){
    const res = await fetch('/generate', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ filename, style })
    });
    return res.json();
}

uploadInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    preview.innerHTML = '<p>Subiendo...</p>';
    const data = await uploadFile(file);
    if (data.error){ preview.innerHTML = `<p class="error">${data.error}</p>`; return; }
    uploadedFilename = data.filename;
    preview.innerHTML = `<img src="${data.url}" alt="Preview" class="preview-img">`;
});

generateBtn.addEventListener('click', async () => {
    if (!uploadedFilename){ alert('Por favor sube una imagen primero.'); return; }
    generateBtn.disabled = true; generateBtn.textContent = 'Generando...';
    const data = await generateDesign(uploadedFilename, styleSelect.value);
    generateBtn.disabled = false; generateBtn.textContent = 'Generar';
    if (data.error){ preview.innerHTML = `<p class="error">${data.error}</p>`; return; }
    preview.innerHTML = `<img src="${data.url}" alt="Generated" class="preview-img">`;
});
</script>
</body>
</html>
"""

def fake_generate_image(src_path, style_name, out_path):
    img = Image.open(src_path).convert("RGBA")
    overlays = {
        "Modern": (30,144,255,40),
        "Classic": (160,82,45,40),
        "Nordic": (240,248,255,40),
        "Japanese": (255,182,193,40),
    }
    overlay = Image.new("RGBA", img.size, overlays.get(style_name, (0,0,0,0)))
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB").filter(ImageFilter.SMOOTH_MORE)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    img.save(out_path, format="JPEG", quality=85)

@app.route('/')
def home():
    return render_template_string(INDEX_HTML)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('image')
    if not file:
        return jsonify({"error":"no file"}), 400
    filename = f"{int(time.time())}_{secure_filename(file.filename)}"
    path = os.path.join(UPLOAD_DIR, filename)
    file.save(path)
    return jsonify({"url": url_for('static', filename=f"uploads/{filename}"), "filename": filename})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json() or {}
    filename = data.get("filename")
    style = data.get("style", "Modern")
    if not filename:
        return jsonify({"error":"missing filename"}), 400
    src = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(src):
        return jsonify({"error":"file not found"}), 404
    out_name = f"gen_{int(time.time())}_{secure_filename(filename)}"
    out_path = os.path.join(GENERATED_DIR, out_name)
    fake_generate_image(src, style, out_path)
    return jsonify({"url": url_for('static', filename=f"generated/{out_name}")})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
# ...existing code...