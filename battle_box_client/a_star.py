from queue import PriorityQueue

def manhattan_distance(loc1, loc2):
    [x1, y1] = loc1
    [x2, y2] = loc2
    a_squared = (x2 - x1) ** 2
    b_squared = (y2 - y1) ** 2
    return (a_squared + b_squared) ** 0.5


def a_star(start, end, neighbors, heuristic=manhattan_distance):
    print("Starting A*")
    neighbors = neighbors or adjacent_locations

    cost_from_start_to_postition = {start: 0}
    estimated_cost_to_end = {start: heuristic(start, end)}

    open_vertices = set([start])
    closed_vertices = set()
    came_from = {}

    current = None

    while len(open_vertices) > 0:
        print("IN WHILE LOOP")
        print("OPEN VERTICIES", open_vertices)
        for pos in open_vertices:
            if not current or estimated_cost_to_end[pos] < estimated_cost_to_end[pos]:
                current = pos

        print("CURRENT", current)
        if current == end:
            path = [current]
            while current in came_from:
                    current = came_from[current]
                    path.append(current)
            path.reverse()
            return path, estimated_cost_to_end[end]

        open_vertices.discard(current)
        closed_vertices.add(current)
        print(closed_vertices, "CLOSED VERTS")

        for neighbor in neighbors(current):
            if neighbor in closed_vertices:
                continue

            candidate_cost = cost_from_start_to_postition[current] + 1

            if neighbor not in open_vertices:
                open_vertices.add(neighbor)
            elif candidate_cost >= cost_from_start_to_postition[neighbor]:
                continue

            came_from[neighbor] = current
            cost_from_start_to_postition[neighbor] = candidate_cost
            estimated_cost_to_end[neighbor] = cost_from_start_to_postition[neighbor] + heuristic(neighbor, end)

