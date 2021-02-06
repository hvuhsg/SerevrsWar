from datetime import timedelta, datetime


MAX_CHUNK_SIZE = 35
SPAWN_RANGE = 2  # Initial range for spawning (got bigger automatically if needed)

PERLIN_NOISE_OCTAVES = 50
RANDOMIZE_SEED = 1

NEW_POWER_RATE = timedelta(minutes=1)  # Add 1 power unit per <NEW_POWER_RATE> time
GAME_START_TIME = datetime.now() + timedelta(seconds=5)
TIME_PER_MOVE = timedelta(seconds=5)

CACHE_SIZE = 1000000  # ITEMS (OBJECTS)
CACHE_TIME = 600 * 5  # SAVE ITEM FOR 5 MINUTES (TIME-TO-LIVE, TTL)
