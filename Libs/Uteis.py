import os
import shutil
from os import listdir
from os.path import basename, isfile, join
import pathlib
from Libs.Logs import Logs
from datetime import *

log = Logs.RetornaLog("--Utilitários--")

class Uteis():
    pass
    #!testa se existe o diretório. se existe, manda verdade. mas se vc quiser verificar e se não existir, já criar, só mandar o segundo argumento = True
    def testa_diretorio(caminho, criar=False):
        if os.path.isdir(caminho):
            return True
        else:
            if criar:
                os.mkdir(caminho)
                return True
            return False
    def ret_nome_arquivo_s_ext(caminho):
        nome_arquivo = pathlib.Path(caminho).stem
        return nome_arquivo
    
    def listar_arquivos_pasta(caminho:str):
        lista = [f for f in listdir(caminho) if isfile(join(caminho, f))]
        return lista
    
               
    def mover_arquivo(path_origem, path_destino, pasta=False, arquivo=''):
        if pasta:
            for item in [join(path_origem, f) for f in listdir(path_origem) if isfile(join(path_origem, f)) ]:
                log.info(f"Movendo arquivo de: {path_origem} para: {path_destino}.")
                shutil.move(item, join(path_destino, basename(item)))
                log.info('Movido com sucesso: "{}" -> "{}"'.format(item, join(path_destino, basename(item))))
        else:
            log.info(f"Movendo arquivo de: {path_origem} para: {path_destino}.")
            shutil.move(path_origem + arquivo, join(path_destino + arquivo))
            log.info('Movido com sucesso: "{}" -> "{}"'.format(path_origem + arquivo , join(path_destino, join(path_destino + arquivo))))
            
    def ajusta_data(data_entrada):
        nova_data = datetime.strptime(data_entrada, f'%d/%m/%Y')
        dt_saida = datetime.strftime(nova_data, f'%d/%m/%Y')
        return dt_saida

    def dt_parser(dt):
        if isinstance(dt, datetime):
            return dt.isoformat()

