from flask import Flask, render_template, request, jsonify
import sqlite3
import requests
import time
from datetime import datetime, timedelta

app = Flask(__name__)
DB_NAME = 'database.db'


# Configurações do Telegram Bot
TELEGRAM_TOKEN = '8788574905:AAEodIH8WuujPpyfW5yKM30wNh4ExttSEPM'
TELEGRAM_CHAT_ID = '982393154'

def inicializar_db():
    """Garante que a tabela existe no banco de dados"""
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras_sensor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperatura REAL NOT NULL,
            umidade REAL NOT NULL,
            status_risco TEXT NOT NULL,
            data_hora TEXT NOT NULL
        )
    ''')
    conexao.commit()
    cursor.close()
    conexao.close()

# Executa a criação da tabela assim que o app inicia
inicializar_db()

ultimo_envio_telegram = 0
INTERVALO_ALERTA_SEGUNDOS = 30  #(30 segundos)

def enviar_alerta_telegram(mensagem):
    """Função para disparar notificação via Telegram respeitando um intervalo de tempo"""
    global ultimo_envio_telegram

    if not TELEGRAM_TOKEN:
        return

    tempo_atual = time.time()

    # Verifica se já passou o tempo mínimo desde o último alerta enviado
    if (tempo_atual - ultimo_envio_telegram) < INTERVALO_ALERTA_SEGUNDOS:
        return  # Sai da função sem enviar para não lotar o chat

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': f"🚨 ALERTA SMART BOUTIQUE 🚨\n\n{mensagem}"
        }
        resposta = requests.post(url, json=payload, timeout=5)

        # Se enviou com sucesso, atualiza o relógio do último envio
        if resposta.status_code == 200:
            ultimo_envio_telegram = tempo_atual

    except Exception as e:
        print(f"Erro ao enviar mensagem no Telegram: {e}")

def conectar_db():
    return sqlite3.connect(DB_NAME)

@app.route('/')
def index():
    try:
        conexao = conectar_db()
        cursor = conexao.cursor()
        cursor.execute("SELECT id, temperatura, umidade, status_risco, data_hora FROM leituras_sensor ORDER BY id DESC LIMIT 1")
        row_ultima = cursor.fetchone()

        ultima_leitura = {'temperatura': 0, 'umidade': 0, 'status_risco': 'Aguardando dados...', 'data_hora': ''}
        if row_ultima:
            ultima_leitura = {'id': row_ultima[0], 'temperatura': row_ultima[1], 'umidade': row_ultima[2], 'status_risco': row_ultima[3], 'data_hora': row_ultima[4]}

        cursor.execute("SELECT id, temperatura, umidade, status_risco, data_hora FROM leituras_sensor ORDER BY id DESC LIMIT 20")
        rows_historico = cursor.fetchall()

        historico = [{'id': r[0], 'temperatura': r[1], 'umidade': r[2], 'status_risco': r[3], 'data_hora': r[4]} for r in rows_historico]

        cursor.close()
        conexao.close()
        return render_template('index.html', ultima=ultima_leitura, historico=historico)
    except Exception as e:
        return f"Erro: {e}"

@app.route('/api/dados_json', methods=['GET'])
def dados_json():
    try:
        conexao = conectar_db()
        cursor = conexao.cursor()

        cursor.execute("SELECT id, temperatura, umidade, status_risco, data_hora FROM leituras_sensor ORDER BY id DESC LIMIT 1")
        row_ultima = cursor.fetchone()
        ultima = {'temperatura': row_ultima[1] if row_ultima else 0, 'umidade': row_ultima[2] if row_ultima else 0, 'status_risco': row_ultima[3] if row_ultima else 'Aguardando', 'data_hora': row_ultima[4] if row_ultima else ''}

        cursor.execute("SELECT id, temperatura, umidade, status_risco, data_hora FROM leituras_sensor ORDER BY id DESC LIMIT 20")
        rows = cursor.fetchall()
        historico = [{'id': r[0], 'temperatura': r[1], 'umidade': r[2], 'status_risco': r[3], 'data_hora': r[4]} for r in rows]

        cursor.close()
        conexao.close()
        return jsonify({'ultima': ultima, 'historico': historico})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/dados', methods=['POST'])
def receber_dados():
    dados = request.get_json()
    if not dados or 'temperatura' not in dados or 'umidade' not in dados:
        return jsonify({'erro': 'Dados incompletos'}), 400

    temperatura = float(dados['temperatura'])
    umidade = float(dados['umidade'])

    # Verifica o risco de mofo
    if temperatura >= 28.0:         #if umidade >= 70.0 && temperatura >= 22.0:
        status_risco = "ALERTA: Risco de Mofo!"
        enviar_alerta_telegram(f"Atenção! Umidade crítica detectada na loja.\nUmidade: {umidade}%\nTemperatura: {temperatura}°C")
    else:
        status_risco = "Ambiente Seguro"

    try:
        # Gera o Horário de Brasília exato (UTC - 3 horas)
        fuso_brasilia = timedelta(hours=-3)
        horario_brasilia = datetime.utcnow() + fuso_brasilia
        data_hora_str = horario_brasilia.strftime('%d-%m-%Y %H:%M:%S')

        conexao = conectar_db()
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO leituras_sensor (temperatura, umidade, status_risco, data_hora) VALUES (?, ?, ?, ?)",
                       (temperatura, umidade, status_risco, data_hora_str))
        conexao.commit()
        cursor.close()
        conexao.close()
        return jsonify({'sucesso': True, 'status': status_risco}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)