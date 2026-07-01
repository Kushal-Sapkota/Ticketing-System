from pydantic import BaseModel, EmailStr, Field

from app.models.enums import AgentRole, AvailabilityStatus


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AgentPublic(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: AgentRole
    availability: AvailabilityStatus
    is_active: bool

    model_config = {"from_attributes": True}


class MeResponse(AgentPublic):
    pass
