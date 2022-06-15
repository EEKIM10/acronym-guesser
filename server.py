import os
import subprocess

import fastapi
import uvicorn
import random
import secrets
import string
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fastapi import Query, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from main import do_shift, wrap_shift, shift_word


sec = HTTPBasic()


def load_words(extra_words: Optional[str] = None) -> Dict[str, List[str]]:
    common = {}
    if extra_words is not None:
        for word in extra_words.split(" "):
            common[word] = []
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

    if default_words.exists():
        with default_words.open() as common_words_file:
            for line in common_words_file.readlines():
                line = line.lower().strip()
                common[line] = []
    for common_word in common.keys():
        for shift in range(len(string.ascii_lowercase)):
            common[common_word].append(shift_word(common_word, shift))
    return common


def encode_caesar_shift(text: str, shift: int):
    if shift == 1337:
        return ultra_encode_caesar_shift(text)

    encoded = shift_word(text, shift)
    return encoded, []


def ultra_encode_caesar_shift(text: str):
    resolved = ""
    keys = []
    for word in text.split(" "):
        random_number = random.randint(1, 26)
        resolved += shift_word(word, random_number) + " "
        keys.append(random_number)
    resolved = resolved[:-1]
    return resolved, keys


def authorise(credentials: HTTPBasicCredentials = Depends(sec)):
    if credentials.username == "nex":
        if secrets.compare_digest(credentials.password, os.getenv("HTTP_PASSWORD", "your mum x")):
            return True
    raise HTTPException(
        401,
        "Invalid username or password",
        {
            "WWW-Authenticate": "Basic realm=\"Global\""
        }
    )


app = fastapi.FastAPI(dependencies=[Depends(authorise)])


@app.post("/encrypt")
def encode(text: str = fastapi.Form(...), shift: int = fastapi.Form(...,), keys: bool = fastapi.Form(False)):
    encoded, _keys = encode_caesar_shift(text, shift)
    if keys:
        return {
            "encoded": encoded,
            "keys": _keys or [wrap_shift(shift)]
        }
    return {
        "encoded": encoded,
    }


@app.post("/decrypt")
def decode(text: str = fastapi.Form(...), words: str = fastapi.Form(None), key: int = fastapi.Form(None)):
    if key is not None:
        return {
            "key": key,
            "decoded": shift_word(text, 26-key),
            "reason": "Key is already known"
        }
    common = load_words(words)

    def find_shift() -> Optional[Tuple[int, str, str, str]]:
        for original_word in text.split():
            original_word = original_word.lower()
            for common_word_inner, common_shifted in common.items():
                if len(common_word_inner) == len(original_word):
                    for _shift_key, shifted_word in enumerate(common_shifted):
                        if shifted_word.lower().strip() == original_word:
                            return _shift_key, common_word_inner, shifted_word, original_word
        return

    shift_key = find_shift()
    if shift_key is not None:
        return {
            "key": shift_key[0],
            "decoded": shift_word(text, 26-shift_key[0]),
            "reason": "%s (%s) matched %r" % (shift_key[1:])
        }
    raise HTTPException(
        400,
        "Unable to detect a shift."
    )


app.mount(
    "/",
    StaticFiles(
        directory="./html/out",
        html=True
    ),
    "static"
)


if __name__ == "__main__":
    uvicorn.run(app)
