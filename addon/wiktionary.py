import re
from dataclasses import dataclass

import requests

from .enums import Gender, SpeachPart


@dataclass
class Page:
    page_id: int
    full_url: str


# https://www.mediawiki.org/wiki/API:Query
SEARCH_URL = "https://de.wiktionary.org/w/api.php"
HEADERS = {"User-Agent": "AnkiAddonBot https://github.com/Alerion/anki-de-translation-addon"}


def find_word_page(word: str) -> Page | None:
    params = {
        "action": "query",
        "format": "json",
        "prop": "info",
        "inprop": "url",
        "titles": word,
    }
    response = requests.get(SEARCH_URL, params, headers=HEADERS).json()
    pages = response["query"]["pages"]
    if not pages:
        return None

    page_item = list(pages.values())[0]

    return Page(
        page_id=page_item["pageid"],
        full_url=page_item["fullurl"],
    )


# https://www.mediawiki.org/wiki/API:Parsing_wikitext
PAGE_URL = "https://de.wiktionary.org/w/api.php"


def get_page_wikitext(page_id: int) -> str:
    params = {
        "action": "parse",
        "format": "json",
        "prop": "wikitext",
        "pageid": page_id,
    }
    response = requests.get(PAGE_URL, params, headers=HEADERS).json()
    wikitext = response["parse"]["wikitext"]["*"]
    assert isinstance(wikitext, str)
    return wikitext


# https://www.mediawiki.org/wiki/API:Parsing_wikitext
FILES_URL = "https://de.wiktionary.org/w/api.php"


def get_file_url(file_name: str) -> str | None:
    params = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "iiprop": "url",
        "titles": f"File:{file_name}",
    }
    response = requests.get(FILES_URL, params, headers=HEADERS).json()
    pages = list(response["query"]["pages"].values())
    imageinfo = pages[0]["imageinfo"][0]
    image_url = imageinfo["url"]
    assert isinstance(image_url, str)
    return image_url


AUDIO_RE = re.compile(r"\{\{Audio\|(?P<file>.*?)(|spr=(?P<spr>at))?\}\}")


def get_best_audio_match(matches: list[re.Match[str]]) -> str | None:
    """
    Return latest one withou specified language. It has the best audio quality.
    """
    for match in reversed(matches):
        if match.group("spr") is not None:
            continue
        file_name = match.group("file")
        if file_name.startswith("De-"):
            return file_name

    if matches:
        return matches[0].group("file")
    return None


AUSSPRACHE_RE = re.compile(r"\{\{Aussprache\}\}(?P<aussprache>.*?)\n\{\{[^{]+\}\}", re.DOTALL)


def get_audio_url_from_wikitext(wikitext: str) -> str | None:
    match = AUSSPRACHE_RE.search(wikitext)
    if not match:
        return None

    matches = list(AUDIO_RE.finditer(match.group("aussprache")))

    if not matches:
        return None
    audio_file_name = get_best_audio_match(matches)
    if not audio_file_name:
        return None

    audio_file_url = get_file_url(audio_file_name)
    if not audio_file_url:
        print(f"Audio file URL was not found for file: {audio_file_name}")
        return None
    return audio_file_url


IPA_RE = re.compile(r"\{\{Lautschrift\|(.*?)\}\}")


def get_ipa_from_wikitext(wikitext: str) -> str | None:
    matches: list[str] = IPA_RE.findall(wikitext)

    if not matches:
        return None
    return matches[0]


SPEECH_PART_RE = re.compile(
    r"\{\{Wortart\|(?P<part>\w+)\|Deutsch\}\}(, +\{\{(?P<gender>f|m|n)\}\})?"
)
KEIN_SINGULAR = "{{kSg.}}"


def get_speach_part_from_wikitext(wikitext: str) -> SpeachPart | None:
    matches = list(SPEECH_PART_RE.finditer(wikitext))
    if not matches:
        return None
    speech_part_match = matches[0].group("part")
    if speech_part_match == "Substantiv":
        if KEIN_SINGULAR in wikitext:
            return SpeachPart.PLURAL
        return SpeachPart.NOUN
    if speech_part_match == "Verb":
        return SpeachPart.VERB
    if speech_part_match == "Adjektiv":
        return SpeachPart.ADJECTIVE
    if speech_part_match == "Lokaladverb":
        return SpeachPart.ADVERB
    if speech_part_match == "Personalpronomen":
        return SpeachPart.PRONOUN
    return None


GENDER_RE = re.compile(r"Genus( \d)?=(?P<gender>f|m|n)")


def get_gender_from_wikitext(wikitext: str) -> Gender | None:
    matches = list(GENDER_RE.finditer(wikitext))
    speech_part_match = matches[0].group("gender")

    if speech_part_match == "m":
        return Gender.MALE
    if speech_part_match == "f":
        return Gender.FEMALE
    if speech_part_match == "n":
        return Gender.NEUTRAL
    return None


PLURAL_RE = re.compile(r"Nominativ Plural(?: 1)?=(?P<plural>\w+)")


def get_plural_from_wikitext(wikitext: str) -> str | None:
    matches = list(PLURAL_RE.finditer(wikitext))
    if not matches:
        return None
    return matches[0].group("plural")


GENITIVE_RE = re.compile(r"Genitiv Singular(?: 1)?=(?P<genitive>\w+)")


def get_genitive_from_wikitext(wikitext: str) -> str | None:
    matches = list(GENITIVE_RE.finditer(wikitext))
    if not matches:
        return None
    return matches[0].group("genitive")


REF_RE = re.compile(r"<ref[^>]*>.*?</ref>")
EXAMPLE_RE = re.compile(r"\{\{Beispiele\}\}(?P<examples>.*?)\n\{\{[^{]+\}\}", re.DOTALL)


def get_examples_from_wikitext(wikitext: str) -> list[str]:
    match = EXAMPLE_RE.search(wikitext)
    if not match:
        return []
    example_text = match.group("examples")
    examples = re.split(r"\n(?=:)", example_text)

    output = []
    for example in examples:
        example = re.sub(r":\[[\w ,–]+\]", "", example)
        example = example.replace("\n", "")
        example = REF_RE.sub("", example)
        example = example.strip()
        example = example.strip("„“=\n»«")
        if not example or example.startswith("::Anneliese") or len(example) > 150:
            continue

        example = re.sub(r"''(.*?)''", r"<b>\1</b>", example)
        output.append(example)

    return output[:5]


HELP_VERB_RE = re.compile(r"Hilfsverb=(?P<help_verb>\w+)")


def get_help_verb_from_wikitext(wikitext: str) -> str | None:
    matches = list(HELP_VERB_RE.finditer(wikitext))
    if not matches:
        return None
    return matches[0].group("help_verb")


PRATERITUM_RE = re.compile(r"Präteritum_ich=(?P<prateritum>[\w ]+)")


def get_prateritum_from_wikitext(wikitext: str) -> str | None:
    matches = list(PRATERITUM_RE.finditer(wikitext))
    if not matches:
        return None
    return matches[0].group("prateritum")


PARTIZIP2_RE = re.compile(r"Partizip II=(?P<partizip2>[\w ]+)")


def get_partizip2_from_wikitext(wikitext: str) -> str | None:
    matches = list(PARTIZIP2_RE.finditer(wikitext))
    if not matches:
        return None
    return matches[0].group("partizip2")
