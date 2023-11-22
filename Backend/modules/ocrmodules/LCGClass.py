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
        X = 0
        Y = 0
        try :
            for page in pages:
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
                        final_df = pd.concat([final_df,df],axis=0,ignore_index=True)
            # print(final_df.to_string())
            co_ordinated_dic = {}
            missing_coordianted_dic = {}
            final_df = final_df[final_df['Y1'].astype(float)<X]   
            tem_df = final_df[final_df['Y1'].astype(float)>Y]
            if tem_df.size == 0 :
                final_df = final_df[final_df['Y1'].astype(float)<Y]
                final_df = final_df[final_df['Y0'].astype(float)>=35]
                final_df = final_df[final_df['Y1'].astype(float)>=20]
            else :
                final_df = final_df[final_df['Y1'].astype(float)>Y]
            
            final_df = final_df.sort_values(by=['X1','Y0'],ignore_index=False)

            final_df['KEY'] = final_df['Y1'] + '_' + final_df['X1']
            key_df = final_df['KEY'].unique()
            for key in key_df:
                if final_df['KEY'].value_counts()[key] > 1 :
                    co_ordinated_dic[key] = final_df['KEY'].value_counts()[key]
                    
            description_df = pd.DataFrame()   
            
            for filter_key in co_ordinated_dic.keys():
                temp_df = pd.DataFrame()
                temp_df = final_df.loc[(final_df.KEY == filter_key)]
                description_df = pd.concat([description_df,temp_df],axis=0)
            
            no_of_rows = int(len(description_df))
            no_of_table_rows = int(len(description_df)//6)
            
            description_df = description_df.sort_values(by=['X1','Y0'],ignore_index=False)
            final_df_details = description_df['DETAIL']
            file_df = pd.DataFrame()
            for item in np.array_split(final_df_details, (no_of_table_rows)):
                temp_df = pd.DataFrame(item)
                temp_df.reset_index(drop=True,inplace=True)
                temp_df = temp_df.transpose()
                file_df = pd.concat([file_df,temp_df],axis=0)
                
            invoice_date = LCGClass.getInvoiceDate(file_path)
            file_df['Invoice Date'] = invoice_date
            file_df.rename(columns={0:'SKU',1:'Produits',2:'Prix',3:'Qté',4:'Taxe',5:'Sous-Total'},inplace=True)
            file_df = file_df.rename(columns={
                'SKU' : 'CODE',
                'Produits' : 'DESCRIPTION',
                'Qté' : 'QUANTITY',
                'Prix' : 'PER_UNIT_PRICE',
                'Sous-Total' : 'TOTAL_AMOUNT',
                'Invoice Date' : 'INVOICE_DATE',
            })
            fp.close()
            print(file_df)
            return file_df
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
        X = 0
        Y = 0
        try :
            for page in pages:
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
                        final_df = pd.concat([final_df,df],axis=0,ignore_index=True)
            
            
            final_df = final_df[final_df['Y1'].astype(float)<=float(X)]
            final_df = final_df[final_df['Y1'].astype(float)>=float(Y)-10]
            final_df = final_df[final_df['Y0'].astype(float)>=60]
            final_df = final_df.sort_values(by=['X1','X0'],ignore_index=True)

            
        
            final_df = pd.DataFrame(final_df['DETAIL'])

            main_df = pd.DataFrame()
            for item in np.array_split(final_df, final_df.size//2):
                test_df = pd.DataFrame()
                temp_df = pd.DataFrame(item)
                
                temp_df.reset_index(drop=True,inplace=True)
                temp_df = temp_df.replace(r'\n','', regex=True) 
                temp_df = temp_df.replace(r':','', regex=True)
                temp_df.columns = temp_df.iloc[0]
                temp_df = temp_df[1:]
                main_df = pd.concat([temp_df,main_df],axis=1)
            fp.close()
            # print(main_df)
            invoice_date = LCGClass.getInvoiceDate(file_path)
            main_df['Invoice Date'] = invoice_date
            main_df = main_df.loc[:,['Sous-total (HT)','Total (HT)','EU-Norm-FR-5.5 (5.5000%)','Taxe','Sous-total (TTC)','Total (TTC)','Invoice Date']]
            main_df = main_df.rename(columns={
                'Total (TTC)' : 'TOTAL_TTC',
                'Total (HT)' : 'TOTAL_HT',
                'Invoice Date' : 'INVOICE_DATE',
                'Taxe' : 'TOTAL_TVA'
            })
            print(main_df)
            return main_df
        except :
            fp.close()
            return final_df
    
    def getInvoiceDate(file_path):
        fp = open(file_path, 'rb')
        rsrcmgr = PDFResourceManager()
        laparams = LAParams(word_margin=0.1)
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = PDFPage.get_pages(fp)
        final_df = pd.DataFrame()
        X = 0
        Y = 0

        for page in pages:
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
        
        fp.close()
        return date_of_invoice
        
if __name__ == '__main__':
    import os
    for file in os.listdir('Invoices/issue/'):
        print(file)
        LCGClass.getDescriptionDetails(r'Invoices/issue/'+file)
        # break
        LCGClass.getTotalDetails(r'Invoices/issue/'+file)
        

