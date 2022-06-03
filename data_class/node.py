from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Node:
    scope_no: int
    father: Optional['Node'] = None