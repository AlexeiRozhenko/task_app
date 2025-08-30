from pydantic import BaseModel, Field, EmailStr, field_validator

class UserRegister(BaseModel):
    username: str
    email: EmailStr = Field(max_length=50)
    password: str

    @field_validator("password")
    def validate_password(cls, password: str):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if password.islower() or password.isupper():
            raise ValueError("Password must contain both uppercase and lowercase letters")
        if password.isalnum():
            raise ValueError("Password must include at least one special character (e.g., !@#$%)")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must include at least one uppercase letter")
        return password


class UserLogin(BaseModel):
    username: str = Field(max_length=50)
    password: str = Field(max_length=30)


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshRequest(BaseModel):
    refresh_token: str