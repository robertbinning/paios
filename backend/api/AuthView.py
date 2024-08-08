from starlette.responses import JSONResponse
from backend.managers.AuthManager import AuthManager
import logging
from backend.schemas import RegistrationOptions, VerifyAuthentication, AuthenticationOptions, VerifyRegistration
import jwt
import datetime
from common.config import SECRET_KEY

logger = logging.getLogger(__name__)

class AuthView:
    def __init__(self):
        self.am = AuthManager()

    async def generate_registration_options(self, body: RegistrationOptions):
        challenge, options = await self.am.registration_options(body["email"])

        if not options:
            return JSONResponse({"error": "Something went wrong"}, status_code=500)
        
        return JSONResponse({"options": options, "challenge": challenge}, status_code=200)

    async def verify_registration(self, body: VerifyRegistration):
        verify = await self.am.registrationResponse(body["challenge"], body["email"], body["user_id"], body["att_resp"])
        if not verify:
            return JSONResponse({"message": "Failed"}, status_code=401)
        
        return JSONResponse({"message": "Success"}, status_code=200)
    
    async def generate_authentication_options(self, body: AuthenticationOptions):
        challenge, options = await self.am.signinRequestOptions(body["email"])
        if not options:
            return JSONResponse({"error": "Something went wrong"}, status_code=500)
         
        return JSONResponse({"options": options, "challenge": challenge}, status_code=200)

    async def verify_authentication(self, body: VerifyAuthentication):
        logger.debug(f"Verifying authentication for email: {body['email']}")
        user = await self.am.signinResponse(body["challenge"], body["email"], body["auth_resp"])

        if not user:
            logger.warning("Authentication failed")
            return JSONResponse({"error": "Authentication failed."}, status_code=401)
         
        token = jwt.encode({
            'user_id': user,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')
        logger.debug(f"Token generated: {token}")

        return JSONResponse({"message": "Success", "token": token}, status_code=200)
    
    async def check_auth(self, request):
        auth_header = request.headers.get('Authorization')
        logger.debug(f"Authorization header: {auth_header}")
        if not auth_header:
            logger.warning("No token provided")
            return JSONResponse({"error": "No token provided"}, status_code=401)

        try:
            token = auth_header.split()[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            logger.debug(f"Token decoded successfully: {payload}")
            return JSONResponse({"message": "Authenticated", "user_id": user_id}, status_code=200)
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return JSONResponse({"error": "Token has expired"}, status_code=401)
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return JSONResponse({"error": "Invalid token"}, status_code=401)

    async def logout(self):
        # With token-based auth, logout is handled client-side
        return JSONResponse({"message": "Logged out successfully"}, status_code=200)