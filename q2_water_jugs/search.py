"""
Search framework for the water-jug problem.

Adapted from the official AIMA Python companion code (aima-python):
    https://github.com/aimacode/aima-python/blob/master/search4e.py

Reference: Russell & Norvig, *AI: A Modern Approach*, 4th ed., Chapter 3.

    Problem      - abstract search problem (Section 3.1.1)
    Node         - search-tree node (Section 3.3.1)
    expand       - Figure 3.7 (EXPAND)
    breadth_first_search - Figure 3.9 pseudocode, translated to Python
"""

from collections import deque


class Problem:
    """Abstract formal problem. Subclasses override actions and result (and is_goal if needed)."""

    def __init__(self, initial=None, goal=None, **kwds):
        self.__dict__.update(initial=initial, goal=goal, **kwds)

    def actions(self, state):
        raise NotImplementedError

    def result(self, state, action):
        raise NotImplementedError

    def is_goal(self, state):
        return state == self.goal

    def action_cost(self, s, a, s1):
        return 1

    def h(self, node):
        return 0

    def __str__(self):
        return "{}({!r}, {!r})".format(type(self).__name__, self.initial, self.goal)


class Node:
    """A node in a search tree."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.__dict__.update(state=state, parent=parent, action=action, path_cost=path_cost) 
        # jug right amount right now, which node did we come FROM, what move got us HERE, how much did it cost to get HERE

    def __repr__(self):
        return "<{}>".format(self.state)

    def __len__(self):
        return 0 if self.parent is None else (1 + len(self.parent))

    def __lt__(self, other):
        return self.path_cost < other.path_cost


failure = Node("failure", path_cost=float("inf"))  # indicates an algorithm could not find a solution


def expand(problem, node):

    # For (12,0,0) it returns [('Empty', 0), ('Pour', 0, 1), ('Pour', 0, 2), ('Fill', 1), ('Fill', 2)]
    # For (0,8,0)  it returns [('Fill', 0), ('Empty', 1), ('Pour', 1, 0), ('Pour', 1, 2), ('Fill', 2)]
    # For (0,0,3)  it returns [('Fill', 0), ('Fill', 1), ('Empty', 2), ('Pour', 2, 0), ('Pour', 2, 1)]
    # For (4,8,0)  it returns [('Fill', 0), ('Empty', 0), ('Pour', 0, 2), ('Empty', 1), ('Pour', 1, 0), ('Pour', 1, 2), ('Fill', 2)]
    """generate the child nodes of node. Given where I am right now, generate all possible next positions." Like looking at a chessboard and listing every valid move."""
    s = node.state # First iteration from BFS (0,0,0) then (12,0,0) (8,0,4) and so on 
    for action in problem.actions(s): # generate possible actions from current state for 12,0,0 it returns [('Empty', 0), ('Pour', 0, 1), ('Pour', 0, 2), ('Fill', 1), ('Fill', 2)]
        s1 = problem.result(s, action) # which state results from taking this action
        cost = node.path_cost + problem.action_cost(s, action, s1) # cost of taking this action
        yield Node(s1, node, action, cost)


def path_actions(node):
    """The list of actions taken to reach this node."""
    if node.parent is None:
        return []
    return path_actions(node.parent) + [node.action]


def path_states(node):
    """The list of states from the root to this node."""
    if node in (failure, None):
        return []
    return path_states(node.parent) + [node.state]


FIFOQueue = deque


def breadth_first_search(problem):
    """ BFS algorithm:

    function BREADTH-FIRST-SEARCH(problem) returns a solution node or failure
        node <- NODE(problem.INITIAL)
        if problem.IS-GOAL(node.STATE) then return node
        frontier <- a FIFO queue, with node as an element
        reached  <- {problem.INITIAL}
        while not IS-EMPTY(frontier) do
            node <- POP(frontier)
            for each child in EXPAND(problem, node) do
                s <- child.STATE
                if problem.IS-GOAL(s) then return child
                if s is not in reached then
                    add s to reached
                    add child to frontier
        return failure
    """
    node = Node(problem.initial) # creates the very first node, start at (0,0,0)
    if problem.is_goal(problem.initial): #checks if the starting state is the goal state such as already done? (edge case)
        return node
    frontier = FIFOQueue([node]) # queue of states to explore, BreadthFirstSearch explores level by level
    reached = {problem.initial} # set of states that have been visited, to avoid loops
    while frontier: # loop until the frontier is empty
        node = frontier.popleft() # get the first node from the frontier
        for child in expand(problem, node): # generate the child nodes of node
            s = child.state # get the state of the child node
            if problem.is_goal(s): # check if the child node is the goal state
                return child # return the child node if it is the goal state
            if s not in reached: # check if the child node has been visited
                reached.add(s) # add the child node to the reached set
                frontier.append(child)
    return failure
