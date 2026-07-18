from fastapi import FastAPI
from models import Register_User, Verify_User, Login_User, Reset_data, check_user
from db import DataBase_helper
from fastapi.responses import JSONResponse
from verfier import Verify
from encrypter import Hash
app = FastAPI()
dbh = DataBase_helper()

@app.post("/register")
def register(user : Register_User):
    
    try:
        rs = dbh.register(fname= user.f_name, lname = user.l_name, email = user.email, code = user.password)
        if rs:
            return JSONResponse(status_code=200, content= {"massage" : "Added Succesfully"})
    except Exception as e:
        return JSONResponse(status_code=500, content= {"massage" : "Issue in backend"})
    

@app.post("/verify")
def verify(data : Verify_User):
    try:
        rs = Verify.verify_token(data.email, data.code)
        if rs:
            return JSONResponse(status_code=200, content= {"massage" : "verified"})
    except Exception as e:
        return JSONResponse(status_code=500, content= {"massage" : "Issue in Backend"})
    
@app.post("/login")
def login(data: Login_User):
    try:
        rs = dbh.Login(data.email, data.password)
        if rs:
            return JSONResponse(status_code=200, content= {"massage" : "verified"})
    except Exception as e:
        return JSONResponse(status_code=500, content= {"massage" : "Issue in Backend"})

@app.post("/check_user")
def check_user_for_pass_reset(user : check_user):
    try:
        if dbh.fetch_user(check_user.email):
            v = Verify()
            code = v.send_token(check_user.email)
            if code:
                rs = dbh.add_reset_token(user['u_id'], code)
                if rs:
                    return JSONResponse(status_code=200, content= {"massage" : "user found proceed to the next page"})
                else:
                    return JSONResponse(status_code=500, content= {"massage" : "Issue in db"})
        else:
            return JSONResponse(status_code=500, content= {"massage" : "No account exists"})
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
