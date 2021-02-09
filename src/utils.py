from typing import Tuple
from datetime import datetime, timezone


def coordinates_to_chunk(x: int, y: int, chunk_size: int) -> Tuple[int, int]:
    """
    Convert x, y coordinates to chunk coordinates
    """
    normal_x = x // chunk_size
    normal_y = y // chunk_size
    middle_x = normal_x*chunk_size+(chunk_size//2)
    middle_y = normal_y*chunk_size+(chunk_size//2)
    return middle_x, middle_y


def time_now():
    return datetime.now(tz=timezone.utc)
