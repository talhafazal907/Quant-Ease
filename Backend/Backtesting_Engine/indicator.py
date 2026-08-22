import pandas as pd
import numpy as np
class Indicators:
    def __init__(self):
        pass

    def add_two_ema(self, ema_short: int, ema_long: int, array: np.array) -> np.array:
        try:
            data = pd.DataFrame(array, columns=["Open", "High", "Low", "Close", "Volume"])
            short_col_name = f"EMA_{ema_short}"
            long_col_name = f"EMA_{ema_long}"

            data[short_col_name] = data["Close"].ewm(span=ema_short, adjust=False).mean()
            data[long_col_name] = data["Close"].ewm(span=ema_long, adjust=False).mean()
            
            return data.to_numpy()
        except Exception as e:
            print(f"Error in add_two_ema: {e}")
            return {"status": "error", "message": str(e), "status" : 0}

    def add_macd(self, ema_fast: int, ema_slow: int, signal_line: int, array: np.array) -> np.array:
        try:
            data = pd.DataFrame(array, columns=["Open", "High", "Low", "Close", "Volume"])
            data["MACD"] = data["Close"].ewm(span=ema_fast, adjust=False).mean() - data["Close"].ewm(span=ema_slow, adjust=False).mean()
            data["Signal"] = data["MACD"].ewm(span=signal_line, adjust=False).mean()
            data.dropna(inplace=True)  # Drop rows with NaN values that may result from the calculations
            return data.to_numpy()
        except Exception as e:
            print(f"Error in add_macd: {e}")
            return {"status": 0, "message": str(e)}

    def add_indicator(self, user_data: dict, data: np.array) -> np.array:
        if user_data["strategy_name"] == "double-ema":
            if user_data['ema_long'] <=0 or user_data["ema_short"] <=0 or user_data["ema_long"] == user_data["ema_short"]:
                return {"status": "error", "message": "EMA periods must be positive integers and ema short should not equal ema long.", "status" : 0}
            else:
                data = self.add_two_ema(user_data["ema_short"], user_data["ema_long"], data)
                return data
        elif user_data["strategy_name"] == "macd":
            if user_data['ema_slow'] <=0 or user_data["ema_fast"] <=0 or user_data["signal_line"] <=0:
                return {"message": "MACD periods must be positive integers.", "status" : 0}
            else:
                data = self.add_macd(user_data["ema_fast"], user_data["ema_slow"], user_data["signal_line"], data)
                return data