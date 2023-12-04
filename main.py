from flask import Flask, render_template, jsonify, request
import paho.mqtt.publish as publish
import sqlite3
import datetime

app = Flask(__name__)

mqtt_broker = "broker.example.com"
mqtt_port = 1883

DB_NAME = 'data.db'

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicoes (
            id INTEGER PRIMARY KEY,
            paciente TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            sensor_1 DECIMAL NOT NULL,
            sensor_2 DECIMAL NOT NULL,
            sensor_3 DECIMAL NOT NULL,
            sensor_4 DECIMAL NOT NULL,
            sensor_5 DECIMAL NOT NULL,
            sensor_6 DECIMAL NOT NULL,
            sensor_7 DECIMAL NOT NULL,
            sensor_8 DECIMAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

create_table()

@app.route('/api/<paciente>', methods=['POST'])
def save(paciente=None):
    sensor_1 = request.json['sensor1']
    sensor_2 = request.json['sensor2']
    sensor_3 = request.json['sensor3']
    sensor_4 = request.json['sensor4']
    sensor_5 = request.json['sensor5']
    sensor_6 = request.json['sensor6']
    sensor_7 = request.json['sensor7']
    sensor_8 = request.json['sensor8']

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO medicoes (paciente, timestamp, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5, sensor_6, sensor_7, sensor_8) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (paciente, datetime.datetime.now(), sensor_1, sensor_2, sensor_3, sensor_4, sensor_5, sensor_6, sensor_7, sensor_8))
        conn.commit()
        conn.close()

        response = {'status': 'success', 'message': 'Data saved successfully'}
        return jsonify(response)

    except Exception as e:
        response = {'status': 'error', 'message': str(e)}
        return jsonify(response), 500

def obter_medicoes(paciente=None):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM medicoes WHERE paciente = ?', (paciente,))
        rows = cursor.fetchall()
        conn.close()

        data_list = []

        for row in rows:
            data_list.append(
                {
                    'id': row[0], 
                    'paciente': row[1], 
                    'timestamp': row[2], 
                    'sensor1': row[3], 
                    'sensor2': row[4], 
                    'sensor3': row[5], 
                    'sensor4': row[6], 
                    'sensor5': row[7], 
                    'sensor6': row[8], 
                    'sensor7': row[9], 
                    'sensor8': row[10]
                }
            )

        return data_list
    except Exception as e:
        return []

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/<paciente>')
def consulta(paciente=None):
    return render_template("consulta.html", paciente=paciente, medicoes=obter_medicoes(paciente))

@app.route('/<paciente>/medicao')
def medicao(paciente=None):
    sensores = {
        'sensor1': 0.0,
        'sensor2': 0.0,
        'sensor3': 0.0,
        'sensor4': 0.0,
        'sensor5': 0.0,
        'sensor6': 0.0,
        'sensor7': 0.0,
        'sensor8': 0.0
    }

    return render_template("medicao.html", sensores=sensores)

if __name__ == '__main__':
    app.run(debug=True)
