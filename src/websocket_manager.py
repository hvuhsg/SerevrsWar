

__all__ = ["WSManager", "get_manager"]


class LoadRange:
    def __init__(self, x, y, chunk_size):
        self.x = x
        self.y = y
        self.chunk_size = chunk_size

    def __getitem__(self, item):
        return getattr(self, item)

    def __hash__(self):
        return hash((self.x, self.y, self.chunk_size))

    @classmethod
    def from_dict(cls, dict_object):
        return cls(**dict_object)


class WSManager:
    def __init__(self):
        self.connections = {}
        self.not_connected_clients = {}
        self.ranges = {}

    def new(self, token, ws):
        """
        New websocket connection
        """
        self.connections[token] = {"ws": ws}

    def remove(self, token):
        """
        Websocket disconnected
        """
        self.connections.pop(token, None)

    def add_load_range(self, token, load_range):
        load_range = LoadRange.from_dict(load_range)
        if load_range not in self.ranges:
            self.ranges[load_range] = {"loaders": []}
        self.ranges[load_range]["loaders"].append(token)

    async def push_update(self, x, y, new_tile):
        for load_range in self.ranges.keys():
            max_x = int(load_range["x"] + load_range["chunk_size"] // 2)
            min_x = int(load_range["x"] - load_range["chunk_size"] // 2)
            max_y = int(load_range["y"] + load_range["chunk_size"] // 2)
            min_y = int(load_range["y"] - load_range["chunk_size"] // 2)
            if min_x <= x <= max_x and min_y <= y <= max_y:
                for token in self.ranges[load_range]["loaders"]:
                    try:  # Do not stop if exception raises
                        connection = self.connections.get(token, None)
                        if connection is not None:
                            ws = connection["ws"]
                            await ws.send_json(new_tile)
                    except Exception as EX:
                        print("Error:", EX)

manager = WSManager()


def get_manager() -> WSManager:
    return manager
