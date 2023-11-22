from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import pandas as pd
import boto3
from pdf2image import convert_from_bytes
from PIL.Image import Image
import io
import csv
import os

class Pimeurs_d_issyClass():
    
    def __init__(self) -> None:
        self.bucket = 'ivanocrprototype'
        self.pdf_folder = 'ProptotypeV1Pdfs/Coutume/'
        self.region_name = 'eu-west-3'
        self.client = boto3.client('textract',self.region_name, 
                            aws_access_key_id = 'AKIAQKPSQOOTKOV75DW7',
                            aws_secret_access_key = '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')
        self.poppler_path = 'poppler-0.68.0/bin'
    
    def image_to_byte_array(self,pil_image: Image):
        img_bytes = io.BytesIO()
        pil_image.save(img_bytes, format=pil_image.format)
        img_bytes = img_bytes.getvalue()
        return img_bytes
    
    def get_text(self,result, blocks_map):
        text = ''
        if 'Relationships' in result:
            for relationship in result['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        word = blocks_map[child_id]
                        if word['BlockType'] == 'WORD':
                            text += word['Text'] + ' '
                        if word['BlockType'] == 'SELECTION_ELEMENT':
                            if word['SelectionStatus'] == 'SELECTED':
                                text += 'X '
        return text
    
    def get_rows_columns_map(self,table_result, blocks_map):
        rows = {}
        for relationship in table_result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    cell = blocks_map[child_id]
                    if cell['BlockType'] == 'CELL':
                        row_index = cell['RowIndex']
                        col_index = cell['ColumnIndex']
                        if row_index not in rows:
                            # create new row
                            rows[row_index] = {}
                        # get the text value
                        rows[row_index][col_index] = self.get_text(cell, blocks_map)
        return rows
    
    def extract_tables(self,textract_response):
        blocks = textract_response['Blocks']
        blocks_map = {}
        table_blocks = []
        for block in blocks:
            blocks_map[block['Id']] = block
            if block['BlockType'] == 'TABLE':
                table_blocks.append(block)
        return blocks_map, table_blocks
    
    def file_tables_to_df(self,textract_response):
        
        blocks_map, table_blocks = self.extract_tables(textract_response)
        all_dfs = []
        i = 0
        if len(table_blocks) <= 0:
            return all_dfs

        for index, table_result in enumerate(table_blocks):
            data_rows = self.get_rows_columns_map(table_result, blocks_map)
            mem_file = io.StringIO()
            writer = csv.DictWriter(mem_file, data_rows[1])
            for row_index in data_rows:
                row_data = {k: v.encode('ascii', 'ignore').decode().replace('$', '') for k, v in
                            data_rows[row_index].items()}
                writer.writerow(row_data)
            mem_file.seek(0)
            if index == 0:
                df = pd.read_csv(mem_file)
                description_df = df[1:]
                # print(description_df)
            elif index == 2 :
                total_df = pd.read_csv(mem_file,header=None)
                total_df = total_df.transpose()
                total_df.columns = total_df.iloc[0]
                total_df = total_df[1:]
                # print(total_df)
        
            i += 1
        
        return description_df,total_df
    
    def getDescriptionDetails(self,file_path):
        fp = open(file_path, 'rb').read()
        
        for image in convert_from_bytes(fp,
                        poppler_path=self.poppler_path,
                        fmt='png'):
            image_bytes = self.image_to_byte_array(image)
            response = self.client.analyze_document(Document={'Bytes': image_bytes}, FeatureTypes=['TABLES'])
            current_tables = self.file_tables_to_df(response)
        
        return current_tables
        
if __name__ == '__main__':
    
    peri = Pimeurs_d_issyClass()
    for pdf_file in os.listdir('InvoicesPDF/Pimeurs d_issy CHECK/'):
        if pdf_file.rsplit('.',1)[1] == 'pdf':
            print('---------------'+pdf_file+'------------------')
            peri.getDescriptionDetails('InvoicesPDF/Pimeurs d_issy CHECK/'+pdf_file)
            break
        else :
            continue
        
