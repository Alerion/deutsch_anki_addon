from .enums import Gender, SpeachPart

RED = "#c12d30"

DER_TEXT = '<span style="color: #2a74ff; font-weight: bold;">der</span>&nbsp;'
DIE_TEXT = '<span style="color: #fd6d85; font-weight: bold;">die</span>&nbsp;'
DAS_TEXT = '<span style="color: #00aa00; font-weight: bold;">das</span>&nbsp;'

NOUN_TEXT = '<span style="color: #3d405b;"><b>NOUN</b></span>'
VERB_TEXT = '<span style="color: #e07a5f;"><b>VERB</b></span>'
ADJECTIVE_TEXT = '<span style="color: #81b29a;"><b>ADJECTIVE</b></span>'
ADVERB_TEXT = '<span style="color: #d68c45;"><b>ADVERB</b></span>'
PRONOMEN_TEXT = '<span style="color: #98c1d9;"><b>PRONOUN</b></span>'
JUNKTION_TEXT = '<span style="color: #333;"><b>JUNKTION</b></span>'
NUMBER_TEXT = '<span style="color: #333;"><b>NUMBER</b></span>'
PLURAL_TEXT = '<span style="color: #333;"><b>PLURAL</b></span>'


SPEACH_PART_TO_TEXT = {
    SpeachPart.NOUN: NOUN_TEXT,
    SpeachPart.VERB: VERB_TEXT,
    SpeachPart.ADVERB: ADVERB_TEXT,
    SpeachPart.ADJECTIVE: ADJECTIVE_TEXT,
    SpeachPart.PRONOUN: PRONOMEN_TEXT,
    SpeachPart.JUNKTION: JUNKTION_TEXT,
    SpeachPart.NUMBER: NUMBER_TEXT,
    SpeachPart.PLURAL: PLURAL_TEXT,
}

GENDER_TO_TEXT = {
    Gender.MALE: DER_TEXT,
    Gender.FEMALE: DIE_TEXT,
    Gender.NEUTRAL: DAS_TEXT,
}

GENDER_TO_ARTICLE = {
    Gender.MALE: "der",
    Gender.FEMALE: "die",
    Gender.NEUTRAL: "das",
}


def bold(text: str) -> str:
    return f'<span style="font-weight: bold;">{text}</span>'


def italic(text: str) -> str:
    return f'<span style="font-style: italic;">{text}</span>'
