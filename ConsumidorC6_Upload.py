from pika import *
from Libs.Logs import Logs
from Libs.AppConfig import appConfig
import Libs.Robos
from Libs.Classes import *
import json
import pymongo
from datetime import date
from Libs.DB import *

ret = Retorno_Inatividade()



def callback(ch, method, propreties ,body):
    try:
        log.info("[x] Dados recebidos:  %r" % body.decode())
        status = -1
        #Chamando os métodos que fazem o tratamento antes do upload
        #!Aqui nesse trecho, estamos pegando o Json da fila e serializando para o objeto up (Upload)
        json_fila = json.loads(body.decode())
        up = C6_Upload_Fila()
        up.numero_processo = json_fila['numero_processo']
        up.data_criacao = json_fila['data_criacao']
        up.status = json_fila['status']
        up.argumento = json_fila['argumento']
        up.caminho_logico_arquivo = json_fila['caminho_logico_arquivo']
        

        log.info('[*] Chamando o método que realiza o upload do arquivo')

        ret = cert.lancamento_copias(up)

        if ret is not None and ret.ativo:
            if ret.processo:
                #!Atualiza o status 
                connmongo.atualiza_mongo({'numero_processo':up.numero_processo},{'status':1})
                log.info(f"[x] Upload:{up.numero_processo} - realizado")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                connmongo.atualiza_mongo({'numero_processo':up.numero_processo},{'status':2})
                log.info(f"[x] Upload:{up.numero_processo} - não realizado")
                ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            ret.processo = False
            while ret.processo == False:
                ret = cert.login_portal()
            
                connmongo.atualiza_mongo({'numero_processo':up.numero_processo},{'status':2})
                log.info(f"[x] Upload:{up.numero_processo} - não realizado")
                ch.basic_ack(delivery_tag=method.delivery_tag)
    except:
        ret.processo = False
        while ret.processo == False:
            ret = cert.login_portal()
            connmongo.atualiza_mongo({'numero_processo':up.numero_processo},{'status':2})
            log.info(f"[x] Upload:{up.numero_processo} - não realizado")
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
    mongocolecao = j.retorna_mongodb_colecao_upload()
    
    #cria o Objeto que vai manipular o Mongo
    #Conexão com o Mongo para gravaço dentro do receita_cad
    connmongo = Mongo(mongobanco, mongocolecao)
    
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
