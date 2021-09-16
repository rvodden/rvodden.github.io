from pydantic import BaseModel
from pydantic.color import Color


class FlareTag(BaseModel):
    bg_color_hex: Color
    text_color_hex: Color
