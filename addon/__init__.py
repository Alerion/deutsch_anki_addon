"""
`setFormat` triggers one of these commands:

https://developer.mozilla.org/en-US/docs/Web/API/document/execCommand
"""

import os.path
import sys
from functools import partial
from typing import Any, Callable

# Inject external dependencies.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "./dependencies"))

import aqt.editor
from aqt import gui_hooks

from .card_html import (
    ADJECTIVE_TEXT,
    ADVERB_TEXT,
    DER_TEXT,
    DIE_TEXT,
    NOUN_TEXT,
    PRONOMEN_TEXT,
    RED,
    VERB_TEXT,
)
from .shortcut_actions.insert_audio_action import insert_audio
from .shortcut_actions.insert_word_description_action import insert_word_description


def change_color(editor: aqt.editor.Editor, color: str, bold: bool = False) -> None:
    editor.web.eval("setFormat('removeFormat')")
    if bold:
        editor.web.eval("setFormat('bold')")

    editor.web.eval(f"setFormat('forecolor', '{color}')")


def insert_template(editor: aqt.editor.Editor) -> None:
    html = "<h2>word</h2>[ipa]"
    editor.web.eval(f"setFormat('insertHTML', '{html}')")


def insert_der(editor: aqt.editor.Editor) -> None:
    editor.web.eval(f"setFormat('insertHTML', '{DER_TEXT}')")


def insert_die(editor: aqt.editor.Editor) -> None:
    editor.web.eval(f"setFormat('insertHTML', '{DIE_TEXT}')")


def insert_das(editor: aqt.editor.Editor) -> None:
    editor.web.eval(f"setFormat('insertHTML', '{DER_TEXT}')")


def insert_noun(editor: aqt.editor.Editor) -> None:
    editor.web.eval(f"setFormat('insertHTML', '{NOUN_TEXT}')")


def insert_verb(editor: aqt.editor.Editor) -> None:
    editor.web.eval(f"setFormat('insertHTML', '{VERB_TEXT}')")


def insert_adjective(editor: aqt.editor.Editor) -> None:
    editor.web.eval(f"setFormat('insertHTML', '{ADJECTIVE_TEXT}')")


def insert_adverb(editor: aqt.editor.Editor) -> None:
    editor.web.eval(f"setFormat('insertHTML', '{ADVERB_TEXT}')")


def insert_pronoun(editor: aqt.editor.Editor) -> None:
    editor.web.eval(f"setFormat('insertHTML', '{PRONOMEN_TEXT}')")


type ShortcutCallback = Callable[[Any], None]


def add_shortcuts(shortcuts: list[tuple[str, ShortcutCallback]], editor: aqt.editor.Editor) -> None:
    shortcuts.append(("F1", partial(insert_word_description, editor)))
    # For edit page. F1 does not work.
    shortcuts.append(("F12", partial(insert_word_description, editor)))
    shortcuts.append(("F2", partial(insert_der, editor)))
    shortcuts.append(("F3", partial(insert_die, editor)))
    shortcuts.append(("F4", partial(insert_das, editor)))

    shortcuts.append(("F5", partial(change_color, editor, RED, bold=True)))

    shortcuts.append(("F6", partial(insert_noun, editor)))
    shortcuts.append(("F7", partial(insert_verb, editor)))
    shortcuts.append(("F8", partial(insert_adjective, editor)))
    shortcuts.append(("F9", partial(insert_adverb, editor)))
    shortcuts.append(("F10", partial(insert_pronoun, editor)))
    shortcuts.append(("Alt+F1", partial(insert_audio, editor)))


# https://addon-docs.ankiweb.net/hooks-and-filters.html
gui_hooks.editor_did_init_shortcuts.append(add_shortcuts)
