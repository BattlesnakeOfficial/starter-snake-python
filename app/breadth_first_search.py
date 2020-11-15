import Classes
import localizer


def bfs_safe_move(start, graph):
    weight_list = []
    possible_moves = graph.neighbors(start)
    for possible_move in possible_moves:
        weight_list.append(
            (bfs_get_weight(graph, possible_move), possible_move))
    move = min(weight_list, key=lambda x: x[0])
    return move[1]


def bfs_get_weight(graph, start):
    instance = 0
    total_weight = 0
    q = Classes.Queue()
    q.put(start)
    visited = set([start])
    while not q.empty() and instance < localizer.MAX_INSTANCE:
        cell = q.get()
        instance += 1
        total_weight += graph.weights.get(cell, 0)
        for neighbor in graph.neighbors(cell):
            if neighbor not in visited:
                q.put(neighbor)
                visited.add(neighbor)
    return total_weight
