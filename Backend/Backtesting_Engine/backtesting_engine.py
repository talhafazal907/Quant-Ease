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
                data_array = data_array.astype(np.float64)
                                
                # Now Numba will happily compile the numerical array
                final_cap, wins, losses, max_dd, eq_curve = loop(
                    data_array, 
                    user_data["capital"], 
                    user_data["risk"], 
                    user_data["reward"])
                trades = wins + losses
                winrate = wins / trades if (trades) > 0 else 0.0
                return {
                    "final_capital": final_cap,
                    "trades": trades,
                    "win_rate": winrate * 100,
                    "max_drawdown": max_dd * 100,
                    "equity_curve": eq_curve,
                    "wins" : wins,
                    "losses" : losses,
                    "status" : 1
                }
            
            if user_data["market_type"] == "futures":
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
                    
                    # 0 = Flat, 1 = Long, -1 = Short
                    position_type = 0
                    
                    open_i = 0; high_i = 1; low_i = 2; close_i = 3; ema_s_i = 5; ema_l_i = 6
                    
                    position_size = 0.0
                    entry_price = 0.0
                    
                    for i in range(len(data_array)-1):
                        ema_short = data_array[i, ema_s_i]
                        ema_long = data_array[i, ema_l_i]

                        execution_price = data_array[i+1, open_i]
                        current_high = data_array[i, high_i]
                        current_low = data_array[i, low_i]

                        long_signal = ema_short > ema_long
                        short_signal = ema_short < ema_long
                        
                        # --- 1. CHECK STOPLOSS & TAKE PROFIT FOR ACTIVE POSITIONS ---
                        if position_type == 1: # LONG POSITION
                            if current_low <= entry_price * (1 - risk):
                                capital = capital + position_size * ((entry_price * (1 - risk)) - entry_price)
                                position_type = 0
                                losses += 1
                            elif current_high >= entry_price * (1 + reward):
                                capital = capital + position_size * ((entry_price * (1 + reward)) - entry_price)
                                position_type = 0
                                wins += 1

                        elif position_type == -1: # SHORT POSITION
                            if current_high >= entry_price * (1 + risk): # Stoploss hit (price went up)
                                capital = capital + position_size * (entry_price - (entry_price * (1 + risk)))
                                position_type = 0
                                losses += 1
                            elif current_low <= entry_price * (1 - reward): # Take-profit hit (price went down)
                                capital = capital + position_size * (entry_price - (entry_price * (1 - reward)))
                                position_type = 0
                                wins += 1

                        # --- 3. EXECUTE NEW ENTRIES ---
                        if position_type == 0:
                            if long_signal:
                                position_type = 1
                                entry_price = execution_price
                                position_size = capital / execution_price
                            elif short_signal:
                                position_type = -1
                                entry_price = execution_price
                                position_size = capital / execution_price
                                
                                
                        # --- 4. UPDATE CURRENT EQUITY ---
                        if position_type == 1: # Floating long equity
                            equity[i+1] = capital + position_size * (data_array[i+1, close_i] - entry_price)
                        elif position_type == -1: # Floating short equity
                            equity[i+1] = capital + position_size * (entry_price - data_array[i+1, close_i])
                        else:
                            equity[i+1] = capital
                            
                            
                        # --- 5. MAX DRAWDOWN LOGIC ---
                        if equity[i+1] > peak_equity:
                            peak_equity = equity[i+1]
                            
                        current_drawdown = (peak_equity - equity[i+1]) / peak_equity
                        
                        if current_drawdown > maxdrawdown:
                            maxdrawdown = current_drawdown
                            
                    return equity[-1], wins, losses, maxdrawdown, equity
                
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
                    "wins" : wins,
                    "losses" : losses,
                    "status" : 1
                }
                
    def run_macd(self, user_data: dict, data_array: np.ndarray) -> dict:
            """
            This function is responsible to run the backtest of the MACD Strategy
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
                    
                    # 0 = Flat, 1 = Buy (Long)
                    position_type = 0
                    
                    # Updated indices for MACD
                    open_i = 0; high_i = 1; low_i = 2; close_i = 3; macd_i = 5; signal_i = 6
                    
                    position_size = 0.0
                    entry_price = 0.0
                    
                    for i in range(len(data_array)-1):
                        macd = data_array[i, macd_i]
                        macd_signal = data_array[i, signal_i]

                        execution_price = data_array[i+1, open_i]
                        current_high = data_array[i, high_i]
                        current_low = data_array[i, low_i]

                        long_signal = macd > macd_signal
                        
                        # --- 1. STRICT STOPLOSS & TAKE PROFIT ---
                        if position_type == 1:
                            if current_low <= entry_price * (1 - risk):
                                capital = position_size * (entry_price * (1 - risk))
                                position_type = 0
                                position_size = 0.0
                                entry_price = 0.0
                                losses += 1
                            elif current_high >= entry_price * (1 + reward):
                                capital = position_size * (entry_price * (1 + reward))
                                position_type = 0
                                position_size = 0.0
                                entry_price = 0.0
                                wins += 1
                                
                        # --- 2. ENTRIES (ONLY IF FLAT) ---
                        # The flat requirement inherently blocks signal interference
                        if position_type == 0:
                            if long_signal:
                                position_type = 1
                                entry_price = execution_price
                                position_size = capital / execution_price
                                
                        # --- 3. UPDATE CURRENT EQUITY ---
                        if position_type == 1:
                            equity[i+1] = position_size * data_array[i+1, close_i]
                        else:
                            equity[i+1] = capital
                            
                        # --- 4. MAX DRAWDOWN LOGIC ---
                        if equity[i+1] > peak_equity:
                            peak_equity = equity[i+1]
                        current_drawdown = (peak_equity - equity[i+1]) / peak_equity
                        if current_drawdown > maxdrawdown:
                            maxdrawdown = current_drawdown
                            
                    return equity[-1], wins, losses, maxdrawdown, equity
                    
                data_array = data_array.astype(np.float64)
                
                final_cap, wins, losses, max_dd, eq_curve = loop(
                    data_array, 
                    user_data["capital"], 
                    user_data["risk"], 
                    user_data["reward"]
                )
                trades = wins + losses
                winrate = wins / trades if trades > 0 else 0.0
                return{
                    "final_capital": final_cap,
                    "trades": trades,
                    "win_rate": winrate * 100,
                    "max_drawdown": max_dd * 100,
                    "equity_curve": eq_curve,
                    "wins" : wins,
                    "losses" : losses,
                    "status" : 1
                }                

            if user_data["market_type"] == "futures":
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
                    
                    # 0 = Flat, 1 = Long, -1 = Short
                    position_type = 0
                    
                    open_i = 0; high_i = 1; low_i = 2; close_i = 3; macd_i = 5; signal_i = 6
                    
                    position_size = 0.0
                    entry_price = 0.0
                    
                    for i in range(len(data_array)-1):
                        macd = data_array[i, macd_i]
                        macd_signal = data_array[i, signal_i]

                        execution_price = data_array[i+1, open_i]
                        current_high = data_array[i, high_i]
                        current_low = data_array[i, low_i]

                        long_signal = macd > macd_signal
                        short_signal = macd_signal > macd
                        
                        # --- 1. STRICT STOPLOSS & TAKE PROFIT ---
                        if position_type == 1: # LONG POSITION
                            if current_low <= entry_price * (1 - risk):
                                capital = capital + position_size * ((entry_price * (1 - risk)) - entry_price)
                                position_type = 0
                                losses += 1
                            elif current_high >= entry_price * (1 + reward):
                                capital = capital + position_size * ((entry_price * (1 + reward)) - entry_price)
                                position_type = 0
                                wins += 1

                        elif position_type == -1: # SHORT POSITION
                            if current_high >= entry_price * (1 + risk): # Stoploss hit (price went up)
                                capital = capital + position_size * (entry_price - (entry_price * (1 + risk)))
                                position_type = 0
                                losses += 1
                            elif current_low <= entry_price * (1 - reward): # Take-profit hit (price went down)
                                capital = capital + position_size * (entry_price - (entry_price * (1 - reward)))
                                position_type = 0
                                wins += 1

                        # --- 2. ENTRIES (ONLY IF FLAT) ---
                        # The flat requirement inherently blocks signal interference
                        if position_type == 0:
                            if long_signal:
                                position_type = 1
                                entry_price = execution_price
                                position_size = capital / execution_price
                            elif short_signal:
                                position_type = -1
                                entry_price = execution_price
                                position_size = capital / execution_price
                                
                        # --- 3. UPDATE CURRENT EQUITY ---
                        if position_type == 1: # Floating long equity
                            equity[i+1] = capital + position_size * (data_array[i+1, close_i] - entry_price)
                        elif position_type == -1: # Floating short equity
                            equity[i+1] = capital + position_size * (entry_price - data_array[i+1, close_i])
                        else:
                            equity[i+1] = capital
                            
                        # --- 4. MAX DRAWDOWN LOGIC ---
                        if equity[i+1] > peak_equity:
                            peak_equity = equity[i+1]
                        current_drawdown = (peak_equity - equity[i+1]) / peak_equity
                        if current_drawdown > maxdrawdown:
                            maxdrawdown = current_drawdown
                            
                    return equity[-1], wins, losses, maxdrawdown, equity

                data_array = data_array.astype(np.float64)
                
                final_cap, wins, losses, max_dd, eq_curve = loop(
                    data_array, 
                    user_data["capital"], 
                    user_data["risk"], 
                    user_data["reward"]
                )
                trades = wins + losses
                winrate = wins / trades if trades > 0 else 0.0
                return {
                    "final_capital": final_cap,
                    "trades": trades,
                    "win_rate": winrate * 100,
                    "max_drawdown": max_dd * 100,
                    "equity_curve": eq_curve,
                    "wins" : wins,
                    "losses" : losses,
                    "status" : 1
                }
    def run_bollinger(self, user_data: dict, data_array: np.ndarray) -> dict:
        """ This function is responsible to run the backtest of the Bollinger Bands Strategy """
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
                
                # 0 = Flat, 1 = Buy (Long)
                position_type = 0
                
                # Indices for Bollinger Bands
                open_i = 0; high_i = 1; low_i = 2; close_i = 3; middle_band_i = 4; upper_band_i = 5; lower_band_i = 6
                
                position_size = 0.0
                entry_price = 0.0
                
                for i in range(len(data_array)-1):
                    upper_band = data_array[i, upper_band_i]
                    middle_band = data_array[i, middle_band_i]
                    lower_band = data_array[i, lower_band_i]

                    execution_price = data_array[i+1, open_i]
                    current_high = data_array[i, high_i]
                    current_low = data_array[i, low_i]
                    
                    # Spot Market: Buy when the closed candle dips below the lower band
                    long_signal = data_array[i, close_i] < lower_band
                    
                    # --- 1. STRICT STOPLOSS & TAKE PROFIT ---
                    if position_type == 1:
                        if current_low <= entry_price * (1 - risk):
                            capital = position_size * (entry_price * (1 - risk))
                            position_type = 0
                            position_size = 0.0
                            entry_price = 0.0
                            losses += 1
                        elif current_high >= entry_price * (1 + reward):
                            capital = position_size * (entry_price * (1 + reward))
                            position_type = 0
                            position_size = 0.0
                            entry_price = 0.0
                            wins += 1
                            
                    # --- 2. ENTRIES (ONLY IF FLAT) ---
                    if position_type == 0:
                        if long_signal:
                            position_type = 1
                            entry_price = execution_price
                            position_size = capital / execution_price
                            
                    # --- 3. UPDATE CURRENT EQUITY ---
                    if position_type == 1:
                        equity[i+1] = position_size * data_array[i+1, close_i]
                    else:
                        equity[i+1] = capital
                        
                    # --- 4. MAX DRAWDOWN LOGIC ---
                    if equity[i+1] > peak_equity:
                        peak_equity = equity[i+1]
                    current_drawdown = (peak_equity - equity[i+1]) / peak_equity
                    if current_drawdown > maxdrawdown:
                        maxdrawdown = current_drawdown
                        
                return equity[-1], wins, losses, maxdrawdown, equity
                
            data_array = data_array.astype(np.float64)
            
            final_cap, wins, losses, max_dd, eq_curve = loop(
                data_array, 
                user_data["capital"], 
                user_data["risk"], 
                user_data["reward"]
            )
            trades = wins + losses
            winrate = wins / trades if trades > 0 else 0.0
            return {
                "final_capital": final_cap,
                "trades": trades,
                "win_rate": winrate * 100,
                "max_drawdown": max_dd * 100,
                "equity_curve": eq_curve,
                "wins": wins,
                "losses": losses,
                "status": 1
            }                
        
        if user_data["market_type"] == "futures":
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
                
                # 0 = Flat, 1 = Long, -1 = Short
                position_type = 0
                
                open_i = 0; high_i = 1; low_i = 2; close_i = 3; middle_band_i = 4; upper_band_i = 5; lower_band_i = 6
                
                position_size = 0.0
                entry_price = 0.0
                
                for i in range(len(data_array)-1):
                    upper_band = data_array[i, upper_band_i]
                    middle_band = data_array[i, middle_band_i]
                    lower_band = data_array[i, lower_band_i]

                    execution_price = data_array[i+1, open_i]
                    current_high = data_array[i, high_i]
                    current_low = data_array[i, low_i]
                    
                    # Futures Market Mean-Reversion Signals
                    long_signal = data_array[i, close_i] < lower_band
                    short_signal = data_array[i, close_i] > upper_band
                    
                    # --- 1. STRICT STOPLOSS & TAKE PROFIT ---
                    if position_type == 1: # LONG POSITION
                        if current_low <= entry_price * (1 - risk):
                            capital = capital + position_size * ((entry_price * (1 - risk)) - entry_price)
                            position_type = 0
                            losses += 1
                        elif current_high >= entry_price * (1 + reward):
                            capital = capital + position_size * ((entry_price * (1 + reward)) - entry_price)
                            position_type = 0
                            wins += 1

                    elif position_type == -1: # SHORT POSITION
                        if current_high >= entry_price * (1 + risk): # Stoploss hit (price went up)
                            capital = capital + position_size * (entry_price - (entry_price * (1 + risk)))
                            position_type = 0
                            losses += 1
                        elif current_low <= entry_price * (1 - reward): # Take-profit hit (price went down)
                            capital = capital + position_size * (entry_price - (entry_price * (1 - reward)))
                            position_type = 0
                            wins += 1

                    # --- 2. ENTRIES (ONLY IF FLAT) ---
                    if position_type == 0:
                        if long_signal:
                            position_type = 1
                            entry_price = execution_price
                            position_size = capital / execution_price
                        elif short_signal:
                            position_type = -1
                            entry_price = execution_price
                            position_size = capital / execution_price
                            
                    # --- 3. UPDATE CURRENT EQUITY ---
                    if position_type == 1: # Floating long equity
                        equity[i+1] = capital + position_size * (data_array[i+1, close_i] - entry_price)
                    elif position_type == -1: # Floating short equity
                        equity[i+1] = capital + position_size * (entry_price - data_array[i+1, close_i])
                    else:
                        equity[i+1] = capital
                        
                    # --- 4. MAX DRAWDOWN LOGIC ---
                    if equity[i+1] > peak_equity:
                        peak_equity = equity[i+1]
                    current_drawdown = (peak_equity - equity[i+1]) / peak_equity
                    if current_drawdown > maxdrawdown:
                        maxdrawdown = current_drawdown
                        
                return equity[-1], wins, losses, maxdrawdown, equity

            data_array = data_array.astype(np.float64)
            
            final_cap, wins, losses, max_dd, eq_curve = loop(
                data_array, 
                user_data["capital"], 
                user_data["risk"], 
                user_data["reward"]
            )
            trades = wins + losses
            winrate = wins / trades if trades > 0 else 0.0
            return {
                "final_capital": final_cap,
                "trades": trades,
                "win_rate": winrate * 100,
                "max_drawdown": max_dd * 100,
                "equity_curve": eq_curve,
                "wins": wins,
                "losses": losses,
                "status": 1
            }

    def run_rsi(self, user_data: dict, data_array: np.ndarray) -> dict:
        """ This function is responsible to run the backtest of the RSI Strategy """
        if user_data["market_type"] == "spot":
            @njit
            # ADDED rsi_oversold and rsi_overbought as arguments for Numba compilation
            def loop(data_array: np.ndarray, capital: float, risk: float, reward: float, rsi_oversold: float):
                # Initialize trackers
                trades = 0
                wins = 0
                losses = 0
                maxdrawdown = 0.0
                
                peak_equity = capital
                
                equity = np.zeros(len(data_array))
                equity[0] = capital
                
                # 0 = Flat, 1 = Buy (Long)
                position_type = 0
                
                # Indices for RSI
                open_i = 0; high_i = 1; low_i = 2; close_i = 3; volume_i = 4; rsi_i = 5
                
                position_size = 0.0
                entry_price = 0.0
                
                for i in range(len(data_array)-1):
                    rsi = data_array[i, rsi_i]
                    
                    execution_price = data_array[i+1, open_i]
                    current_high = data_array[i, high_i]
                    current_low = data_array[i, low_i]
                    
                    # Spot Market: Buy when RSI drops below the user-defined oversold level
                    long_signal = rsi < rsi_oversold
                    
                    # --- 1. STRICT STOPLOSS & TAKE PROFIT ---
                    if position_type == 1:
                        if current_low <= entry_price * (1 - risk):
                            capital = position_size * (entry_price * (1 - risk))
                            position_type = 0
                            position_size = 0.0
                            entry_price = 0.0
                            losses += 1
                        elif current_high >= entry_price * (1 + reward):
                            capital = position_size * (entry_price * (1 + reward))
                            position_type = 0
                            position_size = 0.0
                            entry_price = 0.0
                            wins += 1
                            
                    # --- 2. ENTRIES (ONLY IF FLAT) ---
                    if position_type == 0:
                        if long_signal:
                            position_type = 1
                            entry_price = execution_price
                            position_size = capital / execution_price
                            
                    # --- 3. UPDATE CURRENT EQUITY ---
                    if position_type == 1:
                        equity[i+1] = position_size * data_array[i+1, close_i]
                    else:
                        equity[i+1] = capital
                        
                    # --- 4. MAX DRAWDOWN LOGIC ---
                    if equity[i+1] > peak_equity:
                        peak_equity = equity[i+1]
                    current_drawdown = (peak_equity - equity[i+1]) / peak_equity
                    if current_drawdown > maxdrawdown:
                        maxdrawdown = current_drawdown
                        
                return equity[-1], wins, losses, maxdrawdown, equity
                
            data_array = data_array.astype(np.float64)
            
            # Pass the user data values into the loop
            final_cap, wins, losses, max_dd, eq_curve = loop(
                data_array, 
                user_data["capital"], 
                user_data["risk"], 
                user_data["reward"],
                user_data["rsi_oversold"],
            )
            trades = wins + losses
            winrate = wins / trades if trades > 0 else 0.0
            return {
                "final_capital": final_cap,
                "trades": trades,
                "win_rate": winrate * 100,
                "max_drawdown": max_dd * 100,
                "equity_curve": eq_curve,
                "wins": wins,
                "losses": losses,
                "status": 1
            }                
        
        if user_data["market_type"] == "futures":
            @njit
            # ADDED rsi_oversold and rsi_overbought as arguments
            def loop(data_array: np.ndarray, capital: float, risk: float, reward: float, rsi_oversold: float, rsi_overbought: float):
                # Initialize trackers
                trades = 0
                wins = 0
                losses = 0
                maxdrawdown = 0.0
                
                peak_equity = capital 
                
                equity = np.zeros(len(data_array))
                equity[0] = capital
                
                # 0 = Flat, 1 = Long, -1 = Short
                position_type = 0
                
                open_i = 0; high_i = 1; low_i = 2; close_i = 3; volume_i = 4; rsi_i = 5
                
                position_size = 0.0
                entry_price = 0.0
                
                for i in range(len(data_array)-1):
                    rsi = data_array[i, rsi_i]

                    execution_price = data_array[i+1, open_i]
                    current_high = data_array[i, high_i]
                    current_low = data_array[i, low_i]
                    
                    # Futures Market Signals
                    long_signal = rsi < rsi_oversold
                    short_signal = rsi > rsi_overbought
                    
                    # --- 1. STRICT STOPLOSS & TAKE PROFIT ---
                    if position_type == 1: # LONG POSITION
                        if current_low <= entry_price * (1 - risk):
                            capital = capital + position_size * ((entry_price * (1 - risk)) - entry_price)
                            position_type = 0
                            losses += 1
                        elif current_high >= entry_price * (1 + reward):
                            capital = capital + position_size * ((entry_price * (1 + reward)) - entry_price)
                            position_type = 0
                            wins += 1

                    elif position_type == -1: # SHORT POSITION
                        if current_high >= entry_price * (1 + risk): # Stoploss hit (price went up)
                            capital = capital + position_size * (entry_price - (entry_price * (1 + risk)))
                            position_type = 0
                            losses += 1
                        elif current_low <= entry_price * (1 - reward): # Take-profit hit (price went down)
                            capital = capital + position_size * (entry_price - (entry_price * (1 - reward)))
                            position_type = 0
                            wins += 1

                    # --- 2. ENTRIES (ONLY IF FLAT) ---
                    if position_type == 0:
                        if long_signal:
                            position_type = 1
                            entry_price = execution_price
                            position_size = capital / execution_price
                        elif short_signal:
                            position_type = -1
                            entry_price = execution_price
                            position_size = capital / execution_price
                            
                    # --- 3. UPDATE CURRENT EQUITY ---
                    if position_type == 1: # Floating long equity
                        equity[i+1] = capital + position_size * (data_array[i+1, close_i] - entry_price)
                    elif position_type == -1: # Floating short equity
                        equity[i+1] = capital + position_size * (entry_price - data_array[i+1, close_i])
                    else:
                        equity[i+1] = capital
                        
                    # --- 4. MAX DRAWDOWN LOGIC ---
                    if equity[i+1] > peak_equity:
                        peak_equity = equity[i+1]
                    current_drawdown = (peak_equity - equity[i+1]) / peak_equity
                    if current_drawdown > maxdrawdown:
                        maxdrawdown = current_drawdown
                        
                return equity[-1], wins, losses, maxdrawdown, equity

            data_array = data_array.astype(np.float64)
            
            # Pass the user data values into the loop
            final_cap, wins, losses, max_dd, eq_curve = loop(
                data_array, 
                user_data["capital"], 
                user_data["risk"], 
                user_data["reward"],
                user_data["rsi_oversold"],
                user_data["rsi_overbought"]
            )
            trades = wins + losses
            winrate = wins / trades if trades > 0 else 0.0
            return {
                "final_capital": final_cap,
                "trades": trades,
                "win_rate": winrate * 100,
                "max_drawdown": max_dd * 100,
                "equity_curve": eq_curve,
                "wins": wins,
                "losses": losses,
                "status": 1
            }

    def run_vwap(self, user_data: dict, data_array: np.ndarray) -> dict:
        """ This function is responsible to run the backtest of the VWAP Strategy """
        if user_data["market_type"] == "spot":
            @njit
            def loop(data_array: np.ndarray, capital: float, risk: float, reward: float):
                # Initialize trackers
                trades = 0
                wins = 0
                losses = 0
                maxdrawdown = 0.0
                
                peak_equity = capital
                
                equity = np.zeros(len(data_array))
                equity[0] = capital
                
                # 0 = Flat, 1 = Buy (Long)
                position_type = 0
                
                # Indices for VWAP
                open_i = 0; high_i = 1; low_i = 2; close_i = 3; vol_i = 4; vwap_i = 5; upper_i = 6; lower_i = 7
                
                position_size = 0.0
                entry_price = 0.0
                
                for i in range(len(data_array)-1):
                    lower_band = data_array[i, lower_i]
                    
                    execution_price = data_array[i+1, open_i]
                    current_high = data_array[i, high_i]
                    current_low = data_array[i, low_i]
                    
                    # Spot Market: Buy when price dips below the lower VWAP band
                    long_signal = data_array[i, close_i] < lower_band
                    
                    # --- 1. STRICT STOPLOSS & TAKE PROFIT ---
                    if position_type == 1:
                        if current_low <= entry_price * (1 - risk):
                            capital = position_size * (entry_price * (1 - risk))
                            position_type = 0
                            position_size = 0.0
                            entry_price = 0.0
                            losses += 1
                        elif current_high >= entry_price * (1 + reward):
                            capital = position_size * (entry_price * (1 + reward))
                            position_type = 0
                            position_size = 0.0
                            entry_price = 0.0
                            wins += 1
                            
                    # --- 2. ENTRIES (ONLY IF FLAT) ---
                    if position_type == 0:
                        if long_signal:
                            position_type = 1
                            entry_price = execution_price
                            position_size = capital / execution_price
                            
                    # --- 3. UPDATE CURRENT EQUITY ---
                    if position_type == 1:
                        equity[i+1] = position_size * data_array[i+1, close_i]
                    else:
                        equity[i+1] = capital
                        
                    # --- 4. MAX DRAWDOWN LOGIC ---
                    if equity[i+1] > peak_equity:
                        peak_equity = equity[i+1]
                    current_drawdown = (peak_equity - equity[i+1]) / peak_equity
                    if current_drawdown > maxdrawdown:
                        maxdrawdown = current_drawdown
                        
                return equity[-1], wins, losses, maxdrawdown, equity
                
            data_array = data_array.astype(np.float64)
            
            # Pass the user data values into the loop
            final_cap, wins, losses, max_dd, eq_curve = loop(
                data_array, 
                user_data["capital"], 
                user_data["risk"], 
                user_data["reward"]
            )
            trades = wins + losses
            winrate = wins / trades if trades > 0 else 0.0
            return {
                "final_capital": final_cap,
                "trades": trades,
                "win_rate": winrate * 100,
                "max_drawdown": max_dd * 100,
                "equity_curve": eq_curve,
                "wins": wins,
                "losses": losses,
                "status": 1
            }                
            
        if user_data["market_type"] == "futures":
            @njit
            def loop(data_array: np.ndarray, capital: float, risk: float, reward: float):
                # Initialize trackers
                trades = 0
                wins = 0
                losses = 0
                maxdrawdown = 0.0
                
                peak_equity = capital
                
                equity = np.zeros(len(data_array))
                equity[0] = capital
                
                # 0 = Flat, 1 = Buy (Long), -1 = Short
                position_type = 0
                
                # Indices for VWAP
                open_i = 0; high_i = 1; low_i = 2; close_i = 3; vol_i = 4; vwap_i = 5; upper_i = 6; lower_i = 7
                
                position_size = 0.0
                entry_price = 0.0
                
                for i in range(len(data_array)-1):
                    upper_band = data_array[i, upper_i]
                    lower_band = data_array[i, lower_i]

                    execution_price = data_array[i+1, open_i]
                    current_high = data_array[i, high_i]
                    current_low = data_array[i, low_i]
                    
                    # Futures Market Mean-Reversion Signals
                    long_signal = data_array[i, close_i] < lower_band
                    short_signal = data_array[i, close_i] > upper_band
                    
                    # --- 1. STRICT STOPLOSS & TAKE PROFIT ---
                    if position_type == 1: # LONG POSITION
                        if current_low <= entry_price * (1 - risk):
                            capital = capital + position_size * ((entry_price * (1 - risk)) - entry_price)
                            position_type = 0
                            losses += 1
                        elif current_high >= entry_price * (1 + reward):
                            capital = capital + position_size * ((entry_price * (1 + reward)) - entry_price)
                            position_type = 0
                            wins += 1

                    elif position_type == -1: # SHORT POSITION
                        if current_high >= entry_price * (1 + risk): # Stoploss hit (price went up)
                            capital = capital + position_size * (entry_price - (entry_price * (1 + risk)))
                            position_type = 0
                            losses += 1
                        elif current_low <= entry_price * (1 - reward): # Take-profit hit (price went down)
                            capital = capital + position_size * (entry_price - (entry_price * (1 - reward)))
                            position_type = 0
                            wins += 1

                    # --- 2. ENTRIES (ONLY IF FLAT) ---
                    if position_type == 0:
                        if long_signal:
                            position_type = 1
                            entry_price = execution_price
                            position_size = capital / execution_price
                        elif short_signal:
                            position_type = -1
                            entry_price = execution_price
                            position_size = capital / execution_price
                            
                    # --- 3. UPDATE CURRENT EQUITY ---
                    if position_type == 1: # Floating long equity
                        equity[i+1] = capital + position_size * (data_array[i+1, close_i] - entry_price)
                    elif position_type == -1: # Floating short equity
                        equity[i+1] = capital + position_size * (entry_price - data_array[i+1, close_i])
                    else:
                        equity[i+1] = capital
                        
                    # --- 4. MAX DRAWDOWN LOGIC ---
                    if equity[i+1] > peak_equity:
                        peak_equity = equity[i+1]
                    current_drawdown = (peak_equity - equity[i+1]) / peak_equity
                    if current_drawdown > maxdrawdown:
                        maxdrawdown = current_drawdown
                        
                return equity[-1], wins, losses, maxdrawdown, equity
                
            data_array = data_array.astype(np.float64)
            
            # Pass the user data values into the loop
            final_cap, wins, losses, max_dd, eq_curve = loop(
                data_array, 
                user_data["capital"], 
                user_data["risk"], 
                user_data["reward"]
            )
            trades = wins + losses
            winrate = wins / trades if trades > 0 else 0.0
            return {
                "final_capital": final_cap,
                "trades": trades,
                "win_rate": winrate * 100,
                "max_drawdown": max_dd * 100,
                "equity_curve": eq_curve,
                "wins": wins,
                "losses": losses,
                "status": 1
            }                    
#    def run_stoch_rsi(self, user_data: dict, data_array: np.ndarray) -> dict:
    def run_stoch_rsi(self, user_data: dict, data_array: np.ndarray) -> dict:
        """ This function is responsible to run the backtest of the Stochastic RSI Strategy """
        if user_data["market_type"] == "spot":
            @njit
            def loop(data_array: np.ndarray, capital: float, risk: float, reward: float, oversold: float):
                # Initialize trackers
                trades = 0
                wins = 0
                losses = 0
                maxdrawdown = 0.0
                
                peak_equity = capital
                
                equity = np.zeros(len(data_array))
                equity[0] = capital
                
                position_type = 0 # 0 = Flat, 1 = Buy (Long)
                
                # Indices: Open(0), High(1), Low(2), Close(3), Vol(4), %K(5), %D(6)
                open_i = 0; high_i = 1; low_i = 2; close_i = 3; k_i = 5; d_i = 6
                
                position_size = 0.0
                entry_price = 0.0
                
                for i in range(1, len(data_array)-1):
                    # We need current and previous values to detect a crossover
                    curr_k = data_array[i, k_i]
                    curr_d = data_array[i, d_i]
                    prev_k = data_array[i-1, k_i]
                    prev_d = data_array[i-1, d_i]
                    
                    execution_price = data_array[i+1, open_i]
                    current_high = data_array[i, high_i]
                    current_low = data_array[i, low_i]
                    
                    # Spot Market Signal: %K crosses ABOVE %D while %K is in the oversold zone
                    long_signal = (curr_k > curr_d) and (prev_k <= prev_d) and (curr_k < oversold)
                    
                    # --- 1. STRICT STOPLOSS & TAKE PROFIT ---
                    if position_type == 1:
                        if current_low <= entry_price * (1 - risk):
                            capital = position_size * (entry_price * (1 - risk))
                            position_type = 0
                            position_size = 0.0
                            entry_price = 0.0
                            losses += 1
                        elif current_high >= entry_price * (1 + reward):
                            capital = position_size * (entry_price * (1 + reward))
                            position_type = 0
                            position_size = 0.0
                            entry_price = 0.0
                            wins += 1
                            
                    # --- 2. ENTRIES (ONLY IF FLAT) ---
                    if position_type == 0:
                        if long_signal:
                            position_type = 1
                            entry_price = execution_price
                            position_size = capital / execution_price
                            
                    # --- 3. UPDATE CURRENT EQUITY ---
                    if position_type == 1:
                        equity[i+1] = position_size * data_array[i+1, close_i]
                    else:
                        equity[i+1] = capital
                        
                    # --- 4. MAX DRAWDOWN LOGIC ---
                    if equity[i+1] > peak_equity:
                        peak_equity = equity[i+1]
                    current_drawdown = (peak_equity - equity[i+1]) / peak_equity
                    if current_drawdown > maxdrawdown:
                        maxdrawdown = current_drawdown
                        
                return equity[-1], wins, losses, maxdrawdown, equity
                
            data_array = data_array.astype(np.float64)
            final_cap, wins, losses, max_dd, eq_curve = loop(
                data_array, 
                user_data["capital"], 
                user_data["risk"], 
                user_data["reward"],
                user_data["oversold"]
            )
            trades = wins + losses
            winrate = wins / trades if trades > 0 else 0.0
            return {
                "final_capital": final_cap,
                "trades": trades,
                "win_rate": winrate * 100,
                "max_drawdown": max_dd * 100,
                "equity_curve": eq_curve,
                "wins": wins,
                "losses": losses,
                "status": 1
            }                
            
        if user_data["market_type"] == "futures":
            @njit
            def loop(data_array: np.ndarray, capital: float, risk: float, reward: float, oversold: float, overbought: float):
                trades = 0
                wins = 0
                losses = 0
                maxdrawdown = 0.0
                peak_equity = capital
                
                equity = np.zeros(len(data_array))
                equity[0] = capital
                
                position_type = 0 # 0 = Flat, 1 = Long, -1 = Short
                
                open_i = 0; high_i = 1; low_i = 2; close_i = 3; k_i = 5; d_i = 6
                
                position_size = 0.0
                entry_price = 0.0
                
                # Start at index 1 so we can check i-1 for crossovers
                for i in range(1, len(data_array)-1):
                    curr_k = data_array[i, k_i]
                    curr_d = data_array[i, d_i]
                    prev_k = data_array[i-1, k_i]
                    prev_d = data_array[i-1, d_i]

                    execution_price = data_array[i+1, open_i]
                    current_high = data_array[i, high_i]
                    current_low = data_array[i, low_i]
                    
                    # Futures Market Crossover Signals
                    long_signal = (curr_k > curr_d) and (prev_k <= prev_d) and (curr_k < oversold)
                    short_signal = (curr_k < curr_d) and (prev_k >= prev_d) and (curr_k > overbought)
                    
                    # --- 1. STRICT STOPLOSS & TAKE PROFIT ---
                    if position_type == 1:
                        if current_low <= entry_price * (1 - risk):
                            capital = capital + position_size * ((entry_price * (1 - risk)) - entry_price)
                            position_type = 0
                            losses += 1
                        elif current_high >= entry_price * (1 + reward):
                            capital = capital + position_size * ((entry_price * (1 + reward)) - entry_price)
                            position_type = 0
                            wins += 1

                    elif position_type == -1:
                        if current_high >= entry_price * (1 + risk): 
                            capital = capital + position_size * (entry_price - (entry_price * (1 + risk)))
                            position_type = 0
                            losses += 1
                        elif current_low <= entry_price * (1 - reward): 
                            capital = capital + position_size * (entry_price - (entry_price * (1 - reward)))
                            position_type = 0
                            wins += 1

                    # --- 2. ENTRIES (ONLY IF FLAT) ---
                    if position_type == 0:
                        if long_signal:
                            position_type = 1
                            entry_price = execution_price
                            position_size = capital / execution_price
                        elif short_signal:
                            position_type = -1
                            entry_price = execution_price
                            position_size = capital / execution_price
                            
                    # --- 3. UPDATE CURRENT EQUITY ---
                    if position_type == 1:
                        equity[i+1] = capital + position_size * (data_array[i+1, close_i] - entry_price)
                    elif position_type == -1:
                        equity[i+1] = capital + position_size * (entry_price - data_array[i+1, close_i])
                    else:
                        equity[i+1] = capital
                        
                    # --- 4. MAX DRAWDOWN LOGIC ---
                    if equity[i+1] > peak_equity:
                        peak_equity = equity[i+1]
                    current_drawdown = (peak_equity - equity[i+1]) / peak_equity
                    if current_drawdown > maxdrawdown:
                        maxdrawdown = current_drawdown
                        
                return equity[-1], wins, losses, maxdrawdown, equity

            data_array = data_array.astype(np.float64)
            final_cap, wins, losses, max_dd, eq_curve = loop(
                data_array, 
                user_data["capital"], 
                user_data["risk"], 
                user_data["reward"],
                user_data["oversold"],
                user_data["overbought"]
            )
            trades = wins + losses
            winrate = wins / trades if trades > 0 else 0.0
            return {
                "final_capital": final_cap,
                "trades": trades,
                "win_rate": winrate * 100,
                "max_drawdown": max_dd * 100,
                "equity_curve": eq_curve,
                "wins": wins,
                "losses": losses,
                "status": 1
            }


    def run(self) -> dict:
        try:
            if self.user_data["strategy_name"] == "double-ema":
                data = dl.Load_data(self.user_data["symbol"], self.user_data["time_frame"])
                if len(data) == 0:
                    return {"status": "No data available", "status": 0}
                data_ = i.add_indicator(self.user_data, data)
                if isinstance(data_, dict):
                    return data_
                results = self.run_ema_crossover(user_data=self.user_data, data_array= data_)
                return results
            elif self.user_data["strategy_name"] == "macd":
                data = dl.Load_data(self.user_data["symbol"], self.user_data["time_frame"])
                if len(data) == 0:
                    return {"status": "No data available", "status": 0}
                data_ = i.add_indicator(self.user_data, data)
                if isinstance(data_, dict):
                                return data_
                results = self.run_macd(user_data=self.user_data, data_array= data_)
                return results
            elif self.user_data["strategy_name"] == "bollinger_band":
                data = dl.Load_data(self.user_data["symbol"], self.user_data["time_frame"])
                if len(data) == 0:
                    return {"status": "No data available", "status": 0}
                data_ = i.add_indicator(self.user_data, data)
                if isinstance(data_, dict):
                                return data_
                results = self.run_bollinger(user_data=self.user_data, data_array= data_)
                return results
            elif self.user_data["strategy_name"] == "rsi":
                data = dl.Load_data(self.user_data["symbol"], self.user_data["time_frame"])
                if len(data) == 0:
                    return {"status": "No data available", "status": 0}
                data_ = i.add_indicator(self.user_data, data)
                if isinstance(data_, dict):
                        return data_
                results = self.run_rsi(user_data=self.user_data, data_array= data_)
                return results
            elif self.user_data["strategy_name"] == "vwap":
                data = dl.Load_data(self.user_data["symbol"], self.user_data["time_frame"])
                if len(data) == 0:
                    return {"status": "No data available", "status": 0}
                data_ = i.add_indicator(self.user_data, data)
                if isinstance(data_, dict):
                    return data_
                results = self.run_vwap(user_data=self.user_data, data_array= data_)
                return results
            elif self.user_data["strategy_name"] == "stoch_rsi":
                data = dl.Load_data(self.user_data["symbol"], self.user_data["time_frame"])
                if len(data) == 0:
                    return {"status": "No data available", "status": 0}
                data_ = i.add_indicator(self.user_data, data)
                if isinstance(data_, dict):
                    return data_
                results = self.run_stoch_rsi(user_data=self.user_data, data_array= data_)
                return results
            
        except Exception as e:
            return {"error" : f"Issue {str(e)}", "status" : 0}



    

