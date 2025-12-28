from enum import Enum


class SpeachPart(str, Enum):
    NOUN = "NOUN"
    VERB = "VERB"
    ADJECTIVE = "ADJECTIVE"
    ADVERB = "ADVERB"
    PRONOUN = "PRONOUN"
    NUMBER = "NUMBER"
    JUNKTION = "JUNKTION"
    PLURAL = "PLURAL"


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    NEUTRAL = "NEUTRAL"
