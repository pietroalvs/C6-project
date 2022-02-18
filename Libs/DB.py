
from logging import exception
from pymongo.collection import Collection
from Libs.AppConfig import appConfig
from Libs.Logs import Logs
from Libs.Classes import *
import pymongo


log = Logs.RetornaLog("--ManipulaBanco--")
j= appConfig()


class Mongo():
    
    _db = None
    _banco = None
    _colecao = None
    
    def __init__(self, banco, colecao, local = False):
        if not local:
            mongoconexao = j.retorna_mongodb_conexao()
       
        
        self._db = pymongo.MongoClient(mongoconexao)
        self._banco = self._db[banco]
        self._colecao = self._banco[colecao]
        
        log.info("[x] Conectado ao Mongo")
        


    def atualiza_mongo(self, query, documento):
        doc = self._colecao.find_one(query)
        if doc:
            self._colecao.update_one(query, {"$set": documento}, upsert=False)
            return True
        else:
            Mongo.insere_mongo(self, documento)
            return True
    
    def atualiza_mongo_array(self, query, documento, nomearray):
        #({'ref': ref}, {'$push': {'tags': new_tag}}, upsert = True)
        self._colecao.find_one_and_update(query,{"$addToSet": {nomearray+"$[]": [para_dict(documento)]}}, upsert = True)
    
    def atualiza_mongo_array2(self, query, documento, nomearray):
        #({'ref': ref}, {'$push': {'tags': new_tag}}, upsert = True)
        self._colecao.find_one_and_update(query,{"$addToSet": {nomearray: [para_dict(documento)]}}, upsert = True)
        
            
    def insere_mongo(self,  documento):
        self._colecao._insert(para_dict(documento))
        
    
    def pesquisa_mongo(self, query)-> bool:
        encontrou = self._colecao.find_one(query)
        return encontrou  
    
    def pesquisa_mongo_col(self, query)-> bool:
        if query == '':
            encontrou = self._colecao.find()
        else:
            encontrou = self._colecao.find(query)
        return encontrou 
    
    def deleta_mongo_col(self, query)-> bool:
        self._colecao.delete_many(query)
        
    def incrementar_sequencia(self, nome):
        documento = self._colecao.find_one_and_update({"_id": nome}, {"$inc": {"valor": 1}}, return_document=True)
        return documento["valor"]
    
    def agregar_col(self, pipeline):
        #banco = self._db['MAX']
        #s#elf._colecao = banco['Solicitacao']
        for doc in (self._colecao.aggregate(pipeline)):
            print(doc)
            return doc
    
    def insert_doc(self, doc):
        doc['_id'] = str(self._colecao.find_and_modify(
            query={ 'collection' : 'admin_collection' },
            update={'$inc': {'id': 1}},
            fields={'id': 1, '_id': 0},
            new=True 
        ).get('id'))