import re
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Para gerenciar as mensagens de erro e sucesso

class SistemaBarbearia:
    def __init__(self, banco_dados='barbearia.db'):
        self.banco_dados = banco_dados
        self.conn = sqlite3.connect(self.banco_dados)
        self.cursor = self.conn.cursor()
        self.criar_tabelas()

    def criar_tabelas(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                nome TEXT NOT NULL,
                                telefone TEXT NOT NULL)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS agendamentos (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                cliente_id INTEGER NOT NULL,
                                data_hora TEXT NOT NULL,
                                FOREIGN KEY (cliente_id) REFERENCES clientes(id))''')
        self.conn.commit()

    def cadastrar_cliente(self, nome, telefone):
        if not self.validar_telefone(telefone):
            return False
        self.cursor.execute("INSERT INTO clientes (nome, telefone) VALUES (?, ?)", (nome, telefone))
        self.conn.commit()
        return True

    def validar_telefone(self, telefone):
        return re.match(r'^\(\d{2}\) \d{5}-\d{4}$', telefone)

    def listar_clientes(self):
        self.cursor.execute("SELECT id, nome, telefone FROM clientes")
        return self.cursor.fetchall()

    def agendar_atendimento(self, nome_cliente, data_hora):
        self.cursor.execute("SELECT id, nome FROM clientes WHERE nome = ?", (nome_cliente,))
        cliente = self.cursor.fetchone()

        if not cliente:
            return False

        if not self.validar_data_hora(data_hora):
            return False

        self.cursor.execute("SELECT * FROM agendamentos WHERE data_hora = ?", (data_hora,))
        agendamento_existente = self.cursor.fetchone()

        if agendamento_existente:
            return False

        self.cursor.execute("INSERT INTO agendamentos (cliente_id, data_hora) VALUES (?, ?)", (cliente[0], data_hora))
        self.conn.commit()
        return True

    def validar_data_hora(self, data_hora):
        try:
            data_hora_obj = datetime.strptime(data_hora, "%Y-%m-%d %H:%M")
            if data_hora_obj < datetime.now():
                return False
            return True
        except ValueError:
            return False

    def listar_agendamentos(self):
        self.cursor.execute('''SELECT agendamentos.data_hora, clientes.nome
                               FROM agendamentos
                               JOIN clientes ON agendamentos.cliente_id = clientes.id
                               ORDER BY agendamentos.data_hora''')
        return self.cursor.fetchall()

    def cancelar_agendamento(self, data_hora):
        self.cursor.execute("SELECT * FROM agendamentos WHERE data_hora = ?", (data_hora,))
        agendamento = self.cursor.fetchone()

        if agendamento:
            self.cursor.execute("DELETE FROM agendamentos WHERE data_hora = ?", (data_hora,))
            self.conn.commit()
            return True
        return False

    def fechar_conexao(self):
        self.conn.close()

# Página principal (exibe todos os agendamentos)
@app.route('/')
def index():
    sistema = SistemaBarbearia()
    agendamentos = sistema.listar_agendamentos()
    sistema.fechar_conexao()
    return render_template('index.html', agendamentos=agendamentos)

# Formulário de cadastro de cliente
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        sistema = SistemaBarbearia()
        if sistema.cadastrar_cliente(nome, telefone):
            flash(f"Cliente {nome} cadastrado com sucesso!", "success")
        else:
            flash("Erro ao cadastrar cliente. Verifique o formato do telefone.", "error")
        sistema.fechar_conexao()
        return redirect(url_for('cadastro'))
    
    return render_template('cadastro.html')

# Página para agendar atendimento
@app.route('/agendamento', methods=['GET', 'POST'])
def agendamento():
    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        data_hora = request.form['data_hora']
        sistema = SistemaBarbearia()
        if sistema.agendar_atendimento(nome_cliente, data_hora):
            flash(f"Agendamento confirmado para {nome_cliente} em {data_hora}.", "success")
        else:
            flash("Erro ao agendar. Verifique o nome do cliente ou o horário.", "error")
        sistema.fechar_conexao()
        return redirect(url_for('agendamento'))
    
    return render_template('agendamentos.html')

# Função para cancelar um agendamento
@app.route('/cancelar', methods=['POST'])
def cancelar():
    data_hora = request.form['data_hora']
    sistema = SistemaBarbearia()
    if sistema.cancelar_agendamento(data_hora):
        flash(f"Agendamento para {data_hora} cancelado com sucesso.", "success")
    else:
        flash(f"Erro ao cancelar o agendamento para {data_hora}.", "error")
    sistema.fechar_conexao()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


