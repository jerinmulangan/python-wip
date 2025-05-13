# Define the game tree as given
game_tree = {
    "A1": ["E1", "E2", "E3", "E4"],
    
    "E1": ["M1", "M2"],
    "E2": ["M3", "M4"],
    "E3": ["M5", "M6"],
    "E4": ["M7", "M8"],
    
    "M1": ["N1", "N2"],
    "M2": ["N3"],
    "M3": ["N4", "N5"],
    "M4": ["N6", "N7"],
    "M5": ["N8"],
    "M6": ["N9", "N10"],
    "M7": ["N11"],
    "M8": ["N12", "N13"],
    
    "N1": ["V1", "A2"],
    "N2": ["V2"],
    "N3": ["V3", "A3"],
    "N4": ["V4"],
    "N5": ["V5"],
    "N6": ["A4"],
    "N7": ["V6"],
    "N8": ["A5", "V7"],
    "N9": ["V8"],
    "N10": ["V9"],
    "N11": ["V10"],
    "N12": ["V11"],
    "N13": ["A6", "V12"],
    
    "A2": ["V13", "E5"],
    "A3": ["E6", "V14"],
    "A4": ["V15"],
    "A5": ["E7", "V16"],
    "A6": ["V17"],
    
    "E5": ["M9", "V18"],
    "E6": ["V19"],
    "E7": ["M10", "V20"],
    
    "M9": ["V21"],
    "M10": ["V22"],
    
    "V1": (20, 30, 10, 6),
    "V2": (15, 2, 10, 5),
    "V3": (14, 20, 1, 2),
    "V4": (12, 6, 30, 8),
    "V5": (40, 5, 10, 30),
    "V6": (4, 16, 1, 15),
    "V7": (10, 33, 23, 0),
    "V8": (20, 10, 30, 12),
    "V9": (16, 90, 25, 100),
    "V10": (1, 5, 2, 20),
    "V11": (18, 10, 5, 20),
    "V12": (25, 20, 25, 8),
    "V13": (1, 9, 8, 15),
    "V14": (6, 18, 8, 9),
    "V15": (2, 25, 3, 30),
    "V16": (2, 22, 0, 12),
    "V17": (18, 21, 35, 22),
    "V18": (20, 10, 5, 9),
    "V19": (8, 12, 4, 6),
    "V20": (18, 10, 5, 9),
    "V21": (5, 7, 2, 1),
    "V22": (4, 14, 2, 1)
}

def minimax(node, tree):
    # If the current node is terminal, return its utility tuple.
    if isinstance(tree[node], tuple):
        return tree[node]
    
    # Determine the current player's index using the first character of the node's label.
    # Mapping: 'A' -> 0 (Anne), 'E' -> 1 (Ellen), 'M' -> 2 (Monica), 'N' -> 3 (Nicole)
    player_index = {'A': 0, 'E': 1, 'M': 2, 'N': 3}[node[0]]
    
    # Compute the utility vector for each child recursively.
    child_utilities = [minimax(child, tree) for child in tree[node]]
    
    # The current player chooses the move that maximizes their own utility.
    best_utility = max(child_utilities, key=lambda utility: utility[player_index])
    return best_utility

# Compute the minimax utility vector at the root node A1.
result = minimax("E7", game_tree)
print("Minimax utility vector at E7:", result)
result = minimax("A2", game_tree)
print("Minimax utility vector at A2:", result)
result = minimax("N2", game_tree)
print("Minimax utility vector at N2:", result)
result = minimax("M2", game_tree)
print("Minimax utility vector at M2:", result)
result = minimax("E4", game_tree)
print("Minimax utility vector at E4:", result)
result = minimax("A1", game_tree)
print("Minimax utility vector at A1:", result)

# Determine the winner: the friend with the highest utility value in the resulting vector.
players = ['Anne', 'Ellen', 'Monica', 'Nicole']
winner = players[result.index(max(result))]
print("The winner is:", winner)
