import csv
import os
import shutil
import tempfile
import unittest

from q1_spam_filter import spam_agent as sa

DATA = sa.DATA_DIR


class TestHelpers(unittest.TestCase):
    def test_domain_matching(self):
        self.assertTrue(sa.domain_in("github.com", ["github.com"]))
        self.assertTrue(sa.domain_in("notifications.github.com", ["github.com"]))
        self.assertFalse(sa.domain_in("evilgithub.com", ["github.com"]))
        self.assertFalse(sa.domain_in("", ["github.com"]))

    def test_bad_word_counting(self):
        words = ["free", "cash", "click here"]
        self.assertEqual(sa.count_bad_words("FREE free Free!", words), 3)
        self.assertEqual(sa.count_bad_words("freedom cashew", words), 0)  # whole words only
        self.assertEqual(sa.count_bad_words("Click   here", words), 0)
        self.assertEqual(sa.count_bad_words("click here now, cash", words), 2)


class TestAgentProgram(unittest.TestCase):
    """Test the agent program on its own: percept in, action out."""

    def setUp(self):
        self.agent = sa.SpamFilterAgent(["good.com"], ["bad.com"], ["free", "cash"])

    def percept(self, sender, body):
        raw = "From: {}\nSubject: t\nContent-Type: text/plain\n\n{}\n".format(sender, body)
        return {"filename": "x.eml", "raw": raw.encode()}

    def test_threshold_boundary(self):
        self.assertEqual(self.agent.program(self.percept("a@x.com", "free " * 5)), sa.MOVE_TO_EMAIL)
        self.assertEqual(self.agent.program(self.percept("a@x.com", "free " * 6)), sa.MOVE_TO_SPAM)

    def test_allow_list_wins(self):
        self.assertEqual(self.agent.program(self.percept("a@good.com", "cash " * 50)), sa.MOVE_TO_EMAIL)

    def test_restrict_list_wins(self):
        self.assertEqual(self.agent.program(self.percept("a@bad.com", "hello")), sa.MOVE_TO_SPAM)

    def test_empty_inbox_noop(self):
        self.assertEqual(self.agent.program(None), sa.NO_OP)


class TestEnvironmentWithSampleData(unittest.TestCase):
    """Run the agent on the sample inbox and compare with data/expected.csv."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.inbox = os.path.join(self.tmp, "inbox")
        shutil.copytree(os.path.join(DATA, "inbox"), self.inbox)
        self.out = os.path.join(self.tmp, "out")
        with open(os.path.join(DATA, "expected.csv"), newline="") as f:
            self.expected = {r["filename"]: r for r in csv.DictReader(f)}

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_filter(self, move):
        return sa.run_filter(self.inbox, self.out,
                             os.path.join(DATA, "allow_list.txt"),
                             os.path.join(DATA, "restrict_list.txt"),
                             os.path.join(DATA, "bad_words.txt"), move=move)

    def test_every_email_sorted_correctly(self):
        log = self.run_filter(move=True)
        self.assertEqual(len(log), len(self.expected))
        for name, row in self.expected.items():
            with self.subTest(email=name, reason=row["reason"]):
                self.assertTrue(os.path.exists(os.path.join(self.out, row["expected"], name)))
                other = "email" if row["expected"] == "spam" else "spam"
                self.assertFalse(os.path.exists(os.path.join(self.out, other, name)))
        self.assertEqual(os.listdir(self.inbox), [])  # move mode empties the inbox

    def test_copy_mode_keeps_inbox(self):
        self.run_filter(move=False)
        self.assertEqual(len(os.listdir(self.inbox)), len(self.expected))


if __name__ == "__main__":
    unittest.main()
