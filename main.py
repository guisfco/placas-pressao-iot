from flask import Flask, render_template, jsonify, request
import paho.mqtt.publish as publish
import sqlite3
import datetime

app = Flask(__name__)

mqtt_broker = "broker.example.com" # todo: alterar para o broker correto
mqtt_port = 1883

DB_NAME = 'data.db'

SENSORES_D_ATUAL = 51.0 # todo: popular com valores recebidos do tópico
SENSORES_E_ATUAL = 50.9 # todo: popular com valores recebidos do tópico

def calcular_diferenca_sensores(d, e):
    return round(abs(float(d) - float(e)), 3)

def calcular_predominante(d, e):
    d = float(d)
    e = float(e)

    if d > e:
        return 'Direito'
    elif e > d:
        return 'Esquerdo'
    else:
        return '-'

def criar_tabela():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicoes (
            id INTEGER PRIMARY KEY,
            paciente TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            sensores_d DECIMAL(6,3) NOT NULL,
            sensores_e DECIMAL(6,3) NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

criar_tabela()

@app.route('/api/<paciente>', methods=['POST'])
def salvar_medicao(paciente=None):
    sensores_d = request.json['sensoresD']
    sensores_e = request.json['sensoresE']

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO medicoes (paciente, timestamp, sensores_d, sensores_e) VALUES (?, ?, ?, ?)', (paciente, datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), sensores_d, sensores_e))
        conn.commit()
        conn.close()

        response = {'mensagem': 'Medição inserida com sucesso!'}
        return jsonify(response)

    except Exception as e:
        response = {'mensagem': str(e)}
        return jsonify(response), 500

@app.route('/api/<paciente>/<medicao>', methods=['DELETE'])
def deletar_medicao(paciente=None, medicao=None):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM medicoes WHERE paciente = ? AND id = ?', (paciente, medicao,))
        conn.commit()
        conn.close()

        response = {'mensagem': 'Medição deletada com sucesso!'}
        return jsonify(response)

    except Exception as e:
        response = {'mensagem': str(e)}
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
                    'sensoresD': row[3], 
                    'sensoresE': row[4], 
                    'diferenca': calcular_diferenca_sensores(row[3], row[4]), 
                    'predominante': calcular_predominante(d=row[3], e=row[4])
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
    dados = {
        'sensoresD': SENSORES_D_ATUAL,
        'sensoresE': SENSORES_E_ATUAL,
        'diferenca': calcular_diferenca_sensores(SENSORES_D_ATUAL, SENSORES_E_ATUAL),
        'predominante': calcular_predominante(d=SENSORES_D_ATUAL, e=SENSORES_E_ATUAL)
    }

    return render_template("medicao.html", dados=dados)

if __name__ == '__main__':
    app.run(debug=True)
