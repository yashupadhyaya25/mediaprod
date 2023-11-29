from modules.mail_read.read_inbox import read_mail
from main_ocr import OCR
from modules.dbconnections.mysql import mysql

import os,shutil
from configparser import ConfigParser
from json import loads
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime as dt


#### Environment ####
enivronment = 'production'
# enivronment = 'development'
#### Environment ####

configur = ConfigParser()
config_file_obj = configur.read('config.ini')
invoice_folder_path = configur.get(enivronment,'invoice_folder_path')
user_upload_pdf_path = configur.get(enivronment,'user_upload_pdf')

#### Download Files From Last 1 Days ####
file_list = read_mail()
#### Download Files From Last 1 Days ####


if file_list != [] :
    print('Files Need OCR')
    for file in file_list :
                try :
                    #### DB CONNECTION ####
                    db_connection = mysql.connection(configur.get(enivronment,'mysql_connection_string'))
                    #### DB CONNECTION ####
                    ocr_obj = OCR(file)
                    ocr_data = ocr_obj.ocr()
                    
                    if ocr_data[0].size > 0 and ocr_data[1].size > 0 :
                        description_detail_header = ocr_data[0].columns.tolist()
                        other_detail_header = ocr_data[1].columns.tolist()
                        doctype = ocr_data[2]
                        
                        description_detail_df = ocr_data[0]
                        other_detail_df = ocr_data[1]
                        
                        description_detail = loads(pd.DataFrame(description_detail_df.values).to_json(orient="records"))
                        other_detail = loads(pd.DataFrame(ocr_data[1].values).to_json(orient="records"))
                        
                        description_detail_df['PDF_NAME'] = file.rsplit('_',6)[0]+'.pdf'
                        description_detail_df['INVOICE_TYPE'] = doctype
                        description_detail_df = description_detail_df.loc[:,['CODE','DESCRIPTION','QUANTITY','PER_UNIT_PRICE','TOTAL_AMOUNT','INVOICE_DATE','PDF_NAME','INVOICE_TYPE','UNIQUE_IDENTIFICATION_NUMBER']]
                        
                        other_detail_df['PDF_NAME'] = file.rsplit('_',6)[0]+'.pdf'
                        other_detail_df['INVOICE_TYPE'] = doctype
                        other_detail_df = other_detail_df.loc[:,['TOTAL_TVA','TOTAL_HT','TOTAL_TTC','INVOICE_DATE','PDF_NAME','INVOICE_TYPE','UNIQUE_IDENTIFICATION_NUMBER']]

                        #### REMOVE WITHE SPACE ####
                        description_detail_df['CODE'] = description_detail_df['CODE'].str.strip()
                        description_detail_df['DESCRIPTION'] = description_detail_df['DESCRIPTION'].str.strip()
                        description_detail_df['QUANTITY'] = description_detail_df['QUANTITY'].str.strip()
                        description_detail_df['PER_UNIT_PRICE'] = description_detail_df['PER_UNIT_PRICE'].str.replace('€','').str.strip().str.replace(' ',',')
                        description_detail_df['TOTAL_AMOUNT'] = description_detail_df['TOTAL_AMOUNT'].str.replace('€','').str.strip().str.replace(' ',',')
                        description_detail_df['INVOICE_DATE'] = pd.to_datetime(description_detail_df['INVOICE_DATE'].str.strip()).dt.strftime('%Y-%m-%d')
                        description_detail_df['PDF_NAME'] = description_detail_df['PDF_NAME'].str.strip()
                        description_detail_df['INVOICE_TYPE'] = description_detail_df['INVOICE_TYPE'].str.strip()
                        description_detail_df['UNIQUE_IDENTIFICATION_NUMBER'] = description_detail_df['UNIQUE_IDENTIFICATION_NUMBER'].str.strip()
                        description_detail_df['INVOICE_FROM'] = 'MAIL'
                        description_detail_df['CREATED_ON'] = dt.strftime(dt.now(),'%Y-%m-%d %H:%M:%S')
                        description_detail_df['SYSTEM_NAME'] = file
                        
                        other_detail_df['TOTAL_TTC'] = other_detail_df['TOTAL_TTC'].astype(str).str.replace('€','').str.strip().str.replace(' ',',')
                        other_detail_df['TOTAL_TVA'] = other_detail_df['TOTAL_TVA'].astype(str).str.replace('€','').str.strip().str.replace(' ',',')
                        other_detail_df['TOTAL_HT'] = other_detail_df['TOTAL_HT'].astype(str).str.replace('€','').str.strip().str.replace(' ',',')
                        other_detail_df['INVOICE_DATE'] = pd.to_datetime(other_detail_df['INVOICE_DATE'].astype(str).str.strip()).dt.strftime('%Y-%m-%d')
                        other_detail_df['PDF_NAME'] = other_detail_df['PDF_NAME'].astype(str).str.strip()
                        other_detail_df['INVOICE_TYPE'] = other_detail_df['INVOICE_TYPE'].astype(str).str.strip()
                        other_detail_df['UNIQUE_IDENTIFICATION_NUMBER'] = other_detail_df['UNIQUE_IDENTIFICATION_NUMBER'].astype(str).str.strip()
                        other_detail_df['INVOICE_FROM'] = 'MAIL'
                        other_detail_df['CREATED_ON'] =  dt.strftime(dt.now(),'%Y-%m-%d %H:%M:%S')
                        other_detail_df['SYSTEM_NAME'] = file
                        #### REMOVE WITHE SPACE ####
                        
                        #### Check Whether The Invoice Is Already Present In DB Or Not ####
                        for invoice_number in list(set(description_detail_df['UNIQUE_IDENTIFICATION_NUMBER'].values)) :
                            check_existing_in_description = db_connection.connect().execute(text("Select * from INVOICE_DESCRIPTION where INVOICE_TYPE = '"+doctype+"' and UNIQUE_IDENTIFICATION_NUMBER = '"+invoice_number+"'"))
                            check_existing_in_total = db_connection.connect().execute(text("Select * from INVOICE_TOTAL where INVOICE_TYPE = '"+doctype+"' and UNIQUE_IDENTIFICATION_NUMBER = '"+invoice_number+"'"))
                            
                            description_db_flag =  len(check_existing_in_description.fetchall())
                            total_db_flag = len(check_existing_in_total.fetchall())
                            
                            if description_db_flag == 0 :
                                description_detail_to_db_df = description_detail_df[description_detail_df['UNIQUE_IDENTIFICATION_NUMBER'] == invoice_number]
                                description_detail_to_db_df.to_sql(name = 'INVOICE_DESCRIPTION',con = db_connection,if_exists = 'append',index = False,dtype=None,chunksize = 100,method='multi')
                            
                            if total_db_flag == 0 :
                                other_detail_to_db_df = other_detail_df[other_detail_df['UNIQUE_IDENTIFICATION_NUMBER'] == invoice_number]
                                other_detail_to_db_df.to_sql(name = 'INVOICE_TOTAL',con = db_connection,if_exists = 'append',index = False,dtype=None,chunksize = 100,method='multi')
                        
                        #### Check Whether The Invoice Is Already Present In DB Or Not ####
                        
                        db_connection.dispose()
                        shutil.move(user_upload_pdf_path+file,invoice_folder_path+'completed/'+file)
                    else :
                        shutil.move(user_upload_pdf_path+file,invoice_folder_path+'issue/'+file)
                except Exception as e :
                    print(e)
                    shutil.move(user_upload_pdf_path+file,invoice_folder_path+'issue/'+file)
                    db_connection.dispose()
                    continue
else :  
    print('No New Files To Download')