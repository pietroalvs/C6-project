from datetime import date
from typing import Text
from psycopg2 import connect
from Libs.AppConfig import appConfig
import pika
from Libs.Logs import Logs
from Libs.Classes import *
import re
import pymongo
from openpyxl import load_workbook
import json
from mongoengine import*
import tkinter as tk
from tkinter import Button, messagebox, filedialog, Label, Listbox, Scrollbar, Frame
from tkinter.constants import *
from datetime import date

#Variáveis usadas no contexto. 
#log
log = Logs.RetornaLog("--C6 Bank--")
#Informações coletadas do arquivo AppConfig.json
j = appConfig()
#Data
data_atual = date.today()
data_em_texto = f'{data_atual.day}/{data_atual.month}/{data_atual.year}'
#Retorna o caminho do host do RabbitMQ
host = j.retorna_host_rabbitmq()
mongoconexao = j.retorna_mongodb_conexao()
mongobanco = j.retorna_mongodb_banco()
#mongocolecao = j.retorna_mongodb_colecao_aceite()
myclient = pymongo.MongoClient(mongoconexao)
mydb = myclient[mongobanco]
mycol = mydb['Subsidio']

connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
channel = connection.channel()

channel.queue_declare(queue='Subsidio', durable=True)
channel.queue_purge(queue='Subsidio')


def inicializa_rotinas():
    #Abrindo o Banco para verificar processos existentes
    documentos_existentes = mycol.find({"Status":0})
    contador = 0
    if documentos_existentes:
        regex = "^\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4}"
        for documento in documentos_existentes:
            resultado = re.match(regex, documento['NumeroProcesso'])
            if resultado:
                contador += 1
                a = Subsidio()
                a.NumeroProcesso = documento['NumeroProcesso']
                a.DataSubsidio = documento['DataSubsidio']
                a.Status = documento['Status']
                a.Critica = documento['Critica']

                channel.basic_publish(exchange='', routing_key='Subsidio', body=json.dumps(a.__dict__))
                log.info(json.dumps(a.__dict__))
    if contador > 0:
        listNodes.insert(END, f'Foram encontrados:{contador} processos existentes na base que foram realocados na fila')
    else:
        listNodes.insert(END, f'Não foram encontrados processos na base de dados.')

def executa_acao_subsidio():

    arquivo = filedialog.askopenfilename()
    if arquivo:
        
        arquivo_excel = load_workbook(arquivo)
    
        pla1 = arquivo_excel.active
        # Selecionando a coluna que quero para validar os processos e depois escrever nas colunas
        processos = pla1["A"]
        
        if processos:
            # definindo o pattern regex dos processos
            regex = "^\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4}"
            
            for x in range(len(processos)):
                resultado = re.match(regex, processos[x].value)
                if resultado:
                    encontrou = mycol.find_one({"NumeroProcesso": processos[x].value, "Status":0})
                    if not encontrou:
                        a = Subsidio()
                        a.NumeroProcesso = processos[x].value
                        a.DataSubsidio = data_em_texto
                        a.Status = 0
                        a.Critica = ''
                        mycol._insert(para_dict(a), op_id=a.NumeroProcesso)
                        channel.basic_publish(exchange='', routing_key='Subsidio', body=json.dumps(a.__dict__))
                        log.info(json.dumps(a.__dict__))
                        listNodes.insert(END, json.dumps(a.__dict__))

            arquivo_excel.close()
    else:
        messagebox.showerror("Erro","É necessário selecionar uma planilha para o acionamento do robô.")

#Janela Principal
window = tk.Tk()
window["bg"] = "white"
window.title("Interface do Robô do C6 - Subsídios")
window.geometry("530x300")

#Label inicial 
label = Label(window, text='Selecione o local onde está a planilha de Subsídios para gerar a fila do robô.' ,background="white" )
label.grid(row=1, column=0, ipadx='1', ipady='5', padx='1', pady='5')

#Botão com ação
B = Button(window, text="Acionar a Fila de Subsídios", command=executa_acao_subsidio)
B.grid(row=2, column=0, ipadx='1', ipady='5', padx='1', pady='5')
B.place(x=5,y=40)

#Frame para encaixar a list e o Scroll
frame = Frame(window)
frame.grid(row=2, column=0, ipadx='1', ipady='5', padx='1', pady='5')
frame.place(x=5, y=90)
#lista
listNodes = Listbox(frame, width=80, font=("Helvetica", 8))
listNodes.pack(side="left", fill="y")
#scroll
scrollbar = Scrollbar(frame, orient='vertical')
scrollbar.config(command=listNodes.yview)
scrollbar.pack(side="right", fill="y")
#Associação
listNodes.config(yscrollcommand=scrollbar.set)

inicializa_rotinas()
window.mainloop()




