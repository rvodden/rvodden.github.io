from typing import Optional
from pydantic import AnyUrl, BaseModel


class Organization(BaseModel):
    type_of: str
    username: str
    name: str
    summary: Optional[str]
    twitter_username: Optional[str]
    github_username: Optional[str]
    url: Optional[AnyUrl]
    location: Optional[str]
    tech_stack: Optional[str]
    tag_line: Optional[str]
    story: Optional[str]
    joined_at: Optional[str]	
    profile_image: Optional[AnyUrl]