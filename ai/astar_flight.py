from search import Graph, GraphProblem, astar_search
from search import Node
from search import best_first_graph_search, memoize


# Define the road map as an undirected graph with missing connections added
city_map = Graph({
    "Atlanta": {"Austin": 1315, "Baltimore": 927, "Chicago": 944, "Dallas": 1157, "Houston": 1126,
                 "Indianapolis": 687, "Jacksonville": 458, "Memphis": 541, "Miami": 973, "New Orleans": 682,
                 "New York": 1199, "Newark": 1189, "Philadelphia": 1070, "San Antonio": 1417, "Tampa": 670,
                 "Washington DC": 871},
    "Austin": {"Dallas": 293, "Denver": 1240, "Houston": 235, "Indianapolis": 1489, "Memphis": 900,
                "New Orleans": 737, "Phoenix": 1396, "San Antonio": 118, "Tucson": 1270},
    "Baltimore": {"Boston": 577, "Chicago": 973, "Indianapolis": 819, "Jacksonville": 1096, "Memphis": 1273,
                   "New York": 272, "Newark": 262, "Philadelphia": 144, "Tampa": 1370, "Washington DC": 57},
    "Boston": {"Chicago": 1366, "Indianapolis": 1295, "New York": 305, "Newark": 315, "Philadelphia": 435,
                "Washington DC": 633},
    "Chicago": {"Dallas": 1290, "Denver": 1474, "Indianapolis": 263, "Jacksonville": 1387, "Memphis": 773,
                 "New Orleans": 1339, "New York": 1144, "Newark": 1130, "Philadelphia": 1068, "Washington DC": 955},
    "Dallas": {"Denver": 1064, "Houston": 362, "Indianapolis": 1227, "Jacksonville": 1458, "Memphis": 675,
                "New Orleans": 711, "San Antonio": 406, "Tampa": 1474, "Tucson": 1324},
    "Denver": {"Houston": 1412, "Las Vegas": 972, "Los Angeles": 1334, "Memphis": 1410, "Phoenix": 941,
                "San Antonio": 1289, "San Diego": 1339, "San Jose": 1491, "Tucson": 990},
    "Houston": {"Indianapolis": 1391, "Jacksonville": 1319, "Memphis": 778, "New Orleans": 509,
                  "San Antonio": 304, "Tampa": 1271},
    "Los Angeles": {"Las Vegas": 367, "Oakland": 552, "Phoenix": 573, "Portland": 1329, "San Diego": 179,
                      "San Francisco": 558, "San Jose": 491, "Tucson": 710},
    "Newark": {"Philadelphia": 120, "Washington DC": 318},
    "Philadelphia": {"Tampa": 1492, "Washington DC": 199},
    "Phoenix": {"Las Vegas": 412, "San Antonio": 1361, "San Diego": 480, "San Francisco": 1050,
                 "San Jose": 988, "Tucson": 173},
    "San Antonio": {"Tucson": 1225},
    "San Diego": {"Las Vegas": 426, "San Francisco": 737, "San Jose": 670, "Tucson": 586},
    "San Francisco": {"Las Vegas": 670, "San Jose": 66, "Tucson": 1213},

    "Indianapolis": {"Jacksonville": 1125, "Memphis": 617, "New Orleans": 1147, "New York": 1035,
                      "Newark": 1021, "Philadelphia": 937, "Tampa": 1356, "Washington DC": 789},
    "Jacksonville": {"Memphis": 949, "Miami": 526, "New Orleans": 809, "New York": 1343, "Newark": 1338,
                      "Philadelphia": 1220, "Tampa": 276, "Washington DC": 1040},
    "Las Vegas": {"Los Angeles": 367, "Oakland": 658, "Phoenix": 412, "Portland": 1215, "San Diego": 426,
                   "San Francisco": 670, "San Jose": 615, "Seattle": 1401, "Tucson": 590},
    "Memphis": {"Miami": 1404, "New Orleans": 577, "Philadelphia": 1413, "San Antonio": 1016, "Tampa": 1074, "Washington DC": 1225},
    "Miami": {"New Orleans": 1075, "Tampa": 329, "Washington DC": 1487},
    "New Orleans": {"San Antonio": 814, "Tampa": 773},
    "New York": {"Newark": 14, "Philadelphia": 129, "Washington DC": 328},
    "Oakland": {"Las Vegas": 658, "Phoenix": 1039, "Portland": 858, "San Diego": 731, "San Francisco": 13,
                 "San Jose": 61, "Seattle": 1089, "Tucson": 1203},
    "Portland": {"Las Vegas": 1215, "San Diego": 1499, "San Francisco": 861, "San Jose": 911, "Seattle": 232},
    "San Jose": {"Las Vegas": 615, "Seattle": 1141, "Tucson": 1150},
    "Tampa": {"Washington DC": 1315}
})

def make_bidirectional(graph_data):
    """Ensure all connections in the graph are bidirectional."""
    bidirectional_graph = {}
    
    for city, neighbors in graph_data.items():
        if city not in bidirectional_graph:
            bidirectional_graph[city] = {}
        
        for neighbor, cost in neighbors.items():
            bidirectional_graph[city][neighbor] = cost  # Keep existing connection
            
            # Ensure the reverse connection exists
            if neighbor not in bidirectional_graph:
                bidirectional_graph[neighbor] = {}
            bidirectional_graph[neighbor][city] = cost
    
    return Graph(bidirectional_graph)  # Convert to Graph object

# Convert city_map to bidirectional
city_map = make_bidirectional(city_map.graph_dict)



# Heuristic function: Direct flight distances to Dallas
h_to_dallas = {
    "Los Angeles": 1238, "Dallas": 0, "Denver": 663, "Houston": 225, "Indianapolis": 764,
    "Jacksonville": 907, "Las Vegas": 1069, "Memphis": 420, "Miami": 1111, "New Orleans": 443,
    "New York": 1371, "Newark": 1363, "Oakland": 1473, "Philadelphia": 1298, "Phoenix": 885,
    "Portland": 1632, "San Antonio": 253, "San Diego": 1182, "San Francisco": 1481,
    "San Jose": 1449, "Seattle": 1680, "Tampa": 917, "Tucson": 824, "Washington DC": 1182
}



def astar_search(problem, h=None, display=False):
    """A* search with explicit node expansion tracking."""
    h = memoize(h or problem.h, 'h')
    node_expansions = 0  # Track the number of nodes expanded

    def f(n):
        return n.path_cost + h(n)

    # Wrapper function to count expansions
    def best_first_graph_search_with_expansions(problem, f, display=False):
        """Modified best-first search to count node expansions."""
        from search import PriorityQueue
        node = Node(problem.initial)  # Ensure the root node is a Node object
        frontier = PriorityQueue('min', f)
        frontier.append(node)
        reached = {node.state: node}
        nonlocal node_expansions

        while frontier:
            node = frontier.pop()
            node_expansions += 1  # Increment expansions when a node is removed from the frontier

            if problem.goal_test(node.state):
                node.expanded_count = node_expansions  # Store the expansion count in the solution
                return node

            for child in node.expand(problem):
                if child.state not in reached or child.path_cost < reached[child.state].path_cost:
                    reached[child.state] = child
                    frontier.append(child)

        return None  # No solution found

    solution = best_first_graph_search_with_expansions(problem, f, display)
    
    if solution:
        solution.expanded_count = node_expansions  # Store node expansion count in solution

    return solution



def heuristic(node):
    return h_to_dallas.get(node, float('inf'))

# Solve Los Angeles -> Dallas
problem1 = GraphProblem("Los Angeles", "Dallas", city_map)
problem2 = GraphProblem("Dallas", "Newark", city_map)
solution1 = astar_search(problem1, lambda node: heuristic(node.state))
solution2 = astar_search(problem2, lambda node: heuristic(node.state))

print("A* Search from Los Angeles to Dallas:")
if solution1:
    print("Number of nodes expanded:", solution1.expanded_count)  # Explicit tracking
    print("Length of optimal path:", len(solution1.solution()) + 1)  # Include goal node
    print("Cost of optimal path:", solution1.path_cost)
    print("Path:", " -> ".join(solution1.solution()))
else:
    print("No path found from Los Angeles to Dallas.")

print("A* Search from Dallas to Newark:")
if solution2:
    print("Number of nodes expanded:", solution2.expanded_count)  # Explicit tracking
    print("Length of optimal path:", len(solution2.solution()) + 1)  # Include goal node
    print("Cost of optimal path:", solution2.path_cost)
    print("Path:", " -> ".join(solution2.solution()))
else:
    print("No path found from Dallas to Newark.")


# Check heuristic consistency
def is_heuristic_consistent(graph, heuristic):
    for city in graph.nodes():
        for neighbor, cost in graph.get(city).items():
            if abs(heuristic(GraphProblem(city, "Dallas", graph)) - heuristic(GraphProblem(neighbor, "Dallas", graph))) > cost:
                return False
    return True

print("Is the heuristic consistent?", "Yes" if is_heuristic_consistent(city_map, heuristic) else "No")
