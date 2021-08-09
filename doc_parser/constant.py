# Regex patterns constants
import re

PATTERN_EDUCATION = re.compile(r"^Education ?$")
PATTERN_EXPERIENCE = re.compile(r"^Experience ?$")
PATTERN_PARENTHESES = re.compile(r"\(")
PATTERN_NUMBER = re.compile(r"^\d")
PATTERN_PAGE = re.compile(r"Page")
PATTERN_YEAR = re.compile(r"^\d{4}")
PATTERN_PRESENT_POSITION = re.compile(r"^Present ?")
PATTERN_SYMBOL_NO_LEFT_SPACE = re.compile(r"^[,\)\.:;]$")
PATTERN_SYMBOL_NO_SPACES = re.compile(r"^[\/]$")
PATTERN_SYMBOL_NO_SPACES2 = re.compile(r"^[\/-]$")
PATTERN_SYMBOL_NO_RIGHT_SPACE = re.compile(r"^\($")
PATTERN_MONTH_TEXT = re.compile(r"months?$", re.I)
PATTERN_YEAR_TEXT = re.compile(r"years?", re.I)
PATTERN_MONTH = re.compile(r"^(?:January|February|March|April|May|June|July|August|September|October|November|December)$")
PATTERN_EMAIL = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PATTERN_PHONE_NUMBER = re.compile(r"(\+?370\ ?6|86)\d{2}\ ?\d{5}")
PATTERN_LANGUAGES = re.compile(r"Languages")
PATTERN_TOP_SKILS = re.compile(r"Top Skills")
PATTERN_URL_START = re.compile(r"^www")
PATTERN_MID_DOT = re.compile(r"^·$")

