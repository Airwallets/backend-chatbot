# Schema for api endpoints response (or anything api specific, and not db).
# Avoid using the same schema as the db to avoid leaking secrets (eg: password).

from pydantic import BaseModel
from typing import Optional

class UserResponse(BaseModel):
    """
    Used in replacement of User db schema when return via api.
    To avoid leaking sensitive info (eg: salt password).
    """

    email: str
    name: Optional[str]

