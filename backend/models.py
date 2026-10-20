from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.ext.declarative import declarative_base

# Initialize Argon2 hasher once
ph = PasswordHasher()

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="standard") # 'admin' or 'standard'
    is_active = Column(Boolean, default=True)

    def verify_password(self, plain_password):
        try:
            return ph.verify(self.hashed_password, plain_password)
        except VerifyMismatchError:
            return False
        except Exception:
            return False

    def get_hashed_password(self, plain_password):
        return ph.hash(plain_password)

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Business Fields
    customer_name = Column(String, nullable=False)
    customer_id = Column(String, nullable=False)      # Unique ID from records
    customer_address = Column(String, nullable=False) # Delivery Location
    bottles_delivered = Column(Integer, nullable=False) # Quantity
    
    # Workflow
    status = Column(String, default="PENDING") # PENDING, APPROVED, EXPORTED
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="invoices")

User.invoices = relationship("Invoice", order_by=Invoice.id, back_populates="user")