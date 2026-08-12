import os
import mysql.connector
import pandas as pd
import numpy as np
from dotenv import load_dotenv
load_dotenv()

class Data_loader:
    def __init__(self):
            try:
                    self.conn = mysql.connector.connect(
                        host=os.getenv("HOST"),
                        user=os.getenv("USER"),
                        password=os.getenv("PASS"), 
                        database="backtest_data",
                        port = 3306)
                    self.cursor = self.conn.cursor()
            except mysql.connector.Error as err:
                    self.conn = None
                    self.cursor = None

    def Load_data(self, symbol: str, timeframe: str) -> np.array:
        try:
            table_name = f"{symbol.lower()}_{timeframe.lower()}"
            
            # FIX: Use an f-string to inject the table name directly into the query
            # Wrapping it in backticks is a good practice for MySQL/MariaDB identifiers
            q = f"SELECT open, high, low, close, volume FROM `{table_name}`"
            
            # Execute the query without passing a tuple of values
            self.cursor.execute(q)
            result = self.cursor.fetchall()
            
            return np.array(result)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return np.array([])  # Return an empty array on error