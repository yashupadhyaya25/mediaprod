from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import pandas as pd
import numpy as np

class ReynaudClass():
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
                        if 'Article' in text:
                            X = float(coordinate[1])
                        if 'Total postes' in text:
                            Y = float(coordinate[1])
                        final_df = pd.concat([final_df,df],axis=0,ignore_index=True)
                break

            co_ordinated_dic = {}
            missing_coordianted_dic = {}
            
            final_df = final_df[final_df['Y1'].astype(float)<X]
            final_df = final_df[final_df['Y1'].astype(float)>Y]
            final_df['KEY'] = final_df['Y1'] + '_' + final_df['X1']
            # print(final_df)
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
            no_of_table_rows = int(len(description_df)//7)
            
    
            description_df = description_df.sort_values(by=['X1','Y0'],ignore_index=False)
            final_df_details = description_df['DETAIL']
            file_df = pd.DataFrame()
            for item in np.array_split(final_df_details, (no_of_table_rows)):
                temp_df = pd.DataFrame(item)
                temp_df.reset_index(drop=True,inplace=True)
                temp_df = temp_df.transpose()
                file_df = pd.concat([file_df,temp_df],axis=0)
                            
            file_df.rename(columns={0:'Article',1:'Colis',2:'Quantité',3:'Poids (KG)',4:'Prix unitaire',5:'Total HT',6:'Désignation'},inplace=True)
            fp.close()
            invoice_date = ReynaudClass.getInvoiceDate(file_path)
            file_df['Invoice Date'] = invoice_date
            file_df = file_df.loc[:,['Article','Désignation','Colis','Quantité','Poids (KG)','Prix unitaire','Total HT','Invoice Date']]
            file_df = file_df.rename(columns={
                'Article' : 'CODE',
                'Désignation' : 'DESCRIPTION',
                'Quantité' : 'QUANTITY',
                'Prix unitaire' : 'PER_UNIT_PRICE',
                'Total HT' : 'TOTAL_AMOUNT',
                'Invoice Date' : 'INVOICE_DATE',
            })
            file_df = file_df.astype(str)
            return file_df
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
        Z = 0
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
                        df['DETAIL'] = text.strip()
                        if 'BASE H.T. :' in text:
                            X = float(coordinate[1])
                        if 'A PAYER (EUR)' in text:
                            Y = float(coordinate[1])
                            Z = float(coordinate[0])
                        final_df = pd.concat([final_df,df],axis=0,ignore_index=True)

            final_df = final_df[final_df['Y1'].astype(float)<=float(X)]
            final_df = final_df[final_df['Y1'].astype(float)>=float(Y)-10]
            final_df = final_df.sort_values(by=['X1','Y0'],ignore_index=True)
            final_df = pd.DataFrame(final_df['DETAIL'])

    

            main_df = pd.DataFrame()
            for item in np.array_split(final_df, final_df.size//2):
                test_df = pd.DataFrame()
                temp_df = pd.DataFrame(item)
                total_data = []
                temp_df.reset_index(drop=True,inplace=True)
                
                for inx,data in temp_df.itertuples() :
                    total_data.append(data)
                test_df[total_data[0]] = [str(total_data[1]).strip()]
                main_df = pd.concat([main_df,test_df],axis=1)
            columns = main_df.columns
            
            if 'TVA à 20,00% :' in columns :
                main_df.drop(columns=['TVA à 20,00% :'],inplace=True)
            if 'TVA à 5,50 % :' in columns :
                main_df.drop(columns=['TVA à 5,50 % :'],inplace=True)     
            if 'TVA à 5,50 % :\nTVA à 20,00% :' in columns :
                main_df.drop(columns=['TVA à 5,50 % :\nTVA à 20,00% :'],inplace=True)
            if 'BASE H.T. (1)\n BASE H.T. (2)' in columns :
                main_df = main_df.rename(columns={'BASE H.T. (1)\n BASE H.T. (2)':'BASE H.T - (1)'})
                main_df['BASE H.T - (1)'] = main_df['BASE H.T - (1)'].str.replace(',','.').astype(float)
            if 'BASE H.T. :' in columns :
                main_df['BASE H.T. :'] = main_df['BASE H.T. :'].str.replace(',','.').astype(float)
        
            if 'BASE H.T. :\n BASE H.T. :' in columns :
                main_df[['BASE H.T 1','BASE H.T 2']] = main_df['BASE H.T. :\n BASE H.T. :'].str.split('\n',expand=True)
                main_df['BASE H.T. :'] = main_df['BASE H.T 1'].str.replace(',','.').astype(float) + main_df['BASE H.T 2'].str.replace(',','.').astype(float)
                main_df.drop(columns=['BASE H.T. :\n BASE H.T. :','BASE H.T 1','BASE H.T 2'],inplace=True)

            main_df['BASE H.T'] = main_df['BASE H.T. :'] + main_df['BASE H.T - (1)']
            main_df.drop(columns=['BASE H.T. :','BASE H.T - (1)'],inplace=True)
            
            fp.close()
            invoice_date = ReynaudClass.getInvoiceDate(file_path)
            main_df['Invoice Date'] = invoice_date
            
            main_df = main_df.loc[:,['BASE H.T','TOTAL TVA','A PAYER (EUR)','Invoice Date']]
            main_df = main_df.rename(columns={
                'A PAYER (EUR)' : 'TOTAL_TTC',
                'TOTAL TVA' : 'TOTAL_TVA',
                'BASE H.T' : 'TOTAL_HT',
                'Invoice Date' : 'INVOICE_DATE'
            })
            # print(main_df)
            main_df = main_df.astype(str)
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
        Z = 0
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
                    df['DETAIL'] = text.strip()
                    if 'Date Facture' in text:
                        X = float(coordinate[1])
                    if 'Date Facture' in text:
                        Y = float(coordinate[1])
                        Z = float(coordinate[0])
                    final_df = pd.concat([final_df,df],axis=0,ignore_index=True)

        final_df = final_df[final_df['Y1'].astype(float)<=float(X)]
        final_df = final_df[final_df['Y1'].astype(float)>=float(Y)]
        final_df = final_df.sort_values(by=['X1','Y0'],ignore_index=True)
        final_df = pd.DataFrame(final_df['DETAIL'])
        
        date_set = []
        for data in final_df.itertuples() :
            if 'Date Facture' in data[1] :
                date_of_invoice = data[1].split('\n')[0].split(':')[1].strip()
                date_set.append(date_of_invoice)
        
        fp.close()      
        return list(set(date_set))
        
if __name__ == '__main__':
    ReynaudClass.getDescriptionDetails(r'G:/.shortcut-targets-by-id/10c_wbYjXg65CblXAdT6kdB7EyX88MQSk/0PI_PROJECTS/Ivan - MediaProd/Backend/ProcessedInvoices/Reynaud/Completed/Facture-1074945507-0.pdf')
    ReynaudClass.getTotalDetails(r'G:/.shortcut-targets-by-id/10c_wbYjXg65CblXAdT6kdB7EyX88MQSk/0PI_PROJECTS/Ivan - MediaProd/Backend/ProcessedInvoices/Reynaud/Completed/Facture-1074945507-0.pdf')
        
