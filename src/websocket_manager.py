

__all__ = ["WSManager", "get_manager"]


class WSManager:
    def __init__(self):
        self.connections = {}
        self.not_connected_clients = {}

    def new(self, token, ws):
        self.connections[token] = {"ws": ws, "map_load_squares": []}
        if token in self.not_connected_clients:
            self.connections[token]["map_load_squares"] = self.not_connected_clients[token]["map_load_squares"]
            self.not_connected_clients.pop(token)

    def remove(self, token):
        self.connections.pop(token, None)
        self.not_connected_clients.pop(token, None)

    def add_load_range(self, token, load_range):
        # TODO: optimize by saveing by range and not by token
        if token not in self.connections:
            if token not in self.not_connected_clients:
                self.not_connected_clients[token] = {"map_load_squares": []}
            if load_range not in self.not_connected_clients[token]["map_load_squares"]:
                self.not_connected_clients[token]["map_load_squares"].append(load_range)
        elif load_range not in self.connections[token]["map_load_squares"]:
            self.connections[token]["map_load_squares"].append(load_range)

    async def push_update(self, x, y, new_tile):
        for connection in self.connections.values():
            for square in connection["map_load_squares"]:
                max_x = int(square["x"] + square["chunk_size"] // 2)
                min_x = int(square["x"] - square["chunk_size"] // 2)
                max_y = int(square["y"] + square["chunk_size"] // 2)
                min_y = int(square["y"] - square["chunk_size"] // 2)
                if min_x <= x <= max_x and min_y <= y <= max_y:
                    await connection["ws"].send_json(new_tile)
                    break

manager = WSManager()


def get_manager() -> WSManager:
    return manager
