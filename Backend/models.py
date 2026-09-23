from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Annotated, Literal

"""This file is Responsible for the validation of user inputs from the api endpoints"""

from pydantic import BaseModel, Field, EmailStr
from typing import Annotated

class Register_User(BaseModel):
    f_name: Annotated[str, Field(..., description="First Name of the user")]
    l_name: Annotated[str, Field(..., description="Last Name of the user")]
    email: Annotated[EmailStr, Field(..., description="Email of the user")]
    password: Annotated[str, Field(..., description="password of the user Account")]

class Login_User(BaseModel):
    email : Annotated[EmailStr, Field(..., description="Email of the user")]
    password : Annotated[str, Field(..., description="password of the user Account")]

class Verify_User(BaseModel):
    email : Annotated[EmailStr, Field(..., description="Email of the user")]
    code : Annotated[str, Field(..., description="Verification Code which is recieved by user")]

class  Reset_data(BaseModel):
    code : Annotated[str, Field(..., description="password reset token recieved by user")]
    new_pass : Annotated[str, Field(..., description="new password of the user")]
class  check_user(BaseModel):
        email : Annotated[EmailStr, Field(..., description="Email for the checking user account")]

class Strategy_Result_Request(BaseModel):
    strategy_id: Annotated[int, Field(..., gt=0, description="Primary key of the saved strategy")]

class ema_crossover(BaseModel):
    strategy_name : Annotated[str, Field(..., description="Name of the Strategy or can be indicator name as well like double-EMA, MACD, RSI")]
    ema_short : Annotated[int, Field(..., description="Short exponential moving average of the two emacross strategy")]
    ema_long : Annotated[int, Field(..., description="long exponential moving average of the two emacross strategy")]
    risk : Annotated[float, Field(..., description="risk percentage of the total capital per trade")]
    reward : Annotated[float, Field(..., description="profit percentage of the total capital per trade")]
    market_type : Annotated[Literal["spot", "futures"], Field(..., description="Market type  for backtest example : Spot Market or Futures Market")]
    symbol :  Annotated[str, Field(..., description="SYMBOL of the coin whose data will be used in backtest like BTCUSDT, ETHUSDT")]
    time_frame: Annotated[str, Field(..., description="Timeframe for data of SYMBOL of the coin used in backtest like for 1-minute timeframe is will be 1m, for one-hour it will be 1h")]
    capital : Annotated[float, Field(..., description="Initial capital for the backtest")]

class MACD(BaseModel):
    strategy_name : Annotated[str, Field(..., description="Name of the Strategy or can be indicator name as well like double-EMA, MACD, RSI")]
    ema_fast : Annotated[int, Field(..., description="Short exponential moving average period for the MACD strategy")]
    ema_slow : Annotated[int, Field(..., description="Long exponential moving average period for the MACD strategy")]
    signal_line : Annotated[int, Field(..., description="Signal line period for the MACD strategy")]
    risk : Annotated[float, Field(..., description="risk percentage of the total capital per trade")]
    reward : Annotated[float, Field(..., description="profit percentage of the total capital per trade")]
    market_type : Annotated[Literal["spot", "futures"], Field(..., description="Market type  for backtest example : Spot Market or Futures Market")]
    symbol :  Annotated[str, Field(..., description="SYMBOL of the coin whose data will be used in backtest like BTCUSDT, ETHUSDT")]
    time_frame: Annotated[str, Field(..., description="Timeframe for data of SYMBOL of the coin used in backtest like for 1-minute timeframe is will be 1m, for one-hour it will be 1h")]
    capital : Annotated[float, Field(..., description="Initial capital for the backtest")]

class Bollinger(BaseModel):
    strategy_name : Annotated[str, Field(..., description="Name of the Strategy or can be indicator name as well like double-EMA, MACD, RSI")]
    ema_length : Annotated[int, Field(..., description="moving average period for the Bollinger Bands strategy")]
    std_dev : Annotated[int, Field(..., description="Standard deviation period for the Bollinger Bands strategy")]
    risk : Annotated[float, Field(..., description="risk percentage of the total capital per trade")]
    reward : Annotated[float, Field(..., description="profit percentage of the total capital per trade")]
    market_type : Annotated[Literal["spot", "futures"], Field(..., description="Market type  for backtest example : Spot Market or Futures Market")]
    symbol :  Annotated[str, Field(..., description="SYMBOL of the coin whose data will be used in backtest like BTCUSDT, ETHUSDT")]
    time_frame: Annotated[str, Field(..., description="Timeframe for data of SYMBOL of the coin used in backtest like for 1-minute timeframe is will be 1m, for one-hour it will be 1h")]
    capital : Annotated[float, Field(..., description="Initial capital for the backtest")]

class RSI(BaseModel):
    strategy_name : Annotated[str, Field(..., description="Name of the Strategy or can be indicator name as well like double-EMA, MACD, RSI")]
    rsi_length : Annotated[int, Field(..., description="moving average period for the RSI strategy")]
    rsi_oversold : Annotated[int, Field(..., description="Oversold level for the RSI strategy")]
    rsi_overbought : Annotated[int, Field(..., description="Overbought level for the RSI strategy")]
    risk : Annotated[float, Field(..., description="risk percentage of the total capital per trade")]
    reward : Annotated[float, Field(..., description="profit percentage of the total capital per trade")]
    market_type : Annotated[Literal["spot", "futures"], Field(..., description="Market type  for backtest example : Spot Market or Futures Market")]
    symbol :  Annotated[str, Field(..., description="SYMBOL of the coin whose data will be used in backtest like BTCUSDT, ETHUSDT")]
    time_frame: Annotated[str, Field(..., description="Timeframe for data of SYMBOL of the coin used in backtest like for 1-minute timeframe is will be 1m, for one-hour it will be 1h")]
    capital : Annotated[float, Field(..., description="Initial capital for the backtest")]

class VWAP(BaseModel):
    strategy_name : Annotated[str, Field(..., description="Name of the Strategy or can be indicator name as well like double-EMA, MACD, RSI")]
    vwap_length : Annotated[int, Field(..., description="moving average period for the VWAP strategy")]
    std_dev : Annotated[int, Field(..., description="Standard deviation period for the VWAP strategy")]
    risk : Annotated[float, Field(..., description="risk percentage of the total capital per trade")]
    reward : Annotated[float, Field(..., description="profit percentage of the total capital per trade")]
    market_type : Annotated[Literal["spot", "futures"], Field(..., description="Market type  for backtest example : Spot Market or Futures Market")]
    symbol :  Annotated[str, Field(..., description="SYMBOL of the coin whose data will be used in backtest like BTCUSDT, ETHUSDT")]
    time_frame: Annotated[str, Field(..., description="Timeframe for data of SYMBOL of the coin used in backtest like for 1-minute timeframe is will be 1m, for one-hour it will be 1h")]
    capital : Annotated[float, Field(..., description="Initial capital for the backtest")]

class StochRSI(BaseModel):
    strategy_name : Annotated[str, Field(..., description="Name of the Strategy or can be indicator name as well like double-EMA, MACD, RSI")]
    rsi_length: Annotated[int, Field(..., gt=0, description="RSI lookback period (usually 14)")]
    stoch_length: Annotated[int, Field(..., gt=0, description="Stochastic lookback period (usually 14)")]
    k_smooth: Annotated[int, Field(..., gt=0, description="Smoothing period for %K line (usually 3)")]
    d_smooth: Annotated[int, Field(..., gt=0, description="Smoothing period for %D line (usually 3)")]
    oversold: Annotated[int, Field(..., gt=0, description="Oversold threshold (usually 20)")]
    overbought: Annotated[int, Field(..., gt=0, description="Overbought threshold (usually 80)")]
    risk : Annotated[float, Field(..., description="risk percentage of the total capital per trade")]
    reward : Annotated[float, Field(..., description="profit percentage of the total capital per trade")]
    market_type : Annotated[Literal["spot", "futures"], Field(..., description="Market type  for backtest example : Spot Market or Futures Market")]
    symbol :  Annotated[str, Field(..., description="SYMBOL of the coin whose data will be used in backtest like BTCUSDT, ETHUSDT")]
    time_frame: Annotated[str, Field(..., description="Timeframe for data of SYMBOL of the coin used in backtest like for 1-minute timeframe is will be 1m, for one-hour it will be 1h")]
    capital : Annotated[float, Field(..., description="Initial capital for the backtest")]
