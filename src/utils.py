from datetime import datetime
from perlin_noise import PerlinNoise
from cachetools import cached, TTLCache


from config import PERLIN_NOISE_OCTAVES, RANDOMIZE_SEED, CACHE_SIZE, CACHE_TIME

noise = PerlinNoise(octaves=PERLIN_NOISE_OCTAVES, seed=RANDOMIZE_SEED)


@cached(cache=TTLCache(maxsize=CACHE_SIZE, ttl=CACHE_TIME))
def random_tile(x, y):
    # return (abs(x*y+x+y+round(sin(x+y)*10)) % 9) + 1
    distance_from_center = (x**2 + y**2)**0.5
    return abs(round(noise([x/1000, y/1000])*50 + distance_from_center // 10))


def updated_tile_power(tile, new_power_rate):
    if tile.get("owner", None):
        last_power_calculated = tile.get("updated_at", None)
        return tile["power"] + (datetime.now() - last_power_calculated) // new_power_rate
    return tile["power"]


def coordinates_to_chunk(x, y, chunk_size):
    normal_x = x // chunk_size
    normal_y = y // chunk_size
    middle_x = normal_x*chunk_size+(chunk_size//2)
    middle_y = normal_y*chunk_size+(chunk_size//2)
    return middle_x, middle_y
