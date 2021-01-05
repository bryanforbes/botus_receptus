from __future__ import annotations

import sys

if sys.version_info >= (3, 8):
    from typing import Final as Final
    from typing import Literal as Literal
    from typing import Protocol as Protocol
    from typing import TypedDict as TypedDict
else:
    from typing_extensions import Final as Final  # noqa: F401
    from typing_extensions import Literal as Literal  # noqa: F401
    from typing_extensions import Protocol as Protocol  # noqa: F401
    from typing_extensions import TypedDict as TypedDict  # noqa: F401
