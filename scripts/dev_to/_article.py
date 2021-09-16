from pydantic import BaseModel
from typing import List, Optional

from ._flare_tag import FlareTag
from ._organization import Organization
from ._shared_user import SharedUser

class Article(BaseModel):
    type_of: str
    id: int
    title: str
    description: str
    cover_image: Optional[str]
    readable_publish_date: Optional[str]
    social_image: Optional[str]
    tag_list: List[str]
    tags: Optional[str]
    slug: str
    path: str
    url: str
    canonical_url: str
    comments_count: int
    positive_reactions_count: int
    public_reactions_count: int
    created_at: Optional[str]
    edited_at: Optional[str]
    crossposted_at: Optional[str]
    published_at: Optional[str]
    last_comment_at: Optional[str]
    body_markdown: Optional[str]
    published_timestamp: str # Crossposting or published date time
    user: SharedUser
    reading_time_minutes: int
    organization: Optional[Organization]
    flare_tag: Optional[FlareTag]