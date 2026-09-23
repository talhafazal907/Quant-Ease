from fastapi import Depends, FastAPI, HTTPException, status
from models import *
from db import DataBase_helper
from fastapi.responses import JSONResponse
from verfier import Verify
from encrypter import Hash
from fastapi.middleware.cors import CORSMiddleware
from Backtesting_Engine.backtesting_engine import Backtesting_Engine
from auth import bearer_scheme, create_access_token, decode_access_token
import json
import os
import numpy as np
from pathlib import Path

dbh = DataBase_helper()

app = FastAPI(title = "QuantEase Backend API", description = "This is the backend API for QuantEase App", version = "1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, # Changed to False
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
def register(user : Register_User):
        rs = dbh.register(fname= user.f_name, lname = user.l_name, email = user.email, password = user.password)
        if rs:
            return JSONResponse(status_code=200, content= {"massage" : "Account Registered"})
        else:    
            return JSONResponse(status_code=500, content= {"massage" : "Issue in DB"})
    

@app.post("/verify")
def verify(data: Verify_User):
    try:
        rs = dbh.verify(data.email, data.code)
        if rs:
            # Note: Fixed typo "massage" to "message"
            return JSONResponse(status_code=200, content={"message": "verified"})
        else:
            # Handle the scenario where the code is wrong or email isn't found
            return JSONResponse(status_code=400, content={"message": "Invalid verification code or email"})
            
    except Exception as e:
        # Print the actual error to your terminal for easier future debugging
        print(f"Verification Error: {e}") 
        return JSONResponse(status_code=500, content={"message": "Issue in Backend"})
    
@app.post("/login")
def login(data: Login_User, ):
    try:
        user = dbh.authenticate_user(data.email, data.password)
        if not user:
            return JSONResponse(status_code=401, content={"message": "Wrong Email or Password"})

        access_token = create_access_token(user["u_id"], user["email"])
        return JSONResponse(
            status_code=200,
            content={
                "message": "verified",
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": 24 * 60 * 60,
            },
        )
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})
    except Exception:
        return JSONResponse(status_code=500, content={"message": "Issue in Backend"})

@app.post("/check_user")
def check_user_for_pass_reset(user : check_user):
    try:
        u = dbh.fetch_user(user.email)
        if u:
            v = Verify()
            code = v.send_token(u["email"])
            if code:
                rs = dbh.add_reset_token(u['u_id'], code)
                if rs:
                    return JSONResponse(status_code=200, content= {"massage" : "user found proceed to the next page"})
                else:
                    return JSONResponse(status_code=500, content= {"massage" : "Issue in database"})
            else:
                return JSONResponse(status_code=500, content= {"massage" : "Issue in Backend"})
        else:
            return JSONResponse(status_code=401, content= {"massage" : "No account exists"})
    except Exception as e:
        return JSONResponse(status_code=500, content= {"massage" : "Issue in Backend"})
                


@app.put("/reset_pass")
def reset(data : Reset_data):
    h = Hash()
    hash = h.create_hash(data.new_pass)
    if hash:
        rs = dbh.update_pass(data.code, hash)
        if rs:
            return JSONResponse(status_code=200, content= {"massage" : "password reset succesfully"})
        else:
            return JSONResponse(status_code=500, content= {"massage" : "Issue in Database"})
    else:
        return JSONResponse(status_code=500, content= {"massage" : "Issue in Backend"})

# Now from here started the core  functionality of the QuantEase App

def get_current_user_id(credentials=Depends(bearer_scheme)):
    user_id = decode_access_token(credentials)
    user = dbh.fetch_user_by_id(user_id)
    if not user or user["is_verif"] != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


@app.post("/backtest_two_ema_crossover")
def backtest_two_ema_crossover(data: ema_crossover, user_id: int = Depends(get_current_user_id)):
    try:
        strategy_data = data.model_dump()
        backtester = Backtesting_Engine(strategy_data)
        results = backtester.run()
        
        if results["status"] == 1:
            #Convert the array to a list right before sending the response
            results["equity_curve"] = results["equity_curve"].tolist()
            if not dbh.save_backtest_activity(user_id, strategy_data, results):
                return JSONResponse(status_code=500, content={"message": "Unable to save backtest activity"})
            
            return JSONResponse(status_code=200, content={"message": "Backtest completed successfully", "results": results})
        else:
            return JSONResponse(status_code=500, content={"message": "Backtest failed", "details": results})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Issue in Backend", "error": str(e)})


@app.post("/backtest_macd")
def backtest_macd(data: MACD, user_id: int = Depends(get_current_user_id)):
    try:
        # data.model_dump() passes the validated dictionary to your engine
        strategy_data = data.model_dump()
        backtester = Backtesting_Engine(strategy_data)
        results = backtester.run()
        
        if results["status"] == 1:
            # Convert the array to a list right before sending the response
            results["equity_curve"] = results["equity_curve"].tolist()
            if not dbh.save_backtest_activity(user_id, strategy_data, results):
                return JSONResponse(status_code=500, content={"message": "Unable to save backtest activity"})
            
            return JSONResponse(
                status_code=200, 
                content={
                    "message": "Backtest completed successfully", 
                    "results": results
                }
            )
            
        elif results["status"] == 0:
            # 400 is better here because the engine ran, but the input data/logic failed gracefully
            return JSONResponse(
                status_code=400, 
                content={
                    "message": "Backtest failed to execute completely", 
                    "details": results
                }
            )
            
    except Exception as e:
        # 500 is perfect here, as it catches real crashes
        return JSONResponse(
            status_code=500, 
            content={
                "message": "Internal Backend Issue", 
                "error": str(e)
            }
        )

@app.post("/backtest_bollinger")
def backtest_bollinger(data: Bollinger, user_id: int = Depends(get_current_user_id)):
    try:
        # data.model_dump() passes the validated dictionary to your engine
        strategy_data = data.model_dump()
        backtester = Backtesting_Engine(strategy_data)
        results = backtester.run()
        
        if results["status"] == 1:
            # Convert the array to a list right before sending the response
            results["equity_curve"] = results["equity_curve"].tolist()
            if not dbh.save_backtest_activity(user_id, strategy_data, results):
                return JSONResponse(status_code=500, content={"message": "Unable to save backtest activity"})
            
            return JSONResponse(
                status_code=200, 
                content={
                    "message": "Backtest completed successfully", 
                    "results": results
                }
            )
            
        elif results["status"] == 0:
            # 400 is better here because the engine ran, but the input data/logic failed gracefully
            return JSONResponse(
                status_code=400, 
                content={
                    "message": "Backtest failed to execute completely", 
                    "details": results
                }
            )
            
    except Exception as e:
        # 500 is perfect here, as it catches real crashes
        return JSONResponse(
            status_code=500, 
            content={
                "message": "Internal Backend Issue", 
                "error": str(e)
            }
        )

@app.post("/backtest_rsi")
def backtest_rsi(data: RSI, user_id: int = Depends(get_current_user_id)):
    try:
        # data.model_dump() passes the validated dictionary to your engine
        strategy_data = data.model_dump()
        backtester = Backtesting_Engine(strategy_data)
        results = backtester.run()
        
        if results["status"] == 1:
            # Convert the array to a list right before sending the response
            results["equity_curve"] = results["equity_curve"].tolist()
            if not dbh.save_backtest_activity(user_id, strategy_data, results):
                return JSONResponse(status_code=500, content={"message": "Unable to save backtest activity"})
            
            return JSONResponse(
                status_code=200, 
                content={
                    "message": "Backtest completed successfully", 
                    "results": results
                }
            )
            
        elif results["status"] == 0:
            # 400 is better here because the engine ran, but the input data/logic failed gracefully
            return JSONResponse(
                status_code=400, 
                content={
                    "message": "Backtest failed to execute completely", 
                    "details": results
                }
            )
            
    except Exception as e:
        # 500 is perfect here, as it catches real crashes
        return JSONResponse(
            status_code=500, 
            content={
                "message": "Internal Backend Issue", 
                "error": str(e)
            }
        )

@app.post("/backtest_vwap")
def backtest_vwap(data: VWAP, user_id: int = Depends(get_current_user_id)):
    try:
        # data.model_dump() passes the validated dictionary to your engine
        strategy_data = data.model_dump()
        backtester = Backtesting_Engine(strategy_data)
        results = backtester.run()
        
        if results["status"] == 1:
            # Convert the array to a list right before sending the response
            results["equity_curve"] = results["equity_curve"].tolist()
            if not dbh.save_backtest_activity(user_id, strategy_data, results):
                return JSONResponse(status_code=500, content={"message": "Unable to save backtest activity"})
            
            return JSONResponse(
                status_code=200, 
                content={
                    "message": "Backtest completed successfully", 
                    "results": results
                }
            )
            
        elif results["status"] == 0:
            # 400 is better here because the engine ran, but the input data/logic failed gracefully
            return JSONResponse(
                status_code=400, 
                content={
                    "message": "Backtest failed to execute completely", 
                    "details": results
                }
            )
    except Exception as e:
        # 500 is perfect here, as it catches real crashes
        return JSONResponse(
            status_code=500, 
            content={
                "message": "Internal Backend Issue", 
                "error": str(e)
            }
        )

    
@app.post("/backtest_stoch_rsi")
def backtest_stoch_rsi(data: StochRSI, user_id: int = Depends(get_current_user_id)):
    try:
        # data.model_dump() passes the validated dictionary to your engine
        strategy_data = data.model_dump()
        backtester = Backtesting_Engine(strategy_data)
        results = backtester.run()
        
        if results["status"] == 1:
            # Convert the array to a list right before sending the response
            results["equity_curve"] = results["equity_curve"].tolist()
            if not dbh.save_backtest_activity(user_id, strategy_data, results):
                return JSONResponse(status_code=500, content={"message": "Unable to save backtest activity"})
            
            return JSONResponse(
                status_code=200, 
                content={
                    "message": "Backtest completed successfully", 
                    "results": results
                }
            )
            
        elif results["status"] == 0:
            # 400 is better here because the engine ran, but the input data/logic failed gracefully
            return JSONResponse(
                status_code=400, 
                content={
                    "message": "Backtest failed to execute completely", 
                    "details": results
                }
            )
            
    except Exception as e:
        # 500 is perfect here, as it catches real crashes
        return JSONResponse(
            status_code=500, 
            content={
                "message": "Internal Backend Issue", 
                "error": str(e)
            }
        )
  

@app.get("/my_strategies")
def get_my_strategies(user_id: int = Depends(get_current_user_id)):
    try:
        if not dbh.fetch_user_by_id(user_id):
            return JSONResponse(status_code=404, content={"message": "User not found"})
            
        raw_strategies = dbh.get_user_strategies(user_id)
        parsed_strategies = []
        
        for row in raw_strategies:
            # Decode the bytes object and parse the JSON string into a Python dict
            config_dict = json.loads(row['config_params'].decode('utf-8'))
            
            parsed_strategies.append({
                "id": row['id'],
                "strategy_name": row['Strategy_name'],
                "config_params": config_dict,
                "created_at": row['created_at'].isoformat() # Convert datetime to string
            })
            
        return JSONResponse(
            status_code=200, 
            content={
                "message": "Strategies fetched successfully", 
                "strategies": parsed_strategies
            }
        )
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Issue in Backend", "error": str(e)})


def _json_number(value):
    if value is None:
        return None
    return float(value)


def _load_equity_curve(equity_path: str | bytes | bytearray) -> list:
    """Load a saved curve only from the local equity-curve directory."""
    # FIX: Include bytearray in the instance check
    if isinstance(equity_path, (bytes, bytearray)):
        equity_path = equity_path.decode("utf-8")
        
    if not equity_path:
        raise FileNotFoundError("No equity curve was recorded for this result.")

    curves_directory = (Path(__file__).resolve().parent / "equity_curves").resolve()
    curve_file = Path(equity_path).resolve()
    
    try:
        curve_file.relative_to(curves_directory)
    except ValueError as exc:
        raise ValueError("Invalid equity curve location.") from exc

    if not curve_file.is_file():
        raise FileNotFoundError("The saved equity curve could not be found.")

    return np.load(curve_file, allow_pickle=False).tolist()


@app.post("/results")
def get_strategy_results(data: Strategy_Result_Request, user_id: int = Depends(get_current_user_id)):
    """Return one saved result only when its strategy belongs to the JWT user."""
    try:
        row = dbh.get_user_results_by_strategy_id(data.strategy_id, user_id)
        if not row:
            return JSONResponse(status_code=404, content={"message": "Results not found for this strategy"})

        results = {
            "r_id": row.get("r_id"),
            "s_id": row.get("s_id"),
            "initial_capital": _json_number(row.get("initial_capital")),
            "final_capital": _json_number(row.get("final_capital")),
            "trades": int(row.get("Total_trades") or 0),
            "wins": int(row.get("wins") or 0),
            "losses": int(row.get("Losses") or 0),
            "max_drawdown": _json_number(row.get("max_drawdown")),
            "win_rate": _json_number(row.get("winrate")),
            "equity_curve": _load_equity_curve(row.get("equity_data")),
        }
        return JSONResponse(status_code=200, content={"message": "Results fetched successfully", "results": results})
    except (FileNotFoundError, ValueError):
        return JSONResponse(status_code=500, content={"message": "Saved equity curve is unavailable for this result"})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"message": "Issue in Backend", "error": str(exc)})


