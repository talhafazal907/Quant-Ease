from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Annotated, Literal

"""This file is Responsible for the validation of user inputs from the api endpoints"""

class Register_User(BaseModel):
    f_name : Annotated[...,str, Field(..., description="First Name of the user")]
    l_name : Annotated[..., str, Field(..., description="Last Name of the user")]
    email : Annotated[..., EmailStr, Field(..., description="Email of the user")]
    password : Annotated[..., str, Field(..., description="password of the user Account")]

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