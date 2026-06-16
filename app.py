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

# Esta ruta recibe el formulario de universidades.html y arma el examen con su tiempo
@app.route("/configurar_examen", methods=["POST"])
def configurar_examen():
    # Cacha cuántas preguntas quiere el usuario (por defecto 10)
    cantidad = int(request.form.get("cantidad", 10))
    
    # Asignamos tiempo real: 1 minuto por pregunta
    # Si eligen 10 preguntas -> 10 minutos. Si eligen 120 -> 120 minutos.
    tiempo_minutos = cantidad 
    
    banco_completo = cargar_preguntas_unam()
    
    # Si piden más preguntas de las que hay en el JSON, toma el tope disponible
    num_preguntas = min(cantidad, len(banco_completo))
    
    # Selecciona preguntas al azar sin que se repitan
    preguntas_examen = random.sample(banco_completo, num_preguntas)
    
    # Te manda a la página de examen pasándole las preguntas y el tiempo calculado
    return render_template("examen.html", preguntas=preguntas_examen, tiempo=tiempo_minutos)

# Ruta que procesa las respuestas del alumno y calcula el puntaje
@app.route("/calificar_examen", methods=["POST"])
def calificar_examen():
    banco_completo = cargar_preguntas_unam()
    
    aciertos = 0
    total_preguntas = 0
    resultados = []
    
    # Revisamos cada pregunta del banco para ver si el usuario la contestó
    for pregunta in banco_completo:
        campo_name = f"pregunta_{pregunta['id']}"
        
        # Si esta pregunta venía en el examen que contestó el alumno
        if campo_name in request.form:
            total_preguntas += 1
            respuesta_usuario = request.form.get(campo_name)
            es_correcta = (respuesta_usuario == pregunta['respuesta_correcta'])
            
            if es_correcta:
                aciertos += 1
                
            # Guardamos la info para mostrársela al alumno al final
            resultados.append({
                "materia": pregunta["materia"],
                "pregunta": pregunta["pregunta"],
                "respuesta_usuario": respuesta_usuario,
                "respuesta_correcta": pregunta["respuesta_correcta"],
                "es_correcta": es_correcta
            })
            
    # Calculamos el porcentaje de éxito
    porcentaje = int((aciertos / total_preguntas) * 100) if total_preguntas > 0 else 0
    
    # Enviamos los datos a la plantilla de resultados
    return render_template("resultados.html", 
                           aciertos=aciertos, 
                           total=total_preguntas, 
                           porcentaje=porcentaje, 
                           resultados=resultados)

# Dejamos la ruta vieja por si entran directo, pero ahora vacía por defecto
@app.route("/examen")
def examen():
    return render_template("examen.html", preguntas=[])

if __name__ == "__main__":
    # Permite a Render asignar el puerto automáticamente en internet
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
