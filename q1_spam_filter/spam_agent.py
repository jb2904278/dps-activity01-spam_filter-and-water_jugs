"""
Q1 - Spam Filter Email Agent (simple reflex agent).

The environment is a mail folder: an inbox of .eml files plus two output folders,
spam/ and email/. On each step the agent perceives one email and acts by moving it
to one of those folders.

Rules, checked in order (first match wins):
    R1  sender domain is on the ALLOW list       -> MOVE_TO_EMAIL  (whatever the content)
    R2  sender domain is on the RESTRICT list    -> MOVE_TO_SPAM   (whatever the content)
    R3  more than 5 bad words in the body/text   -> MOVE_TO_SPAM
    R4  otherwise                                -> MOVE_TO_EMAIL

Run from the Activity01 folder:
    python -m q1_spam_filter.spam_agent                 # uses the sample data
    python -m q1_spam_filter.spam_agent --inbox path/to/inbox --out path/to/output --move
"""

import argparse
import email
import html
import os
import re
import shutil
from email import policy
from email.utils import parseaddr

try:
    from .agents import Agent, Environment, Rule, SimpleReflexAgentProgram, Thing
except (ImportError, ValueError):
    from agents import Agent, Environment, Rule, SimpleReflexAgentProgram, Thing

MOVE_TO_SPAM = "MoveToSpam"
MOVE_TO_EMAIL = "MoveToEmail"
NO_OP = "NoOperation"

BAD_WORD_THRESHOLD = 5  # spam when the count is MORE than this (6 or more)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")


# --------------------------------------------------------------------------- #
# Knowledge the agent has: the three lists
# --------------------------------------------------------------------------- #
def load_list(path):
    """Read one entry per line, in lowercase. Blank lines and lines starting with # are skipped."""
    entries = [] # list of strings which will store the allowed and restricted domains and the bad words in separate load_list call
    with open(path, encoding="utf-8") as f: # opening the file
        for line in f: # iterating over each line in the file
            line = line.strip().lower() # removing whitespace and converting to lowercase
            if line and not line.startswith("#"): # if the line is not empty and not starting with #
                entries.append(line) # append the line to the list
    return entries


def domain_in(domain, domains):
    """True if domain is on the list or is a subdomain of a listed domain.
    Example: news.github.com matches github.com."""
    domain = (domain or "").lower().strip(".")
    return any(domain == d or domain.endswith("." + d) for d in domains)


# --------------------------------------------------------------------------- #
# Sensors: reading an .eml file
# --------------------------------------------------------------------------- #
def parse_eml(raw_bytes):
    """Parse raw .eml bytes into a percept dictionary:
    {'sender', 'domain', 'subject', 'text'}.

    'text' combines every readable text part: the body (text/plain or text/html)
    and any text attachments. Each part is decoded from base64 or
    quoted-printable. Binary parts such as images and PDFs are skipped."""
    msg = email.message_from_bytes(raw_bytes, policy=policy.default)
    _, address = parseaddr(str(msg.get("From", "")))
    domain = address.rsplit("@", 1)[1].lower() if "@" in address else ""

    texts = []
    for part in msg.walk():
        if part.is_multipart() or part.get_content_maintype() != "text":
            continue
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        charset = part.get_content_charset() or "utf-8"
        try:
            text = payload.decode(charset, errors="replace")
        except LookupError:  # unknown charset name
            text = payload.decode("utf-8", errors="replace")
        if part.get_content_subtype() == "html":
            text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        texts.append(text)

    return {
        "sender": address.lower(),
        "domain": domain,
        "subject": str(msg.get("Subject", "")),
        "text": "\n".join(texts),
    }


def count_bad_words(text, bad_words):
    """Count every match of a bad-word-list entry in the text. Matching ignores case,
    uses whole words only, and counts repeats ("free free" counts as 2)."""
    text = text.lower()
    total = 0
    for word in bad_words:
        pattern = r"(?<![a-z0-9])" + re.escape(word) + r"(?![a-z0-9])"
        total += len(re.findall(pattern, text))
    return total


# --------------------------------------------------------------------------- #
# The agent: INTERPRET-INPUT + condition-action rules + Figure 2.10 program
# --------------------------------------------------------------------------- #
def make_interpret_input(allow_list, restrict_list, bad_words): # inputs are allowed list, restricted list and bad words
    """INTERPRET-INPUT: turn a raw percept into an abstract state description."""

    def interpret_input(percept):
        if percept is None:
            return {"empty": True}
        info = parse_eml(percept["raw"])
        return {
            "empty": False,
            "domain": info["domain"],
            "allowed": domain_in(info["domain"], allow_list),
            "restricted": domain_in(info["domain"], restrict_list),
            "bad_word_count": count_bad_words(info["text"], bad_words),
        }

    return interpret_input


SPAM_RULES = [
    Rule("inbox empty", lambda s: s["empty"], NO_OP), # if inbox is empty, do nothing
    Rule("allow-listed domain", lambda s: s["allowed"], MOVE_TO_EMAIL), # if domain is allowed, move to email
    Rule("restricted domain", lambda s: s["restricted"], MOVE_TO_SPAM), # if domain is restricted, move to spam
    Rule("too many bad words", lambda s: s["bad_word_count"] > BAD_WORD_THRESHOLD, MOVE_TO_SPAM), # if too many bad words, move to spam
    Rule("default", lambda s: True, MOVE_TO_EMAIL), # default action is to move to email
]


def SpamFilterAgent(allow_list, restrict_list, bad_words): # accepts allowed list, restricted list and bad words
    """Build a simple reflex agent for spam filtering."""
    program = SimpleReflexAgentProgram(
        SPAM_RULES, make_interpret_input(allow_list, restrict_list, bad_words) # creating the agent by passing spam rules and interpret input function
    )
    return Agent(program) # returning the agent


# --------------------------------------------------------------------------- #
# The environment: a mail folder
# --------------------------------------------------------------------------- #
class EmailFile(Thing):
    def __init__(self, path):
        self.path = path
        self.__name__ = os.path.basename(path)


class MailboxEnvironment(Environment):
    """Inbox folder of .eml files plus spam/ and email/ output folders.

    percept(agent)          -> {'filename', 'raw'} for the next unsorted email, or None
    execute_action(a, act)  -> moves (or copies) that email into spam/ or email/
    """

    def __init__(self, inbox_dir, spam_dir, email_dir, move=False):
        super().__init__()
        self.spam_dir, self.email_dir, self.move = spam_dir, email_dir, move
        os.makedirs(spam_dir, exist_ok=True)
        os.makedirs(email_dir, exist_ok=True)
        for name in sorted(os.listdir(inbox_dir)):
            if name.lower().endswith(".eml"):
                self.add_thing(EmailFile(os.path.join(inbox_dir, name))) # adding the email file to the environment
        self.log = []  # (filename, action) for each email handled

    def current_email(self):
        return self.things[0] if self.things else None

    def percept(self, agent):
        item = self.current_email()
        if item is None:
            return None
        with open(item.path, "rb") as f:
            return {"filename": item.__name__, "raw": f.read()}

    def execute_action(self, agent, action):
        item = self.current_email()
        if item is None or action == NO_OP:
            return
        target = self.spam_dir if action == MOVE_TO_SPAM else self.email_dir
        dest = os.path.join(target, item.__name__)
        (shutil.move if self.move else shutil.copy2)(item.path, dest)
        self.things.pop(0)
        self.log.append((item.__name__, action))
        agent.performance += 1

    def is_done(self):
        return not self.things or super().is_done()


def run_filter(inbox, out_dir, allow_path, restrict_path, bad_words_path, move=False):
    """Sort every email in inbox into out_dir/spam and out_dir/email.
    Returns a list of (filename, action) pairs."""
    agent = SpamFilterAgent(load_list(allow_path), load_list(restrict_path), load_list(bad_words_path))
    env = MailboxEnvironment(inbox, os.path.join(out_dir, "spam"), os.path.join(out_dir, "email"), move=move)
    env.add_thing(agent)
    env.run()
    return env.log


def main(argv=None):
    p = argparse.ArgumentParser(description="Simple reflex spam-filter agent") #python standard library for parsing command line arguments
    p.add_argument("--inbox", default=os.path.join(DATA_DIR, "inbox")) #path to inbox directory
    p.add_argument("--out", default=os.path.join(HERE, "output")) #path to output directory
    p.add_argument("--allow", default=os.path.join(DATA_DIR, "allow_list.txt")) #path to allow list
    p.add_argument("--restrict", default=os.path.join(DATA_DIR, "restrict_list.txt")) #path to restrict list
    p.add_argument("--badwords", default=os.path.join(DATA_DIR, "bad_words.txt")) #path to bad words list
    p.add_argument("--move", action="store_true", help="move files instead of copying them")
    args = p.parse_args(argv)

    log = run_filter(args.inbox, args.out, args.allow, args.restrict, args.badwords, args.move)
    for name, action in log:
        print("{:<32} -> {}".format(name, "spam/" if action == MOVE_TO_SPAM else "email/"))
    print("\nSorted {} emails into {}".format(len(log), os.path.abspath(args.out)))


if __name__ == "__main__":
    main()
