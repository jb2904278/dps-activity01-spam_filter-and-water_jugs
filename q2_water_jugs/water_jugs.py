"""
Q2 - Three-jug water problem as a search problem, solved with breadth-first search (Figure 3.9).

State:       tuple (a, b, c), the gallons in the 12-, 8- and 3-gallon jugs
Initial:     (0, 0, 0), all jugs empty
Goal test:   some jug holds exactly 1 gallon
Actions:     ('Fill', i)      fill jug i from the faucet
             ('Empty', i)     pour jug i out onto the ground
             ('Pour', i, j)   pour jug i into jug j until i is empty or j is full
Transition:  see WaterJugProblem.result
Cost:        1 per action

Run from the Activity01 folder:
    python -m q2_water_jugs.water_jugs
    python -m q2_water_jugs.water_jugs --capacities 12 8 3 --goal 1
"""

import argparse

try:
    from .search import Problem, breadth_first_search, failure, path_actions, path_states
except (ImportError, ValueError):
    from search import Problem, breadth_first_search, failure, path_actions, path_states


class WaterJugProblem(Problem):
    def __init__(self, capacities=(12, 8, 3), goal=1, initial=None): 
    # default capacities are 12, 8, 3 gallons and the goal is to have 1 gallon in any jug, start with all empty
        capacities = tuple(capacities) # makes it a tuple, immutable, can't be changed
        if initial is None: # checks if the initial state is None (no value assigned)
            initial = tuple(0 for _ in capacities) # initializes the jugs to empty like (0,0,0)
        super().__init__(initial=tuple(initial), goal=goal, capacities=capacities) # passes the initial state, goal state, and capacities to the parent class (Problem) such as jug capacities(12,8,3), goal(1), initial(0,0,0)

    def actions(self, state): # accepts: state tuple e.g. (4, 8, 0) → returns: list of valid action tuples e.g. [('Fill',2), ('Empty',1), ('Pour',1,2)]
        """Applicable actions only. Actions that would leave the state unchanged are
        skipped (filling a full jug, emptying an empty one, pouring from an empty jug
        or into a full one)."""
        caps = self.capacities # gets the capacities of the jugs
        acts = [] # initializes an empty list to store the actions
        for i in range(len(caps)): # loops through the jugs we get index of the jug like 0,1,2,3 for 4 jugs
            if state[i] < caps[i]: # checks if the current jug is not full, if 0 < 12 is true then it adds the "Fill" action to the list
                acts.append(("Fill", i)) # adds the "Fill" action to the list e.g. for first jug it adds ('Fill', 0)
            if state[i] > 0: #  checks if the current jug is not empty. If 0 > 0 is FALSE, skip (can't empty an already empty jug)
                acts.append(("Empty", i)) # adds the "Empty" action to the list e.g. for first jug it adds ('Empty', 0)
            for j in range(len(caps)): # loops through the jugs we get index of the jug like 0,1,2,3 for 4 jugs
                if i != j and state[i] > 0 and state[j] < caps[j]: # checks if the current jug is not empty and the other jug is not full 
                    acts.append(("Pour", i, j)) # adds the "Pour" action to the list
        return acts

    def result(self, state, action): # accepts: state tuple e.g. (4, 8, 0) AND action tuple e.g. ('Pour', 1, 2) → returns: new state tuple e.g. (4, 5, 3)
        s = list(state) # it changes (0,0,0) to [0,0,0] so we can change it
        kind, i = action[0], action[1] # it unpacks the action tuple into kind and i i.e. ("Fill" , 0) becomes kind = "Fill", i = 0
        if kind == "Fill": # if action is "Fill"
            s[i] = self.capacities[i] # fills the jug i i.e. s[0] = 12, so it makes it (12,0,0)
        elif kind == "Empty": # if action is "Empty"
            s[i] = 0 # empties the jug i
        elif kind == "Pour": # if action is "Pour"
            j = action[2]
            amount = min(s[i], self.capacities[j] - s[j]) # calculates the amount of water to be poured
            s[i] -= amount
            s[j] += amount
        else:
            raise ValueError("Unknown action: {}".format(action))
        return tuple(s)

    def is_goal(self, state): # accepts: state tuple e.g. (4, 1, 3) → returns: True if 1 is anywhere in the tuple, False otherwise
        return self.goal in state

    def describe(self, action): # accepts: action tuple e.g. ('Pour', 0, 1) → returns: human-readable string e.g. 'Pour 12-gal jug into 8-gal jug' (only used for printing the solution)
        caps = self.capacities
        if action[0] == "Pour":
            return "Pour {}-gal jug into {}-gal jug".format(caps[action[1]], caps[action[2]])
        if action[0] == "Fill":
            return "Fill {}-gal jug".format(caps[action[1]])
        return "Empty {}-gal jug".format(caps[action[1]])


def reachable_states(problem): # accepts: a WaterJugProblem object → returns: a set of ALL reachable state tuples e.g. {(0,0,0), (12,0,0), (4,8,0), ...} used only to count how big the state space is
    """Every state reachable from the initial state. Used to report how big the state space is."""
    seen, frontier = {problem.initial}, [problem.initial]
    while frontier:
        s = frontier.pop()
        for a in problem.actions(s):
            s1 = problem.result(s, a)
            if s1 not in seen:
                seen.add(s1)
                frontier.append(s1)
    return seen


def main(argv=None):
    p = argparse.ArgumentParser(description="Water jug problem solved with breadth-first search")
    p.add_argument("--capacities", type=int, nargs="+", default=[12, 8, 3])
    p.add_argument("--goal", type=int, default=1)
    args = p.parse_args(argv)

    problem = WaterJugProblem(args.capacities, args.goal)
    print("Jugs: {}  initial: {}  goal: some jug holds {} gal".format(
        problem.capacities, problem.initial, problem.goal))
    print("Reachable states: {}".format(len(reachable_states(problem))))

    solution = breadth_first_search(problem)
    if solution is failure:
        print("No solution: the goal cannot be reached.")
        return
    print("Solution found in {} steps:".format(len(solution)))
    print("   start                                    {}".format(problem.initial))
    for n, (a, s) in enumerate(zip(path_actions(solution), path_states(solution)[1:]), 1):
        print("{:>2}. {:<40} {}".format(n, problem.describe(a), s))


if __name__ == "__main__":
    main()
