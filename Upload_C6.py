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
data_atual = datetime.today()
data_em_texto = f'{data_atual.day}/{data_atual.month}/{data_atual.year}'

def dt_parser(dt):
    if isinstance(dt, datetime):
        return dt.isoformat()

def ajusta_data(data_entrada):
    nova_data = datetime.strptime(data_entrada, f'%d/%m/%Y')
    dt_saida = datetime.strftime(nova_data, f'%d/%m/%Y')
    return dt_saida


def mover_arquivo(path_origem, path_destino, pasta=False, arquivo=''):
    if not Path(path_destino).is_dir():
        os.mkdir(path_destino)
        
    if pasta:
        for item in [join(path_origem, f) for f in listdir(path_origem) if isfile(join(path_origem, f)) ]:
            log.info(f"Movendo arquivo de: {path_origem} para: {path_destino}.")
            shutil.move(item, join(path_destino, basename(item)))
            log.info('Movido com sucesso: "{}" -> "{}"'.format(item, join(path_destino, basename(item))))
    else:
        log.info(f"Movendo arquivo de: {path_origem} para: {path_destino}.")
        shutil.move(path_origem + arquivo, join(path_destino + arquivo))
        log.info('Movido com sucesso: "{}" -> "{}"'.format(path_origem + arquivo , join(path_destino, join(path_destino + arquivo))))



def arquivos_existentes(caminho):
    #caminho da pasta que está sendo monitorada.
    caminho_pasta = caminho
    #retorna a lista de arquivos dentro da pasta ignorando as subpastas
    lista_de_arquivos = [f for f in listdir(caminho_pasta) if isfile(join(caminho_pasta, f))]
    #conectando na fila do rabbitmq
    con_fila = Produtor.ConectaRabbit(data.retorna_host_rabbitmq())
    canal = Produtor.CriarCanal(con_fila)
    contador_fila = 0
    log.info(f'Aquivos encontrados na pasta')
    for arquivo in lista_de_arquivos:
        try:
            if not os.path.isdir(caminho + arquivo):
                origem = caminho + arquivo                
            
                arquivo_analisado = _destino + pathlib.Path(origem).name
                nome_arquivo = os.path.basename(origem)
                contador_fila += 1

                #Regex do padrão CNJ para identificar o numero do processo dentro do nome do arquivo
                regex = "\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4}"
                #verificando se existe o padrão CNJ dentro do nome do arquivo.
                encontrou_cnj = re.search(regex, nome_arquivo)
                up = Upload()
                
                if encontrou_cnj:
                    #método que retorna o padrão encontrado dentro do regex (retorna uma lista)
                    cnj_processo = re.findall(regex,nome_arquivo)
                    #testar se a lista tem valor
                    if cnj_processo:
                        up.NumeroProcesso = cnj_processo[0]
                        up.CaminhoArquivo = arquivo_analisado
                        up.NomeArquivo = nome_arquivo
                        up.DataCriacao = dt_parser(datetime.strptime(data_em_texto,"%d/%m/%Y"))
                        up.Status = 0
                
                        #chamar o método que move o arquivo da pasta monitorada para a pasta de "fila"
                        mover_arquivo(caminho, _destino, False, arquivo)
                        log.info(f"Criando mensagem com o conteúdo: {j.dumps(para_dict(up))}")
                        #comando que realiza o cadastro na fila do Rabbit
                        Produtor.CriaMensagem(canal, "UploadC6", j.dumps(para_dict(up)), True)
                        #Inserindo o registro no Mongo
                        tabelamongo.insert_one(para_dict(up))
                        
        except Exception as e:
            log.info(e)

    Produtor.FechaConRabbit(con_fila)
    
#Classe Main da aplicação 
if __name__ == "__main__":
    #Caminho da pasta monitorada
    log.info(f"Iniciando Monitoramento na pasta: {_origem}")
    arquivos = arquivos_existentes(_origem)

    
