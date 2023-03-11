slugs = {
    "а": "a", "б": "b", "в": "v", "г": "g",
    "д": "d", "е": "e", "ё": "yo", "ж": "zh",
    "з": "z", "и": "i", "й": "y", "к": "k",
    "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t",
    "у": "u", "ф": "f", "х": "h", "ц": "c",
    "ч": "ch", "ш": "sh", "щ": "sh", "ы": "i",
    "э": "e", "ю": "yu", "я": "ya", "-": "_", " ": "_"
}


def genSlug(value: str):
    value = value.lower()
    newSlug = ""
    for i in value:
        newSlug += slugs[i]
    return newSlug
