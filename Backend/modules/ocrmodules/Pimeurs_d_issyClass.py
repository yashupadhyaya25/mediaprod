from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import pandas as pd
import numpy as np

class Pimeurs_d_issyClass():
    
    def getDescriptionDetails(file_path):
        main_df = pd.DataFrame()
        fp = open(file_path, 'rb')
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = PDFPage.get_pages(fp)
        X = 0
        Y = 0
        try :
            for page in pages:
                # print(page)
                final_df = pd.DataFrame()
                interpreter.process_page(page)
                layout = device.get_result()
                for lobj in layout:
                    if isinstance(lobj, LTTextBox):
                        df = pd.DataFrame(columns=['Y0','Y1','X0','X1','DETAIL'])
                        text = lobj.get_text()
                        if 'Notes' not in str(text):
                            coordinate = str(lobj.bbox)[1:-1].split(",")
                            df['Y0'] = [coordinate[0]]
                            df['Y1'] = [coordinate[1]]
                            df['X0'] = [coordinate[2]]
                            df['X1'] = [coordinate[3]]
                            df['DETAIL'] = text.replace('\n',' ')
                            if 'Libellé' in text:
                                X = coordinate[1]
                            if 'Détail TVA' in text:
                                Y = coordinate[1]
                    
                            final_df = pd.concat([final_df,df],axis=0,ignore_index=True)
                # print(final_df)
                final_df = final_df[final_df['Y1'].astype(float)<float(X)]
                final_df = final_df[final_df['Y1'].astype(float)>float(Y)]

                final_df = final_df.sort_values(by=['X1'],ignore_index=True,ascending=True)
                final_df = final_df.sort_values(by=['X0'],ignore_index=True,ascending=False)
                final_df = final_df.sort_values(by=['Y0'],ignore_index=True,ascending=True)
                final_df['KEY'] = final_df['Y1'] + '_' + final_df['X1']
                
                co_ordinated_dic = {}
                key_df = final_df['KEY'].unique()
                for key in key_df:
                    if final_df['KEY'].value_counts()[key] > 4 :
                        co_ordinated_dic[key] = final_df['KEY'].value_counts()[key]
                        
                description_df = pd.DataFrame()   
                
                for filter_key in co_ordinated_dic.keys():
                    temp_df = pd.DataFrame()
                    temp_df = final_df.loc[(final_df.KEY == filter_key)]
                    description_df = pd.concat([description_df,temp_df],axis=0)
                
                no_of_rows = int(len(final_df))
                file_df = pd.DataFrame()
                
                if no_of_rows < 1:
                    continue
                
                no_of_table_rows = int(len(final_df)//5)
                # print(description_df)
                if description_df.size > 0 :
                    description_df['X0'] = description_df['X0'].apply(float)
                    description_df['X1'] = description_df['X1'].apply(float)
                    description_df['Y0'] = description_df['Y0'].apply(float)
                    description_df = description_df.sort_values(by=['X1','Y0','X0'],ignore_index=True,ascending=True)
                    final_df_details = description_df['DETAIL']
                
                    for item in np.array_split(final_df_details, no_of_table_rows):
                        temp_df = pd.DataFrame(item)
                        temp_df.reset_index(drop=True,inplace=True)
                        temp_df = temp_df.transpose()
                        file_df = pd.concat([file_df,temp_df],axis=0)

                    file_df[['Montant','Taxes']]= file_df[4].str.split('€',expand=True)
                    file_df.drop(columns=4,inplace=True)
                    invoice_date = Pimeurs_d_issyClass.getInvoiceDate(page)
                    file_df['Invoice Date'] = invoice_date
                    main_df = pd.concat([main_df,file_df],axis=0)
                
            fp.close()
            main_df.rename(columns={0:'Libellé',1:'Conditionnement',2:'Quantité',3:'Prix unitaire',4:'Montant'},inplace=True)
            main_df['Montant'] = main_df['Montant'].astype(str)
            main_df['CODE'] = ''
            main_df = main_df.rename(columns={
                'CODE' : 'CODE',
                'Libellé' : 'DESCRIPTION',
                'Quantité' : 'QUANTITY',
                'Prix unitaire' : 'PER_UNIT_PRICE',
                'Montant' : 'TOTAL_AMOUNT',
                'Invoice Date' : 'INVOICE_DATE',
            })
            # print(main_df)
            return main_df
        except :
            fp.close()
            return main_df

    
    def getTotalDetails(file_path):
        fp = open(file_path, 'rb')
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = PDFPage.get_pages(fp)
        final_df = pd.DataFrame()
        X = 0
        Y = 0
        total_df = pd.DataFrame()
        try :
            for page in pages:
                interpreter.process_page(page)
                layout = device.get_result()
                for lobj in layout:
                    if isinstance(lobj, LTTextBox):
                        df = pd.DataFrame(columns=['Y0','Y1','X0','X1','DETAIL'])
                        text = lobj.get_text()
                        if 'Notes' not in str(text):
                            coordinate = str(lobj.bbox)[1:-1].split(",")
                            df['Y0'] = [coordinate[0]]
                            df['Y1'] = [coordinate[1]]
                            df['X0'] = [coordinate[2]]
                            df['X1'] = [coordinate[3]]
                            df['DETAIL'] = text.replace('\n',' ')
                            if 'Total HT' in text:
                                X = coordinate[1]
                            if 'Total TTC' in text:
                                Y = coordinate[1]
                            final_df = pd.concat([final_df,df],axis=0,ignore_index=True)
                try :
                    final_df = final_df[final_df['Y1'].astype(float)<=float(X)]
                    final_df = final_df[final_df['Y1'].astype(float)>=float(Y)]    

                    final_temp_df = final_df[final_df['Y0'].astype(float)>=float(X)+150]     
                    if len(final_temp_df) == 0 :
                        final_temp_df = final_df[final_df['Y0'].astype(float)>=float(X)+100]     
                    
                    final_temp_df = pd.DataFrame(final_temp_df['DETAIL'])
                    final_temp_df[['Total HT','Total TVA','Total TTC','REXXXX']] = final_temp_df['DETAIL'].str.split('€',expand=True)
                    final_temp_df.drop(columns=['DETAIL','REXXXX'],inplace=True)
                    final_temp_df.dropna(inplace=True)
                    invoice_date = Pimeurs_d_issyClass.getInvoiceDate(page)
                    final_temp_df = final_temp_df.astype(str)
                    final_temp_df['Invoice Date'] = invoice_date
                    total_df = pd.concat([total_df,final_temp_df],axis=0)
                    total_df = total_df.mask(total_df.eq('None')).dropna()
                except :
                    continue
            fp.close()
            total_df = total_df.rename(columns={
                'Total TTC' : 'TOTAL_TTC',
                'Total TVA' : 'TOTAL_TVA',
                'Total HT' : 'TOTAL_HT',
                'Invoice Date' : 'INVOICE_DATE'
            })
            # print(total_df)
            return total_df
        except :
            fp.close()
            return total_df
    
    def getInvoiceDate(page):
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
                    Z = float(coordinate[0])
                final_df = pd.concat([final_df,df],axis=0,ignore_index=True)

        final_df = final_df[final_df['Y1'].astype(float)<=float(X)]
        final_df = final_df[final_df['Y1'].astype(float)>=float(Y)]
        final_df = final_df['DETAIL']
        invoice_date = (str(final_df.values[0]).split('\n')[1].split('-')[1])[0:4] + '-' + (str(final_df.values[0]).split('\n')[1].split('-')[1])[4:6] + '-' + (str(final_df.values[0]).split('\n')[1].split('-')[1])[6:]
        return invoice_date
        
if __name__ == '__main__':
    # Pimeurs_d_issyClass.getDescriptionDetails(r'C:/Users/Yash/Downloads/RL-20230601-02235_Partie1.pdf')
    # Pimeurs_d_issyClass.getDescriptionDetails(r'C:/Users/Yash/Downloads/RL-20231101-04523.pdf')
    Pimeurs_d_issyClass.getTotalDetails(r'C:/Users/Yash/Downloads/RL-20231101-04523.pdf')
    # Pimeurs_d_issyClass.getTotalDetails(r'G:\.shortcut-targets-by-id\10c_wbYjXg65CblXAdT6kdB7EyX88MQSk\0PI_PROJECTS\Ivan - MediaProd\Backend\ML\ML - InvoicesPDF\Training_PDFs\3_Pimeurs d_issy/RL-20230601-02235_Partie1.pdf')
    # Pimeurs_d_issyClass.getInvoiceDate(r'G:\.shortcut-targets-by-id\10c_wbYjXg65CblXAdT6kdB7EyX88MQSk\0PI_PROJECTS\Ivan - MediaProd\ML\ML - InvoicesPDF\Training_PDFs\3_Pimeurs d_issy/RL-20230601-02235_Partie1.pdf')