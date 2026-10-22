import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import Session, sessionmaker
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Annotated
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Local Imports
from models import Base, User, Invoice
from schemas import UserCreate, InvoiceCreate, InvoiceResponse, Token
from qb_export import generate_iif_string

# --- Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-for-local-testing-only-do-not-use-in-prod-1234567890abcdef")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL")

# Default to SQLite if no DATABASE_URL is provided (Local Dev)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./water_company.db"
    print("⚠️  No DATABASE_URL found. Falling back to SQLite (Local Dev Mode).")

# Determine Engine Configuration based on URL Scheme
if DATABASE_URL.startswith("postgresql"):
    # Ensure we use the modern psycopg v3 driver
    if "+psycopg://" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,      # Check if connection is alive before using
        pool_size=5,             # Keep small pool for free tiers
        max_overflow=10,         # Allow burst connections
        echo=False               # Set True to debug SQL queries
    )
else:
    # SQLite specific settings
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="Water Co Billing API")

# --- CORS Middleware ---
# For Production, replace '*' with your actual frontend domain (e.g., Vercel/Netlify URL)
# For Cloudflare Tunnels, you MUST add the specific trycloudflare.com subdomain here
origins = [
    "http://localhost:5173",       # Local Vite
    "http://127.0.0.1:5173",       # Local Vite Alt
    "https://jesus-rescue-corpus-incentives.trycloudflare.com", # <--- PASTE YOUR CURRENT FRONTEND CLOUDFLARE URL HERE
    # Add more origins as needed, e.g.:
    # "https://your-app.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Dependencies ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DbDep = Annotated[Session, Depends(get_db)]

def get_current_user(token: str = Depends(oauth2_scheme), db: DbDep = None):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

# --- Helper Functions ---

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Startup Event: Create Tables & Default Admin ---
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        # Test Connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Successfully connected to Database.")
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        print("✅ Database schema verified/created.")

        # Create Default Admin if missing
        admin = db.query(User).filter(User.username == "qbbadmin").first()
        if not admin:
            print("🛠️  Creating default admin user...")
            new_admin = User(username="qbbadmin", email="admin@water.co", role="admin")
            new_admin.hashed_password = new_admin.get_hashed_password("ChangeMe123!")
            db.add(new_admin)
            db.commit()
            print("✅ Default Admin Created: qbbadmin / ChangeMe123!")
        else:
            print("ℹ️  Admin user 'qbbadmin' already exists.")
            
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        # Do not exit(1) so the server starts even if DB is down, allowing health checks
    finally:
        db.close()

# --- Endpoints ---

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: DbDep = None):
    """
    Handles user login and returns a JWT token containing 'sub' (username) and 'role'.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # IMPORTANT: Include 'role' in the token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=dict)
def register_user(user_in: UserCreate, db: DbDep = None):
    """
    Registers a new standard user.
    """
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = User(username=user_in.username, email=user_in.email, role=user_in.role)
    new_user.hashed_password = new_user.get_hashed_password(user_in.password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": f"User '{new_user.username}' registered successfully."}

@app.post("/invoices/", response_model=InvoiceResponse)
def create_invoice(invoice_in: InvoiceCreate, current_user: User = Depends(get_current_user), db: DbDep = None):
    """
    Creates a new invoice entry. Linked to the current logged-in user.
    """
    invoice_data = invoice_in.model_dump()
    new_invoice = Invoice(**invoice_data, user_id=current_user.id)
    
    db.add(new_invoice)
    try:
        db.commit()
        db.refresh(new_invoice)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
        
    return new_invoice

@app.get("/invoices/my", response_model=list[InvoiceResponse])
def get_my_invoices(current_user: User = Depends(get_current_user), db: DbDep = None):
    """
    Returns all invoices created by the current user.
    """
    return db.query(Invoice).filter(Invoice.user_id == current_user.id).order_by(Invoice.created_at.desc()).all()

@app.get("/invoices/pending", response_model=list[InvoiceResponse])
def get_pending_invoices(admin_user: User = Depends(require_admin), db: DbDep = None):
    """
    Returns all invoices with status 'PENDING'. Only accessible by Admins.
    """
    return db.query(Invoice).filter(Invoice.status == "PENDING").all()

@app.get("/invoices/approved/count", response_model=dict)
def get_approved_count(admin_user: User = Depends(require_admin), db: DbDep = None):
    """
    Returns the total count of APPROVED invoices.
    """
    count = db.query(func.count(Invoice.id)).filter(Invoice.status == "APPROVED").scalar()
    return {"count": count}

@app.patch("/invoices/{invoice_id}/approve", response_model=InvoiceResponse)
def approve_invoice(invoice_id: int, admin_user: User = Depends(require_admin), db: DbDep = None):
    """
    Marks an invoice as APPROVED.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice.status = "APPROVED"
    db.commit()
    db.refresh(invoice)
    return invoice

@app.get("/export/iif")
def export_approved_to_iif(admin_user: User = Depends(require_admin), db: DbDep = None):
    """
    Generates a QuickBooks .IIF file from all APPROVED invoices.
    Marks them as EXPORTED afterwards to prevent duplicates.
    """
    invoices = db.query(Invoice).filter(Invoice.status == "APPROVED").all()
    
    if not invoices:
        raise HTTPException(status_code=404, detail="No approved invoices to export")
        
    iif_content = generate_iif_string(invoices)
    
    # Mark them as EXPORTED
    for inv in invoices:
        inv.status = "EXPORTED"
    db.commit()
    
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        content=iif_content, 
        media_type="application/octet-stream", 
        headers={
            "Content-Disposition": "attachment; filename=qb_batch_import.iif"
        }
    )
    
# Add this to the VERY END of backend/main.py

if __name__ == "__main__":
    import uvicorn
    # Render provides PORT env var. Default to 8000 for local dev.
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)