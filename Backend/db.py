import mysql.connector
from encrypter import Hash
from dotenv import load_dotenv
import os
import json
import numpy as np
import uuid
load_dotenv()

class DataBase_helper:
    """This class will help in performing the CRUD operations and is the middle part between the backend and the database server"""
    def __init__(self, dict = True):
        try:
            self.conn = mysql.connector.connect(
                host=os.getenv("HOST"),
                user=os.getenv("USER"),
                password=os.getenv("PASS"), 
                database=os.getenv("DB"),
                port = 3306)
            if not dict:
                self.cursor = self.conn.cursor()
            else:
                self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as err:
            self.conn = None
            self.cursor = None


    def fetch_user(self, email: str):
        query = "SELECT * FROM users WHERE email = %s"
        self.cursor.execute(query, (email,))
        user = self.cursor.fetchone()
        if user:
            return user
        else: 
            return None

    def fetch_user_by_id(self, user_id: int):
        try:
            query = "SELECT * FROM users WHERE u_id = %s"
            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchone()
        except mysql.connector.Error:
            return None
    
    def get_user_strategies(self, user_id: int):
        try:
            query = "SELECT * FROM strategies WHERE s_id = %s"
            self.cursor.execute(query, (user_id,))
            strategies = self.cursor.fetchall()
            return strategies
        except mysql.connector.Error:
            return None

    def get_results_by_strategy_id(self, strategy_id: int):
        try:
            query = "SELECT * FROM results WHERE s_id = %s"
            self.cursor.execute(query, (strategy_id,))
            return self.cursor.fetchone()
        except mysql.connector.Error:
            return None

    def register(self, fname, lname, email, password):
        
        try:
            """from verfier import Verify
            v = Verify()
            code = v.send_token(email)"""
            h = Hash()
            hash = h.create_hash(password)
            if hash:
                query = "INSERT INTO users (f_name,	l_name,	p_hash,	email) VALUES (%s, %s, %s, %s)"
                # Pass the variables as a tuple to execute() to safely inject them
                self.cursor.execute(query, (fname, lname, hash, email))
                # 3. Fixed typo: changed self.cn to self.conn
                query = """UPDATE users SET is_verif = TRUE WHERE email = %s"""
                self.cursor.execute(query, (email,))
                self.conn.commit()
                return 1
            else: 
                return None
        except mysql.connector.Error as err:
            return None    
        

    def verify(self, email: str, code : str):
        try:
            query = """SELECT v_code FROM users WHERE email = %s"""
            self.cursor.execute(query, (email,))
            user = self.cursor.fetchone()
            if user and str(user['v_code']) == code:
                query = """UPDATE users SET is_verif = TRUE WHERE email = %s"""
                self.cursor.execute(query, (email,))
                self.conn.commit()
                return 1
            else:
                return None
        except mysql.connector.Error as err:
                    return None
 
    def Login(self, email, password):
        try:
            from encrypter import Hash
            h = Hash()
            # 1. Changed 'LIKE' to '=' for exact, secure matching
            query = "SELECT * FROM users WHERE email = %s"
            self.cursor.execute(query, (email,))
            user = self.cursor.fetchone()
            if user["is_verif"] == 1:
                rs = h.match(password, user['p_hash'])
                if rs:
                    return 1
                else:
                    return None
            else:
                return None
        except mysql.connector.Error as err:
            # This will now print the EXACT reason if MySQL rejects the query
            return None

    def authenticate_user(self, email: str, password: str):
        """Return the verified user record when the supplied credentials are valid."""
        try:
            user = self.fetch_user(email)
            if user and user["is_verif"] == 1 and Hash().match(password, user["p_hash"]):
                return user
            return None
        except (mysql.connector.Error, KeyError, TypeError):
            return None

    def save_backtest_activity(self, user_id: int, strategy_data: dict, results: dict):
        """Persist strategy configuration and store equity curve as binary .npy file on disk."""
        try:
            # 1. Ensure target directory exists on disk
            folder_path = r"D:\Quant-Ease\Backend\equity_curves"
            os.makedirs(folder_path, exist_ok=True)

            # 2. Insert Strategy configuration
            strategy_query = """
                INSERT INTO strategies (s_id, Strategy_name, config_params)
                VALUES (%s, %s, %s)
            """
            self.cursor.execute(
                strategy_query,
                (
                    user_id,
                    strategy_data["strategy_name"],
                    json.dumps(strategy_data),
                ),
            )
            strategy_id = self.cursor.lastrowid

            # 3. Save the NumPy equity array directly to disk using the strategy_id
            file_name = f"equity_{uuid.uuid4().hex}.npy"
            file_path = os.path.join(folder_path, file_name)
            np.save(file_path, results["equity_curve"])

            # 4. Insert Result metrics, storing file_path in equity_data column
            result_query = """
                INSERT INTO results
                    (s_id, initial_capital, final_capital, Total_trades, wins, Losses, max_drawdown, equity_data, winrate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(
                result_query,
                (
                    strategy_id,
                    strategy_data["capital"],
                    results["final_capital"],
                    results["trades"],
                    results["wins"],
                    results["losses"],
                    results["max_drawdown"],
                    file_path,  # Stores path string: "D:\Quant-Ease\Backend\equity_curves\equity_strat_X.npy"
                    results["win_rate"],
                ),
            )
            self.conn.commit()
            return 1
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Database insertion failed: {e}") 
            return None
    
    def add_reset_token(self, u_id: int, code: str):
        try:
            query = "INSERT INTO password_rest_tokens (u_id, token) VALUES (%s, %s)"
            self.cursor.execute(query, (u_id,code))
            self.conn.commit()
            return 1          
        except mysql.connector.Error as err:
            # This will now print the EXACT reason if MySQL rejects the query
            return None
    
    def update_pass(self, code : str, hash : str):
        try:
            #fetch uid
            q = """SELECT u_id FROM password_rest_tokens WHERE token = %s"""
            self.cursor.execute(q, (code,))
            id = self.cursor.fetchone()

            #updating hash
            query = "UPDATE users SET p_hash = %s where u_id = %s"
            self.cursor.execute(query, (hash, id['u_id']))
            self.conn.commit()
            #seting verification code to 0000 
            query = "UPDATE password_rest_tokens SET token = %s where token = %s"
            self.cursor.execute(query, (0000, code))
            self.conn.commit()
            return 1
        except mysql.connector.Error as err:
            # This will now print the EXACT reason if MySQL rejects the query
            return None    
