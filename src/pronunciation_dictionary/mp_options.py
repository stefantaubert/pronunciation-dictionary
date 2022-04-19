from dataclasses import dataclass
from typing import Optional


@dataclass()
class MultiprocessingOptions():
  n_jobs: int
  maxtasksperchild: Optional[int]
  chunksize: int
