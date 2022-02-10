#!/usr/bin/env python
import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from Libs.Logs import Logs

log = Logs.RetornaLog("--ManipulaFila--")


class Produtor(object):

    def __init__(self) -> None:
        super().__init__()
        
    def ConectaRabbit(host_rabbit:str)->BlockingConnection:
        """Abre a conexão com o Rabbit MQ

        Args:
            host_rabbit (str): Endereço do servidor do Rabbit MQ

        Returns:
            BlockingConnection: Retorna a conexão aberta, ou o objeto nulo
        """
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host_rabbit, heartbeat=None, blocked_connection_timeout=30))
            log.info("Conexão aberta com sucesso")
            return connection
        except:
            return None

    def CriarCanal(conexao:BlockingConnection)->BlockingChannel:
        """Cria o canal do Rabbit

        Args:
            conexao (BlockingConnection): Recebe a conexão aberta como argumento principal

        Returns:
            [BlockingChannel]: [Retorna o objeto do canal]
        """
        canal = conexao.channel()
        log.info("Canal aberto com sucesso")
        return canal

    def CriaMensagem(canal:BlockingChannel, fila:str, mensagem:str, criafila:bool = False):
        """Cria a mensagem na fila proposta e passada como parametro

        Args:
            canal (BlockingChannel): Canal criado
            fila (str): Nome da fila que receberá a mensagem
            mensagem (str): conteúdo da mensagem geralmente recebido em Json
        
        """
        if criafila == True:
            try:
            #Declara que a fila é durável 
                canal.queue_declare(fila, passive=True, durable=True)
                log.info("Fila encontrada e declarada")
            except:
                canal.queue_declare(queue=fila, passive=False, durable=True)
                log.info("Fila não existente criada")

        #Executa o comando de publicação
        canal.basic_publish(exchange='', routing_key=fila, body=mensagem, properties=pika.BasicProperties(delivery_mode=2,)) 
        log.info("Mensagem enviada com sucesso")
        

    def FechaConRabbit(conexao:BlockingConnection):
        if conexao.is_open:
            conexao.close()



        
