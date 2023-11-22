from modules.ocrmodules.CoutumeClass import CoutumeClass
from modules.ocrmodules.CremerieClass import CremerieClass
from modules.ocrmodules.Pimeurs_d_issyClass import Pimeurs_d_issyClass
from modules.ocrmodules.ReynaudClass import ReynaudClass
from modules.ocrmodules.LCGClass import LCGClass
from modules.classify_document.FindDocumentTypeClass import FindDocumentType
from modules.extract_raw_text.ExtractPdfText import ExtractPdfText
from modules.dbconnections.mysql import mysql

from configparser import ConfigParser
from flask import Flask, jsonify, request
import os

#### Environment ####
enivronment = 'production'
# enivronment = 'development'
#### Environment ####

configur = ConfigParser()
config_file_obj = configur.read('config.ini')
user_upload_pdf_path = configur.get(enivronment,'user_upload_pdf')
invoice_folder_path = configur.get(enivronment,'invoice_folder_path')

class_call_dic = {
    'coutume':CoutumeClass,
    'cremerie' : CremerieClass,
    'lcg' : LCGClass,
    'reynaud':ReynaudClass,
    'pimeurs_d_issy' : Pimeurs_d_issyClass
    }

class OCR():
    
    def __init__(self,file_name) -> None:
        self.file_name = file_name
    
    def ocr(self):
        if self.file_name not in os.listdir(invoice_folder_path+'completed') :
            #### Extract Raw Text from PDFs that user uploads in web ####
            text = ExtractPdfText.pdf_to_text(self.file_name)
            # print(text)
            find_doc_type_obj = FindDocumentType(text)
            #### Extract Raw Text from PDFs that user uploads in web ####
            
            #### Find Document Type ####
            doc_type = find_doc_type_obj.finddocumenttype()
            doc_type = max(zip(doc_type.values(), doc_type.keys()))[1]
            print(doc_type)
            #### Find Document Type ####
            
            #### Calling OCR Modules as per DOC TYPE ####
            get_description_details = class_call_dic.get(doc_type.lower()).getDescriptionDetails(file_path=user_upload_pdf_path+self.file_name)
            get_description_details['QUANTITY'] = get_description_details['QUANTITY'].str.replace(',','.')
            get_description_details['PER_UNIT_PRICE'] = get_description_details['PER_UNIT_PRICE'].str.replace(',','.')
            get_description_details['TOTAL_AMOUNT'] = get_description_details['TOTAL_AMOUNT'].str.replace(',','.')
            get_other_info = class_call_dic.get(doc_type.lower()).getTotalDetails(file_path=user_upload_pdf_path+self.file_name)
            get_other_info['TOTAL_HT'] = get_other_info['TOTAL_HT'].str.replace(',','.')
            get_other_info['TOTAL_TTC'] = get_other_info['TOTAL_TTC'].str.replace(',','.')
            get_other_info['TOTAL_TVA'] = get_other_info['TOTAL_TVA'].str.replace(',','.')
            #### Calling OCR Modules as per DOC TYPE ####
            
            print(get_description_details)
            print(get_other_info)
            return get_description_details,get_other_info,doc_type
        
        else :
            return jsonify({'data':'','message':'Invoice OCR already done'})
     
# if __name__ == '__main__':
#     OCR.text