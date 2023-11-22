from flask import Flask, jsonify, request
from flask_cors import *
from main_ocr import OCR
from configparser import ConfigParser
from datetime import datetime as dt
from json import loads
import pandas as pd
from modules.dbconnections.mysql import mysql
import os
import shutil

#### Environment ####
enivronment = 'production'
# enivronment = 'development'
#### Environment ####

configur = ConfigParser()
config_file_obj = configur.read('config.ini')
user_upload_pdf_path = configur.get(enivronment,'user_upload_pdf')
invoice_folder_path = configur.get(enivronment,'invoice_folder_path')
user_upload_pdf_image = configur.get(enivronment,'user_upload_pdf_image')
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app)

def download_pdf(file_name,pdf_data): 
    pdf_data = request.files['file']
    pdf_data.save(user_upload_pdf_path+file_name)

@app.route('/v1/ocr', methods = ['POST'])
def ocr():
        #### DB CONNECTION ####
        db_connection = mysql.connection(configur.get(enivronment,'mysql_connection_string'))
        #### DB CONNECTION ####
    
        pdf_data = request.get_data()
        file_name = request.files['file'].filename.rsplit('.',1)[0]+'_'+dt.strftime(dt.now(),'%y_%m_%d_%H_%M_%S')+'.pdf'.replace('-','_')
        try :
            if request.files['file'].filename.rsplit('.',1)[1] == 'pdf' and request.files['file'].filename not in os.listdir(invoice_folder_path+'completed') :
                download_pdf(file_name,pdf_data)
                ocr_obj = OCR(file_name)
                ocr_data = ocr_obj.ocr()
                
                description_detail_header = ocr_data[0].columns.tolist()
                other_detail_header = ocr_data[1].columns.tolist()
                doctype = ocr_data[2]
                
                description_detail_df = ocr_data[0]
                other_detail_df = ocr_data[1]
                
                description_detail = loads(pd.DataFrame(description_detail_df.values).to_json(orient="records"))
                other_detail = loads(pd.DataFrame(ocr_data[1].values).to_json(orient="records"))
                # print(description_detail)
                description_detail_df['PDF_NAME'] = request.files['file'].filename
                description_detail_df['INVOICE_TYPE'] = doctype
                description_detail_df = description_detail_df.loc[:,['CODE','DESCRIPTION','QUANTITY','PER_UNIT_PRICE','TOTAL_AMOUNT','INVOICE_DATE','PDF_NAME','INVOICE_TYPE']]
                
                other_detail_df['PDF_NAME'] = request.files['file'].filename
                other_detail_df['INVOICE_TYPE'] = doctype
                # print(other_detail_df)
                other_detail_df = other_detail_df.loc[:,['TOTAL_TVA','TOTAL_HT','TOTAL_TTC','INVOICE_DATE','PDF_NAME','INVOICE_TYPE']]
                
                #### REMOVE WITHE SPACE ####
                description_detail_df['CODE'] = description_detail_df['CODE'].str.strip()
                description_detail_df['DESCRIPTION'] = description_detail_df['DESCRIPTION'].str.strip()
                description_detail_df['QUANTITY'] = description_detail_df['QUANTITY'].str.strip()
                description_detail_df['PER_UNIT_PRICE'] = description_detail_df['PER_UNIT_PRICE'].str.strip()
                description_detail_df['TOTAL_AMOUNT'] = description_detail_df['TOTAL_AMOUNT'].str.strip()
                description_detail_df['INVOICE_DATE'] = description_detail_df['INVOICE_DATE'].str.strip()
                description_detail_df['PDF_NAME'] = description_detail_df['PDF_NAME'].str.strip()
                description_detail_df['INVOICE_TYPE'] = description_detail_df['INVOICE_TYPE'].str.strip() 
                
                other_detail_df['TOTAL_TTC'] = other_detail_df['TOTAL_TTC'].astype(str).str.strip()
                other_detail_df['TOTAL_TVA'] = other_detail_df['TOTAL_TVA'].astype(str).str.strip()
                other_detail_df['TOTAL_HT'] = other_detail_df['TOTAL_HT'].astype(str).str.strip()
                other_detail_df['INVOICE_DATE'] = other_detail_df['INVOICE_DATE'].astype(str).str.strip()
                other_detail_df['PDF_NAME'] = other_detail_df['PDF_NAME'].astype(str).str.strip()
                other_detail_df['INVOICE_TYPE'] = other_detail_df['INVOICE_TYPE'].astype(str).str.strip()
                #### REMOVE WITHE SPACE ####
                
                description_detail_df.to_sql(name = 'INVOICE_DESCRIPTION',con = db_connection,if_exists = 'append',index = False,dtype=None,method='multi')
                other_detail_df.to_sql(name = 'INVOICE_TOTAL',con = db_connection,if_exists = 'append',index = False,dtype=None,method='multi')
                db_connection.dispose()
                shutil.move(user_upload_pdf_path+file_name,invoice_folder_path+'completed/'+file_name.rsplit('_',6)[0]+'.pdf')
                return jsonify({'description_data':description_detail,'other_data':other_detail,'description_detail_header':description_detail_header,'other_detail_header':other_detail_header,'message':'Completed'})
            else :
                db_connection.dispose()
                return jsonify({'data':'','message':'Invoice that you have uploaded is not pdf or already processed'})
            
        except Exception as e:
            print(e)
            db_connection.dispose()
            shutil.move(user_upload_pdf_path+file_name,invoice_folder_path+'issue/'+file_name.rsplit('_',6)[0]+'.pdf')
            return jsonify({'data':'','message':'Error occured please ensure you have select the correct pdf'})

@app.route('/v1/test', methods = ['GET'])
def test():
    return jsonify({'message':'Connection Succesfull'})

if __name__ == '__main__':
	app.run(debug = True)