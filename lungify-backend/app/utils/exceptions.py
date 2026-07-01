from __future__ import annotations


class LungifyError(Exception):
    status_code = 400
    code = "lungify_error"

    def __init__(self, message: str, *, status_code: int | None = None, code: str | None = None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code
        self.message = message


class ValidationError(LungifyError):
    code = "validation_error"


class ModelUnavailableError(LungifyError):
    status_code = 503
    code = "model_unavailable"

