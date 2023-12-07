from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import pandas as pd
import numpy as np
import os

class CremerieClass():
    def getDescriptionDetails(file_path):
        fp = open(file_path, 'rb')
        rsrcmgr = PDFResourceManager()
        laparams = LAParams(line_overlap=0.3,char_margin=1,word_margin=0.2,line_margin=0.2,detect_vertical=True,all_texts=True)
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = PDFPage.get_pages(fp)
        final_df = pd.DataFrame()
        X = 0
        Y = 0
        try :
            for page in pages:
                page_df = pd.DataFrame()
                co_ordinated_dic = {}
                interpreter.process_page(page)
                layout = device.get_result()
                for lobj in layout:
                    if isinstance(lobj, LTTextBox):
                        df = pd.DataFrame(columns=['Y0','Y1','X0','X1','DETAIL'])
                        text = lobj.get_text()     
                        coordinate = str(lobj.bbox)[1:-1].split(",")
                        df['Y0'] = [coordinate[0]]
                        df['Y1'] = [coordinate[1]]
                        df['X0'] = [coordinate[2]]
                        df['X1'] = [coordinate[3]]
                        df['DETAIL'] = text.replace('\n',' ')
                        if 'Description' in text:
                            X = float(coordinate[1])
                        if 'Total HT' in text:
                            Y = float(coordinate[1])
                        page_df = pd.concat([page_df,df],axis=0,ignore_index=True)
                
                if page_df.size > 5 :
                    page_df = page_df[page_df['Y1'].astype(float)<X]
                    page_df = page_df[page_df['Y1'].astype(float)>Y]
                    
                    page_df['KEY'] = page_df['Y1'] + '_' + page_df['X1']
                    
                    key_df = page_df['KEY'].unique()
                    for key in key_df:
                        if page_df['KEY'].value_counts()[key] > 1 :
                            co_ordinated_dic[key] = page_df['KEY'].value_counts()[key]
                    
                    description_df = pd.DataFrame()
                    for filter_key in co_ordinated_dic.keys():
                        temp_df = pd.DataFrame()
                        temp_df = page_df.loc[(page_df.KEY == filter_key)]
                        description_df = pd.concat([description_df,temp_df],axis=0)
                    
                    no_of_rows = int(len(page_df))
                    no_of_table_rows = int(len(page_df)//6)
                    description_df = description_df.sort_values(by=['X1','Y0'],ignore_index=False)
                    final_df_details = description_df['DETAIL']
                    
                    file_df = pd.DataFrame()
                    for item in np.array_split(final_df_details, (no_of_table_rows)):
                        temp_df = pd.DataFrame(item)
                        temp_df.reset_index(drop=True,inplace=True)
                        temp_df = temp_df.transpose()
                        file_df = pd.concat([file_df,temp_df],axis=0)
                    
                    invoice_date = CremerieClass.getInvoiceDate(page)
                    file_df['Invoice Date'] = invoice_date
                    invoice_number = CremerieClass.getInvoiceNumber(page)
                    file_df['UNIQUE_IDENTIFICATION_NUMBER'] = invoice_number
                    restaurant_name = CremerieClass.getRestaurantName(page)
                    file_df['RESTAURANT_NAME'] = restaurant_name
                    final_df = pd.concat([final_df,file_df],axis=0)
                    
            fp.close()       
            
            final_df.rename(columns={0:'Code',1:'Qté',2:'PU HT',3:'Montant HT',4:'TVA',5:'Description'},inplace=True)
            final_df = final_df.loc[:,['Code','Description','Qté','PU HT','Montant HT','TVA','Invoice Date','UNIQUE_IDENTIFICATION_NUMBER','RESTAURANT_NAME']]
            final_df = final_df.rename(columns={
                'Code' : 'CODE',
                'Description' : 'DESCRIPTION',
                'Qté' : 'QUANTITY',
                'PU HT' : 'PER_UNIT_PRICE',
                'Montant HT' : 'TOTAL_AMOUNT',
                'Invoice Date' : 'INVOICE_DATE'
            })
            return final_df
        except :
            fp.close()
            return final_df
    
    def getTotalDetails(file_path):
        fp = open(file_path, 'rb')
        rsrcmgr = PDFResourceManager()
        laparams = LAParams(word_margin=0.1)
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = PDFPage.get_pages(fp)
        final_df = pd.DataFrame()
        X = 0
        Y = 0
        try :
            for page in pages:
                page_df = pd.DataFrame()
                interpreter.process_page(page)
                layout = device.get_result()
                for lobj in layout:
                    if isinstance(lobj, LTTextBox):
                        df = pd.DataFrame(columns=['Y0','Y1','X0','X1','DETAIL'])
                        text = lobj.get_text()     
                        coordinate = str(lobj.bbox)[1:-1].split(",")
                        df['Y0'] = [coordinate[0]]
                        df['Y1'] = [coordinate[1]]
                        df['X0'] = [coordinate[2]]
                        df['X1'] = [coordinate[3]]
                        df['DETAIL'] = text
                        if 'Total HT' in text:
                            X = float(coordinate[1])
                        if 'Total TTC' in text:
                            Y = float(coordinate[1])
                            Z = float(coordinate[0])
                        page_df = pd.concat([page_df,df],axis=0,ignore_index=True)
                
                if page_df.size > 5 :
                    page_df = page_df[page_df['Y1'].astype(float)<=float(X)]
                    page_df = page_df[page_df['Y1'].astype(float)>=float(Y)-10]
                    page_df = page_df[page_df['Y0'].astype(float)>=float(Z)]
                    page_df = page_df.sort_values(by=['X1','Y0'],ignore_index=True)
                    page_df = pd.DataFrame(page_df['DETAIL'])
                    
                    
                    main_df = pd.DataFrame()
                    for item in np.array_split(page_df, page_df.size//2):
                        test_df = pd.DataFrame()
                        temp_df = pd.DataFrame(item)
                        temp_df.reset_index(drop=True,inplace=True)
                        for inx,data in temp_df.itertuples() :
                            list_len = data.split('\n')
                            for data in list_len[0:len(list_len)-1] :
                                test_df = pd.concat([test_df,pd.DataFrame([data])],axis=0,ignore_index=True) 
                        if test_df.size > 2 :      
                            test_df.reset_index(drop=True,inplace=True)
                            index = (test_df.size // 2) - 1
                            for inx,data in test_df.itertuples():
                                if inx <= index:
                                    main_df[str(test_df.loc[[inx+2]]).replace('0','').replace('\n','').replace(str(inx+2),'').strip()] = [data]
                        else :  
                            main_df[str(test_df.loc[[1]]).replace('0','').replace('\n','').replace(str(1),'').strip()] = test_df.loc[[0]]
                    invoice_date = CremerieClass.getInvoiceDate(page)
                    main_df['Invoice Date'] = invoice_date
                    invoice_number = CremerieClass.getInvoiceNumber(page)
                    main_df['UNIQUE_IDENTIFICATION_NUMBER'] = invoice_number
                    restaurant_name = CremerieClass.getRestaurantName(page)
                    main_df['RESTAURANT_NAME'] = restaurant_name
                    final_df = pd.concat([final_df,main_df],axis=0)
                    
            fp.close()
            
            
            final_df = final_df.loc[:,['Total HT','Total TVA','Total TTC','Invoice Date','UNIQUE_IDENTIFICATION_NUMBER','RESTAURANT_NAME']]
            final_df = final_df.rename(columns={
                'Total TTC' : 'TOTAL_TTC',
                'Total TVA' : 'TOTAL_TVA',
                'Total HT' : 'TOTAL_HT',
                'Invoice Date' : 'INVOICE_DATE'
            })
            return final_df
        except :
            fp.close()
            return final_df

    def getInvoiceDate(page):
        try :
            rsrcmgr = PDFResourceManager()
            laparams = LAParams(word_margin=0.1)
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            pages = PDFPage.get_pages(page)
            final_df = pd.DataFrame()
            X = 0
            Y = 0
            interpreter.process_page(page)
            layout = device.get_result()
            for lobj in layout:
                if isinstance(lobj, LTTextBox):
                    df = pd.DataFrame(columns=['Y0','Y1','X0','X1','DETAIL'])
                    text = lobj.get_text()     
                    coordinate = str(lobj.bbox)[1:-1].split(",")
                    df['Y0'] = [coordinate[0]]
                    df['Y1'] = [coordinate[1]]
                    df['X0'] = [coordinate[2]]
                    df['X1'] = [coordinate[3]]
                    df['DETAIL'] = text
                    if 'Date' in text:
                        X = float(coordinate[1])
                    if 'N°Document' in text:
                        Y = float(coordinate[1])
                        Z = float(coordinate[0])
                    final_df = pd.concat([final_df,df],axis=0,ignore_index=True)
            
            final_df = final_df[final_df['Y1'].astype(float)<=float(X)]
            final_df = final_df[final_df['Y1'].astype(float)>=float(Y)]
            final_df = final_df.replace(r'\n','', regex=True) 
            final_df = final_df[final_df.DETAIL.str.match('[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]')]
            final_df = final_df['DETAIL']
            invoice_date  = final_df.values[0]
            return invoice_date
        except :
            return np.NaN
    
    def getInvoiceNumber(page) :
        try :
            rsrcmgr = PDFResourceManager()
            laparams = LAParams(word_margin=0.1)
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            pages = PDFPage.get_pages(page)
            final_df = pd.DataFrame()
            X = 0
            Y = 0
            interpreter.process_page(page)
            layout = device.get_result()
            for lobj in layout:
                if isinstance(lobj, LTTextBox):
                    df = pd.DataFrame(columns=['Y0','Y1','X0','X1','DETAIL'])
                    text = lobj.get_text()     
                    coordinate = str(lobj.bbox)[1:-1].split(",")
                    df['Y0'] = [coordinate[0]]
                    df['Y1'] = [coordinate[1]]
                    df['X0'] = [coordinate[2]]
                    df['X1'] = [coordinate[3]]
                    df['DETAIL'] = text
                    if 'Date' in text:
                        X = float(coordinate[1])
                    if 'Description' in text:
                        Y = float(coordinate[1])
                        Z = float(coordinate[3])
                    final_df = pd.concat([final_df,df],axis=0,ignore_index=True)
            
            
            final_df = final_df[final_df['Y1'].astype(float)<=float(X)]
            final_df = final_df[final_df['Y1'].astype(float)>=float(Y)]
            final_df = final_df.replace(r'\n','', regex=True)
            final_df = final_df.replace(r'N°Document','', regex=True)
            
            final_df = final_df[final_df.DETAIL.str.match('[0-9]{3,}')]
            final_df = final_df['DETAIL']
            invoice_number  = final_df.values[0]
            return invoice_number
        except :
            return np.NaN
        
    def getRestaurantName(page) :
        try :
            rsrcmgr = PDFResourceManager()
            laparams = LAParams(word_margin=0.1)
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            final_df = pd.DataFrame()
            X = 0
            Y = 0
            interpreter.process_page(page)
            layout = device.get_result()
            for lobj in layout:
                if isinstance(lobj, LTTextBox):
                    df = pd.DataFrame(columns=['Y0','Y1','X0','X1','DETAIL'])
                    text = lobj.get_text()     
                    coordinate = str(lobj.bbox)[1:-1].split(",")
                    df['Y0'] = [coordinate[0]]
                    df['Y1'] = [coordinate[1]]
                    df['X0'] = [coordinate[2]]
                    df['X1'] = [coordinate[3]]
                    df['DETAIL'] = text
                    if 'Facture' in text:
                        X = float(coordinate[1])
                        Z = float(coordinate[2])
                    if 'Facture' in text:
                        Y = float(coordinate[1])
                    final_df = pd.concat([final_df,df],axis=0,ignore_index=True)

            final_df = final_df[final_df['Y1'].astype(float)<=float(X)]
            final_df = final_df[final_df['Y1'].astype(float)>=float(Y)]
            final_df['X1'] = final_df['X1'].astype(float)
            final_df['X0'] = final_df['X0'].astype(float)
            final_df = final_df.sort_values(by=['X1','X0'],ignore_index=True)
            final_df = final_df['DETAIL'].head(1)
            
            restaurant_name = final_df.values[0].split('\n')
            restaurant_name = [name.lower() for name in restaurant_name]
            if '29 rue de trévise' in restaurant_name or '29 rue trévise' in restaurant_name :
                return 'BON BOUQUET'
            elif '7 rue keller' in restaurant_name :
                return 'KAFKAF'
            elif '96 bd de sébastopol' in restaurant_name or '96 boulevard de sebastopol' in restaurant_name :
                return 'SANTA LYNA'
            else :
                return final_df.values[0].split('\n')[1].upper().strip()
        except :
            return np.NaN
    
if __name__ == '__main__':
    pass