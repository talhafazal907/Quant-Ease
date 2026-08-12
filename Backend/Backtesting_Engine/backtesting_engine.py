from .indicator import Indicators
from .data import Data_loader
from numba import njit
import numpy as np

dl= Data_loader()
i = Indicators()

class Backtesting_Engine:
    def __init__(self, data : dict):
        self.user_data = data

    def run_ema_crossover(self, user_data :dict, data_array: np.array) -> dict:
            """
            This function is responsible to run the backtest of the  Two Ema-Crossover Strategy
            """
            if user_data["market_type"] == "spot":
                @njit
                def loop(data_array: np.ndarray, capital: float, risk: float = 0.01, reward: float = 0.02):
                    # Initialize trackers
                    trades = 0
                    wins = 0
                    losses = 0
                    maxdrawdown = 0.0
                    
                    
                    peak_equity = capital 

                    equity = np.zeros(len(data_array))
                    equity[0] = capital
                    position = False
                    
                    open_i = 0; high_i = 1; low_i = 2; close_i = 3; ema_s_i = 5; ema_l_i = 6
                    
                    position_size = 0.0
                    entry_price = 0.0
                    
                    for i in range(len(data_array)-1):
                        ema_short = data_array[i, ema_s_i]
                        ema_long = data_array[i, ema_l_i]

                        execution_price = data_array[i+1, open_i]
                        current_high = data_array[i, high_i]
                        current_low = data_array[i, low_i]

                        buy_signal = ema_short > ema_long
                        
                        if position:
                            # Stoploss
                            if current_low <= entry_price * (1 - risk):
                                capital = position_size * (entry_price * (1 - risk))
                                position = False
                                position_size = 0.0 
                                entry_price = 0.0   
                                losses += 1

                            # Take-profit
                            elif current_high >= entry_price * (1 + reward):
                                capital = position_size * (entry_price * (1 + reward))
                                position = False
                                position_size = 0.0 
                                entry_price = 0.0   
                                wins += 1

                        if not position and buy_signal:
                            position = True
                            entry_price = execution_price
                            position_size = capital / execution_price
                            
                        # Update current equity
                        if position:
                            equity[i+1] = position_size * data_array[i+1, close_i]
                        else:
                            equity[i+1] = capital
                            
                        # --- MAX DRAWDOWN LOGIC ---
                        # 1. Update the peak if the current equity is the highest seen so far
                        if equity[i+1] > peak_equity:
                            peak_equity = equity[i+1]
                            
                        # 2. Calculate the drop from the peak as a percentage
                        current_drawdown = (peak_equity - equity[i+1]) / peak_equity
                        
                        # 3. If this drop is the largest seen, record it
                        if current_drawdown > maxdrawdown:
                            maxdrawdown = current_drawdown
                            
                    return equity[-1], wins, losses, maxdrawdown, equity
                
                # Safety Check: If indicator calculation failed, stop and return the error
                    
                # THE FIX: Force the entire array into pure floats.
                # This strips away any 'decimal.Decimal' or string objects from the database.
                data_array = data_array.astype(np.float64)
                
                # Now Numba will happily compile the numerical array
                final_cap, wins, losses, max_dd, eq_curve = loop(
                    data_array, 
                    user_data["capital"], 
                    user_data["risk"], 
                    user_data["reward"]
                )
                trades = wins + losses
                winrate = wins / trades if (trades) > 0 else 0.0
                return {
                    "final_capital": final_cap,
                    "trades": trades,
                    "win_rate": winrate * 100,
                    "max_drawdown": max_dd * 100,
                    "equity_curve": eq_curve,
                    "status" : 1
                }
                

    def run(self) -> dict:
        try :
            if self.user_data["strategy_name"] == "double-ema":
                data = dl.Load_data(self.user_data["symbol"], self.user_data["time_frame"])
                if len(data) == 0:
                    return {"status": "No data available", "status": 0}
                data_ = i.add_indicator(self.user_data, data)
                if isinstance(data_, dict): 
                    return data_
                results = self.run_ema_crossover(user_data=self.user_data, data_array= data_)
                return results
        except Exception as e:
            return {"error" : f"Issue {str(e)}", "status" : 0}



    

