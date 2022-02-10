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


def callback(ch, method,properties, body):
    try:
        log.info("[x] Dados recebidos:  %r" % body.decode())
        status = -1
        #Chamando os métodos que fazem o tratamento antes do upload
        json_eba = json.loads(body.decode())
        a = Subsidio()
        a.NumeroProcesso = json_eba['NumeroProcesso']
        a.DataSubsidio = json_eba['DataSubsidio']
        a.Status = json_eba['Status']

        log.info('[*] Chamando o método que realiza o lancamento de subsídio')

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

    
    log = Logs.RetornaLog("--ConsumidorFila: C6 | Subsidio--")
    j = appConfig()
    cert = Libs.Robos.C6()
    
    host = j.retorna_host_rabbitmq()
    mongoconexao = j.retorna_mongodb_conexao()
    mongobanco = j.retorna_mongodb_banco()
    #mongocolecao = j.retorna_mongodb_colecao_subssidio()

    myclient = pymongo.MongoClient(mongoconexao)
    mydb = myclient[mongobanco]
    mycol = mydb['Subsidio']

    data_atual = date.today()
    data_em_texto = f'{data_atual.day}/{data_atual.month}/{data_atual.year}'
    
    ret.processo = False
    while ret.processo == False:
        ret = cert.login_portal()
        
    connection = BlockingConnection(ConnectionParameters(host=host))
    log.info('[*] Abrindo conexão...')
    channel = connection.channel()
    log.info('[*] Criando canal...')
    channel.queue_declare(queue='Subsidio', passive=False,durable=True, exclusive=False, auto_delete=False)
    log.info('[*] Setando a fila e preparando para consumo...')
    log.info('[*] Aguardando para consumo...')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='Subsidio',on_message_callback=callback)
    channel.start_consuming()
