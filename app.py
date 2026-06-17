import os
import json
import random
from flask import Flask, render_template, request

app = Flask(__name__)

# Función centralizada y robusta para cargar archivos JSON
def cargar_datos(nombre_archivo):
    # Esto asegura que busque en la carpeta 'data' sin importar dónde se ejecute el script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base_dir, 'data', nombre_archivo)
    
    if os.path.exists(ruta):
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error de sintaxis en {nombre_archivo}: {e}")
            return []
    return []

# Funciones específicas para cada banco
def cargar_preguntas_unam(): return cargar_datos('unam.json')
def cargar_preguntas_ipn(): return cargar_datos('ipn.json')
def cargar_preguntas_uam(): return cargar_datos('uam.json')

def cargar_temarios():
    return cargar_datos('temarios.json')

@app.route("/")
def inicio(): return render_template("index.html")

@app.route("/universidades")
def universidades(): return render_template("universidades.html")

@app.route("/consejos")
def consejos(): return render_template("consejos.html")

@app.route("/study_center")
def study_center():
    return render_template("study_center.html", temarios=cargar_temarios())

@app.route("/configurar_examen", methods=["POST"])
def configurar_examen():
    universidad = request.form.get("universidad", "unam")
    cantidad = int(request.form.get("cantidad", 10))
    tiempo_minutos = cantidad 
    
    # Seleccionar banco
    if universidad == "ipn":
        banco_completo = cargar_preguntas_ipn()
    elif universidad == "uam":
        banco_completo = cargar_preguntas_uam()
    else:
        banco_completo = cargar_preguntas_unam()
        
    num_preguntas = min(cantidad, len(banco_completo))
    preguntas_examen = random.sample(banco_completo, num_preguntas) if num_preguntas > 0 else []
        
    return render_template("examen.html", preguntas=preguntas_examen, tiempo=tiempo_minutos)

@app.route("/calificar_examen", methods=["POST"])
def calificar_examen():
    # Unir bancos para calificar
    banco_completo = cargar_preguntas_unam() + cargar_preguntas_ipn() + cargar_preguntas_uam()
    
    aciertos = 0
    total_preguntas = 0
    resultados = []
    
    for pregunta in banco_completo:
        campo_name = f"pregunta_{pregunta['id']}"
        if campo_name in request.form:
            total_preguntas += 1
            request_usuario = request.form.get(campo_name)
            es_correcta = (request_usuario == pregunta['respuesta_correcta'])
            if es_correcta: aciertos += 1
                
            resultados.append({
                "materia": pregunta["materia"],
                "pregunta": pregunta["pregunta"],
                "respuesta_usuario": request_usuario,
                "respuesta_correcta": pregunta["respuesta_correcta"],
                "es_correcta": es_correcta
            })
            
    porcentaje = int((aciertos / total_preguntas) * 100) if total_preguntas > 0 else 0
    return render_template("resultados.html", aciertos=aciertos, total=total_preguntas, 
                           porcentaje=porcentaje, resultados=resultados)

@app.route("/examen")
def examen(): return render_template("examen.html", preguntas=[])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
