import random

import pytest
from main import shift_word

arguments = []

with open("words.txt") as words_file:
    for _n, line in enumerate(words_file.readlines()):
        arguments.append((line.strip(), _n))

arguments = random.sample(arguments, 1000)


@pytest.mark.parametrize("word,n", arguments)
def test_shift_word(word: str, n: int):
    if n % 26 == 0:
        n = 0
    word = word.lower()
    shifted = shift_word(word, n).lower()
    if n == 0:
        assert word == shifted, "No shift was performed but got shifted word: %r -> %r." % (word, shifted)
    else:
        assert word != shifted, "Shift was performed but the shift of %d didn't actually do anything: %r -> %r" % (
            n, word, shifted
        )
