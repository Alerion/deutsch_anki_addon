import re

import aqt.editor
from aqt import mw
from aqt.utils import showInfo

from .. import wiktionary
from ..ai.explain_word import ExplainWordResponse, explain_word_with_ai
from ..card_html import (
    GENDER_TO_ARTICLE,
    GENDER_TO_TEXT,
    SPEACH_PART_TO_TEXT,
    bold,
    italic,
)
from ..enums import SpeachPart


def insert_word_description(editor: aqt.editor.Editor) -> None:
    config = mw.addonManager.getConfig(__name__)
    if config is None:
        showInfo("Config is not available")
        return

    if editor.note is None:
        showInfo("No note found in editor")
        return

    clipboard = editor.mw.app.clipboard()
    if clipboard is None:
        showInfo("Clipboard is not available")
        return

    word = clipboard.text().strip()
    word_to_translate = word

    if not word:
        showInfo("No word found in clipboard")
        return

    page = wiktionary.find_word_page(word)
    if not page:
        showInfo(f"Page not found for word '{word}'")
        return

    wikitext = wiktionary.get_page_wikitext(page.page_id)
    if not wikitext:
        showInfo(f"No wikitext found for: {word}")
        return

    # Set speech part into Info.
    speech_part = wiktionary.get_speach_part_from_wikitext(wikitext)
    if speech_part in SPEACH_PART_TO_TEXT:
        editor.note["Info"] = SPEACH_PART_TO_TEXT[speech_part]

    editor.note["Front"] = ""
    editor.note["Example"] = ""

    explain_word_with_ai_response: ExplainWordResponse = explain_word_with_ai(word, speech_part)

    # Add translation.
    if not editor.note["Back"].strip():
        editor.note["Back"] = _generate_back(explain_word_with_ai_response)

    # NOUN
    article_text = ""
    if speech_part == SpeachPart.NOUN:
        # Set article.
        gender = wiktionary.get_gender_from_wikitext(wikitext)
        if gender:
            article_text = GENDER_TO_TEXT[gender]
            word_to_translate = f"{GENDER_TO_ARTICLE[gender]} {word_to_translate}"

        # Set Example field.
        plural = wiktionary.get_plural_from_wikitext(wikitext)
        genitive = wiktionary.get_genitive_from_wikitext(wikitext)
        editor.note["Example"] = (
            f'<span class="plural-label">plural:</span>'
            f'&nbsp;<span class="plural-value">{plural or "-"}</span>'
            f'&nbsp;<span class="genitive-label">genitive:</span>'
            f'&nbsp;<span class="genitive-value">{genitive}</span>'
        )

    if speech_part == SpeachPart.VERB:
        # Add word forms.
        prateritum = wiktionary.get_prateritum_from_wikitext(wikitext)
        partizip2 = wiktionary.get_partizip2_from_wikitext(wikitext)
        editor.note["Example"] = (
            f'<span class="prateritum-label">Präteritum:</span>'
            f'&nbsp;<span class="prateritum-value">{prateritum}</span>'
            f'&nbsp;<span class="partizip2-label">Partizip II:</span>'
            f'&nbsp;<span class="partizip2-value">{partizip2}</span>'
        )

        # Add help verb.
        help_verb = wiktionary.get_help_verb_from_wikitext(wikitext)
        if help_verb == "sein":
            editor.note["Example"] += (
                f'&nbsp;<span class="hilfsverb-label">Hilfsverb:</span>'
                f'&nbsp;<span class="hilfsverb-value">{help_verb}</span>'
            )

    # Add examples.
    editor.note["Example"] += '<ul class="examples">'
    for usage_example in explain_word_with_ai_response.usage_examples:
        editor.note["Example"] += f"<li>{usage_example}</li>"
    editor.note["Example"] += "</ul>"

    # Add synonyms.
    if explain_word_with_ai_response.synonyms:
        editor.note["Example"] += (
            '<span class="synonyms-label">Синоніми:</span><ul class="synonyms-list">'
        )
        for synonym in explain_word_with_ai_response.synonyms:
            editor.note["Example"] += (
                f"<li>{bold(synonym.word)} - {italic(synonym.difference)}</li>"
            )
        editor.note["Example"] += "</ul>"

    # Add additional info.
    if explain_word_with_ai_response.additional_info:
        editor.note["Example"] += (
            '<span class="additional-info-label">Додаткова інформація:</span>'
            '<ul class="additional-info-list">'
        )
        for info in explain_word_with_ai_response.additional_info:
            editor.note["Example"] += f"<li>{info}</li>"
        editor.note["Example"] += "</ul>"

    # Add Wiktionary URL.
    editor.note["Example"] += f'<a href="{page.full_url}">{page.full_url}</a>'

    editor.set_note(editor.note)

    # Load IPA
    ipa = wiktionary.get_ipa_from_wikitext(wikitext)

    # Insert word
    html = f"<h2>{article_text}{word.strip()}</h2>[{ipa}]"
    editor.web.eval(f"setFormat('insertHTML', '{html}')")

    # Insert audio
    audio_url = wiktionary.get_audio_url_from_wikitext(wikitext)
    if audio_url:
        audio_url = f"\n{audio_url}"
        clipboard.setText(audio_url)
        # Trigger audio paste, so Anki can replace with proper tag.
        editor.onPaste()
        clipboard.setText(word)
    else:
        showInfo(f"Audio file was not found for: {word}")

    # Get selected text.
    # def callback(*args, **kwargs):
    #     print(args, kwargs)
    # editor.web.evalWithCallback("window.getSelection().toString()", callback)


def _generate_back(explain_word_with_ai_response: ExplainWordResponse) -> str:
    back = _format_text_with_parentheses(explain_word_with_ai_response.ukrainian_translation)

    if explain_word_with_ai_response.additional_context:
        back += f"<br>{italic(explain_word_with_ai_response.additional_context)}"

    return back


def _format_text_with_parentheses(text: str) -> str:
    parts = re.split(r"(\([^)]+\))", text)

    result = []
    for part in parts:
        if part.startswith("("):
            result.append(part)
        elif part.strip():
            result.append(bold(part))

    return "".join(result)
