import string
import textwrap
from typing import Optional, List


def wrap_shift(_key: int) -> int:
    """Returns the wrapped shift"""
    if _key > 25:
        _key = 25
    if _key <= -26:
        _key = -26
    return _key


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
    print("="*15)
    print("=", "This guesser is shit", "=")
    print("=", "Honestly you're better at doing it yourself.", "=")
    print("="*15)
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
        shift = input("Shift (-26 to 26): ")
        try:
            shift = int(shift)
        except ValueError:
            print("Please input a number between -26 and 26.")
        else:
            shift = wrap_shift(shift)
            break

    encoded = shift_word(text, shift)
    print("Encoded text @ %d: %s" % (shift, encoded))


def decode_caesar_shift():
    def find_shift() -> Optional[int]:
        for original_word in encrypted.split():
            original_word = original_word.lower()
            print("[Detecting shift] Original word:", original_word)
            for common_word_inner, common_shifted in common.items():
                if len(common_word_inner) == len(original_word):
                    print("[Detecting shift] Checking shifts on common word:", common_word_inner)
                    for shift_key, shifted_word in enumerate(common_shifted):
                        print(
                            "[Detecting shift] Comparing words %r (%r) and %r."
                            % (shifted_word, common_word_inner, original_word)
                        )
                        if shifted_word.lower().strip() == original_word:
                            print("[Detecting shift] Detected shift on word %r: %d!" % (common_word_inner, shift_key))
                            return shift_key
                    else:
                        print("[Detecting shift] Common word %r not in sentence." % common_word_inner)
        return

    common = {
        "the": [],
        "be": [],
        "and": [],
        "of": [],
        "to": [],
        "in": [],
        "you": [],
        "it": [],
        "me": [],
        "our": [],
        "she": [],
        "her": [],
        "they": [],
        "them": [],
        "cry": [],
        "sorry": [],
        "nexus": [],
        "want": [],
    }
    for common_word in common.keys():
        for shift in range(len(string.ascii_lowercase)):
            common[common_word].append(shift_word(common_word, shift))

    encrypted = input("Encoded text: ").lower().strip()
    encrypted = "".join(let if let in string.ascii_lowercase + " " else "?" for let in encrypted)
    expected_words_original = input("Any expected words? (hit enter for blank): ")
    if expected_words_original:
        expected_words = [x.lower() for x in expected_words_original.split()]
        new_common = {
            word: [shift_word(word, shift) for shift in range(len(string.ascii_lowercase))]
            for word in expected_words
        }
        common = {**new_common, **common}

    key = find_shift()
    if key is not None:
        print("Detected key:", key)
        print("Decoded text:", shift_word(encrypted, -key))
    else:
        print(
            "Failed to automatically detect shift key. Would you like to sift through possible combinations"
            " manually? (This will show you one line at a time with each possible shift)"
        )
        value = input("> ")
        if value.lower().startswith("y") is False:
            print("Cancelling.")
            return
        else:
            first_line = textwrap.shorten(encrypted.splitlines(False)[0], 128, placeholder="")
            for shift_key in range(-len(string.ascii_lowercase), len(string.ascii_lowercase)):
                decoded = shift_word(first_line, shift_key)
                print(" ", decoded, end="\r")
                if input().lower().startswith("y"):
                    print(decoded)
                    print("Encryption key was", shift_key)
                    return


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


while True:
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        break
