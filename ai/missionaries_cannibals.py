from search import Problem, breadth_first_graph_search, uniform_cost_search
from search import PriorityQueue, Node

def uniform_cost_graph_search(problem):
    """Uniform Cost Search (UCS) using a priority queue."""
    frontier = PriorityQueue(order='min', f=lambda node: node.path_cost)
    frontier.append(Node(problem.initial))
    explored = set()
    
    while frontier:
        node = frontier.pop()
        
        if problem.goal_test(node.state):
            return node
        
        explored.add(node.state)
        
        for action in problem.actions(node.state):
            child = node.child_node(problem, action)
            
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                incumbent = frontier[child]
                if child.path_cost < incumbent.path_cost:
                    frontier.replace(incumbent, child)
    
    return None  # No solution found

class MissionariesCannibals(Problem):
    def __init__(self, M, C, boat_capacity):
        """
        M: total missionaries
        C: total cannibals
        boat_capacity: maximum number of people in the boat
        """
        self.M = M
        self.C = C
        self.boat_capacity = boat_capacity
        self.expanded = 0  # Count of node expansions
        initial = (M, C, 1)  # All on left bank with boat
        goal = (0, 0, 0)  # Goal: all on right bank, boat on right
        super().__init__(initial, goal)

    def actions(self, state):
        """
        Returns a list of valid moves: (missionaries, cannibals) to move.
        """
        self.expanded += 1  # Count expansions
        m, c, b = state
        possible_actions = []

        # Determine the side we're picking from
        if b == 1:  # Boat on left side
            max_m, max_c = m, c
            new_boat = 0  # Boat moves to right
        else:  # Boat on right side
            max_m, max_c = self.M - m, self.C - c
            new_boat = 1  # Boat moves to left

        # Generate all valid actions within boat capacity
        for i in range(self.boat_capacity + 1):
            for j in range(self.boat_capacity + 1):
                if 1 <= i + j <= self.boat_capacity:  # Must take at least one
                    if i >= j or i == 0:  # Missionaries can't be outnumbered
                        if i <= max_m and j <= max_c:  # Don't take more than available
                            new_state = (m - i if b == 1 else m + i,
                                         c - j if b == 1 else c + j,
                                         new_boat)
                            if self.is_valid_state(new_state):
                                possible_actions.append((i, j))
        return possible_actions

    def result(self, state, action):
        """
        Applies action to state, returning new state.
        """
        m, c, b = state
        i, j = action
        return (m - i, c - j, 0) if b == 1 else (m + i, c + j, 1)

    def goal_test(self, state):
        """
        Returns True if the goal state is reached.
        """
        return state == self.goal

    def is_valid_state(self, state):
        """
        Returns True if state is valid (within bounds and safe).
        """
        m, c, _ = state
        if not (0 <= m <= self.M and 0 <= c <= self.C):
            return False  # Out of bounds
        if (m > 0 and m < c) or ((self.M - m) > 0 and (self.M - m) < (self.C - c)):
            return False  # Cannibals outnumber missionaries on either bank
        return True


def main():
    """ Runs the problem with BFS and UCS."""
    test_cases = [(4, 4, 3), (6, 6, 4)]
    for M, C, boat_capacity in test_cases:
        print(f"Solving for M={M}, C={C}, Boat Capacity={boat_capacity}\n")
        problem = MissionariesCannibals(M, C, boat_capacity)
        
        # BFS Search
        solution = breadth_first_graph_search(problem)
        if solution:
            print("BFS Solution:")
            print("Nodes expanded:", problem.expanded)
            print("Path length:", len(solution.path()))
            print("Solution path:", [node.state for node in solution.path()])
        else:
            print("No BFS solution found.")
        
        print("\n------------------\n")
        
        # UCS Search
        problem.expanded = 0  # Reset expansion counter
        solution = uniform_cost_graph_search(problem)
        if solution:
            print("UCS Solution:")
            print("Nodes expanded:", problem.expanded)
            print("Path length:", len(solution.path()))
            print("Solution path:", [node.state for node in solution.path()])
        else:
            print("No UCS solution found.")
        
        print("\n==================\n")

if __name__ == '__main__':
    main()
