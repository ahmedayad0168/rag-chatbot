from string import printable
import pyodbc
import pandas as pd

def get_connection():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=DESKTOP-MA33VD7\AHMED;'
        'DATABASE=university;'
        'Trusted_Connection=yes;'
        )
    return conn

def fetch_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)

    return df

# ================== Get All Tables ==================
def get_all_tables():
    query = """
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_TYPE='BASE TABLE'
    """
    df = fetch_data(query)
    return df["TABLE_NAME"].tolist()

# read data from conn
def get_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students")
    rows = cursor.fetchall()

    #for row in rows:
    #    print(row)

    return rows

# read data with pandas 
def get_courses():
    print(fetch_data("SELECT * FROM Courses"))

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE Names (
        name VARCHAR(50),
        name_id INT PRIMARY KEY
        )
        """)
    conn.commit()
    print("Table 'Names' created successfully.")


