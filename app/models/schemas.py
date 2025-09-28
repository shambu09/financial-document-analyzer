from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum


# Enums
class ReportStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=1, max_length=72, description="Password (max 72 characters due to bcrypt limitation)")
    
    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password cannot be longer than 72 bytes. Please use a shorter password.')
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=1, max_length=72, description="Password (max 72 characters due to bcrypt limitation)")
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    
    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v):
        if v is not None and len(v.encode('utf-8')) > 72:
            raise ValueError('Password cannot be longer than 72 bytes. Please use a shorter password.')
        return v


class UserResponse(UserBase):
    id: str  # String ID for all databases
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Authentication Schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=1, max_length=72, description="New password (max 72 characters due to bcrypt limitation)")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password_length(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('New password cannot be longer than 72 bytes. Please use a shorter password.')
        return v


# Session Schemas
class SessionResponse(BaseModel):
    id: str  # String ID for all databases
    user_id: str
    session_token: str
    refresh_token: str
    expires_at: datetime
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Document Schemas
class DocumentBase(BaseModel):
    original_name: str
    size_bytes: int


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: str  # String ID for all databases
    user_id: str
    stored_name: str
    path: str
    checksum: Optional[str]
    created_at: datetime
    updated_at: datetime
    download_url: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DocumentSearchParams(BaseModel):
    search_query: Optional[str] = None
    page: int = 1
    page_size: int = 20


# Analysis Report Schemas
class AnalysisReportBase(BaseModel):
    analysis_type: str
    query: str
    file_name: str
    summary: Optional[str] = None


class AnalysisReportCreate(AnalysisReportBase):
    document_id: Optional[Union[int, str]] = None  # Support both SQLite (int) and MongoDB (str) IDs
    report_path: str
    status: ReportStatus = ReportStatus.PENDING


class AnalysisReportResponse(AnalysisReportBase):
    id: str  # String ID for all databases
    user_id: str
    document_id: Optional[str]  # String ID for all databases
    report_path: str
    status: ReportStatus
    created_at: datetime
    updated_at: datetime
    download_url: Optional[str] = None

    class Config:
        from_attributes = True


class AnalysisReportListResponse(BaseModel):
    reports: List[AnalysisReportResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AnalysisReportSearchParams(BaseModel):
    analysis_type: Optional[str] = None
    search_query: Optional[str] = None
    page: int = 1
    page_size: int = 20


class AnalysisReportUpdate(BaseModel):
    summary: Optional[str] = None


# Analysis Request Schemas
class AnalysisRequest(BaseModel):
    query: str = "Analyze this financial document"


class AnalysisResponse(BaseModel):
    status: str
    analysis_type: str
    query: str
    analysis: str
    file_processed: str
    user_id: str
    report_id: Union[int, str]
    report_download_url: str


# Statistics Schemas
class UserStatsResponse(BaseModel):
    total_documents: int
    total_reports: int
    reports_by_type: dict


class ReportStatsResponse(BaseModel):
    total_reports: int
    by_analysis_type: dict


# Error Schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    detail: List[dict]
    error_code: str = "validation_error"


# Health Check Schemas
class HealthResponse(BaseModel):
    status: str
    version: str
    available_analysis_types: List[str]


class RootResponse(BaseModel):
    message: str
    version: str
