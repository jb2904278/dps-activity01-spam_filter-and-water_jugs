import json
import os
import unittest

from q2_water_jugs.search import Node, breadth_first_search, failure, path_actions, path_states
from q2_water_jugs.water_jugs import WaterJugProblem, reachable_states

CASES = os.path.join(os.path.dirname(__file__), "..", "q2_water_jugs", "data", "test_cases.json")


def replay(problem, actions):
    """Apply the actions one by one from the initial state and return the final state."""
    s = problem.initial
    for a in actions:
        assert a in problem.actions(s), "action {} not applicable in {}".format(a, s)
        s = problem.result(s, a)
    return s


class TestTransitionModel(unittest.TestCase):
    def setUp(self):
        self.p = WaterJugProblem((12, 8, 3), 1)

    def test_fill_and_empty(self):
        self.assertEqual(self.p.result((0, 0, 0), ("Fill", 0)), (12, 0, 0))
        self.assertEqual(self.p.result((5, 2, 3), ("Empty", 1)), (5, 0, 3))

    def test_pour_until_target_full(self):
        self.assertEqual(self.p.result((12, 0, 0), ("Pour", 0, 1)), (4, 8, 0))

    def test_pour_until_source_empty(self):
        self.assertEqual(self.p.result((0, 0, 3), ("Pour", 2, 1)), (0, 3, 0))

    def test_no_useless_actions(self):
        self.assertNotIn(("Empty", 0), self.p.actions((0, 0, 0)))
        self.assertNotIn(("Fill", 0), self.p.actions((12, 0, 0)))
        self.assertNotIn(("Pour", 1, 2), self.p.actions((0, 0, 3)))

    def test_water_never_exceeds_capacity(self):
        for s in reachable_states(self.p):
            for amount, cap in zip(s, self.p.capacities):
                self.assertTrue(0 <= amount <= cap)


class TestBreadthFirstSearch(unittest.TestCase):
    def test_assignment_problem(self):
        p = WaterJugProblem((12, 8, 3), 1)
        sol = breadth_first_search(p)
        self.assertIsNot(sol, failure)
        self.assertEqual(len(sol), 3)
        self.assertIn(1, sol.state)
        self.assertEqual(replay(p, path_actions(sol)), sol.state)
        self.assertEqual(path_states(sol)[0], (0, 0, 0))

    def test_goal_at_initial_state(self):
        p = WaterJugProblem((12, 8, 3), 1, initial=(1, 0, 0))
        sol = breadth_first_search(p)
        self.assertEqual(len(sol), 0)
        self.assertEqual(path_actions(sol), [])

    def test_cases_from_file(self):
        with open(CASES) as f:
            cases = json.load(f)
        for c in cases:
            with self.subTest(case=c["name"]):
                p = WaterJugProblem(c["capacities"], c["goal"])
                sol = breadth_first_search(p)
                if c["expected_steps"] is None:
                    self.assertIs(sol, failure)
                else:
                    self.assertEqual(len(sol), c["expected_steps"])
                    self.assertIn(c["goal"], replay(p, path_actions(sol)))

    def test_bfs_is_optimal(self):
        """No solution can be shorter than the BFS one: check every state at smaller depths."""
        p = WaterJugProblem((12, 8, 3), 1)
        depth = len(breadth_first_search(p))
        level = {p.initial}
        for _ in range(depth - 1):
            level = {p.result(s, a) for s in level for a in p.actions(s)}
            self.assertFalse(any(p.is_goal(s) for s in level))


if __name__ == "__main__":
    unittest.main()
