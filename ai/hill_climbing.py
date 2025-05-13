graph = {
    "N1": {"N3": 8, "N5": 7, "N7": 6, "N8": 4},
    "N2": {"N4": 9, "N6": 4, "N7": 5, "N9": 6, "N11": 7},
    "N3": {"N1": 8, "N4": 9, "N9": 7, "N10": 6, "N12": 6},
    "N4": {"N2": 9, "N3": 9, "N10": 3},
    "N5": {"N1": 7, "N6": 6, "N11": 10},
    "N6": {"N2": 4, "N5": 6, "N8": 9, "N12": 5},
    "N7": {"N1": 6, "N2": 5},
    "N8": {"N1": 4, "N6": 9, "N12": 6},
    "N9": {"N2": 6, "N3": 7},
    "N10": {"N3": 6, "N4": 3},
    "N11": {"N2": 7, "N5": 10},
    "N12": {"N3": 6, "N6": 5, "N8": 6}
}

def objective_function(cost):
    return 20 - cost

def hill_climbing(start_node, steps):
    current_node = start_node
    visited = set()
    path = []
    
    for step in range(steps):
        path.append((current_node, objective_function(0 if step == 0 else graph[path[-1][0]][current_node])))
        visited.add(current_node)
        
        neighbors = {node: cost for node, cost in graph[current_node].items() if node not in visited}
        
        if not neighbors:
            break
        
        best_next_node = min(neighbors, key=lambda node: (-objective_function(neighbors[node]), node))
        current_node = best_next_node
    
    return path

# Running the hill-climbing search from N5 for 4 steps
path = hill_climbing("N5", 5)

# Printing results
for step, (node, obj_value) in enumerate(path, start=1):
    print(f"Step {step}: {node}, {obj_value}")
