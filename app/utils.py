from passlib.context import CryptContext

# Create password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Return a bcrypt-hashed version of the given plain password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if the plain password matches the stored hashed password."""
    return pwd_context.verify(plain_password, hashed_password)
