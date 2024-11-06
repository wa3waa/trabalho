import re
from datetime import datetime

class Cliente:
    def __init__(self, nome, telefone):
        self.nome = nome
        self.telefone = telefone
    
    def __str__(self):
        return f"{self.nome} - {self.telefone}"

class Barbearia:
    def __init__(self):
        self.clientes = {}
        self.agendamentos = {}
    
    def cadastrar_cliente(self, nome, telefone):
        if not self._validar_telefone(telefone):
            print("Telefone inválido. O formato deve ser (XX) XXXXX-XXXX.")
            return
        
        cliente = Cliente(nome, telefone)
        self.clientes[nome.lower()] = cliente
        print(f"Cliente {nome} cadastrado com sucesso!")
    
    def _validar_telefone(self, telefone):
        return re.match(r'^\(\d{2}\) \d{5}-\d{4}$', telefone)
    
    def listar_clientes(self):
        if not self.clientes:
            print("Nenhum cliente cadastrado.")
            return
        
        print("Clientes cadastrados:")
        for cliente in self.clientes.values():
            print(cliente)
    
    def agendar_atendimento(self, nome_cliente, data_hora):
        nome_cliente = nome_cliente.lower()
        
        if nome_cliente not in self.clientes:
            print(f"Cliente {nome_cliente} não encontrado.")
            return
        
        if not self._validar_data_hora(data_hora):
            print("Data e hora inválidas. O formato correto é AAAA-MM-DD HH:MM.")
            return
        
        if data_hora in self.agendamentos:
            print(f"Já existe um agendamento para {self.agendamentos[data_hora].nome} em {data_hora}.")
            return
        
        self.agendamentos[data_hora] = self.clientes[nome_cliente]
        print(f"Agendamento confirmado para {self.clientes[nome_cliente].nome} em {data_hora}.")
    
    def _validar_data_hora(self, data_hora):
        try:
            data_hora_obj = datetime.strptime(data_hora, "%Y-%m-%d %H:%M")
            if data_hora_obj < datetime.now():
                print("A data e hora não podem ser no passado.")
                return False
            return True
        except ValueError:
            return False
    
    def listar_agendamentos(self):
        if not self.agendamentos:
            print("Nenhum agendamento encontrado.")
            return
        
        print("Atendimentos agendados:")
        for data_hora, cliente in sorted(self.agendamentos.items()):
            print(f"{data_hora}: {cliente.nome}")

    def cancelar_agendamento(self, data_hora):
        if data_hora in self.agendamentos:
            cliente = self.agendamentos.pop(data_hora)
            print(f"Agendamento de {cliente.nome} para {data_hora} cancelado com sucesso.")
        else:
            print(f"Não há agendamento para o horário {data_hora}.")

def exibir_menu():
    print("\nSistema de Agendamentos da Barbearia")
    print("1. Cadastrar Cliente")
    print("2. Listar Clientes")
    print("3. Agendar Atendimento")
    print("4. Listar Agendamentos")
    print("5. Cancelar Agendamento")
    print("6. Sair")

def obter_opcao():
    return input("Escolha uma opção: ")

def processar_opcao(opcao, barbearia):
    if opcao == '1':
        nome = input("Digite o nome do cliente: ")
        telefone = input("Digite o telefone do cliente (ex: (XX) XXXXX-XXXX): ")
        barbearia.cadastrar_cliente(nome, telefone)
    elif opcao == '2':
        barbearia.listar_clientes()
    elif opcao == '3':
        nome_cliente = input("Digite o nome do cliente: ")
        data_hora = input("Digite a data e hora do atendimento (ex: 2024-10-10 15:30): ")
        barbearia.agendar_atendimento(nome_cliente, data_hora)
    elif opcao == '4':
        barbearia.listar_agendamentos()
    elif opcao == '5':
        data_hora = input("Digite a data e hora do agendamento a ser cancelado (ex: 2024-10-10 15:30): ")
        barbearia.cancelar_agendamento(data_hora)
    elif opcao == '6':
        print("Saindo do sistema...")
        return False
    else:
        print("Opção inválida! Tente novamente.")
    return True

def main():
    barbearia = Barbearia()
    
    while True:
        exibir_menu()
        opcao = obter_opcao()
        if not processar_opcao(opcao, barbearia):
            break

if __name__ == "__main__":
    main()
