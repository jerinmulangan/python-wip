from collections import defaultdict

game_tree = {
    "A1": {"type": "max", "children": ["C1", "C2", "C3"]},
    "C1": {"type": "chance", "children": [{"node": "B1", "probability": 0.2}, {"node": "B2", "probability": 0.8}]},
    "C2": {"type": "chance", "children": [{"node": "B3", "probability": 0.6}, {"node": "B4", "probability": 0.4}]},
    "C3": {"type": "chance", "children": [{"node": "B5", "probability": 0.2},{"node": "B6", "probability": 0.8}]},
    "B1": {"type": "min", "children": ["C4", "C5"]},
    "B2": {"type": "min", "children": ["C6", "C7"]},
    "B3": {"type": "min", "children": ["C8", "C9"]},
    "B4": {"type": "min", "children": ["C10", "C11"]},
    "B5": {"type": "min", "children": ["C12", "C13"]},
    "B6": {"type": "min", "children": ["C14", "C15"]},
    "C4": {"type": "chance", "children": [{"node": "t1", "probability": 0.2}, {"node": "A2", "probability": 0.8}]},
    "C5": {"type": "chance", "children": [{"node": "A3", "probability": 0.8}, {"node": "t2", "probability": 0.2}]},
    "C6": {"type": "chance", "children": [{"node": "t3", "probability": 0.4}, {"node": "t4", "probability": 0.6}]},
    "C7": {"type": "chance", "children": [{"node": "t5", "probability": 0.8}, {"node": "t6", "probability": 0.2}]},
    "C8": {"type": "chance", "children": [{"node": "t7", "probability": 0.6}, {"node": "t8", "probability": 0.4}]},
    "C9": {"type": "chance", "children": [{"node": "t9", "probability": 0.4}, {"node": "t10", "probability": 0.6}]},
    "C10": {"type": "chance", "children": [{"node": "t11", "probability": 0.2}, {"node": "t12", "probability": 0.8}]},
    "C11": {"type": "chance", "children": [{"node": "t13", "probability": 0.2}, {"node": "t14", "probability": 0.8}]},
    "C12": {"type": "chance", "children": [{"node": "t15", "probability": 0.8}, {"node": "t16", "probability": 0.2}]},
    "C13": {"type": "chance", "children": [{"node": "t17", "probability": 0.4}, {"node": "t18", "probability": 0.6}]},
    "C14": {"type": "chance", "children": [{"node": "t19", "probability": 0.8}, {"node": "t20", "probability": 0.2}]},
    "C15": {"type": "chance", "children": [{"node": "t21", "probability": 0.2}, {"node": "t22", "probability": 0.8}]},
    "A2": {"type": "max", "children": ["t25", "t23"]},
    "A3": {"type": "max", "children": ["t24", "t26"]}
}

# Assign terminal node values
terminal_values = {
    "t1": 2, "t2": -1, "t3": 0, "t4": 3, "t5": 5, "t6": -1,
    "t7": 3, "t8": 8, "t9": -5, "t10": 4, "t11": -3, "t12": 6,
    "t13": 7, "t14": 10, "t15": 9, "t16": 13, "t17": 19, "t18": 20,
    "t19": 21, "t20": -4, "t21": -5, "t22": -10, "t23": 5, "t24": -6,
    "t25": 6, "t26": 3
}

def expectimax(node):
    if node in terminal_values:
        return terminal_values[node]
    
    node_info = game_tree.get(node)
    
    if node_info is None:
        raise ValueError(f"Node '{node}' not found in game tree!")

    if node_info["type"] == "max":
        return max(expectimax(child) for child in node_info["children"])
    
    elif node_info["type"] == "min":
        return min(expectimax(child) for child in node_info["children"])
    
    elif node_info["type"] == "chance":
        return sum(child["probability"] * expectimax(child["node"]) for child in node_info["children"])

try:
    result = expectimax("B1")
    print("Expected value at B1: ", result)
    result = expectimax("A1")
    print("Expected value at root (A1):", result)
except ValueError as e:
    print(e)




result = expectimax("B1")
print("Expected value at B1: ", result)
result = expectimax("A1")
print("Expected value at root (A1):", result)
