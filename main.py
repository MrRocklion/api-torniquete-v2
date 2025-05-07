from flask import Flask, request, jsonify, abort,render_template
import threading
from rs232 import rs232Comunication
from MecanismLogic import Manager
from database.SqliteManager import SqliteManager


#version 4.0
app = Flask(__name__)
stop_event = threading.Event()


@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    if request.method == 'POST':
        operation = request.form.get('operation')
        if operation == 'read_sensor':
            estado = manager.read_sensor()
            result = f'sensor: {estado}'
        elif operation == 'generate_pass':
            manager.generate_pass()
            result = f'Pase Normal generado'
        elif operation == 'generate_special_pass':
            manager.generate_special_pass()
            result = f'Pase Especial generado'
        elif operation == 'test_lock':
            manager.test_lock()
            result = 'Cerradura Testeada Con Exito'
        elif operation == 'test_arrow_light':
            manager.test_arrow_light()
            result = 'Luz Led Testeada Con Exito'
        else:
            result = f'Error Operacion No existente'
    return render_template('home.html', result=result)
    
@app.route("/datos")
def datos():
    return rs232.getData()

if __name__ == "__main__":
    rs232 = rs232Comunication( stop_event=stop_event)
    manager = Manager(stop_event=stop_event,rs232=rs232)

    database = SqliteManager(stop_event=stop_event,rs232=rs232) 
    rs232.start()
    manager.start()
    database.start()


    try:
        app.run(host='0.0.0.0', port=5000,use_reloader=False)
    finally:
        stop_event.set()
        rs232.join()
        manager.join()
        database.join()
        # audio.join()
        print("programa terminado!")

#'/dev/ttyUSB0'
#'/dev/ttyACM0'