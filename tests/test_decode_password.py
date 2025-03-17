from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Example verification function
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Usage example
stored_hash = "$2b$12$KNUeyBDFLu6bRprf94MRhumOgBBaxaAc1RH3HqWDe1KUaaHACZ2AW"
is_valid = verify_password("ngocdz123", stored_hash)
print(f"Password is valid: {is_valid}")