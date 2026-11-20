class AppError(Exception):
    """Base class for domain errors raised by the service layer.

    Routers translate these into HTTP responses. Keeping them framework
    agnostic lets the service/repository layers be unit tested without
    FastAPI or HTTP in the loop at all.
    """


class NotFoundError(AppError):
    pass


class ConflictError(AppError):
    pass


class PermissionDeniedError(AppError):
    pass


class InvalidCredentialsError(AppError):
    pass


class InvalidTokenError(AppError):
    pass
