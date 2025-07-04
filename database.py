import sqlite3

def connect_db():
    return sqlite3.connect('inventory.db')

def setup_database():
    with open('db_setup.sql', 'r') as f:
        sql_script = f.read()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
