import pandas as pd
import numpy as np

class Indicators:
    def __init__(self):
        pass

    def add_two_ema(self, ema_short: int, ema_long: int, array: np.array) -> np.array | dict:
        try:
            data = pd.DataFrame(array, columns=["Open", "High", "Low", "Close", "Volume"]).astype(float)
            short_col_name = f"EMA_{ema_short}"
            long_col_name = f"EMA_{ema_long}"

            data[short_col_name] = data["Close"].ewm(span=ema_short, adjust=False).mean()
            data[long_col_name] = data["Close"].ewm(span=ema_long, adjust=False).mean()
            
            return data.to_numpy()
        except Exception as e:
            print(f"Error in add_two_ema: {e}")
            return {"status": "error", "message": str(e), "status" : 0}

    def add_macd(self, ema_fast: int, ema_slow: int, signal_line: int, array: np.array) -> np.array | dict:
        try:
            data = pd.DataFrame(array, columns=["Open", "High", "Low", "Close", "Volume"]).astype(float)
            data["MACD"] = data["Close"].ewm(span=ema_fast, adjust=False).mean() - data["Close"].ewm(span=ema_slow, adjust=False).mean()
            data["Signal"] = data["MACD"].ewm(span=signal_line, adjust=False).mean()
            data.dropna(inplace=True)  # Drop rows with NaN values that may result from the calculations
            return data.to_numpy()
        except Exception as e:
            print(f"Error in add_macd: {e}")
            return {"status": 0, "message": str(e)}

    def add_bollinger_band(self, ema_length: int, std_dev: int, array: np.ndarray) -> np.ndarray | dict:
        try:
            data = pd.DataFrame(array, columns=["Open", "High", "Low", "Close", "Volume"]).astype(float)
            
            # DROP VOLUME HERE so that MA securely becomes Index 4
            data.drop(columns=["Volume"], inplace=True)
            
            data["MA"] = data["Close"].rolling(window=ema_length).mean()
            data["STD"] = data["Close"].rolling(window=ema_length).std()
            data["Upper_Band"] = data["MA"] + (data["STD"] * std_dev)
            data["Lower_Band"] = data["MA"] - (data["STD"] * std_dev)
            
            data.dropna(inplace=True)
            data.drop(columns=["STD"], inplace=True)  # Drops STD, leaving MA, Upper, Lower at indices 4, 5, 6
            
            return data.to_numpy()
            
        except Exception as e:
            print(f"Error in add_bollinger_band: {e}")
            return {"status": 0, "message": str(e)}

    def add_rsi(self, rsi_length: int, array: np.ndarray) -> np.ndarray | dict:
        try:
            # FIX: Added .astype(float) to instantly convert all string data to numbers
            data = pd.DataFrame(array, columns=["Open", "High", "Low", "Close", "Volume"])
            data = data.astype(float)  # Ensure all data is numeric for calculations
            # 1. Calculate price differences
            delta = data["Close"].diff()
            
            # 2. Separate gains and losses (clip is faster and cleaner than where)
            gain = delta.clip(lower=0)
            loss = -1 * delta.clip(upper=0)
            
            # 3. Apply Wilder's Smoothing (alpha = 1 / length) instead of standard rolling mean
            avg_gain = gain.ewm(alpha=1/rsi_length, min_periods=rsi_length, adjust=False).mean()
            avg_loss = loss.ewm(alpha=1/rsi_length, min_periods=rsi_length, adjust=False).mean()
            
            # 4. Calculate RS and safely handle Division by Zero
            rs = avg_gain / avg_loss
            
            # np.where ensures that if avg_loss is 0, RSI goes to 100 instead of returning NaN/Inf
            data["RSI"] = np.where(avg_loss == 0, 100, 100 - (100 / (1 + rs)))
            
            data.dropna(inplace=True)
            return data.to_numpy()
            
        except Exception as e:
            print(f"Error in add_rsi: {e}")
            return {"status": 0, "message": str(e)}

    def add_vwap(self, vwap_length: int, std_dev: float, array: np.ndarray) -> np.ndarray | dict:
        try:
            # Ensure all data is numeric instantly
            data = pd.DataFrame(array, columns=["Open", "High", "Low", "Close", "Volume"]).astype(float)
            
            # 1. Calculate the Typical Price (TP)
            data["TP"] = (data["High"] + data["Low"] + data["Close"]) / 3.0
            
            # 2. Multiply TP by Volume
            data["TP_V"] = data["TP"] * data["Volume"]
            
            # 3. Multiply TP squared by Volume (Required for Volume-Weighted Variance)
            data["TP2_V"] = (data["TP"] ** 2) * data["Volume"]
            
            # 4. Calculate the Rolling Sums
            roll_vol = data["Volume"].rolling(window=vwap_length).sum()
            roll_tp_v = data["TP_V"].rolling(window=vwap_length).sum()
            roll_tp2_v = data["TP2_V"].rolling(window=vwap_length).sum()
            
            # 5. Calculate Moving VWAP
            data["VWAP"] = roll_tp_v / roll_vol
            
            # 6. Calculate Volume-Weighted Standard Deviation
            # Math formula: Variance = Mean(X^2) - Mean(X)^2
            variance = (roll_tp2_v / roll_vol) - (data["VWAP"] ** 2)
            
            # .clip(lower=0) prevents floating-point inaccuracies from creating microscopic negative numbers
            std = np.sqrt(variance.clip(lower=0))
            
            # 7. Calculate the Upper and Lower Bands
            data["Upper_Band"] = data["VWAP"] + (std_dev * std)
            data["Lower_Band"] = data["VWAP"] - (std_dev * std)
            
            # 8. Clean up intermediate math columns so they don't bloat the final array
            data.drop(columns=["TP", "TP_V", "TP2_V"], inplace=True)
            data.dropna(inplace=True)
            
            return data.to_numpy()
            
        except Exception as e:
            print(f"Error in add_vwap: {e}")
            return {"status": 0, "message": str(e)}

    def add_stoch_rsi(self, rsi_length: int, stoch_length: int, k_smooth: int, d_smooth: int, array: np.ndarray) -> np.ndarray | dict:
        try:
            # Ensure all data is numeric instantly
            data = pd.DataFrame(array, columns=["Open", "High", "Low", "Close", "Volume"]).astype(float)
            
            # --- 1. Calculate Standard RSI ---
            delta = data["Close"].diff()
            gain = delta.clip(lower=0)
            loss = -1 * delta.clip(upper=0)
            
            avg_gain = gain.ewm(alpha=1/rsi_length, min_periods=rsi_length, adjust=False).mean()
            avg_loss = loss.ewm(alpha=1/rsi_length, min_periods=rsi_length, adjust=False).mean()
            
            rs = avg_gain / avg_loss
            rsi = np.where(avg_loss == 0, 100, 100 - (100 / (1 + rs)))
            data["RSI"] = rsi
            
            # --- 2. Calculate Stochastic RSI ---
            # Find the Min and Max RSI over the stochastic window
            min_rsi = data["RSI"].rolling(window=stoch_length).min()
            max_rsi = data["RSI"].rolling(window=stoch_length).max()
            
            # Calculate raw StochRSI (scaled 0 to 100)
            # np.where safely handles edge cases where max_rsi == min_rsi (division by zero)
            raw_stoch_rsi = np.where(
                max_rsi == min_rsi, 
                0, 
                ((data["RSI"] - min_rsi) / (max_rsi - min_rsi)) * 100
            )
            data["Raw_Stoch"] = raw_stoch_rsi
            
            # --- 3. Calculate %K and %D lines ---
            data["%K"] = data["Raw_Stoch"].rolling(window=k_smooth).mean()
            data["%D"] = data["%K"].rolling(window=d_smooth).mean()
            
            # Drop intermediate columns to keep array clean for Numba
            data.drop(columns=["RSI", "Raw_Stoch"], inplace=True)
            data.dropna(inplace=True)
            
            return data.to_numpy()
            
        except Exception as e:
            print(f"Error in add_stoch_rsi: {e}")
            return {"status": 0, "message": str(e)}

    def add_supertrend(self, atr_length: int, multiplier: float, array: np.ndarray) -> np.ndarray | dict:
        try:
            data = pd.DataFrame(array, columns=["Open", "High", "Low", "Close", "Volume"]).astype(float)
            
            # --- 1. Calculate Average True Range (ATR) ---
            prev_close = data["Close"].shift(1)
            tr1 = data["High"] - data["Low"]
            tr2 = (data["High"] - prev_close).abs()
            tr3 = (data["Low"] - prev_close).abs()
            
            # TR is the maximum of the three values
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # TradingView uses Wilder's RMA for ATR by default
            atr = tr.ewm(alpha=1/atr_length, min_periods=atr_length, adjust=False).mean()
            
            # --- 2. Calculate Basic Bands ---
            hl2 = (data["High"] + data["Low"]) / 2.0
            bub = hl2 + (multiplier * atr)  # Basic Upper Band
            blb = hl2 - (multiplier * atr)  # Basic Lower Band
            
            # --- 3. Recursive Final Bands & Supertrend Math ---
            close_arr = data["Close"].to_numpy()
            bub_arr = bub.to_numpy()
            blb_arr = blb.to_numpy()
            
            fub = np.zeros(len(data))
            flb = np.zeros(len(data))
            st_arr = np.zeros(len(data))
            dir_arr = np.zeros(len(data))
            
            for i in range(atr_length, len(data)):
                # Calculate Final Upper Band (FUB)
                if bub_arr[i] < fub[i-1] or close_arr[i-1] > fub[i-1]:
                    fub[i] = bub_arr[i]
                else:
                    fub[i] = fub[i-1]
                    
                # Calculate Final Lower Band (FLB)
                if blb_arr[i] > flb[i-1] or close_arr[i-1] < flb[i-1]:
                    flb[i] = blb_arr[i]
                else:
                    flb[i] = flb[i-1]
                    
                # Calculate Supertrend Line and Direction
                if i == atr_length:
                    st_arr[i] = fub[i]
                    dir_arr[i] = -1
                else:
                    if dir_arr[i-1] == -1 and close_arr[i] <= fub[i]:
                        st_arr[i] = fub[i]
                        dir_arr[i] = -1
                    elif dir_arr[i-1] == -1 and close_arr[i] > fub[i]:
                        st_arr[i] = flb[i]
                        dir_arr[i] = 1 # Flip to Bullish
                    elif dir_arr[i-1] == 1 and close_arr[i] >= flb[i]:
                        st_arr[i] = flb[i]
                        dir_arr[i] = 1
                    elif dir_arr[i-1] == 1 and close_arr[i] < flb[i]:
                        st_arr[i] = fub[i]
                        dir_arr[i] = -1 # Flip to Bearish
                        
            data["Supertrend"] = st_arr
            data["Trend_Dir"] = dir_arr
            
            # Crop out the first `atr_length` rows since they are just NaNs/Zeros
            data = data.iloc[atr_length:].copy()
            data.dropna(inplace=True)
            
            return data.to_numpy()
            
        except Exception as e:
            print(f"Error in add_supertrend: {e}")
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
            
        elif user_data["strategy_name"] == "bollinger_band":
                    if user_data['ema_length'] <=0 or user_data["std_dev"] <=0:
                        return {"message": "Bollinger Band parameters must be positive integers.", "status" : 0}
                    else:
                        data = self.add_bollinger_band(user_data["ema_length"], user_data["std_dev"], data)
                        return data

        elif user_data["strategy_name"] == "rsi":
                    if user_data['rsi_length'] <=0 or user_data["rsi_overbought"] <=0 or user_data["rsi_oversold"] <=0:
                        return {"message": "RSI parameters must be positive integers.", "status" : 0}
                    else:
                        data = self.add_rsi(user_data["rsi_length"], data)
                        return data
        elif user_data["strategy_name"] == "vwap":
                            if user_data['vwap_length'] <=0:
                                return {"message": "VWAP parameters must be positive integers.", "status" : 0}
                            else:
                                data = self.add_vwap(user_data["vwap_length"], user_data["std_dev"], data)
                                return data            
        elif user_data["strategy_name"] == "stoch_rsi":
                            if user_data['rsi_length'] <=0 and user_data["stoch_length"] <=0:
                                return {"message": "StochRSI parameters must be positive integers.", "status" : 0}
                            else:
                                data = self.add_stoch_rsi(user_data["rsi_length"], user_data["stoch_length"], user_data["k_smooth"], user_data["d_smooth"], data)
                                return data            
        elif user_data["strategy_name"] == "super_trend":
                            if user_data['atr_length'] <=0 and user_data["multiplier"] <=0:
                                return {"message": "SuperTrend parameters must be positive integers.", "status" : 0}
                            else:
                                data = self.add_supertrend(user_data["atr_length"], user_data["multiplier"], data)
                                return data            
        