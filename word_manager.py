import book_manager as bm
from lxml import etree
import re


def is_continue_word(word):
    if re.findall(r"[\W^ ]|[1-9]", word):
        return True
    if word in ["и", "в", "то", "что", "не", "как", "на", "из", "с", "а", "под", "только", "или", "еще", "да", "от",
                "у", "около", "но", "при", "же", "так", "если", "за", "который", "к", "те", "этот", "этого", "того",
                "чтобы  ", "чтоб", "бы", "по", "ли", "ну", "весь", "вся", "всю"]:
        return True
    if word in ["!", "..."]:
        return True
    if word in ["почти", "быть", "буду", "был", "была", "были"]:
        return True
    return False

def is_pronoun(word):
    return word in ["я", "ты", "он", "она", "вы", "мы", "этот", "тот", "они", "кто-то", "некто", "никто", "все", "это", "себя"]
