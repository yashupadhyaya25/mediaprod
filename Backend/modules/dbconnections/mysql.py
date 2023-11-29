import sqlalchemy

class mysql() :    
    def connection(connection_string):
        conn_str = connection_string
        conn = sqlalchemy.create_engine(conn_str)
        return conn