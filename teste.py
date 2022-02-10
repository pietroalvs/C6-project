#! SCRIPT DE FILA
import Libs.Robos
from Libs.Classes import *

ret = Retorno_Inatividade()
cert = Libs.Robos.C6()
#!tratamento do Xgracco para login. é um laço que enquanto o ret.processo não for igual a verdade ele não sai daqui. 
ret.processo = False
while ret.processo == False:
    ret = cert.login_portal()

#{"NumeroProcesso": "5013492-78.2021.8.21.0033",
# "NomeArquivo": "PROTOCOLO CONTESTACAO - 5013492-78.2021.8.21.0033 - 29-09-2021.pdf",
# "CaminhoArquivo": "C:\\Temp\\Arquivos\\NaFila\\PROTOCOLO CONTESTACAO - 5013492-78.2021.8.21.0033 - 29-09-2021.pdf",
# "Status": 0,
# "Critica": "",
# "DataCriacao": "2022-01-25T00:00:00",
# "DataUpload": null}


up = Upload()
# ARRUMAR O REGEX PARAA COLETAR O TIPO DE PROTOCOLO E NUMERO PROCESSO
up.NumeroProcesso = '5010466-25.2021.8.24.0054'
up.NomeArquivo = 'PROTOCOLO CONTESTAÇÃO - 5010466-25.2021.8.24.0054 - 15-09-2021'
up.CaminhoArquivo = 'C:/Users/Pietro/Desktop/C6_arquivos'

cert.lancamento_copias(up)




