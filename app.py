from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import os

# Intenta obtener la clave de la API desde variables de entorno (ideal para Render)
API_KEY = os.getenv("FIREBASE_API_KEY")

# Si no está en variables de entorno (ej. en local), intenta cargarla desde un archivo local
if not API_KEY:
    try:
        from credenciales import API_KEY as LOCAL_API_KEY
        API_KEY = LOCAL_API_KEY
    except ImportError:
        raise Exception("No se encontró la clave API. Asegúrate de tener FIREBASE_API_KEY o credenciales.py.")

# Configura la app de Flask
app = Flask(__name__)

# Clave secreta para manejar sesiones (también puede venir de entorno o usar valor por defecto)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "clave_local_segura")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # URL para autenticación con Firebase
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

            # Si el login fue exitoso
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

if __name__ == "__main__":
    app.run(debug=True)
