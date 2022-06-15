import random
import string
import sys
import textwrap
import os
from pathlib import Path
from typing import Optional


def wrap_shift(_key: int) -> int:
    """Returns the wrapped shift"""
    new_key = 0
    for _ in range(_key):
        new_key += 1
        if new_key > 25:
            new_key = 0
        elif new_key < 0:
            new_key = 0

    return new_key


def do_shift(_key: int) -> str:
    """
    Just shifts the alphabet by the given key

    :param _key: The amount to move - negative for left-shift, positive for right shift
    :return: the shifted alphabet
    """
    _key = wrap_shift(_key)
    result = string.ascii_lowercase[_key:] + string.ascii_lowercase[:_key]
    return result


shifts = []
for i in range(len(string.ascii_lowercase)):
    shifts.append(do_shift(i))


def shift_word(word: str, _key: int) -> str:
    """
    Performs a caesar shift.

    :param word: The word (or phrase) to shift
    :param _key: The key by which to shift
    :return: The encrypted word
    """
    word = word.lower().strip()
    _key = wrap_shift(_key)
    org_al = string.ascii_lowercase
    alphabet = shifts[_key]
    new = ""
    for letter in list(word):
        if letter not in alphabet:
            new += letter
            continue
        index = org_al.index(letter.lower())
        new += alphabet[index]
    return new


def acronym():
    print("=" * 15)
    print("=", "This guesser is shit", "=")
    print("=", "Honestly you're better at doing it yourself.", "=")
    print("=" * 15)
    decoded = ""
    with open("./words.txt") as file:
        all_words = [word.lower().strip() for word in file.readlines()]
        _acronym = input("Acronym: ")
        for letter in _acronym:
            previous_word = None
            for word in all_words:
                if "'" in word:
                    continue
                if not word.lower().startswith(letter.lower()):
                    continue
                print(" ", decoded, word, end="\r")
                _n = input().lower().strip()
                if _n.startswith("y"):
                    decoded += " " + word
                    break
                elif _n == "back":
                    decoded += " " + previous_word
                    break
                else:
                    previous_word = word
                    continue
            else:
                decoded += " [%s]" % letter

    print(decoded)


def encode_caesar_shift():
    text = input("Text to encode: ")
    while True:
        shift = input("Shift (-26 to 26, or blank for random): ")
        try:
            shift = int(shift or str(int(os.urandom(1).hex(), base=16)))
        except ValueError:
            print("Please input a number between -26 and 26.")
        else:
            if shift == 1337:
                return ultra_encode_caesar_shift(text)
            shift = wrap_shift(shift)
            break

    encoded = shift_word(text, shift)
    print("Encoded text @ %d: %s" % (shift, encoded))


def ultra_encode_caesar_shift(text: str):
    resolved = ""
    keys = []
    for word in text.split(" "):
        random_number = random.randint(-26, 26)
        resolved += shift_word(word, random_number) + " "
        keys.append(random_number)
    resolved = resolved[:-1]
    if sys.stdout.isatty():
        print("Encoded text: %s" % resolved)
        print("Encryption Keys: %s" % " ".join(str(n) for n in keys))
    return resolved, keys


def decode_caesar_shift():
    def manual_search():
        print(
            "Failed to automatically detect shift key. Would you like to sift through possible combinations"
            " manually? (This will show you one line at a time with each possible shift)"
        )
        value = input("> ")
        if value.lower().startswith("y") is False:
            print("Cancelling.")
            return
        else:
            print("This will print the first line of each possible shift.")
            print("If it looks like the shift has decoded correctly, type y and hit enter.")
            print("If it does not look correct, press enter to move on to the next shift.")
            first_line = textwrap.shorten(encrypted.splitlines(False)[0], 128, placeholder="")
            for shift_key in range(-len(string.ascii_lowercase), len(string.ascii_lowercase)):
                decoded = shift_word(first_line, shift_key)
                print(" ", decoded, end="\r")
                if input().lower().startswith("y"):
                    print(decoded)
                    print("Encryption key was", shift_key)
                    return
            else:
                print("That's all the possible combinations!")

    def find_shift() -> Optional[int]:
        for original_word in encrypted.split():
            original_word = original_word.lower()
            print("[Detecting shift] Original word:", original_word)
            for common_word_inner, common_shifted in common.items():
                if len(common_word_inner) == len(original_word):
                    print("[Detecting shift] Checking shifts on common word:", common_word_inner)
                    for _shift_key, shifted_word in enumerate(common_shifted):
                        print(
                            "[Detecting shift] Comparing words %r (%r) and %r."
                            % (shifted_word, common_word_inner, original_word)
                        )
                        if shifted_word.lower().strip() == original_word:
                            print("[Detecting shift] Detected shift on word %r: %d!" % (common_word_inner, _shift_key))
                            return _shift_key
                    else:
                        print("[Detecting shift] Common word %r not in sentence." % common_word_inner)
        return

    common = {}
    here = Path(__file__).parent
    # Add user custom words first
    default_words = here / "default_words.txt"
    user_words = here / "custom_words.txt"
    if user_words.exists():
        with user_words.open() as common_user_words_file:
            for line in common_user_words_file.readlines():
                line = line.lower().strip()
                if not line or line.startswith("#"):
                    continue
                common[line] = []
        print("Loaded user words file (custom_words.txt)")
    else:
        print("No user words found. If you would like to curate what the program looks for (to make automatic "
              "decryption more accurate), create a file called 'custom_words.txt' and write whatever words you want"
              " on each line. (note: lines starting with # are ignored)")

    if not default_words.exists():
        print(
            "Failed to load default common words (default_words.txt) as the file does not exist."
            " Please make sure you've supplied some custom words, otherwise automatic decryption will not work."
        )
    else:
        with default_words.open() as common_words_file:
            for line in common_words_file.readlines():
                line = line.lower().strip()
                common[line] = []
    for common_word in common.keys():
        for shift in range(len(string.ascii_lowercase)):
            common[common_word].append(shift_word(common_word, shift))

    print(
        "Loaded {:,} common words with {:,} total shifted common words.".format(
            len(common), sum(map(lambda x: len(x), common.values()))
        )
    )

    encrypted = input("Encoded text: ").lower().strip()
    encrypted = "".join(let if let in string.ascii_lowercase + " " else "?" for let in encrypted)
    expected_words_original = input("Any expected words? (hit enter for blank): ")
    if expected_words_original:
        expected_words = [x.lower() for x in expected_words_original.split()]
        new_common = {
            word: [shift_word(word, shift) for shift in range(len(string.ascii_lowercase))] for word in expected_words
        }
        common = {**new_common, **common}

    key = find_shift()
    if key is not None:
        print("Detected key:", key)
        print("Decoded text:", shift_word(encrypted, -key))
        if input("Does this look correct? [Y/n] ").lower().startswith("n"):
            manual_search()
    else:
        manual_search()


def menu():
    while True:
        options = [acronym, encode_caesar_shift, decode_caesar_shift]
        for n, func in enumerate(options):
            print(f"%d. %s" % (n, func.__name__.replace("_", " ")))
        v = input("> ")
        try:
            v = int(v)
            assert v in range(len(options))
        except ValueError:
            print("Please input a number.")
        except AssertionError:
            print("Please input a valid number.")
        else:
            print()
            try:
                options[v]()
            except KeyboardInterrupt:
                print("%r interrupted." % options[v].__name__)
            else:
                print("%r finished." % options[v].__name__)
            print()


if __name__ == "__main__":
    while True:
        try:
            menu()
        except (KeyboardInterrupt, EOFError):
            break
