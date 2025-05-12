# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    
    # first check
    '''
    print ("Start:", problem.getStartState())
    print ("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print ("Start's successors:", problem.getSuccessors(problem.getStartState()))
    '''
    # use stack to implement dfs
    # stack is the froniter and visited is the explored
    from util import Stack
    fringe = Stack()
    visited = set()   

    # get the start state and push states to frontier (state., path and cost like it says)
    start = problem.getStartState()
    fringe.push((start, [], 0))

    # as long as there is more to explore
    # check the sttates in the frontier by popping off the stack
    # if it's a goal, return the solution path
    # if it's not in explored, add it
    # had to push the child nodes in reverse order to get the right expansion
    while not fringe.isEmpty():
        currState, path, cost = fringe.pop()
        if problem.isGoalState(currState): 
            return path  
        if currState not in visited: 
            visited.add(currState)
            successors = problem.getSuccessors(currState)
            for child, direction, step_cost in reversed(successors):  
                if child not in visited:
                    fringe.push((child, path + [direction], cost + step_cost))

    return [] 
    
    util.raiseNotDefined()

def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"

    # same idea but use queue for fifo
    # queue is the frontier and visited is the explored
    from util import Queue

    fringe = Queue() 
    visited = set() 

    # get the start state and push states to frontier (state., path and cost like it says)
    start = problem.getStartState()
    fringe.push((start, [], 0))  

    # as long as there is more to explore
    # check the sttates in the frontier by popping off the queue
    # if it's a goal, return the solution path
    # if it's not in explored, add it
    # i could use normal push because fifo maintains the order
    while not fringe.isEmpty():
        currState, path, cost = fringe.pop()
        if problem.isGoalState(currState): 
            return path  
        if currState not in visited:
            visited.add(currState)
            successors = problem.getSuccessors(currState)
            for child, direction, step_cost in successors:
                if child not in visited:
                    fringe.push((child, path + [direction], cost + step_cost))

    return []

    util.raiseNotDefined()

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"

    # use priority queue because you need to keep track of cost too
    # p queue is the frontier and visited is the explored
    from util import PriorityQueue

    fringe = PriorityQueue()
    visited = set() 

    # get the start state and push states to frontier (state, path cost) add priority for cost
    start = problem.getStartState()
    fringe.push((start, [], 0), 0)

    # as long as there is more to explore
    # check the state in the frontier by popping off the p queue
    # if it's a goal, return the lowest cost solution path
    # if it's not in explored, add it (only process it if it's not explored)
    # push the child nodes with their updated costs and get the total cost from the start
    while not fringe.isEmpty():
        currState, path, cost = fringe.pop()
        if problem.isGoalState(currState):
            return path 
        if currState not in visited: 
            visited.add(currState)
            successors = problem.getSuccessors(currState)
            for child, direction, step_cost in successors:
                if child not in visited:
                    new_cost = cost + step_cost
                    fringe.push((child, path + [direction], new_cost), new_cost)

    return []

    util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"

     # use priority queue because you need to keep track of cost for a star
    # p queue is the frontier and visited is the explored
    from util import Queue, PriorityQueue

    fringe = PriorityQueue()
    visited = set()

    # get the start state and push states to frontier (state, path cost) add priority for f = g + h
    start = problem.getStartState()
    fringe.push((start, [], 0), 0) 

    # as long as there is more to explore
    # check the state in the frontier by popping off the p queue
    # if it's a goal, return the lowest cost solution path
    # if it's not in explored, add it (only process it if it's not explored)
    # same idea, but use the f = g + h heuristic
    while not fringe.isEmpty():
        currState, path, cost = fringe.pop()
        if problem.isGoalState(currState):
            return path 
        if currState not in visited: 
            visited.add(currState)
            successors = problem.getSuccessors(currState)
            for child, direction, step_cost in successors:
                if child not in visited:
                    new_cost = cost + step_cost
                    priority = new_cost + heuristic(child, problem)
                    fringe.push((child, path + [direction], new_cost), priority)

    return []

    util.raiseNotDefined()


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
