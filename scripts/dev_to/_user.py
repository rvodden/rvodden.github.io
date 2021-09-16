from pydantic import AnyUrl, BaseModel


class User(BaseModel):
    type_of: str
    id: int
    username: str
    name: str
    summary: str = None
    twitter_username: str = None
    github_username: str = None
    website_url: AnyUrl = None
    location: str = None
    joined_at: str
    profile_image: str