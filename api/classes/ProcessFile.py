
import json
from api.classes.FormRecognizer import FormRecognizer

import pandas as pd

from api.classes.Openai import Openai

from django.conf import settings

from datetime import date

from api.crud import File, Subject

class ProcessFile():
    
    def __init__(self, fileStorage, csvPaths = 'csv_chunks'):
        self.formRecognizer = FormRecognizer()
        self.openai = Openai()
        self.csvPaths =  csvPaths
        
        self.fileStorage = fileStorage
        
        self.file = File()
        self.subject = Subject()
        
        self.__checkPaths()
    
    def __checkPaths(self):

        if not self.fileStorage.existsFolder(self.csvPaths):
            self.fileStorage.mkdir(self.csvPaths)
    
    def getColumns(self):
        return self.columns
    
    def preProcess(self, file):
        
        content = self.formRecognizer.readContentFile(file)
            
        chunks = content.split(". ")
        
        chunks_df = pd.DataFrame(chunks, columns=['chunk'])
              
        chunks_df['embedding'] = chunks_df['chunk'].apply(lambda x: self.openai.get_embedding(x))
        chunks_df['tokens'] = chunks_df['chunk'].apply(lambda x: len(self.openai.word_tokenize(x)))
        chunks_df['id'] = chunks_df['chunk'].apply(lambda _: id)    

        return chunks_df        
        
    def searchCv(self, chunk_df, q):
        chunk_df['similarity'] = chunk_df['embedding'].apply(lambda x: self.openai.cosine_similarity(x, self.openai.get_embedding(q)))
        return chunk_df.sort_values('similarity', ascending=False)
           
    def completionCv(self, question, cv_chunk_result):
        jsonData = json.dumps(cv_chunk_result['chunk'])
                        
        prompt = f"Dado el siguient JSON:\n{jsonData}\nDevuelve un json con el siguiente formato:\n - 'response' Una respuesta descriptiva y formal indicando que name o names (refiriendote a estos como empleado) contestan mejor a la pregunta y porque (no debes nombrar ningun identificador)\n - 'id_results' Una lista de objetos con información del identificador o identificadores que mejor contestes a la pregunta y que mencionaste en la respuesta anterior. Debe tener el siguiente formato:\n · 'id': El identificador\nPregunta:\n{question}\nSi no encuentras ningún resultado o respuesta, indicalo en el 'message' y su porque y la lista de id_results debería estar vacía"        
                
        return self.openai.completion(prompt).replace("\n", "").replace("\t", "")
       
    def loadNewFile(self, file, id, name, pdfSavePath, subject, userId):
        
        if not self.subject.exists(subject, userId): return False
                
        chunks_df = self.preProcess(file)
        
        self.saveCsvFile(chunks_df, id)
                
        self.file.create(id, name, pdfSavePath, userId, subjectId=subject)
        
        return self.getDataDocuments(userId, id)
    
    def updatePreProcess(self, id, file, userId):
        
        if not self.file.exists(id, userId): return False
        
        chunks_df = self.preProcess(file)
        
        self.saveCsvFile(chunks_df, id)
    
    def readCsvFile(self, id):
        return self.fileStorage.readCsv(f"{self.csvPaths}/{str(id)}.csv")
    
    def saveCsvFile(self, df, id):
        self.fileStorage.saveCsv(df, f"{self.csvPaths}/{id}.csv")
    
    def deleteCsvFile(self, id):
        return self.fileStorage.remove(f"{self.csvPaths}/{id}.csv")
    
    def deleteAllCsvFiles(self, list = None):
        if list is None:
            self.fileStorage.removeAllFiles(f"{self.csvPaths}/")
        else:
            for id in list:
                self.deleteCsvFile(id)
    
    def queryDocuments(self, query):
        
        cv_data = self.readCsvData()
        
        cv = {
                'chunk': {},
            }
        
        for _id in cv_data.index.to_list():
        
            id = _id
        
            cv_df = self.readCsvFile(id)
            
            cv_df['embedding'] = cv_df['embedding'].apply(lambda x : [float(value) for value in x.replace('[', '').replace(']', '').replace(' ', '').split(',')])
            
            cv_df = self.searchCv(cv_df, query)
                
            cv['chunk'][str(id)] = {
                'text': cv_df.loc[cv_df.index.to_list()[0], 'chunk'] + ". " + cv_df.loc[cv_df.index.to_list()[1], 'chunk'],
                'name': cv_data.loc[id]['name']
                }
            
        cv_df = pd.DataFrame(cv)
        
        response = self.completionCv(query, cv)
        
        print(response)
        
        start_pos = response.find("{")
        end_pos = response.rfind("}")

        if start_pos != -1 and end_pos != -1:
            json_str = response[start_pos:end_pos+1]
            data = json.loads(json_str)
            
    
            for result in data['id_results']:
                result['text'] = cv['chunk'][result['id']]['text']
                result['name'] = cv['chunk'][result['id']]['name']
            
            return data
        
        return None
    
    def deleteDocument(self, userId, id):
        
        if not self.file.exists(id, userId): return False
                
        self.file.remove(userId, id)        
        
        self.deleteCsvFile(id)
        
        return True
        
    
    def deleteAllDocuments(self, userId):
        
        idsRemove = [x['id'] for x in self.getDataDocuments(userId)]
                
        self.file.remove(userId)
        
        self.deleteAllCsvFiles(idsRemove)
        
        return idsRemove
            
        
    def getDataDocuments(self, userId, id = None):
                
        def generateData(f):
            return {
                'id': str(f.id),
                'name': f.name,
                'subject': {
                    'id': str(f.subject.id),
                    'name': f.subject.name,
                    'color': f.subject.color
                }
            }
                    
        if id is not None: return generateData(self.file.get(userId, id)) if self.file.exists(id, userId) else False

                        
        return [generateData(x) for x in self.file.get(userId)]
    
    def updateDataDocument(self, id, name, subject, userId):
        
        if not self.file.exists(id, userId) or not self.subject.exists(subject, userId): return False
        
        self.file.update(id, name, userId, subjectId=subject)
        
        return self.getDataDocuments(userId, id)
            
        
