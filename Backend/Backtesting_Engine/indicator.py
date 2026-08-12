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
            return {"status": "error", "message": str(e), "val": None}
        

    def add_indicator(self, strategy: dict, data: np.array) -> np.array:
        if strategy["strategy_name"] == "double-ema":
            if strategy['ema_long'] <=0 or strategy["ema_short"] <=0 or strategy["ema_long"] == strategy["ema_short"]:
                return {"status": "error", "message": "EMA periods must be positive integers and ema short should not equal ema long.", "status" : 0}
            else:
                data = self.add_two_ema(strategy["ema_short"], strategy["ema_long"], data)
                return data
