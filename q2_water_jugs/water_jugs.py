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
        capacities = tuple(capacities)
        if initial is None:
            initial = tuple(0 for _ in capacities)
        super().__init__(initial=tuple(initial), goal=goal, capacities=capacities)

    def actions(self, state):
        """Applicable actions only. Actions that would leave the state unchanged are
        skipped (filling a full jug, emptying an empty one, pouring from an empty jug
        or into a full one)."""
        caps = self.capacities
        acts = []
        for i in range(len(caps)):
            if state[i] < caps[i]:
                acts.append(("Fill", i))
            if state[i] > 0:
                acts.append(("Empty", i))
            for j in range(len(caps)):
                if i != j and state[i] > 0 and state[j] < caps[j]:
                    acts.append(("Pour", i, j))
        return acts

    def result(self, state, action):
        s = list(state)
        kind, i = action[0], action[1]
        if kind == "Fill":
            s[i] = self.capacities[i]
        elif kind == "Empty":
            s[i] = 0
        elif kind == "Pour":
            j = action[2]
            amount = min(s[i], self.capacities[j] - s[j])
            s[i] -= amount
            s[j] += amount
        else:
            raise ValueError("Unknown action: {}".format(action))
        return tuple(s)

    def is_goal(self, state):
        return self.goal in state

    def describe(self, action):
        caps = self.capacities
        if action[0] == "Pour":
            return "Pour {}-gal jug into {}-gal jug".format(caps[action[1]], caps[action[2]])
        if action[0] == "Fill":
            return "Fill {}-gal jug".format(caps[action[1]])
        return "Empty {}-gal jug".format(caps[action[1]])


def reachable_states(problem):
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
