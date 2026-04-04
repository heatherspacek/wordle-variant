from textual.app import App, ComposeResult
# from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, RichLog, Collapsible

from enum import StrEnum
import array
import itertools


Clue = StrEnum("Clue", names="g y n")

BG_SEQ = "\x1b[48;2;{0};{1};{2}m"
FG_SEQ = "\x1b[38;2;{0};{1};{2}m"
CLEANUP = "\x1b[0m"


def fmt_yellow(s):
    return BG_SEQ.format("255", "255", "0") + FG_SEQ.format("0", "0", "255") + f" {s} "


def fmt_white(s):
    return BG_SEQ.format("255", "255", "255") + FG_SEQ.format("22", "22", "22") + f" {s} "


def fmt_green(s):
    return BG_SEQ.format("0", "150", "0") + FG_SEQ.format("255", "222", "255") + f" {s} "


def multifmt(s: str, seq: str):
    ret = ""
    for letter, color in zip(s, seq):
        match color:
            case "y":
                ret += fmt_yellow(letter.upper())
            case "g":
                ret += fmt_green(letter.upper())
            case "n":
                ret += fmt_white(letter.upper())
    ret += CLEANUP
    return ret


def score(word: str, target: str):
    score_result = [Clue.n] * 5
    # Frequency table for "target"
    freq = array.array('b', b'\x00' * 26)
    for b in target.encode():
        freq[b-97] += 1
    # freq = defaultdict(int)
    # for target_letter in target:
    #     freq[target_letter] += 1
    # Green pass
    for i in range(5):
        if word[i] == target[i]:
            score_result[i] = Clue.g
            freq[ord(target[i])-97] -= 1

    # Yellow pass
    for i in range(5):
        if score_result[i] is Clue.n:
            fi = ord(word[i]) - 97
            if freq[fi] > 0:
                score_result[i] = Clue.y
                freq[fi] -= 1

    return score_result


def determine_pool(word, clues, all_words):
    # Find all words that could be solutions, given a particular word and set of clues.
    def equality(c1, c2):
        return (
            c1[0] == c2[0]
            and c1[1] == c2[1]
            and c1[2] == c2[2]
            and c1[3] == c2[3]
            and c1[4] == c2[4]
        )

    eligible_words = [
        w for w in all_words
        if equality(score(word, w), clues)
    ]

    return eligible_words


def compare_pools(word, all_words):
    # Find the largest reduction in the pool that still allows the
    # puzzle to be solved.

    clue_options = itertools.product(*[Clue] * 5)
    pool_sizes = {
        clue_set: len(determine_pool(word, clue_set, all_words))
        for clue_set in clue_options
    }
    return pool_sizes


def play(pool_sizes: dict, turn: int):
    # given computed pool sizes, choose a suitable narrowing-of-pool and
    # issue clues.
    cluesets_by_value = sorted(pool_sizes.keys(), key=lambda k: pool_sizes[k])
    cluesets_viable = list(filter(lambda x: pool_sizes[x] > turn, cluesets_by_value))
    if len(cluesets_viable) < 1:
        # The game is "lost" at this point-- not enough words to finish
        return "ggggg"
    midpoint = len(cluesets_viable) // 2
    return cluesets_viable[midpoint]


class Letter(Static):
    DEFAULT_CSS = """
Letter {
    width: 5;
    height: 3;
    border: $secondary round;
    content-align: center middle;
}
Letter.green {
  background: green;
  color: white;
}
Letter.yellow {
  background: yellow;
  color: black;
}
Letter.white {
  background: white;
  color: black;
}
"""


TITLE_ART = """\
░██████╗░██████╗░██╗░░░██╗░█████╗░███╗░░██╗██████╗░██╗░░░░░███████╗
██╔════╝██╔═══██╗██║░░░██║██╔══██╗████╗░██║██╔══██╗██║░░░░░██╔════╝
╚█████╗░██║██╗██║██║░░░██║███████║██╔██╗██║██║░░██║██║░░░░░█████╗░░
░╚═══██╗╚██████╔╝██║░░░██║██╔══██║██║╚████║██║░░██║██║░░░░░██╔══╝░░
██████╔╝░╚═██╔═╝░╚██████╔╝██║░░██║██║░╚███║██████╔╝███████╗███████╗
╚═════╝░░░░╚═╝░░░░╚═════╝░╚═╝░░╚═╝╚═╝░░╚══╝╚═════╝░╚══════╝╚══════╝\
"""


class GameApp(App):

    DEFAULT_CSS = """\
* {
    align: center top;
}
#title {
    content-align: center top;
}
#main-container {
    height:18;
}
    """

    wordpool = []
    loaded_guess = []
    guess_n = 0

    def compose(self) -> ComposeResult:
        yield Static(TITLE_ART, id="title")
        with Collapsible(title="Rules"):
            yield Static("Be yourself and have fun.")
        # yield RichLog()
        with Vertical(id="main-container"):
            for row_n in range(6):
                with Horizontal(id=f"horz-{row_n}"):
                    for _ in range(5):
                        yield Letter(" ")

    def on_key(self, ev):
        if ev.key == "backspace":
            if len(self.loaded_guess) > 0:
                _ = self.loaded_guess.pop()
        elif ev.key == "enter":
            self.notify("you clicked enter 😳")
        elif ev.character and ev.character.lower() in "abcdefghijklmniopqrstuvwxyz":
            if len(self.loaded_guess) < 5:
                self.loaded_guess.append(ev.character.lower())
                self.query_one(Letter).update(ev.character.upper())
                # self.query_one(Letter).add_class("green")

        for i, letter_widget in enumerate(self.query("#horz-0 Letter").results()):
            if i >= len(self.loaded_guess):
                letter_widget.update(" ")
            else:
                letter_widget.update(self.loaded_guess[i].upper())


if __name__ == "__main__":

    # with open("data/answers.txt") as f:
    #     answer_words = f.read().splitlines()
    # with open("data/guesses.txt") as f:
    #     legal_but_not_answer_words = f.read().splitlines()
    # all_words = sorted(answer_words + legal_but_not_answer_words)

    # prev_guesses = []
    # words_pool = all_words
    # for turn in range(6, 0, -1):
    #     while True:
    #         guess = input(">")
    #         if guess in all_words and guess not in prev_guesses:
    #             prev_guesses += guess
    #             break
    #     poolz = compare_pools(guess, words_pool)
    #     clueset = play(poolz, turn)
    #     words_pool = determine_pool(guess, clueset, words_pool)
    #     print(multifmt(guess, clueset), f"Remaining: {len(words_pool)}")

    app = GameApp()
    app.run()
