from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import pandas as pd
import numpy as np

class LCGClass():
    def getDescriptionDetails(file_path):
        fp = open(file_path, 'rb')
        rsrcmgr = PDFResourceManager()
        laparams = LAParams(line_overlap=0.3,char_margin=1,word_margin=0.2,line_margin=0.2,detect_vertical=True,all_texts=True)
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = PDFPage.get_pages(fp)
        final_df = pd.DataFrame()
        page_no = 1
        try :
            for page in pages:
                X = 0
                Y = 0
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
                        df['DETAIL'] = text.replace('\n',' ')
                        if 'Produits' in text:
                            X = float(coordinate[1])
                        if 'Sous-total (HT)' in text:
                            Y = float(coordinate[1])
                        page_df = pd.concat([page_df,df],axis=0,ignore_index=True)

                co_ordinated_dic = {}
                page_df = page_df[page_df['Y1'].astype(float)<X]   
                tem_df = page_df[page_df['Y1'].astype(float)>Y]
                if tem_df.size == 0 :
                    page_df = page_df[page_df['Y1'].astype(float)<Y]
                    page_df = page_df[page_df['Y0'].astype(float)>=35]
                    page_df = page_df[page_df['Y1'].astype(float)>=20]
                else :
                    page_df = page_df[page_df['Y1'].astype(float)>Y]
                
                # print('----> '+str(page_no))  
                if page_df.size > 0 :
                    page_df = page_df.sort_values(by=['X1','Y0'],ignore_index=False)
                    page_df['KEY'] = page_df['Y1'] + '_' + page_df['X1']
                    key_df = page_df['KEY'].unique()
                    for key in key_df:
                        if page_df['KEY'].value_counts()[key] > 5 :
                            co_ordinated_dic[key] = page_df['KEY'].value_counts()[key]      
                    description_df = pd.DataFrame()   
                    for filter_key in co_ordinated_dic.keys():
                        temp_df = pd.DataFrame()
                        temp_df = page_df.loc[(page_df.KEY == filter_key)]
                        description_df = pd.concat([description_df,temp_df],axis=0)

                no_of_table_rows = int(len(description_df)//6)
                description_df = description_df.sort_values(by=['X1','Y0'],ignore_index=False)
                final_df_details = description_df['DETAIL']             
                file_df = pd.DataFrame()
                                
                for item in np.array_split(final_df_details, (no_of_table_rows)):
                    temp_df = pd.DataFrame(item)
                    temp_df.reset_index(drop=True,inplace=True)
                    temp_df = temp_df.transpose()
                    file_df = pd.concat([file_df,temp_df],axis=0)
                
                invoice_date = LCGClass.getInvoiceDate(page)
                if str(invoice_date) != 'nan':
                    previous_page_date = invoice_date
                    file_df['Invoice Date'] = invoice_date
                else :
                    file_df['Invoice Date'] = previous_page_date
                
                invoice_number = LCGClass.getInvoiceNumber(page)
                if str(invoice_number) != 'nan': 
                    previous_page_invoice_number = invoice_number
                    file_df['UNIQUE_IDENTIFICATION_NUMBER'] = invoice_number  
                else :
                    file_df['UNIQUE_IDENTIFICATION_NUMBER'] = previous_page_invoice_number 
                    
                restaurant_name = LCGClass.getRestaurantName(page)
                if str(restaurant_name) != 'nan': 
                    previous_restaurant_name = restaurant_name
                    file_df['RESTAURANT_NAME'] = restaurant_name  
                else :
                    file_df['RESTAURANT_NAME'] = previous_restaurant_name
                # print(restaurant_name)
                page_no += 1
                final_df = pd.concat([final_df,file_df],axis=0)
                
            
            final_df.drop_duplicates(inplace=True)
            
            final_df.rename(columns={0:'SKU',1:'Produits',2:'Prix',3:'Qté',4:'Taxe',5:'Sous-Total'},inplace=True)
            final_df = final_df.rename(columns={
                'SKU' : 'CODE',
                'Produits' : 'DESCRIPTION',
                'Qté' : 'QUANTITY',
                'Prix' : 'PER_UNIT_PRICE',
                'Sous-Total' : 'TOTAL_AMOUNT',
                'Invoice Date' : 'INVOICE_DATE',
            })
            fp.close()
            # print(final_df)
            return final_df
        except Exception as e:
            # print(e)
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
        page_no = 1
        try :
            for page in pages:
                X = 0
                Y = 0
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
                        if 'Sous-total (HT)' in text:
                            X = float(coordinate[1])
                        if 'Total (TTC)' in text:
                            Y = float(coordinate[1])
                            Z = float(coordinate[0])
                        page_df = pd.concat([page_df,df],axis=0,ignore_index=True)
           
                page_df = page_df[page_df['Y1'].astype(float)<=float(X)]
                page_df = page_df[page_df['Y1'].astype(float)>=float(Y)-10]
                page_df = page_df[page_df['Y0'].astype(float)>=60]
                page_df['X1'] = page_df['X1'].astype(float)
                page_df['X0'] = page_df['X0'].astype(float)
                page_df = page_df.sort_values(by=['X1','X0'],ignore_index=True)
                page_df = pd.DataFrame(page_df['DETAIL'])
                main_df = pd.DataFrame()
                # print('----> '+str(page_no))
                if page_df.size > 0 :
                    for item in np.array_split(page_df, page_df.size//2):
                        temp_df = pd.DataFrame(item)
                        temp_df.reset_index(drop=True,inplace=True)
                        temp_df = temp_df.replace(r'\n','', regex=True) 
                        temp_df = temp_df.replace(r':','', regex=True)
                        temp_df.columns = temp_df.iloc[0]
                        temp_df = temp_df[1:]
                        main_df = pd.concat([temp_df,main_df],axis=1)
                
                main_df['PDF_PAGE_NO'] = page_no        
                invoice_date = LCGClass.getInvoiceDate(page)
                if str(invoice_date) != 'nan':
                    previous_page_date = invoice_date
                    main_df['Invoice Date'] = invoice_date
                else :
                    main_df['Invoice Date'] = previous_page_date
                
                invoice_number = LCGClass.getInvoiceNumber(page)
                if str(invoice_number) != 'nan': 
                    previous_page_invoice_number = invoice_number
                    main_df['UNIQUE_IDENTIFICATION_NUMBER'] = invoice_number  
                else :
                    main_df['UNIQUE_IDENTIFICATION_NUMBER'] = previous_page_invoice_number  
                
                restaurant_name = LCGClass.getRestaurantName(page)
                if str(restaurant_name) != 'nan': 
                    previous_restaurant_name = restaurant_name
                    main_df['RESTAURANT_NAME'] = restaurant_name  
                else :
                    main_df['RESTAURANT_NAME'] = previous_restaurant_name

                final_df = pd.concat([final_df,main_df],axis=0,ignore_index=True)              
                page_no += 1 
                                
            fp.close()
            final_df = final_df.loc[:,['Sous-total (HT)','Total (HT)','EU-Norm-FR-5.5 (5.5000%)','Taxe','Sous-total (TTC)','Total (TTC)','Invoice Date','UNIQUE_IDENTIFICATION_NUMBER','RESTAURANT_NAME']]
            final_df = final_df.rename(columns={
                'Total (TTC)' : 'TOTAL_TTC',
                'Total (HT)' : 'TOTAL_HT',
                'Invoice Date' : 'INVOICE_DATE',
                'Taxe' : 'TOTAL_TVA'
            })
            return final_df
        except :
            fp.close()
            final_df = pd.DataFrame()
            return final_df
    
    def getInvoiceDate(page):
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
                    if 'Date de livraison' in text:
                        X = float(coordinate[1])
                    if 'Date de livraison' in text:
                        Y = float(coordinate[1])
                        Z = float(coordinate[0])
                    final_df = pd.concat([final_df,df],axis=0,ignore_index=True)
            final_df = final_df[final_df['Y1'].astype(float)<=float(X)]
            
            final_df = final_df[final_df['Y1'].astype(float)>=float(Y)-10]
            final_df = final_df.sort_values(by=['X1'],ignore_index=True)
            final_df = pd.DataFrame(final_df['DETAIL'])
            for data in final_df.itertuples() :
                    date_of_invoice = data[1].split(':')[1].replace('\n','').strip()
            return date_of_invoice
        
        except :
            return np.NaN

    def getInvoiceNumber(page) :
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
                    if 'Facture' in text:
                        Y = float(coordinate[1])
                        Z = float(coordinate[3])
                    final_df = pd.concat([final_df,df],axis=0,ignore_index=True)

            final_df = final_df[final_df['Y1'].astype(float)<=float(X)]
            final_df = final_df[final_df['Y1'].astype(float)>=float(Y)]
            final_df = final_df.replace(r'\n','', regex=True)
            final_df = final_df.replace(r'Facture','', regex=True)
            final_df = final_df.replace(r'#','', regex=True)
            final_df = final_df[final_df.DETAIL.str.match('[0-9]*')]
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
                    if 'Vendu à :' in text:
                        X = float(coordinate[1])
                        Z = float(coordinate[2])
                    if 'Mode de paiement' in text:
                        Y = float(coordinate[1])
                    final_df = pd.concat([final_df,df],axis=0,ignore_index=True)
            final_df = final_df[final_df['Y1'].astype(float)<float(X)]
            final_df = final_df[final_df['Y1'].astype(float)>float(Y)]
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
                return final_df.values[0].split('\n')[1]
        except :
            return np.NaN
                    
    
if __name__ == '__main__':
    pass
        

