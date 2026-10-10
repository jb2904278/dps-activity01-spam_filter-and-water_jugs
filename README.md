# DPS970 – Activity 1

Implementations for **Q1 (Spam Filter Agent)** and **Q2 (Three-Jug Search Problem)**.

The code is Python 3.8 or newer and uses the **standard library only**, so nothing needs to be installed. The design follows the textbook's agent framework and search problem formulation.

## Project layout

```
Activity01/
├── q1_spam_filter/
│   ├── agents.py                  # Thing, Agent, Environment, Rule, SimpleReflexAgentProgram
│   ├── spam_agent.py              # INTERPRET-INPUT, rules, MailboxEnvironment, command-line program
│   └── data/                      # TEST DATA
│       ├── allow_list.txt
│       ├── restrict_list.txt
│       ├── bad_words.txt
│       ├── expected.csv           # expected folder for each sample email, with the reason
│       └── inbox/*.eml            # 11 sample emails covering every rule and edge case
├── q2_water_jugs/
│   ├── search.py                  # Problem, Node, expand, breadth_first_search
│   ├── water_jugs.py              # WaterJugProblem + command-line program
│   └── data/test_cases.json       # TEST DATA: jug sizes, goal, expected solution length
├── tests/
│   ├── test_spam_agent.py
│   └── test_water_jugs.py
└── .github/workflows/tests.yml    # GitHub Actions: runs the tests on every push
```

## Running the tests

From the `Activity01` root directory:

**Run all 17 tests:**
```bash
python3 -m unittest discover -s tests -t . -v
```

**Run Q1 tests only (8 tests):**
```bash
python3 -m unittest tests/test_spam_agent.py -v
```

**Run Q2 tests only (9 tests):**
```bash
python3 -m unittest tests/test_water_jugs.py -v
```

These 17 tests check rule priority (allow list overriding bad words), threshold boundaries (5 is clean, 6 is spam), domain and subdomain matching, decoding of base64, HTML and text attachments, sorting of every sample email against `expected.csv`, the water jug transition model, BFS solutions for each case in `test_cases.json` (including unsolvable cases), and that BFS returns the shortest solution.

**GitHub Actions:** push this folder to a GitHub repository and `.github/workflows/tests.yml` runs the tests, then both demos, on Python 3.9 and 3.12 on every push or pull request. You can also start it by hand from the **Actions** tab.

## Running the programs

**Q1 – spam filter**

```bash
python3 -m q1_spam_filter.spam_agent                     # sorts the sample inbox into q1_spam_filter/output/{spam,email}
python3 -m q1_spam_filter.spam_agent --inbox <dir> --out <dir> --move
#   optional: --allow <file> --restrict <file> --badwords <file>
```

By default the emails are **copied**, so the sample inbox stays intact for the next run. Add `--move` to move them instead.

**Q2 – water jugs**

```bash
python3 -m q2_water_jugs.water_jugs                      # 12/8/3 gallon jugs, goal = 1 gallon
python3 -m q2_water_jugs.water_jugs --capacities 8 5 3 --goal 4
```

Expected output:

```
Jugs: (12, 8, 3)  initial: (0, 0, 0)  goal: some jug holds 1 gal
Reachable states: 314
Solution found in 3 steps:
   start                                    (0, 0, 0)
 1. Fill 12-gal jug                          (12, 0, 0)
 2. Pour 12-gal jug into 8-gal jug           (4, 8, 0)
 3. Pour 12-gal jug into 3-gal jug           (1, 8, 3)
```
