from typing import Optional
from pydantic import AnyUrl, BaseModel


class SharedUser(BaseModel):
    name: str
    username: str
    twitter_username: Optional[str]
    github_username: Optional[str]
    website_url: Optional[AnyUrl]
    profile_image: Optional[AnyUrl]
    profile_image_90: Optional[AnyUrl]