import pymysql


class DatabaseConnection:
    def __init__(self, use_local=True):
        self.use_local = use_local

    def connect_to_db(self):
        if self.use_local:
            try:
                connection = pymysql.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='mydb17'
                )
                print("Connected to local MySQL.")
                print(self.use_local)
                return connection
            except pymysql.MySQLError as e:
                print(f"Error connecting to local MySQL: {e}")
                return None
        else:
            try:
                print("testtest")
                connection = pymysql.connect(
                    host='circuitxtract-sql-server.mysql.database.azure.com',
                    user='azure',
                    password='alpha@123',
                    database='circuitxtract',
                    ssl={'ca': r'C:\Users\Alven\Documents\PD_2\PF_v11\raw\DigiCertGlobalRootCA.crt.pem'}
                )
                print("Connected to Azure MySQL.")
                return connection
            except pymysql.MySQLError as e:
                print(f"Failed to connect to Azure MySQL: {e}")
                try:
                    connection = pymysql.connect(
                        host='localhost',
                        user='root',
                        password='',
                        database='mydb17'
                    )
                    print("Fallback: Connected to local MySQL.")
                    return connection
                except pymysql.MySQLError as e_local:
                    print(f"Failed to connect to local MySQL as fallback: {e_local}")
                    return None


# # To prioritize Azure connection first:
# db = DatabaseConnection(use_local=False)
# connection = db.connect_to_db()

# # Or to prioritize Local connection:
# db = DatabaseConnection(use_local=True)
# connection = db.connect_to_db()
