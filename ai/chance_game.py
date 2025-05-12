game_tree = {
    "M1": {"type": "max", "children": ["C1", "C2", "C3", "C4"]},
    "C1": {"type": "chance", "children": [{"node": "N1", "probability": 0.2}, {"node": "N2", "probability": 0.8}]},
    "C2": {"type": "chance", "children": [{"node": "N3", "probability": 0.6}, {"node": "N4", "probability": 0.4}]},
    "C3": {"type": "chance", "children": [{"node": "N5", "probability": 0.3}, {"node": "N6", "probability": 0.7}]},
    "C4": {"type": "chance", "children": [{"node": "N7", "probability": 0.9}, {"node": "N8", "probability": 0.1}]},
    "N1": {"type": "min", "children": ["C5", "C6"]},
    "N2": {"type": "min", "children": ["C7"]},
    "N3": {"type": "min", "children": ["C8"]},
    "N4": {"type": "min", "children": ["C9"]},
    "N5": {"type": "min", "children": ["C10"]},
    "N6": {"type": "min", "children": ["C11"]},
    "N7": {"type": "min", "children": ["C12"]},
    "N8": {"type": "min", "children": ["C13"]},
    "C5": {"type": "chance", "children": [{"node": "2", "probability": 0.9}, {"node": "-22", "probability": 0.1}]},
    "C6": {"type": "chance", "children": [{"node": "M9", "probability": 0.3}, {"node": "M10", "probability": 0.7}]},
    "C7": {"type": "chance", "children": [{"node": "15", "probability": 0.4}, {"node": "9", "probability": 0.6}]},
    "C8": {"type": "chance", "children": [{"node": "1", "probability": 0.3}, {"node": "M11", "probability": 0.7}]},
    "C9": {"type": "chance", "children": [{"node": "-12", "probability": 0.9}, {"node": "3", "probability": 0.1}]},
    "C10": {"type": "chance", "children": [{"node": "5", "probability": 0.4}, {"node": "M12", "probability": 0.6}]},
    "C11": {"type": "chance", "children": [{"node": "-5", "probability": 0.6}, {"node": "11", "probability": 0.4}]},
    "C12": {"type": "chance", "children": [{"node": "-22", "probability": 0.3}, {"node": "M13", "probability": 0.7}]},
    "C13": {"type": "chance", "children": [{"node": "2", "probability": 0.2}, {"node": "4", "probability": 0.8}]},
    "M9": {"type": "max", "children": ["C14"]},
    "M10": {"type": "max", "children": ["C15"]},
    "M11": {"type": "max", "children": ["C16", "C17"]},
    "M12": {"type": "max", "children": ["C18"]},
    "M13": {"type": "max", "children": ["C19", "C20"]},
    "C14": {"type": "chance", "children": [{"node": "11", "probability": 0.7}, {"node": "-5", "probability": 0.3}]},
    "C15": {"type": "chance", "children": [{"node": "0", "probability": 0.8}, {"node": "10", "probability": 0.2}]},
    "C16": {"type": "chance", "children": [{"node": "-9", "probability": 0.5}, {"node": "9", "probability": 0.5}]},
    "C17": {"type": "chance", "children": [{"node": "13", "probability": 0.6}, {"node": "-2", "probability": 0.4}]},
    "C18": {"type": "chance", "children": [{"node": "-13", "probability": 0.1}, {"node": "15", "probability": 0.9}]},
    "C19": {"type": "chance", "children": [{"node": "7", "probability": 0.1}, {"node": "9", "probability": 0.9}]},
    "C20": {"type": "chance", "children": [{"node": "10", "probability": 0.6}, {"node": "0", "probability": 0.4}]},
    "2": {"utility": 2},
    "-22": {"utility": -22},
    "15": {"utility": 15},
    "9": {"utility": 9},
    "1": {"utility": 1},
    "-12": {"utility": -12},
    "3": {"utility": 3},
    "5": {"utility": 5},
    "-5": {"utility": -5},
    "11": {"utility": 11},
    "4": {"utility": 4},
    "0": {"utility": 0},
    "-9": {"utility": -9},
    "13": {"utility": 13},
    "-2": {"utility": -2},
    "-13": {"utility": -13},
    "7": {"utility": 7},
    "15": {"utility": 15},
    "10": {"utility": 10}
}

def expectimax(node_name):
    node = game_tree[node_name]

    # Base Case: Terminal node with a static evaluation
    if "utility" in node:
        #print(f"Terminal node {node_name} with utility {node['utility']}")
        return node["utility"]

    node_type = node["type"]

    # max node: choose the highest value among children
    if node_type == "max":
        #print(f"\nEvaluating MAX node {node_name} with children {node['children']}")
        child_values = []
        for child in node["children"]:
            val = expectimax(child)
            child_values.append(val)
        best_value = max(child_values)
        #print(f"MAX node {node_name} child utilities: {child_values} --> selected {best_value}")
        return best_value

    # min node: choose the lowest value among children
    elif node_type == "min":
        #print(f"\nEvaluating MIN node {node_name} with children {node['children']}")
        child_values = []
        for child in node["children"]:
            val = expectimax(child)
            child_values.append(val)
        best_value = min(child_values)
        #print(f"MIN node {node_name} child utilities: {child_values} --> selected {best_value}")
        return best_value

    # chance node: compute the weighted average of children
    elif node_type == "chance":
        #print(f"\nEvaluating CHANCE node {node_name} with outcomes:")
        expected_value = 0
        for outcome in node["children"]:
            child_node = outcome["node"]
            probability = outcome["probability"]
            child_val = expectimax(child_node)
            weighted_val = probability * child_val
            #print(f"  Outcome node {child_node} with probability {probability} yields {child_val} (weighted: {weighted_val})")
            expected_value += weighted_val
        #print(f"CHANCE node {node_name} expected value: {expected_value}")
        return expected_value

    else:
        raise ValueError(f"Unknown node type: {node_type}")

# Example: Compute the expected utility from the root node "A1"
result = expectimax("M10")
print("\nOptimal expected utility from M10:", result)
result = expectimax("M9")
print("\nOptimal expected utility from M9:", result)
result = expectimax("N5")
print("\nOptimal expected utility from N5:", result)
result = expectimax("M1")
print("\nOptimal expected utility from M1:", result)