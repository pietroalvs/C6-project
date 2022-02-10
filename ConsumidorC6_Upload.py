from pika import *
from Libs.Logs import Logs
from Libs.AppConfig import appConfig
import Libs.Robos
from Libs.Classes import *
import json
import pymongo
from datetime import date

ret = Retorno_Inatividade()


def atualiza_mongo(conexao_mongo, processo, status, critica):
    doc = conexao_mongo.find_one({"NumeroProcesso": processo, "Status": 0})
    if doc:
        doc['Status'] = status
        doc['DataSubsidio'] = data_em_texto
        doc['Critica'] = critica
        conexao_mongo.update_one({"NumeroProcesso": processo, "Status": 0}, {"$set": doc}, upsert=False)


def callback(ch, method, body):
    try:
        log.info("[x] Dados recebidos:  %r" % body.decode())
        status = -1
        #Chamando os métodos que fazem o tratamento antes do upload
        #!Aqui nesse trecho, estamos pegando o Json da fila e serializando para o objeto up (Upload)
        json_fila = json.loads(body.decode())
        up = Upload()
        up.NumeroProcesso = json_fila['NumeroProcesso']
        up.DataCriacao = json_fila['DataSubsidio']
        up.Status = json_fila['Status']

        log.info('[*] Chamando o método que realiza o upload do arquivo')

        ret = cert.lancamento_processo_subsidio(a)

        if ret is not None and ret.ativo:
            if ret.processo:
                atualiza_mongo(mycol, a.NumeroProcesso, 1, f"Subsídio do processo: {a.NumeroProcesso} - realizado")
                log.info(f"[x] Subsídio:{a.NumeroProcesso} - realizado")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                atualiza_mongo(mycol, a.NumeroProcesso, 2,f"Subsídio do processo: {a.NumeroProcesso} - não realizado")
                log.info(f"[x] Subsídio:{a.NumeroProcesso} - não realizado")
                ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            ret.processo = False
            while ret.processo == False:
                ret = cert.login_portal()
            
                atualiza_mongo(mycol, a.NumeroProcesso, 2,f"Subsídio do processo: {a.NumeroProcesso} - não realizado")
                log.info(f"[x] Subsídio:{a.NumeroProcesso} - não realizado")
                ch.basic_ack(delivery_tag=method.delivery_tag)
    except:
        ret.processo = False
        while ret.processo == False:
            ret = cert.login_portal()
            atualiza_mongo(mycol, a.NumeroProcesso, 2,f"Subsídio do processo: {a.NumeroProcesso} - não realizado")
            log.info(f"[x] Subsídio:{a.NumeroProcesso} - não realizado")
            ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":

    #cria o objeto de log
    log = Logs.RetornaLog("--Consumidor Fila: C6 | Uploads--")
    #cria o objeto de configuração do sistema
    j = appConfig()
    #Cria o objeto da lib dos robos 
    cert = Libs.Robos.C6()
    
    #pega os dados de conexão do Rabbit e Mongo
    host = j.retorna_host_rabbitmq()
    mongoconexao = j.retorna_mongodb_conexao()
    mongobanco = j.retorna_mongodb_banco()
    
    #cria o Objeto que vai manipular o Mongo
    myclient = pymongo.MongoClient(mongoconexao)
    mydb = myclient[mongobanco]
    mycol = mydb['Upload']

    #pegando a data do dia e transformando em texto
    data_atual = date.today()
    data_em_texto = f'{data_atual.day}/{data_atual.month}/{data_atual.year}'
    
    #!tratamento do Xgracco para login. é um laço que enquanto o ret.processo não for igual a verdade ele não sai daqui. 
    ret.processo = False
    while ret.processo == False:
        ret = cert.login_portal()
    
    #Chama os dados para o consumo da fila
    connection = BlockingConnection(ConnectionParameters(host=host))
    log.info('[*] Abrindo conexão...')
    channel = connection.channel()
    log.info('[*] Criando canal...')
    channel.queue_declare(queue='UploadC6', passive=False,durable=True, exclusive=False, auto_delete=False)
    log.info('[*] Setando a fila e preparando para consumo...')
    log.info('[*] Aguardando para consumo...')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='UploadC6',on_message_callback=callback)
    channel.start_consuming()
