import os
import json
import random
from flask import Flask, render_template, request

app = Flask(__name__)

# Función para cargar las preguntas de la UNAM desde la carpeta data
def cargar_preguntas_unam():
    ruta = os.path.join('data', 'unam.json')
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/universidades")
def universidades():
    return render_template("universidades.html")

@app.route("/consejos")
def consejos():
    return render_template("consejos.html")

# Esta nueva ruta recibe el formulario de universidades.html y arma el examen
@app.route("/configurar_examen", methods=["POST"])
def configurar_examen():
    # Cacha cuántas preguntas quiere el usuario (por defecto 10)
    cantidad = int(request.form.get("cantidad", 10))
    
    banco_completo = cargar_preguntas_unam()
    
    # Si piden más preguntas de las que hay en el JSON, toma el tope disponible
    num_preguntas = min(cantidad, len(banco_completo))
    
    # Selecciona preguntas al azar sin que se repitan
    preguntas_examen = random.sample(banco_completo, num_preguntas)
    
    # Te manda a la página de examen pasándole la lista de preguntas aleatorias
    return render_template("examen.html", preguntas=preguntas_examen)

# Dejamos la ruta vieja por si entran directo, pero ahora vacía por defecto
@app.route("/examen")
def examen():
    return render_template("examen.html", preguntas=[])

if __name__ == "__main__":
    # Cambiamos esto para que Render pueda asignar el puerto automáticamente en internet
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
