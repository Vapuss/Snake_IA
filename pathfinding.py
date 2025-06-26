import heapq
from config import BLOCK_SIZE, SW, SH

DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

REVERSE_DIRECTIONS = {v: k for k, v in DIRECTIONS.items()}

def a_star(start, goal, obstacles, grid_width=None, grid_height=None):
    """
    start, goal: (x, y) tuples in grid coordinates
    obstacles: set of (x, y) positions that are blocked
    grid_width, grid_height: optional grid dimensions, inferred from config if None
    """
    grid_width = grid_width or (SW // BLOCK_SIZE)
    grid_height = grid_height or (SH // BLOCK_SIZE)

    def in_bounds(pos):
        x, y = pos
        return 0 <= x < grid_width and 0 <= y < grid_height

    def neighbors(pos):
        result = []
        for dx, dy in DIRECTIONS.values():
            nxt = (pos[0] + dx, pos[1] + dy)
            if in_bounds(nxt) and nxt not in obstacles:
                result.append(nxt)
        return result

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for nxt in neighbors(current):
            new_cost = cost_so_far[current] + 1
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                priority = new_cost + heuristic(goal, nxt)
                heapq.heappush(frontier, (priority, nxt))
                came_from[nxt] = current

    # reconstrucție drum
    if goal not in came_from:
        return None  # nu există cale

    path = []
    node = goal
    while node != start:
        path.append(node)
        node = came_from[node]
    path.reverse()

    if not path:
        return None

    dx = path[0][0] - start[0]
    dy = path[0][1] - start[1]
    return REVERSE_DIRECTIONS.get((dx, dy))
