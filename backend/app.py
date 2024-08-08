from pathlib import Path
from connexion import AsyncApp
from connexion.resolver import MethodResolver
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from backend.middleware.auth_middleware import verify_token

def create_backend_app():
    apis_dir = Path(__file__).parent.parent / 'apis' / 'paios'
    connexion_app = AsyncApp(__name__, specification_dir=apis_dir)

    allow_origins = [
        'http://localhost',
        'http://localhost:3080',
        'http://localhost:5173'
    ]

    # Add CORS middleware
    connexion_app.add_middleware(
        CORSMiddleware,
        position=MiddlewarePosition.BEFORE_EXCEPTION,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Range", "X-Total-Count"],
    )

    # Add authentication middleware
    connexion_app.add_middleware(verify_token)

    # Add API with validation
    connexion_app.add_api(
        'openapi.yaml',
        resolver=MethodResolver('backend.api'),
        resolver_error=501,
        validate_responses=True,
        strict_validation=True
    )
    return connexion_app