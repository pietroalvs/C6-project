import logging


class Logs():
    
    def __init__(self) -> None:
        pass
    def RetornaLog(nome:str):
    
        log = logging.getLogger(nome)
        log.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
        file_handler = logging.FileHandler('LogAplicacao.log')
        file_handler.setLevel(logging.ERROR)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        log.addHandler(file_handler)
        log.addHandler(stream_handler)

        return log
       
        
