from datetime import timedelta

from utils import time_now


MAX_CHUNK_SIZE = 35
SPAWN_RANGE = 2  # Initial range for spawning (got bigger automatically if needed)

INITIAL_POWER = 50
TOKEN_GENERATION_RETRY = 2

PERLIN_NOISE_OCTAVES = 50
RANDOMIZE_SEED = 1

NEW_POWER_RATE = timedelta(minutes=1)  # Add 1 power unit per <NEW_POWER_RATE> time
GAME_START_TIME = time_now() + timedelta(seconds=5)
TIME_PER_MOVE = timedelta(seconds=1)
MOVES_PER_TURN = 5

CACHE_SIZE = 1000000  # ITEMS (OBJECTS)
CACHE_TIME = 600 * 5  # SAVE ITEM FOR 5 MINUTES (TIME-TO-LIVE, TTL)
