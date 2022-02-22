import json

class Retorno_Inatividade(object):
    def __init__(self):
        self.ativo = False
        self.processo= False
class Aceite(object):
    def __init__(self):
        self.NumeroProcesso = ''
        self.DataAceite =''
        self.Status = ''
        self.Critica = ''

class Upload(object):
    def __init__(self):
        self.NumeroProcesso = ''
        self.NomeArquivo = ''
        self.CaminhoArquivo = ''
        self.Status = -1
        self.Critica = ''
        self.DataCriacao = None
        self.DataUpload = None
        

class Subsidio(object):
    def __init__(self):
        self.NumeroProcesso = ''
        self.DataSubsidio = ''
        self.Status = ''
        self.Critica = ''
        
class C6_Upload_Fila(object):
    def __init__(self):
        self.numero_processo = ''
        self.argumento = -1
        self.data_criacao = None
        self.status = 0
        self.caminho_logico_arquivo = ''  
        
class retorno_usuario:
    def __init__(self) -> None:
        self.usuario1 = False
        self.usuario2 = False
        self.usuario3 = False
        
    
def para_dict(obj):
    # Se for um objeto, transforma num dict
    if hasattr(obj, '__dict__'):
        obj = obj.__dict__

    # Se for um dict, lê chaves e valores; converte valores
    if isinstance(obj, dict):
        return {k: para_dict(v) for k, v in obj.items()}
    # Se for uma lista ou tupla, lê elementos; também converte
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return [para_dict(e) for e in obj]
    # Se for qualquer outra coisa, usa sem conversão
    else:
        return obj
