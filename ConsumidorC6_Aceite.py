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
    doc = conexao_mongo.find_one({"NumeroProcesso": processo})
    if doc:
        doc['Status'] = status
        doc['DataAceite'] = data_em_texto
        doc['Critica'] = critica
        conexao_mongo.update_one({"_id": doc['_id']}, {"$set": doc}, upsert=False)


def callback(ch, method,properties, body):
    try:
        ret = Retorno_Inatividade()
        log.info("[x] Dados recebidos:  %r" % body.decode())
        status = -1
        #Chamando os métodos que fazem o tratamento antes do upload
        json_eba = json.loads(body.decode())
        a = Aceite()
        a.NumeroProcesso = json_eba['NumeroProcesso']
        a.DataAceite = json_eba['DataAceite']
        a.Status = json_eba['Status']

        log.info('[*] Chamando o método que realiza o Aceite')
        
        
        ret = cert.consulta_processo_aceite(a)
        
        if ret is not None and ret.ativo:
            if ret.processo:
                atualiza_mongo(mycol, a.NumeroProcesso, 1, f"Aceite do processo: {a.NumeroProcesso} - realizado")
                log.info(f"[x] Aceite:{a.NumeroProcesso} - realizado")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                atualiza_mongo(mycol, a.NumeroProcesso, 2,f"Aceite do processo: {a.NumeroProcesso} - não realizado")
                log.info(f"[x] Aceite:{a.NumeroProcesso} - não realizado")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                #!Alocando para fila de erro. 
                channel2.basic_publish(exchange='', routing_key='AceiteErro', body=json.dumps(a.__dict__))
        else:
            ret.processo = False
            while ret.processo == False:
                ret = cert.login_portal()
            
                atualiza_mongo(mycol, a.NumeroProcesso, 2,f"Aceite do processo: {a.NumeroProcesso} - não realizado")
                log.info(f"[x] Aceite:{a.NumeroProcesso} - não realizado")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                #!Alocando para fila de erro. 
                channel2.basic_publish(exchange='', routing_key='AceiteErro', body=json.dumps(a.__dict__))
                
    except:
        ret.processo = False
        while ret.processo == False:
            ret = cert.login_portal()
        
            atualiza_mongo(mycol, a.NumeroProcesso, 2,f"Aceite do processo: {a.NumeroProcesso} - não realizado")
            log.info(f"[x] Aceite:{a.NumeroProcesso} - não realizado")
            ch.basic_ack(delivery_tag=method.delivery_tag)  
            #!Alocando para fila de erro. 
            channel2.basic_publish(exchange='', routing_key='AceiteErro', body=json.dumps(a.__dict__))  



if __name__ == "__main__":

        log = Logs.RetornaLog("--ConsumidorFila: C6 | Aceite--")
        j = appConfig()
        cert = Libs.Robos.C6()
        
        host = j.retorna_host_rabbitmq()
        mongoconexao = j.retorna_mongodb_conexao()
        mongobanco = j.retorna_mongodb_banco()
        mongocolecao = j.retorna_mongodb_colecao_aceite()

        myclient = pymongo.MongoClient(mongoconexao)
        mydb = myclient[mongobanco]
        mycol = mydb[mongocolecao]

        data_atual = date.today()
        data_em_texto = f'{data_atual.day}/{data_atual.month}/{data_atual.year}'
        
        
        ret.processo = False
        while ret.processo == False:
            ret = cert.login_portal()

        connection = BlockingConnection(ConnectionParameters(host=host))
        log.info('[*] Abrindo conexão...')
        channel = connection.channel()
        log.info('[*] Criando canal...')
        channel.queue_declare(queue='Aceite', passive=False,durable=True, exclusive=False, auto_delete=False)
        log.info('[*] Setando a fila e preparando para consumo...')
        log.info('[*] Aguardando para consumo...')
        
        #*Criando mais um canal de fila de erro, para alocar possíveis falhas para lá. 
        channel2 = connection.channel()
        channel2.queue_declare(queue='AceiteErro', passive=False,durable=True, exclusive=False, auto_delete=False)
        log.info('[*] Setando a fila de erro e preparando para consumo...')
        log.info('[*] Aguardando para consumo...')

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='Aceite',on_message_callback=callback)
        channel.start_consuming()

