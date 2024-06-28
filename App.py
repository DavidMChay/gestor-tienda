#ACTIVAR ENTORNO VIRTUAL - TODOS LOS COMANDOS SE EJECUTAN EN LA TERMINAL
#1. Set-ExecutionPolicy Unrestricted -Scope Process
#2. .\env\Scripts\activate
#ACTIVAR SERVDOR DE PYTHON
#1. flask run --port 8000
#Nota: Esto se hace dentro de la carpeta donde se encuentra el archivo App.py

# app.py
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True)
