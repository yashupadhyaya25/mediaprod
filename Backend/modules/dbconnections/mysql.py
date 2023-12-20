import sqlalchemy

class mysql() :    
    def connection(connection_string):
        conn_str = connection_string
        conn = sqlalchemy.create_engine(conn_str,pool_size=100, max_overflow=-1,echo=True)
        return conn