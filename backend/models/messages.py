from pydantic import BaseModel
from typing import Optional, List


class AgentMessage(BaseModel):
    # ✅ Core fields
    file_id: Optional[str] = None
    file_name: str
    source: str = "drive"

    # ✅ Content from Extractor
    content: Optional[bytes] = None

    # ✅ Classification
    category: Optional[str] = None
    tags: List[str] = []

    # ✅ Deduplication
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    file_hash: Optional[str] = None

    # ✅ Archiving
    should_archive: bool = False
    action_reason: Optional[str] = None