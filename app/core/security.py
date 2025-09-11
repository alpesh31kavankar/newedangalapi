from passlib.context import CryptContext

# Create a context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash a plain password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Optional: Add password verification function
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
