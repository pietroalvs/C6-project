import json
from os import path
from pathlib import Path

class appConfig():
    __json = None
    __data = None
    """Classe para manipular o Json com o caminho das pastas a serem lidos 
    """

    def __init__(self):
        self.__json = Path(Path.home(),'Temp','appConfig.json')
        with open(self.__json, encoding='utf-8-sig') as f:
            self.__data = json.load(f)

    def retorna_dados_json(self, strjson):
        return json.load(strjson)

    #Região de configuração de S3 Amazon
    def retorna_access_key_s3(self) -> str:
        return self.__data['AmazonS3']['Accesskey']
    
    def retorna_secret_access_key_s3(self) -> str:
        return self.__data['AmazonS3']['SecretAccessKey']

    def retorna_bucket_s3(self) -> str:
        return self.__data['AmazonS3']['Bucket']
    
    
    
    def retorna_url_hom_max(self) -> str:
        return self.__data["IntegracaoMAX"]["urlHomologacao"]

    def retorna_url_prod_max(self) -> str:
        return self.__data["IntegracaoMAX"]["urlProducao"]
    
    def retorna_token_api_max(self) -> str:
        return self.__data["IntegracaoMAX"]["token"]
    
    def retorna_servico_api_documentos(self) -> str:
        return self.__data["IntegracaoMAX"]["Servicos"]["documentos"]

    def retorna_servico_api_solicitacoes(self) -> str:
        return self.__data["IntegracaoMAX"]["Servicos"]["solicitacao"]

    def retorna_servico_api_cadastro_processo(self) -> str:
        return self.__data["IntegracaoMAX"]["Servicos"]["cadastrar"]

    def retorna_server_wdg(self) -> str:
        return self.__data["SQLWDG"]["server"]

    def retorna_nomebanco_wdg(self) -> str:
        return self.__data["SQLWDG"]["nomebanco"]

    def retorna_usuario_wdg(self) -> str:
        return self.__data["SQLWDG"]["usuario"]

    def retorna_senha_wdg(self) -> str:
        return self.__data["SQLWDG"]["senha"]

    def retorna_server_pg(self) -> str:
        return self.__data["Postgree"]["server"]

    def retorna_nomebanco_pg(self) -> str:
        return self.__data["Postgree"]["nomebanco"]

    def retorna_usuario_pg(self) -> str:
        return self.__data["Postgree"]["usuario"]

    def retorna_senha_pg(self) -> str:
        return self.__data["Postgree"]["senha"]
    
    def retorna_dados_json(self, strjson):
        return json.load(strjson)

    def retorna_smtp_email(self) -> str:
        return self.__data["Email"]["smtp"]

    def retorna_pasta_origem(self) -> str:
        return self.__data["Pastas"]["PastaMonitorada"]
    
    def retorna_pasta_destino(self) -> str:
        return self.__data["Pastas"]["PastaDestino"]

    def retorna_porta_email(self):
        return self.__data["Email"]["porta"]

    def retorna_usuario_email(self) -> str:
        return self.__data["Email"]["usuario"]

    def retorna_senha_email(self) -> str:
        return self.__data["Email"]["senha"]
    
    def retorna_host_rabbitmq(self) -> str:
        return self.__data["Rabbit"]["Conexao"]

    def retorna_c6_url(self) -> str:
        return self.__data["C6"]["url"]   

    def retorna_c6_login(self) -> str:
        return self.__data["C6"]["login"]

    def retorna_c6_senha(self) -> str:
        return self.__data["C6"]["senha"]
    
    def retorna_c6_login2(self) -> str:
        return self.__data["C6"]["login2"]
    
    def retorna_c6_senha2(self) -> str:
        return self.__data["C6"]["senha2"]

    def retorna_mongodb_conexao(self) -> str:
        return self.__data["MongoDB"]["Conexao"]

    def retorna_mongodb_banco(self) -> str:
        return self.__data["MongoDB"]["BancoC6"]

    def retorna_mongodb_colecao_aceite(self) -> str:
        return self.__data["MongoDB"]["Colecao"]["Aceite"]
    
    def retorna_mongodb_colecao_subssidio(self) -> str:
        return self.__data["MongoDB"]["Colecao"]["Subssidio"]
    
    def retorna_mongodb_colecao_subssidio(self) -> str:
        return self.__data["MongoDB"]["Colecao"]["Subssidio"]
    
    def retorna_mongodb_colecao_upload(self) -> str:
        return self.__data["MongoDB"]["Colecao"]["Upload"]
    
    def retorna_pasta_origem_copias(self) -> str:
        return self.__data["Pastas"]["PastaMonitoradaUpload"]
    
    def retorna_pasta_nafila(self) -> str:
        return self.__data["Pastas"]["PastaDestinoUpload"]
    
    
    
