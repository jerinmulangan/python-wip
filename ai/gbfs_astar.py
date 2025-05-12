from search import Problem
from search import astar_search
from search import Node, PriorityQueue
from utils import memoize
from math import ceil


class MissionariesCannibals(Problem):
    def __init__(self, M, C, B):
        """Initialize the problem with M missionaries, C cannibals, and a boat capacity B."""
        self.M = M
        self.C = C
        self.B = B
        self.initial = (M, C, 1)  # All missionaries and cannibals on the wrong side
        self.goal = (0, 0, 0)  # Everyone on the correct side
        super().__init__(self.initial, self.goal)

    def actions(self, state):
        """Return valid actions for a given state."""
        m, c, b = state
        moves = []
        direction = -1 if b == 1 else 1  # Moving forward or back
        for missionaries in range(self.B + 1):
            for cannibals in range(self.B + 1):
                if 1 <= missionaries + cannibals <= self.B:  # Must move at least 1 and at most B
                    # Ensure boat itself is safe
                    if missionaries > 0 and missionaries < cannibals:
                        continue  #  Skip invalid moves where cannibals outnumber missionaries in the boat
                    new_m = m + direction * missionaries
                    new_c = c + direction * cannibals
                    if 0 <= new_m <= self.M and 0 <= new_c <= self.C:
                        # Ensure riverbanks remain safe on **both** sides
                        left_safe = (new_m == 0 or new_m >= new_c)
                        right_safe = ((self.M - new_m) == 0 or (self.M - new_m) >= (self.C - new_c))
                        if left_safe and right_safe:
                            moves.append((missionaries, cannibals))
        return moves

    def result(self, state, action):
        """Return the resulting state after applying an action."""
        m, c, b = state
        missionaries, cannibals = action
        direction = -1 if b == 1 else 1  # Determine move direction
        return (m + direction * missionaries, c + direction * cannibals, 1 - b)


    def goal_test(self, state):
        """Check if the goal state is reached."""
        return state == self.goal

    def h(self, node):
        m, c, _ = node.state
        return (m + c) / self.B  # Matches the provided hint




def best_first_graph_search(problem, f, display=False):
    """Search the nodes with the lowest f scores first."""
    f = memoize(f, 'f')
    node = Node(problem.initial)
    frontier = PriorityQueue('min', f)
    frontier.append(node)
    explored = set()
    nodes_expanded = 0  # Track nodes expanded

    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            if display:
                print(f"{nodes_expanded} nodes expanded.")
            return node, nodes_expanded  #  Always return a tuple

        explored.add(node.state)

        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
                nodes_expanded += 1  # Count only when a new node is expanded
            elif child in frontier:
                if f(child) < frontier[child]:
                    del frontier[child]
                    frontier.append(child)

    return None, nodes_expanded  #  Always return a tuple


def astar_search(problem, h=None, display=False):
    """A* search algorithm that returns both the solution and the number of nodes expanded."""
    h = memoize(h or problem.h, 'h')
    solution, nodes_expanded = best_first_graph_search(problem, lambda n: n.path_cost + h(n), display)
    return solution, nodes_expanded  # Always return a tuple


problem1 = MissionariesCannibals(4, 4, 3)
solution1, nodes_expanded1 = best_first_graph_search(problem1, lambda n: problem1.h(n))

print("Greedy Best First Search:")
print("Number of nodes expanded:", nodes_expanded1)

if solution1:  # Handle the case where no solution is found
    print("Length of optimal path:", len(solution1.path()))
else:
    print("No solution found.")

problem2 = MissionariesCannibals(11, 11, 4)
solution2, nodes_expanded2 = astar_search(problem2)

print("A* Search:")
print("Number of nodes expanded:", nodes_expanded2)

if solution2:
    print("Length of optimal path:", len(solution2.path()))
else:
    print("No solution found.")
