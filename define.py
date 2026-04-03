import tqdm
import json
import subprocess

with open("data/guesses.txt") as f:
    answer_words = f.read().splitlines()

defined_words = []

for aw in tqdm.tqdm(answer_words):
    subp = subprocess.run(
        [
            "curl",
            f"https://freedictionaryapi.com/api/v1/entries/en/{aw}"
        ],
        capture_output=True
    )
    result = json.loads(subp.stdout)
    try:
        defn = result["entries"][0]["senses"][0]["definition"]
    except (KeyError, IndexError):
        defn = "<freedictionaryapi.com could not provide a definition.>"

    defined_words += f"{aw}     {defn}\n"

with open("data/guesses_and_defs.txt", 'w') as f2:
    f2.writelines(defined_words)
