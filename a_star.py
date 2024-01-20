import heapq

def manhattan_distance(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])


def astar_search(grid, start, goal):
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Possible movement directions: right, left, down, up

    def is_valid_move(x, y):
        return 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] == 0

    def reconstruct_path(came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.insert(0, current)
        return path

    open_set = []  # Priority queue to store nodes to be explored
    heapq.heappush(open_set, (0, start))  # Initial node with priority 0
    came_from = {}  # Dictionary to store the parent node for each node
    g_score = {start: 0}  # Dictionary to store the cost from start to each node

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return reconstruct_path(came_from, current)

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)

            if is_valid_move(neighbor[0], neighbor[1]):
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    priority = tentative_g_score + manhattan_distance(neighbor, goal)
                    heapq.heappush(open_set, (priority, neighbor))
                    came_from[neighbor] = current

    return None  # No path found