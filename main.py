from enum import StrEnum
import itertools
from collections import defaultdict


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


def score(word, target):
    score_result = [Clue.n] * 5
    # Frequency table
    freq = defaultdict(int)
    for target_letter in target:
        freq[target_letter] += 1

    # Green pass
    for i in range(5):
        if word[i] == target[i]:
            score_result[i] = Clue.g
            freq[target[i]] -= 1

    # Yellow pass
    intersection = set(word) & set(target)
    for i, w_letter in enumerate(word):
        if (w_letter in intersection) and score_result[i] == Clue.n and freq[w_letter] > 0:
            score_result[i] = Clue.y

    return score_result


def determine_pool(word, clues, all_words):
    # Find all words that could be solutions, given a particular word and set of clues.
    def equality(c1, c2):
        return all([ca == cb for ca, cb in zip(c1, c2)])

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
    ...


if __name__ == "__main__":

    with open("data/answers.txt") as f:
        answer_words = f.read().splitlines()
    with open("data/guesses.txt") as f:
        legal_but_not_answer_words = f.read().splitlines()
    all_words = sorted(answer_words + legal_but_not_answer_words)

    # while True:
    #     word = input("start word > ")
    #     clues = input("clues: >")
    #     print(multifmt(word, clues))
    #     pool = determine_pool(word, clues, all_words)
    #     print("Pool has: ", len(pool))
    #     print(", ".join(pool))

    word = "stoat"
    compare_pools(word, all_words)

    # breakpoint()
