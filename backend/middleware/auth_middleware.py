import jwt
from starlette.responses import JSONResponse
from common.config import SECRET_KEY
from starlette.types import ASGIApp, Receive, Scope, Send
import logging

logger = logging.getLogger(__name__)

class VerifyTokenMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        path = scope["path"]
        logger.debug(f"Request path: {path}")
        
        # Allow access to static assets, manifest, authentication endpoints, and WebAuthn endpoints without a token
        if (path == "/" or 
            path.startswith('/api/v1/auth') or 
            path.startswith('/#/login') or 
            path.startswith('/assets/') or 
            path == '/manifest.json' or 
            path == '/favicon.png' or
            path == '/favicon.ico' or
            path.startswith('/api/v1/webauthn/')):
            logger.debug("Path exempted from authentication")
            return await self.app(scope, receive, send)

        headers = dict(scope["headers"])
        auth_header = headers.get(b"authorization", b"").decode()
        logger.debug(f"Authorization header: {auth_header}")

        if not auth_header:
            logger.warning("No token provided")
            response = JSONResponse({"error": "No token provided"}, status_code=401)
            await response(scope, receive, send)
            return

        try:
            token = auth_header.split()[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            scope["user_id"] = payload['user_id']
            logger.debug(f"Token decoded successfully: {payload}")
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            response = JSONResponse({"error": "Token has expired"}, status_code=401)
            await response(scope, receive, send)
            return
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            response = JSONResponse({"error": "Invalid token"}, status_code=401)
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)

verify_token = VerifyTokenMiddleware