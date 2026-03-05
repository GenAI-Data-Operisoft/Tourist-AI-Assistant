"""Simple Cognito authentication for FastAPI"""
import os
import jwt
import requests
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from functools import lru_cache

security = HTTPBearer(auto_error=False)

COGNITO_REGION = os.getenv('COGNITO_REGION', 'ap-south-1')
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID', '')
COGNITO_APP_CLIENT_ID = os.getenv('COGNITO_APP_CLIENT_ID', '')

@lru_cache()
def get_jwks():
    """Get Cognito public keys"""
    url = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    return requests.get(url).json()

def verify_token(token: str):
    """Verify JWT token"""
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header['kid']
        
        jwks = get_jwks()
        key = next((k for k in jwks['keys'] if k['kid'] == kid), None)
        if not key:
            raise HTTPException(401, "Invalid token")
        
        from jwt.algorithms import RSAAlgorithm
        public_key = RSAAlgorithm.from_jwk(key)
        
        payload = jwt.decode(
            token, public_key, algorithms=['RS256'],
            audience=COGNITO_APP_CLIENT_ID,
            options={"verify_exp": True}
        )
        return payload
    except Exception as e:
        raise HTTPException(401, f"Auth failed: {str(e)}")

async def get_current_user(credentials = Depends(security)):
    """Get authenticated user"""
    if not credentials:
        raise HTTPException(401, "Not authenticated")
    return verify_token(credentials.credentials)
