from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

class FormRecognizer():
    
    def __init__(self, key = "21b91e366acb41c3a4eae3d061ea68e9", endPoint = "https://formsrecognizerpasiona.cognitiveservices.azure.com/"):
        
        self.FORM_RECOGNIZER_KEY = key
        self.FORM_RECOGNIZER_END_POINT = endPoint
        
    def readContentFile(self, document):
        
        document_analysis_client = DocumentAnalysisClient(
            endpoint = self.FORM_RECOGNIZER_END_POINT,
            credential = AzureKeyCredential(self.FORM_RECOGNIZER_KEY)
        )
        
        poller = document_analysis_client.begin_analyze_document("prebuilt-read", document)
        
        result = poller.result()
        
        return result.to_dict()['content'].replace("\n", ' ') 