from configparser import ConfigParser
from sqlalchemy import text
import pandas as pd
from modules.product_mapping.FetchFromGsheetClass import FetchFromGsheetClass
from modules.product_mapping.UpdateDataInGsheetClass import UpdateDataInGsheetClass
from modules.dbconnections.mysql import mysql


#### Environment ####
enivronment = 'production'
# enivronment = 'development'
#### Environment ####

configur = ConfigParser()
config_file_obj = configur.read('config.ini')
product_mapping_spread_sheet_id = configur.get(enivronment,'product_mapping_spread_sheet_id')
product_mapping_spread_sheet_range = configur.get(enivronment,'product_mapping_spread_sheet_range')

class ProductMapping() :
    
    def __init__(self) -> None:
        pass
    
    def get_gsheet_values(self):
        fetch_from_gsheet_obj = FetchFromGsheetClass(product_mapping_spread_sheet_id,product_mapping_spread_sheet_range)
        gsheet_data_df = fetch_from_gsheet_obj.get_values()
        return gsheet_data_df
    
    def get_all_products_from_db(self):
        db_connection = mysql.connection(configur.get(enivronment,'mysql_connection_string'))
        products_df = pd.read_sql(sql="select distinct(DESCRIPTION) from INVOICE_DESCRIPTION",con=db_connection)
        db_connection.dispose()
        products_df['L'] = ''
        products_df['ML'] = ''
        products_df['KG'] = ''
        products_df['GM'] = ''
        products_df['PC'] = ''
        products_df['PRODUCT_GROUP'] = ''
        return products_df
    
    def update_data(self):
        db_connection = mysql.connection(configur.get(enivronment,'mysql_connection_string'))
        final_df = pd.DataFrame()
        gsheet_df = self.get_gsheet_values()
        db_df = self.get_all_products_from_db()
        temp_df = pd.merge(left=db_df,right=gsheet_df,how='left',on=['DESCRIPTION'])
        final_df['DESCRIPTION'] = temp_df['DESCRIPTION']
        final_df['L'] = temp_df['L_y']
        final_df['ML'] = temp_df['ML_y']
        final_df['KG'] = temp_df['KG_y']
        final_df['GM'] = temp_df['GM_y']
        final_df['PC'] = temp_df['PC_y']
        final_df['PRODUCT_GROUP'] = temp_df['PRODUCT_GROUP_y']
        final_df.fillna('',inplace=True)
        # print(final_df)
        # final_df.to_csv('final.csv',index=False)
        final_df.to_sql(name='PRODUCT_MAPPING',con=db_connection,if_exists='replace',index=False)
        db_connection.dispose()
        obj_update_gsheet = UpdateDataInGsheetClass(product_mapping_spread_sheet_id,product_mapping_spread_sheet_range)
        obj_update_gsheet.update_values(final_df)
        

if __name__ == '__main__' :
    obj_product_mapping = ProductMapping()
    obj_product_mapping.update_data()