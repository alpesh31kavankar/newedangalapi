# from sqlalchemy import Column, Integer, String, Text, DateTime, func
# from app.database import Base

# class User(Base):
#     __tablename__ = "users"

#     user_id = Column(Integer, primary_key=True, index=True)
#     username = Column(String(100), unique=True, index=True, nullable=False)
#     email = Column(String(200), unique=True, index=True, nullable=False)
#     password_hash = Column(Text, nullable=False)
#     full_name = Column(String(200), nullable=True)
#     phone_number = Column(String(20), nullable=True)
#     address = Column(Text, nullable=True)
#     created_at = Column(DateTime(timezone=False), server_default=func.now())


from sqlalchemy import Column, BigInteger, String, Boolean, Date, Text, TIMESTAMP
from sqlalchemy.sql import func
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True, index=True)
    password_hash = Column(Text, nullable=False)
    gender = Column(String(10))
    birth_date = Column(Date, nullable=False)
    pincode = Column(String(12), nullable=False)
    referral_code = Column(String(20), unique=True)
    referred_by = Column(String(20))
    profile_image = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    mobile_no = Column(String(15), unique=True, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
