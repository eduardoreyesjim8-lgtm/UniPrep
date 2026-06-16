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

# Función para cargar las preguntas del IPN desde la carpeta data de Render
def cargar_preguntas_ipn():
    ruta = "/opt/render/project/src/data/ipn.json"
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

# Esta ruta recibe el formulario de universidades.html y arma el examen del IPN
@app.route("/configurar_examen_ipn", methods=["POST"])
def configurar_examen_ipn():
    # 1. Cargamos el banco completo del IPN
    banco_completo = cargar_preguntas_ipn()
    
    # 2. Obtenemos el tipo de examen que seleccionó el usuario en el formulario
    tipo_examen = request.form.get("tipo_examen") # 'simulacro' o por materia
    
    if tipo_examen == "simulacro":
        limite_preguntas = 140 if len(banco_completo) >= 140 else len(banco_completo)
        preguntas_seleccionadas = random.sample(banco_completo, limite_preguntas)
    else:
        materia_seleccionada = request.form.get("materia")
        preguntas_filtradas = [p for p in banco_completo if p["materia"] == materia_seleccionada]
        
        limite = 20 if len(preguntas_filtradas) >= 20 else len(preguntas_filtradas)
        preguntas_seleccionadas = random.sample(preguntas_filtradas, limite)
        
    return render_template("examen.html", preguntas=preguntas_seleccionadas)

# Esta ruta recibe el formulario de universidades.html y arma el examen de la UNAM
@app.route("/configurar_examen", methods=["POST"])
def configurar_examen():
    cantidad = int(request.form.get("cantidad", 10))
    tiempo_minutos = cantidad 
    
    banco_completo = cargar_preguntas_unam()
    num_preguntas = min(cantidad, len(banco_completo))
    preguntas_examen = random.sample(banco_completo, num_preguntas)
    
    return render_template("examen.html", preguntas=preguntas_examen, tiempo=tiempo_minutos)

# Ruta que procesa las respuestas del alumno y calcula el puntaje (Soporta UNAM e IPN)
@app.route("/calificar_examen", methods=["POST"])
def calificar_examen():
    # Unimos ambos bancos de preguntas para que pueda calificar cualquier examen sin importar la universidad
    banco_completo = cargar_preguntas_unam() + cargar_preguntas_ipn()
    
    aciertos = 0
    total_preguntas = 0
    resultados = []
    
    # Revisamos cada pregunta para ver si el usuario la contestó
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

@app.route("/examen")
def examen():
    return render_template("examen.html", preguntas=[])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
