from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/examen")
def examen():
    return render_template("examen.html")

@app.route("/universidades")
def universidades():
    return render_template("universidades.html")

@app.route("/consejos")
def consejos():
    return render_template("consejos.html")

if __name__ == "__main__":
    app.run(debug=True)
