"""Pydantic data models for GEO Crystal."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, HttpUrl


class GEOScore(BaseModel):
    """Model representing a GEO score with breakdown."""

    total_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Total GEO score out of 100",
    )
    breakdown: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed breakdown of score components",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "total_score": 75.5,
                "breakdown": {
                    "content_quality": 80.0,
                    "structure": 70.0,
                    "metadata": 75.0,
                },
            },
        }


class PageContent(BaseModel):
    """Model representing page content."""

    url: HttpUrl = Field(description="URL of the page")
    content: str = Field(description="Extracted content from the page")
    content_type: str = Field(
        default="text/html",
        description="MIME type of the content",
    )
    word_count: int = Field(
        default=0,
        ge=0,
        description="Word count of the content",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "url": "https://example.com/page",
                "content": "<html>...</html>",
                "content_type": "text/html",
                "word_count": 500,
            },
        }


class WebsiteAudit(BaseModel):
    """Model representing a website audit."""

    url: HttpUrl = Field(description="URL of the website/page audited")
    audit_date: datetime = Field(
        default_factory=datetime.now,
        description="Date and time of the audit",
    )
    geo_score: GEOScore = Field(description="GEO score for the website/page")
    findings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed findings from the audit",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "audit_date": "2024-01-01T00:00:00",
                "geo_score": {
                    "total_score": 75.5,
                    "breakdown": {},
                },
                "findings": {
                    "issues": [],
                    "recommendations": [],
                },
            },
        }


class TransformationResult(BaseModel):
    """Model representing a content transformation result."""

    original: str = Field(description="Original content")
    transformed: str = Field(description="Transformed content")
    score_before: float = Field(
        ge=0.0,
        le=100.0,
        description="GEO score before transformation",
    )
    score_after: float = Field(
        ge=0.0,
        le=100.0,
        description="GEO score after transformation",
    )
    transformation_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the transformation",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "original": "Original content text",
                "transformed": "Optimized content text",
                "score_before": 60.0,
                "score_after": 85.0,
                "transformation_metadata": {
                    "changes_made": ["added_keywords", "improved_structure"],
                },
            },
        }

