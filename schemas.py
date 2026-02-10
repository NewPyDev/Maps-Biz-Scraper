"""Pydantic schemas for API validation"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ScrapeRequest(BaseModel):
    """Schema for scrape request validation"""

    category: str = Field(..., min_length=1, max_length=100, description="Business category")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    country: str = Field(default="", max_length=100, description="Country name (optional)")
    max_results: Optional[int] = Field(
        default=None, ge=1, le=1000, description="Maximum results to scrape"
    )

    @field_validator("category", "city")
    @classmethod
    def validate_no_special_chars(cls, v: str) -> str:
        """Ensure no dangerous characters that could cause XSS or injection attacks"""
        dangerous_chars = ["<", ">", "&", '"', "'", ";", "(", ")", "{", "}", "[", "]"]
        if any(char in v for char in dangerous_chars):
            raise ValueError(f"Special characters not allowed: {', '.join(dangerous_chars)}")
        return v.strip()

    @field_validator("max_results")
    @classmethod
    def validate_max_results(cls, v: Optional[int]) -> Optional[int]:
        """Validate max results is reasonable"""
        if v and v > 1000:
            raise ValueError("Max results cannot exceed 1000")
        return v


class ExportRequest(BaseModel):
    """Schema for export request validation"""

    format: str = Field(default="csv", pattern="^(csv|json|pdf)$", description="Export format")
    city: Optional[str] = Field(default=None, max_length=100)
    category: Optional[str] = Field(default=None, max_length=100)
    has_website: Optional[bool] = Field(default=None)

    @field_validator("city", "category")
    @classmethod
    def validate_filter_fields(cls, v: Optional[str]) -> Optional[str]:
        """Validate filter fields"""
        if v is None:
            return v
        dangerous_chars = ["<", ">", "&", '"', "'"]
        if any(char in v for char in dangerous_chars):
            raise ValueError("Special characters not allowed in filters")
        return v.strip()
