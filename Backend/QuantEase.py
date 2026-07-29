from fastapi import FastAPI
from models import Register_User, Verify_User, Login_User, Reset_data, check_user
from db import DataBase_helper
from fastapi.responses import JSONResponse
from verfier import Verify
from encrypter import Hash
from fastapi.middleware.cors import CORSMiddleware

dbh = DataBase_helper()

app = FastAPI()

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
def login(data: Login_User):
    try:
        rs = dbh.Login(data.email, data.password)
        if rs:
            return JSONResponse(status_code=200, content= {"massage" : "verified"})
        else:
            return JSONResponse(status_code= 401, content={"message":"Wrong Email or Password"})
    except Exception as e:
        return JSONResponse(status_code=500, content= {"massage" : "Issue in Backend"})

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
