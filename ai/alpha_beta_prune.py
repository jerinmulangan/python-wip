import math

game_tree = {
    "N1": {"player": "Max", "children": ["N5", "N4", "N3", "N2"]},
    "N5": {"player": "Min", "children": ["N9", "v1"]},
    "N4": {"player": "Min", "children": ["v2", "N8"]},
    "N3": {"player": "Min", "children": ["v3", "N7"]},
    "N2": {"player": "Min", "children": ["N6", "v4"]},
    "N9": {"player": "Max", "children": ["v5", "v6"]},
    "N8": {"player": "Max", "children": ["v7"]},
    "N7": {"player": "Max", "children": ["v8", "N10", "v9"]},
    "N6": {"player": "Max", "children": ["v10", "v11"]},
    "N10": {"player": "Min", "children": ["v12"]}
    
    
    
}

game_tree.update({
    "v1": {"utility": 22}, "v2": {"utility": 4}, "v3": {"utility": 7},
    "v4": {"utility": 4}, "v5": {"utility": 12}, "v6": {"utility": 6},
    "v7": {"utility": 9}, "v8": {"utility": 3}, "v9": {"utility": 8},
    "v10": {"utility": 12}, "v11": {"utility": 5}, "v12": {"utility": 5}
})

def alpha_beta(node, alpha, beta, depth=0):
    """ Alpha-Beta Pruning Algorithm with Correct Traversal and Debugging """
    indent = "  " * depth  
    if "utility" in game_tree[node]:  
        print(f"{indent}{node}: α={alpha}, β={beta}, value={game_tree[node]['utility']}, PRUNE=NONE")
        return game_tree[node]["utility"]

    is_max = game_tree[node]["player"] == "Max"
    value = -math.inf if is_max else math.inf
    pruned_nodes = []

    print(f"{indent}{node} (START): α={alpha}, β={beta}, value={value}")

    for child in game_tree[node]["children"]:
        child_value = alpha_beta(child, alpha, beta, depth + 1)


        if is_max:
            value = max(value, child_value)
            alpha = max(alpha, value)
        else:
            value = min(value, child_value)
            beta = min(beta, value)

        print(f"{indent}{node} (UPDATED): α={alpha}, β={beta}, value={value} after visiting {child}")


        if beta <= alpha:
            prune_type = "BETA" if is_max else "ALPHA"
            pruned_nodes = game_tree[node]["children"][game_tree[node]["children"].index(child) + 1:]
            print(f"{indent}{node} PRUNED {pruned_nodes} ({prune_type} PRUNE)")
            break 

    return value

def print_trace():

    alpha, beta = -math.inf, math.inf
    alpha_beta("N1", alpha, beta)

print_trace()
