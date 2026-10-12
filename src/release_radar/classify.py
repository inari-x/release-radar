from typing import Literal

from pydantic import BaseModel

Category = Literal["breaking", "deprecation", "feature", "fix", "other"]


class ClassifiedChange(BaseModel):
    summary: str
    category: Category
    reason: str


class ReleaseClassification(BaseModel):
    changes: list[ClassifiedChange]
    