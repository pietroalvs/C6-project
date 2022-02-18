import Libs.Robos
from datetime import datetime as date
from Libs.DB import*
from Libs.Classes import *
from Libs.Uteis import *
import re


data_atual = date.today()
data_em_texto = f'{data_atual.year}-{data_atual.month}-{data_atual.day}'


#!localizar o caminho da pasta
pasta = r'\\10.67.0.24\\nj.11\\GED\\PORTAL\\NJ.05\\BANCO C6 CONSIGNADO S.A\\'

#!regex cnj
regex_argumento = "SENTENÇA EXTINÇÃO|SENTENÇA PROCEDENTE|SENTENÇA IMPROCEDENTE|SENTEÇA PARCIALMENTE PROCEDENTE"
regex_cnj = "^\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4}"
#!Usar a lib Uteis que vou mandar para vcs.. colocar na pasta Libs
#!Esse comando recebe o argumento do caminho da pasta a ser lida e retorna uma lista de arquivos nela contidos. 
lista = Uteis.listar_arquivos_pasta(pasta)

objetos_fila = []

if lista:
    for l in lista:
        #!O Laço percorre a lista de arquivos. Aqui a gente separa tudo q precisa, cria o objeto da nossa fila. Ou seja, para cada arquivo lido no laço, a gente cria um objeto e separa as informações.
        objeto_fila = C6_Upload_Fila()
        objeto_fila.caminho_logico_arquivo = pasta + l
        objeto_fila.status = 0
        objeto_fila.data_criacao = date.strptime(data_em_texto,"%Y-%m-%d")
        
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
 
            objetos_fila.append(objeto_fila)
        
    for o in objetos_fila:
        print(o.argumento)
        print(o.numero_processo)
        print(o.status)
        print(o.caminho_logico_arquivo)
        print(o.data_criacao)


ret = Retorno_Inatividade()
cert = Libs.Robos.C6()

ret.processo = False
while ret.processo == False:
    ret = cert.login_portal()





