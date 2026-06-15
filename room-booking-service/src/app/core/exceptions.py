from fastapi import HTTPException, status

class NotFound(HTTPException):
    def __init__(self, detail: str = "Not Found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class Forbidden(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class Conflict(HTTPException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class Unauthorized(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
        