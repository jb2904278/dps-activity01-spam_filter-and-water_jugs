"""
Agent framework for the spam-filter agent.

    Thing        - any object that can be in an environment
                   (from aima-python; not in textbook pseudocode but used in the
                    companion code so agents and environment items share one list)
    Agent        - a Thing whose `program` maps a percept to an action
    Environment  - gives percepts to agents and carries out their actions
    Rule         - a condition-action rule (used by the simple reflex agent)
    SimpleReflexAgentProgram - Figure 2.10 pseudocode, translated to Python
"""


class Thing:
    """Any physical object that can appear in an Environment."""

    def __repr__(self):
        return "<{}>".format(getattr(self, "__name__", self.__class__.__name__))

    def is_alive(self):
        return hasattr(self, "alive") and self.alive


class Agent(Thing): # agent is inherting from Thing
    """An Agent is a Thing with a program: program(percept) -> action.

    The program is a black box. It only sees the percept it is given."""

    def __init__(self, program=None):
        self.alive = True
        self.performance = 0
        if program is None or not callable(program):
            raise ValueError("An Agent needs a callable agent program")
        self.program = program


class Rule:
    """A condition-action rule: if condition(state) then action."""

    def __init__(self, name, condition, action):
        self.name = name
        self.condition = condition
        self.action = action

    def matches(self, state):
        return self.condition(state)

    def __repr__(self):
        return "Rule({!r} -> {!r})".format(self.name, self.action)


def rule_match(state, rules):
    """Return the first rule whose condition holds for the state."""
    for rule in rules:
        if rule.matches(state):
            return rule
    return None


def SimpleReflexAgentProgram(rules, interpret_input):
    """

    function SIMPLE-REFLEX-AGENT(percept) returns an action
        persistent: rules, a set of condition-action rules
        state  <- INTERPRET-INPUT(percept)
        rule   <- RULE-MATCH(state, rules)
        action <- rule.ACTION
        return action
    """

    def program(percept):
        state = interpret_input(percept)
        rule = rule_match(state, rules)
        action = rule.action
        return action

    return program


class Environment:
    """Abstract class for environments (AIMA agents.py).

    Subclasses define percept(), execute_action() and optionally is_done()."""

    def __init__(self):
        self.things = []
        self.agents = []

    def percept(self, agent):
        raise NotImplementedError

    def execute_action(self, agent, action):
        raise NotImplementedError

    def is_done(self):
        return not any(agent.is_alive() for agent in self.agents)

    def step(self):
        """Run the environment for one time step: each agent gets a percept,
        chooses an action, and the environment carries it out."""
        if not self.is_done():
            actions = []
            for agent in self.agents:
                if agent.alive:
                    actions.append(agent.program(self.percept(agent)))
                else:
                    actions.append("")
            for agent, action in zip(self.agents, actions):
                self.execute_action(agent, action)

    def run(self, steps=1000):
        for _ in range(steps):
            if self.is_done():
                return
            self.step()

    def add_thing(self, thing):
        if isinstance(thing, Agent):
            self.agents.append(thing)
        else:
            self.things.append(thing)
