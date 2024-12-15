import pandas as pd
from typing import Any, Protocol

class ConuntStrat(Protocol):
    def __call__(self, df: pd.DataFrame, **kwds: Any) -> pd.DataFrame:
        ...