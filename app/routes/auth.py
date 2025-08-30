from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import app.schemas.auth as auth_schemas
import app.models as models
from app.database import SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os 

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7
router_auth = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials",
                                         headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credential_exception
    
    except JWTError:
        raise credential_exception

    user = db.query(models.UsersDB).filter(models.UsersDB.id == user_id).first()
    if user is None:
        raise credential_exception
    
    if db.query(models.BlacklistedTokenDB).filter_by(token=token).first():
        raise credential_exception

    return user


### Register new user ###
@router_auth.post("/register")
def user_register(user: auth_schemas.UserRegister, db: Session = Depends(get_db)):
    
    # check if user already exists
    existing_user = db.query(models.UsersDB).filter(
        (models.UsersDB.username == user.username) | 
        (models.UsersDB.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username or email already registered")

    # add new user
    new_user = models.UsersDB(
        username=user.username,
        email=user.email,
        hashed_password=pwd_context.hash(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "message": f"User {new_user.id} registered",
    }


### User login ###
@router_auth.post("/login", response_model=auth_schemas.TokenData)
def user_login(login: auth_schemas.UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(models.UsersDB).filter(models.UsersDB.username == login.username).first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User not found")

    if not pwd_context.verify(login.password, existing_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect username, email or password")
    
    access_token = create_access_token(data={"sub": str(existing_user.id)})
    
    refresh_token = create_refresh_token(data={"sub": str(existing_user.id)})
    
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

    db_refresh = models.RefreshTokenDB(
        token=refresh_token,
        user_id=existing_user.id,
        expires_at=expires_at
    )
    db.add(db_refresh)
    db.commit()

    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


### Refresh access token ###
@router_auth.post("/refresh", response_model=auth_schemas.TokenData)
def refresh_token(refresh_request: auth_schemas.RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Invalid refresh token")
        
        db_token = db.query(models.RefreshTokenDB).filter_by(token=refresh_request.refresh_token).first()
        if db_token is None or db_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Refresh token expired or invalid")
        
        access_token = create_access_token(data={"sub": str(user_id)})
    
        new_refresh_token = create_refresh_token(data={"sub": str(user_id)})
        
        db_token.token = new_refresh_token
        db_token.expires_at = datetime.fromtimestamp(
            jwt.decode(new_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])["exp"],
            tz=timezone.utc
        )
        db.commit()
        
        return {
            "access_token": access_token, 
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username, email or password")
        

### User logout ###
@router_auth.post("/logout")
def user_logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    blacklisted_token = models.BlacklistedTokenDB(
        token=token,
        expires_at=expires_at,
        user_id=user_id
    )

    db.add(blacklisted_token)
    db.query(models.RefreshTokenDB).filter(models.RefreshTokenDB.user_id == user_id).delete()
    db.commit()

    return {"message": "Successfully logged out"}