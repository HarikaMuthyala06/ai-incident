from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone
import uuid

from app.models.user import UserCreate, UserLogin, UserResponse, TokenResponse, UserRole
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.database import get_db_collection

router = APIRouter()
security = HTTPBearer(auto_error=False)

async def init_default_users():
    """Seed initial demo accounts for immediate testing."""
    users_col = get_db_collection("users")
    existing_admin = await users_col.find_one({"username": "admin"})
    if not existing_admin:
        admin_doc = {
            "_id": str(uuid.uuid4()),
            "id": "USR-001",
            "username": "admin",
            "email": "admin@incidentagent.com",
            "full_name": "SRE Lead Admin",
            "role": UserRole.ADMIN,
            "hashed_password": hash_password("admin123"),
            "created_at": datetime.now(timezone.utc)
        }
        await users_col.insert_one(admin_doc)

    existing_eng = await users_col.find_one({"username": "engineer"})
    if not existing_eng:
        eng_doc = {
            "_id": str(uuid.uuid4()),
            "id": "USR-002",
            "username": "engineer",
            "email": "engineer@incidentagent.com",
            "full_name": "Alex Rivers (On-Call SRE)",
            "role": UserRole.ENGINEER,
            "hashed_password": hash_password("engineer123"),
            "created_at": datetime.now(timezone.utc)
        }
        await users_col.insert_one(eng_doc)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Dependency to extract & validate JWT Bearer token from headers."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in."
        )
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token is invalid or expired. Please log in again."
        )
    
    users_col = get_db_collection("users")
    user_doc = await users_col.find_one({"username": payload["sub"]})
    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found.")
    
    return UserResponse(
        id=user_doc.get("id", str(user_doc.get("_id"))),
        email=user_doc["email"],
        username=user_doc["username"],
        role=user_doc.get("role", UserRole.ENGINEER),
        full_name=user_doc.get("full_name"),
        created_at=user_doc["created_at"]
    )

@router.post("/register", response_model=TokenResponse)
async def register(user_in: UserCreate):
    users_col = get_db_collection("users")
    # Check if username or email already taken
    existing_user = await users_col.find_one({"$or": [{"username": user_in.username}, {"email": user_in.email}]})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email is already registered.")

    user_id = f"USR-{str(uuid.uuid4())[:8].upper()}"
    new_doc = {
        "_id": str(uuid.uuid4()),
        "id": user_id,
        "username": user_in.username,
        "email": user_in.email,
        "full_name": user_in.full_name or user_in.username,
        "role": user_in.role if user_in.role in [UserRole.ADMIN, UserRole.ENGINEER] else UserRole.ENGINEER,
        "hashed_password": hash_password(user_in.password),
        "created_at": datetime.now(timezone.utc)
    }
    await users_col.insert_one(new_doc)

    access_token = create_access_token({"sub": new_doc["username"], "role": new_doc["role"]})
    user_resp = UserResponse(
        id=user_id,
        email=new_doc["email"],
        username=new_doc["username"],
        role=new_doc["role"],
        full_name=new_doc["full_name"],
        created_at=new_doc["created_at"]
    )
    return TokenResponse(access_token=access_token, user=user_resp)

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    # Ensure demo users are seeded
    await init_default_users()
    
    users_col = get_db_collection("users")
    user_doc = await users_col.find_one({
        "$or": [
            {"username": credentials.username_or_email},
            {"email": credentials.username_or_email}
        ]
    })
    
    if not user_doc or not verify_password(credentials.password, user_doc.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password."
        )

    access_token = create_access_token({"sub": user_doc["username"], "role": user_doc.get("role", UserRole.ENGINEER)})
    user_resp = UserResponse(
        id=user_doc.get("id", str(user_doc.get("_id"))),
        email=user_doc["email"],
        username=user_doc["username"],
        role=user_doc.get("role", UserRole.ENGINEER),
        full_name=user_doc.get("full_name"),
        created_at=user_doc["created_at"]
    )
    return TokenResponse(access_token=access_token, user=user_resp)

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: UserResponse = Depends(get_current_user)):
    return current_user
