# Mapping from player name to the index in the utility vector.
player_to_index = {
    "Anne": 0,
    "Ellen": 1,
    "Monica": 2,
    "Nicole": 3,
}

# Terminal utility vectors provided.
v1  = (20, 30, 10, 6)
v2  = (15, 2, 10, 5)
v3  = (14, 20, 1, 2)
v4  = (12, 6, 30, 8)
v5  = (40, 5, 10, 30)
v6  = (4, 16, 1, 15)
v7  = (10, 33, 23, 0)
v8  = (20, 10, 30, 12)
v9  = (16, 90, 25, 100)
v10 = (1, 5, 2, 20)
v11 = (18, 10, 5, 20)
v12 = (25, 20, 25, 8)
v13 = (1, 9, 8, 15)
v14 = (6, 18, 8, 9)
v15 = (2, 25, 3, 30)
v16 = (2, 22, 0, 12)
v17 = (18, 21, 35, 22)
v18 = (20, 10, 5, 9)
v19 = (8, 12, 4, 6)
v20 = (18, 10, 5, 9)
v21 = (5, 7, 2, 1)
v22 = (4, 14, 2, 1)

# Define a simple tree node.
class Node:
    def __init__(self, name, player=None, children=None, value=None):
        """
        name: string label
        player: whose turn is at this node ("Anne", "Ellen", etc.) – for internal nodes.
        children: list of Node objects.
        value: for terminal nodes, a tuple (Anne, Ellen, Monica, Nicole)
        """
        self.name = name
        self.player = player
        self.children = children if children is not None else []
        self.value = value

# Create terminal nodes.
T_v1  = Node("v1",  value=v1)
T_v2  = Node("v2",  value=v2)
T_v3  = Node("v3",  value=v3)
T_v4  = Node("v4",  value=v4)
T_v5  = Node("v5",  value=v5)
T_v6  = Node("v6",  value=v6)
T_v7  = Node("v7",  value=v7)
T_v8  = Node("v8",  value=v8)
T_v9  = Node("v9",  value=v9)
T_v10 = Node("v10", value=v10)
T_v11 = Node("v11", value=v11)
T_v12 = Node("v12", value=v12)
T_v13 = Node("v13", value=v13)
T_v14 = Node("v14", value=v14)
T_v15 = Node("v15", value=v15)
T_v16 = Node("v16", value=v16)
T_v17 = Node("v17", value=v17)
T_v18 = Node("v18", value=v18)
T_v19 = Node("v19", value=v19)
T_v20 = Node("v20", value=v20)
T_v21 = Node("v21", value=v21)
T_v22 = Node("v22", value=v22)

# Now build the internal nodes.
# (Our assumed structure is as follows:
#  - Node E7 (Ellen) has children v1, v2, v3, v4.
#  - Node E4 (Ellen) has children: E7 and v5.
#  - Node M2 (Monica) has children: v6, v7, v8, v9, v10.
#  - Node N2 (Nicole) has children: v11, v12, v13, v14, v15, v16, v17, v18, v19, v20, v21, v22.
#  - Node A2 (Anne) has children: M2 and N2.
#  - Root A1 (Anne) has children: A2 and E4.)
E7 = Node("E7", player="Ellen", children=[T_v1, T_v2, T_v3, T_v4])
E4 = Node("E4", player="Ellen", children=[E7, T_v5])
M2 = Node("M2", player="Monica", children=[T_v6, T_v7, T_v8, T_v9, T_v10])
N2 = Node("N2", player="Nicole", children=[T_v11, T_v12, T_v13, T_v14, T_v15, T_v16, T_v17, T_v18, T_v19, T_v20, T_v21, T_v22])
A2 = Node("A2", player="Anne", children=[M2, N2])
A1 = Node("A1", player="Anne", children=[A2, E4])

# max^n (multiplayer minimax) algorithm.
def maxn(node):
    # If node is terminal, return its utility vector.
    if node.value is not None:
        return node.value

    # Determine current player's index.
    curr_player = node.player
    player_idx = player_to_index[curr_player]
    
    # Recursively evaluate children.
    child_values = [maxn(child) for child in node.children]
    
    # Choose the child that maximizes the current player's utility.
    best_value = child_values[0]
    for val in child_values[1:]:
        if val[player_idx] > best_value[player_idx]:
            best_value = val
    return best_value

# Compute minimax values for the requested nodes.
val_E7 = maxn(E7)
val_A2 = maxn(A2)
val_M2 = maxn(M2)
val_N2 = maxn(N2)
val_E4 = maxn(E4)
val_A1 = maxn(A1)

# Function to pretty-print the result.
def print_value(node_name, value):
    print(f"Utility at node {node_name}:")
    print(f"  Anne:   {value[0]}")
    print(f"  Ellen:  {value[1]}")
    print(f"  Monica: {value[2]}")
    print(f"  Nicole: {value[3]}\n")

print_value("E7", val_E7)
print_value("A2", val_A2)
print_value("M2", val_M2)
print_value("N2", val_N2)
print_value("E4", val_E4)
print_value("A1", val_A1)

# Determine the winner at A1 (the friend with the highest utility).
# (Indices: 0: Anne, 1: Ellen, 2: Monica, 3: Nicole)
players = ["Anne", "Ellen", "Monica", "Nicole"]
winner_index = max(range(4), key=lambda i: val_A1[i])
winner = players[winner_index]
print(f"In node A1 the maximum utility is {val_A1[winner_index]} for {winner}.\n"
      f"--> Thus, {winner} won the game.")
