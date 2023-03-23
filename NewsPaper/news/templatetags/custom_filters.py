from django import template

register = template.Library()

BANNED_WORDS = [
    'game',
    'Kombat',
]

@register.filter()
def censor(text: str):
    if type(text) is not str:
        raise ValueError('censor filter works only with type "str"')

    for word in BANNED_WORDS:
        text = text.replace(word, f"{word[0]}{'*'*(len(word)-1)}")
        word = word.title()
        text = text.replace(word, f"{word[0]}{'*'*(len(word)-1)}")
    return text