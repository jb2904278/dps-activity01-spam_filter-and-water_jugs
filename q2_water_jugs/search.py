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

    def __repr__(self):
        return "<{}>".format(self.state)

    def __len__(self):
        return 0 if self.parent is None else (1 + len(self.parent))

    def __lt__(self, other):
        return self.path_cost < other.path_cost


failure = Node("failure", path_cost=float("inf"))  # indicates an algorithm could not find a solution


def expand(problem, node):
    """Figure 3.7: generate the child nodes of node."""
    s = node.state
    for action in problem.actions(s):
        s1 = problem.result(s, action)
        cost = node.path_cost + problem.action_cost(s, action, s1)
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
    """Figure 3.9 (AIMA 4e):

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
    node = Node(problem.initial)
    if problem.is_goal(problem.initial):
        return node
    frontier = FIFOQueue([node])
    reached = {problem.initial}
    while frontier:
        node = frontier.popleft()
        for child in expand(problem, node):
            s = child.state
            if problem.is_goal(s):
                return child
            if s not in reached:
                reached.add(s)
                frontier.append(child)
    return failure
