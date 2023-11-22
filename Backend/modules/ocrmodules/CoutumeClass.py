from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import pandas as pd
import numpy as np

class CoutumeClass():
    
    def getDescriptionDetails(file_path):
            fp = open(file_path, 'rb')
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            pages = PDFPage.get_pages(fp)

            final_df = pd.DataFrame()
            X = 0
            Y = 0
            try :
                for page in pages:
                    # print('Processing next page...')
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
                                if 'Description' in text:
                                    X = coordinate[1]
                                if 'Total net HT' in text:
                                    Y = coordinate[1]
                                final_df = pd.concat([final_df,df],axis=0,ignore_index=True)
                    if X == 0 and Y == 0:
                        final_df = pd.DataFrame()
                final_df = final_df[final_df['Y1'].astype(float)<float(X)]
                final_df = final_df[final_df['Y1'].astype(float)>float(Y)]
                no_of_rows = int(len(final_df))
                file_df = pd.DataFrame()
                if no_of_rows < 1:
                    return file_df
                no_of_table_rows = int(len(final_df)//5)
        
                final_df = final_df.sort_values(by=['X1','Y0'],ignore_index=True)
                final_df_details = final_df['DETAIL']
                
                for item in np.array_split(final_df_details, no_of_table_rows):
                    temp_df = pd.DataFrame(item)
                    temp_df.reset_index(drop=True,inplace=True)
                    temp_df = temp_df.transpose()
                    file_df = pd.concat([file_df,temp_df],axis=0)

                fp.close()
                return file_df
            
            except :
                fp.close()
                return final_df
    
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
                            if 'Total net HT' in text:
                                X = coordinate[1]
                            if 'Total à régler' in text:
                                Y = coordinate[1]
                            final_df = pd.concat([final_df,df],axis=0,ignore_index=True)
                if X == 0 and Y == 0:
                    final_df = pd.DataFrame()

            final_df = final_df[final_df['Y1'].astype(float)<=float(X)]
            final_df = final_df[final_df['Y1'].astype(float)>float(Y)]
            final_df = final_df.sort_values(by=['X1','X0'],ignore_index=True)
            no_of_rows = int(len(final_df))
            no_of_table_rows = int(len(final_df)/2)
            final_df_details = final_df['DETAIL']
            file_df = pd.DataFrame()
            for item in np.array_split(final_df_details, no_of_table_rows):
                temp_df = pd.DataFrame(item)
                temp_df.reset_index(drop=True,inplace=True)
                temp_df = temp_df.transpose()
                file_df = pd.concat([file_df,temp_df],axis=0)
            fp.close()
            return file_df
        except :
            fp.close()
            return final_df