from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import os
import firebase_admin
from firebase_admin import credentials, initialize_app

# Inicializar Firebase solo si no está ya inicializado
if not firebase_admin._apps:
    try:
        # Ruta para Render (montada como secreto)
        firebase_key_path = "/etc/secrets/serviceAccountKey.json"
        if not os.path.exists(firebase_key_path):
            # Ruta local (cuando desarrollas en tu PC)
            firebase_key_path = os.path.join(os.path.dirname(__file__), "credenciales", "serviceAccountKey.json")

        cred = credentials.Certificate(firebase_key_path)
        initialize_app(cred)
    except Exception as e:
        print(f"Error al inicializar Firebase: {e}")
        raise

# Obtener la API_KEY de entorno o archivo local
API_KEY = os.getenv("FIREBASE_API_KEY")
if not API_KEY:
    try:
        from credenciales import API_KEY as LOCAL_API_KEY
        API_KEY = LOCAL_API_KEY
    except ImportError:
        raise Exception("No se encontró la clave API. Usa una variable de entorno 'FIREBASE_API_KEY' o el archivo 'credenciales.py'.")

# Configuración de la aplicación Flask
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "clave_local_segura")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        try:
            res = requests.post(url, json=payload)
            res.raise_for_status()
            data = res.json()

            session["user"] = data["localId"]
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("bienvenida"))

        except requests.exceptions.HTTPError:
            flash("Correo o contraseña incorrectos.", "error")
        except Exception as e:
            flash("Error al procesar la solicitud. Inténtalo de nuevo.", "error")
            print(f"Error general: {e}")

    return render_template("login.html")

@app.route("/bienvenida")
def bienvenida():
    if "user" in session:
        return render_template("bienvenida.html")
    else:
        flash("Debes iniciar sesión para acceder a esta página.", "info")
        return redirect(url_for("login"))

@app.route("/grupos_familiares")
def grupos_familiares():
    if "user" in session:
        return render_template("gruposfamiliares.html")
    else:
        flash("Debes iniciar sesión para ver esta página.", "info")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.", "success")
    return redirect(url_for("login"))

# ✅ Ruta de verificación de salud para Render
@app.route("/salud")
def salud():
    return "Aplicación funcionando correctamente.", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
