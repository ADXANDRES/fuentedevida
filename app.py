from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
# Asegúrate de que 'credenciales.py' exista en el mismo directorio que 'app.py'
# y contenga una línea como: API_KEY = "tu_clave_api_aqui"
from credenciales import API_KEY

app = Flask(__name__)
# ¡IMPORTANTE! Cambia esto por una cadena secreta muy segura y larga para producción
app.secret_key = "una_clave_secreta_muy_segura_y_larga_para_tu_app_de_iglesia"

# Ruta para el login (página de inicio)
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # URL de la API de Firebase para iniciar sesión con email/contraseña
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        try:
            res = requests.post(url, json=payload)
            res.raise_for_status()  # Lanza una excepción para errores HTTP (4xx o 5xx)
            data = res.json()
            session["user"] = data["localId"]  # Guarda el ID del usuario en la sesión
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("bienvenida")) # Redirige al menú principal

        except requests.exceptions.RequestException as e:
            print(f"Error durante la autenticación: {e}")
            flash("Correo o contraseña incorrectos.", "error") # Mensaje de error para el usuario
            return render_template("login.html") # Vuelve a mostrar el formulario de login

    # Si es una solicitud GET, simplemente muestra la página de login
    return render_template("login.html")

# Ruta protegida para el menú principal (bienvenida)
@app.route("/bienvenida")
def bienvenida():
    # Verifica si el usuario está logueado
    if "user" in session:
        return render_template("bienvenida.html")
    else:
        flash("Debes iniciar sesión para acceder a esta página.", "info")
        return redirect(url_for("login"))

# Ruta para la página de Grupos Familiares
@app.route("/grupos_familiares")
def grupos_familiares():
    # Es buena práctica proteger también las páginas internas
    if "user" in session:
        return render_template("gruposfamiliares.html") # Nombre del archivo HTML
    else:
        flash("Debes iniciar sesión para ver esta página.", "info")
        return redirect(url_for("login"))

# Ruta para cerrar sesión
@app.route("/logout")
def logout():
    session.clear()  # Limpia todos los datos de la sesión
    flash("Has cerrado sesión correctamente.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True) # debug=True es solo para desarrollo, desactívalo en producción
