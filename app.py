from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
from PIL import Image
import base64
import hashlib
from io import BytesIO

app = Flask(__name__)


# ==========================
# MEMBUAT KUNCI DARI PASSWORD
# ==========================
def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)


# ==========================
# ENKRIPSI AES (FERNET)
# ==========================
def encrypt_data(data, password):
    key = generate_key(password)
    cipher = Fernet(key)
    encrypted = cipher.encrypt(data.encode())
    return encrypted.decode()


# ==========================
# DEKRIPSI AES (FERNET)
# ==========================
def decrypt_data(data, password):
    key = generate_key(password)
    cipher = Fernet(key)
    decrypted = cipher.decrypt(data.encode())
    return decrypted.decode()


# ==========================
# HALAMAN UTAMA
# ==========================
@app.route("/")
def index():
    return render_template("index.html")


# ==========================
# ENKRIPSI + STEGANOGRAFI
# ==========================
@app.route("/encrypt", methods=["POST"])
def encrypt():

    nama = request.form["nama"]
    bank = request.form["bank"]
    rekening = request.form["rekening"]
    catatan = request.form["catatan"]
    password = request.form["password"]

    image = request.files["image"]

    data = f"""Nama : {nama}
Bank : {bank}
Nomor Rekening : {rekening}
Catatan : {catatan}"""

    try:
        # Enkripsi teks dengan AES (Fernet)
        encrypted = encrypt_data(data, password)

        # Buka gambar dengan PIL dan paksa ke mode RGB
        # (mode P/palette akan bikin stegano stuck nunggu input di terminal)
        pil_image = Image.open(image).convert("RGB")

        # Sisipkan teks terenkripsi ke dalam gambar (LSB steganography)
        secret_image = lsb.hide(pil_image, encrypted)

        img_io = BytesIO()
        secret_image.save(img_io, "PNG")
        img_io.seek(0)

        return send_file(
            img_io,
            mimetype="image/png",
            as_attachment=True,
            download_name="rekening_rahasia.png"
        )

    except Exception as e:
        return render_template(
            "index.html",
            result=f"Terjadi kesalahan saat enkripsi: {e}"
        )


# ==========================
# DEKRIPSI
# ==========================
@app.route("/decrypt", methods=["POST"])
def decrypt():

    password = request.form["password"]
    image = request.files["image"]

    try:
        pil_image = Image.open(image).convert("RGB")

        hidden = lsb.reveal(pil_image)

        if hidden is None:
            raise ValueError("Tidak ada data tersembunyi pada gambar ini.")

        result = decrypt_data(hidden, password)

        return render_template(
            "index.html",
            result=result
        )

    except Exception:
        return render_template(
            "index.html",
            result="Password salah atau gambar tidak berisi data."
        )


import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )