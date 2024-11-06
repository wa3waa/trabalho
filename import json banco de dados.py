import re
import sqlite3
from datetime import datetime

class Cliente:
    def __init__(self, nome, telefone):
        self.nome = nome
        self.telefone = telefone
    
    def __str__(self):
        return f"{self.nome} - {self.telefone}"

class SistemaBarbearia:
    def __init__(self, banco_dados='barbearia.db'):
        self.banco_dados = banco_dados
        self.conn = sqlite3.connect(self.banco_dados)
        self.cursor = self.conn.cursor()
        self.criar_tabelas()

    def criar_tabelas(self):
        # Criação das tabelas no banco de dados
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
            print("Formato de telefone inválido. Utilize o formato (XX) XXXXX-XXXX.")
            return

        self.cursor.execute("INSERT INTO clientes (nome, telefone) VALUES (?, ?)", (nome, telefone))
        self.conn.commit()
        print(f"Cliente {nome} cadastrado com sucesso!")

    def validar_telefone(self, telefone):
        return re.match(r'^\(\d{2}\) \d{5}-\d{4}$', telefone)

    def listar_clientes(self):
        self.cursor.execute("SELECT id, nome, telefone FROM clientes")
        clientes = self.cursor.fetchall()

        if not clientes:
            print("Não há clientes cadastrados.")
            return

        print("Clientes cadastrados:")
        for cliente in clientes:
            print(f"{cliente[1]} - {cliente[2]}")

    def agendar_atendimento(self, nome_cliente, data_hora):
        self.cursor.execute("SELECT id, nome FROM clientes WHERE nome = ?", (nome_cliente,))
        cliente = self.cursor.fetchone()

        if not cliente:
            print(f"Cliente {nome_cliente} não encontrado.")
            return

        if not self.validar_data_hora(data_hora):
            print("Data e hora inválidas. Use o formato: AAAA-MM-DD HH:MM.")
            return

        self.cursor.execute("SELECT * FROM agendamentos WHERE data_hora = ?", (data_hora,))
        agendamento_existente = self.cursor.fetchone()

        if agendamento_existente:
            print(f"Já existe um agendamento para {nome_cliente} em {data_hora}.")
            return

        self.cursor.execute("INSERT INTO agendamentos (cliente_id, data_hora) VALUES (?, ?)", (cliente[0], data_hora))
        self.conn.commit()
        print(f"Agendamento confirmado para {nome_cliente} em {data_hora}.")

    def validar_data_hora(self, data_hora):
        try:
            data_hora_obj = datetime.strptime(data_hora, "%Y-%m-%d %H:%M")
            if data_hora_obj < datetime.now():
                print("A data e hora não podem ser no passado.")
                return False
            return True
        except ValueError:
            return False

    def listar_agendamentos(self):
        self.cursor.execute('''SELECT agendamentos.data_hora, clientes.nome
                               FROM agendamentos
                               JOIN clientes ON agendamentos.cliente_id = clientes.id
                               ORDER BY agendamentos.data_hora''')
        agendamentos = self.cursor.fetchall()

        if not agendamentos:
            print("Não há agendamentos no sistema.")
            return

        print("Agendamentos confirmados:")
        for agendamento in agendamentos:
            print(f"{agendamento[0]}: {agendamento[1]}")

    def cancelar_agendamento(self, data_hora):
        self.cursor.execute("SELECT * FROM agendamentos WHERE data_hora = ?", (data_hora,))
        agendamento = self.cursor.fetchone()

        if agendamento:
            self.cursor.execute("DELETE FROM agendamentos WHERE data_hora = ?", (data_hora,))
            self.conn.commit()
            print(f"Agendamento para {data_hora} cancelado com sucesso.")
        else:
            print(f"Não foi encontrado agendamento para o horário {data_hora}.")

    def fechar_conexao(self):
        self.conn.close()

def exibir_menu():
    print("\nBem-vindo ao sistema de agendamento da Barbearia!")
    print("Escolha uma das opções abaixo:")
    print("1. Cadastrar Cliente")
    print("2. Listar Clientes")
    print("3. Agendar Atendimento")
    print("4. Listar Agendamentos")
    print("5. Cancelar Agendamento")
    print("6. Sair")

def obter_opcao():
    return input("Digite sua opção: ")

def processar_opcao(opcao, sistema):
    if opcao == '1':
        nome = input("Digite o nome do cliente: ")
        telefone = input("Digite o telefone do cliente (ex: (XX) XXXXX-XXXX): ")
        sistema.cadastrar_cliente(nome, telefone)
    elif opcao == '2':
        sistema.listar_clientes()
    elif opcao == '3':
        nome_cliente = input("Digite o nome do cliente: ")
        data_hora = input("Digite a data e hora do atendimento (ex: 2024-10-10 15:30): ")
        sistema.agendar_atendimento(nome_cliente, data_hora)
    elif opcao == '4':
        sistema.listar_agendamentos()
    elif opcao == '5':
        data_hora = input("Digite a data e hora do agendamento que deseja cancelar (ex: 2024-10-10 15:30): ")
        sistema.cancelar_agendamento(data_hora)
    elif opcao == '6':
        print("Saindo... Até logo!")
        return False
    else:
        print("Opção inválida. Tente novamente.")
    return True

def main():
    sistema = SistemaBarbearia()

    while True:
        exibir_menu()
        opcao = obter_opcao()
        if not processar_opcao(opcao, sistema):
            break

    sistema.fechar_conexao()

if __name__ == "__main__":
    main()

