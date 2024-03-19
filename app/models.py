from dataclasses import dataclass
from typing import List, Optional


@dataclass
class User():
    id: int
    firstname: str
    lastname: str
    email: str
    password: str
    rgpd_right: bool


@dataclass
class Image():
    image: bytes
    keypoint: List[float]
    label: str
    user_id: int
