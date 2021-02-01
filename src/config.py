from datetime import timedelta, datetime


MAX_CHUNK_SIZE = 35
SPAWN_RANGE = 2

PERLIN_NOISE_OCTAVES = 50
RANDOMIZE_SEED = 1

NEW_POWER_RATE = timedelta(minutes=1)
START_MOVE_TIME = datetime.now() + timedelta(seconds=5)
TIME_PER_MOVE = timedelta(seconds=5)

CACHE_SIZE = 1000000  # ITEMS (OBJECTS)
CACHE_TIME = 600 * 5  # SAVE ITEM FOR 5 MINUTES
