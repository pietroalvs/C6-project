import json as j
import os
import pathlib
import re
import shutil
from datetime import datetime
from msilib.schema import Patch
from os import listdir
from os.path import basename, isfile, join
from pathlib import Path

import pymongo

from Libs.AppConfig import appConfig
from Libs.Classes import *
from Libs.Logs import Logs
from Libs.RabbitMQ import *
from Libs.Uteis import *

#instancia variavel de objeto de log
log = Logs.RetornaLog("--Upload de pastas C6--")

log.info("Iniciando operação")
log.info("Abrindo arquivo de configuração")

#instancia variavel de objeto de AppConfig
data = appConfig()
_origem = data.retorna_pasta_origem_copias()
_destino = data.retorna_pasta_nafila()


#instancia variavel de objeto de MongoDB (banco de dados)
mongoconexao = data.retorna_mongodb_conexao()
mongobanco = data.retorna_mongodb_banco()
mongocolecao = data.retorna_mongodb_colecao_upload()
#Cria o objeto de conexão com o Mongo
conexaomongo = pymongo.MongoClient(mongoconexao)
bancomongo = conexaomongo[mongobanco]
tabelamongo = bancomongo[mongocolecao]

#Data
data_atual = date.today()
data_em_texto = f'{data_atual.year}-{data_atual.month}-{data_atual.day}'


def arquivos_existentes(caminho):
    
    #conectando na fila do rabbitmq
    con_fila = Produtor.ConectaRabbit(data.retorna_host_rabbitmq())
    canal = Produtor.CriarCanal(con_fila)
   
    
        
    #!regex que trata a nomenclatura dos arquivos na pasta
    regex_argumento = "SENTENÇA EXTINÇÃO|SENTENÇA PROCEDENTE|SENTENÇA IMPROCEDENTE|SENTEÇA PARCIALMENTE PROCEDENTE"
    #!regex cnj
    regex_cnj = "^\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4}"
    #!Usar a lib Uteis que vou mandar para vcs.. colocar na pasta Libs
    #!Esse comando recebe o argumento do caminho da pasta a ser lida e retorna uma lista de arquivos nela contidos. 
    #! CAMINHO PASTA
    _caminho = r'\\10.67.0.24\\nj.11\\GED\\PORTAL\\NJ.05\\BANCO C6 CONSIGNADO S.A\\'
    lista = Uteis.listar_arquivos_pasta(_caminho)
    
    if lista:
        log.info(f'Aquivos encontrados na pasta')
        for l in lista:
            #!O Laço percorre a lista de arquivos. Aqui a gente separa tudo q precisa, cria o objeto da nossa fila. Ou seja, para cada arquivo lido no laço, a gente cria um objeto e separa as informações.
            objeto_fila = C6_Upload_Fila()
            objeto_fila.caminho_logico_arquivo = _caminho + l
            objeto_fila.status = 0
            objeto_fila.data_criacao = data_em_texto
            
            #! aqui vamos usar o split com a lógica de separar os nomes, porque usam "-" para separar, então a gente aproveita isso 
            lista_arquivos  = l.split('-',1) #!quebra apenas no primeiro "-" porque senão bagunça o CNJ
            
            if lista_arquivos:
                
                #!Verificação de argumento *** Pietro aqui é melhor a gente verificar, e não no código do robô em si. 
                regex_consulta = re.search(regex_argumento, lista_arquivos[0])
                if regex_consulta != None:
                    objeto_fila.argumento = 1
                else:
                    objeto_fila.argumento = 2
                    
                teste_regex = re.search(regex_cnj, lista_arquivos[1].strip())
                if teste_regex:
                    objeto_fila.numero_processo = re.findall(regex_cnj, lista_arquivos[1].strip())[0]

                #!INSERIU NO BANCO CERTINHO 
                tabelamongo.insert_one(para_dict(objeto_fila))
                
                canal.basic_publish(exchange='', routing_key='UploadC6', body=json.dumps(para_dict(objeto_fila)))
                
    Produtor.FechaConRabbit(con_fila)
    
#Classe Main da aplicação 
if __name__ == "__main__":
    #Caminho da pasta monitorada
    log.info(f"Iniciando Monitoramento na pasta: {_origem}")
    arquivos = arquivos_existentes(_origem)

    
