import os
import json
import random
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Función para cargar las preguntas de la UNAM desde la carpeta data
def cargar_preguntas_unam():
    ruta = os.path.join('data', 'unam.json')
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Función para cargar las preguntas del IPN desde la carpeta data de Render
def cargar_preguntas_ipn():
    ruta = "/opt/render/project/src/data/ipn.json"
    if not os.path.exists(ruta):
        # Respaldo local por si pruebas en tu computadora
        ruta = os.path.join('data', 'ipn.json')
        
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Función para cargar las preguntas de la UAM desde la carpeta data
def cargar_preguntas_uam():
    ruta = os.path.join('data', 'uam.json')
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

@app.route("/study_center")
def study_center():
    return render_template("study_center.html")

# Ruta unificada que recibe los formularios de universidades.html (UNAM, IPN y UAM)
@app.route("/configurar_examen", methods=["POST"])
def configurar_examen():
    universidad = request.form.get("universidad", "unam")
    cantidad = int(request.form.get("cantidad", 10))
    tiempo_minutos = cantidad # 1 minuto por pregunta de manera predeterminada
    
    # Seleccionamos el banco correspondiente según la universidad del formulario
    if universidad == "ipn":
        banco_completo = cargar_preguntas_ipn()
    elif universidad == "uam":
        banco_completo = cargar_preguntas_uam()
    else:
        banco_completo = cargar_preguntas_unam()
        
    # Validamos que no pidamos más preguntas de las que existen en el JSON
    num_preguntas = min(cantidad, len(banco_completo))
    
    if num_preguntas > 0:
        preguntas_examen = random.sample(banco_completo, num_preguntas)
    else:
        preguntas_examen = []
        
    return render_template("examen.html", preguntas=preguntas_examen, tiempo=tiempo_minutos)

# Ruta que procesa las respuestas del alumno y calcula el puntaje (Soporta UNAM, IPN y UAM)
@app.route("/calificar_examen", methods=["POST"])
def calificar_examen():
    # Unimos los tres bancos de preguntas para calificar globalmente buscando por ID de pregunta
    banco_completo = cargar_preguntas_unam() + cargar_preguntas_ipn() + cargar_preguntas_uam()
    
    aciertos = 0
    total_preguntas = 0
    resultados = []
    
    # Revisamos cada pregunta para ver si el usuario la contestó en su examen actual
    for pregunta in banco_completo:
        campo_name = f"pregunta_{pregunta['id']}"
        
        # Si esta pregunta venía en el examen que se le renderizó al alumno
        if campo_name in request.form:
            total_preguntas += 1
            respuesta_usuario = request.form.get(campo_name)
            es_correcta = (respuesta_usuario == pregunta['respuesta_correcta'])
            
            if es_correcta:
                aciertos += 1
                
            # Guardamos el resultado detallado
            resultados.append({
                "materia": pregunta["materia"],
                "pregunta": pregunta["pregunta"],
                "respuesta_usuario": respuesta_usuario,
                "respuesta_correcta": pregunta["respuesta_correcta"],
                "es_correcta": es_correcta
            })
            
    # Calculamos el porcentaje de éxito
    porcentaje = int((aciertos / total_preguntas) * 100) if total_preguntas > 0 else 0
    
    # Enviamos los datos procesados a la plantilla de resultados
    return render_template("resultados.html", 
                           aciertos=aciertos, 
                           total=total_preguntas, 
                           porcentaje=porcentaje, 
                           resultados=resultados)

@app.route("/examen")
def examen():
    return render_template("examen.html", preguntas=[])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
