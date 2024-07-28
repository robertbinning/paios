from pathlib import Path
from connexion import AsyncApp
from connexion.resolver import MethodResolver
from connexion.middleware import MiddlewarePosition
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from backend.hooks.webauthn import router

def create_backend_app():
    apis_dir = Path(__file__).parent.parent / 'apis' / 'paios'

    allow_origins = [
        'https://localhost',
        'https://localhost:3080',
        'https://localhost:5173'
    ]

    fastapi_app = FastAPI()

    fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    fastapi_app.include_router(router)

    connexion_app = AsyncApp(__name__, specification_dir=apis_dir)

    connexion_app.app = fastapi_app

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

    # Add API with validation
    connexion_app.add_api(
        'openapi.yaml',
        resolver=MethodResolver('backend.api'),
        resolver_error=501,
        # TODO: Validation has a performance impact and may want to be disabled in production
        validate_responses=True,  # Validate responses against the OpenAPI spec
        strict_validation=True    # Validate requests strictly against the OpenAPI spec
    )
    return connexion_app, fastapi_app
