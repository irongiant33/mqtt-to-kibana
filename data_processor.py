import re

def remove_strings_within_square_brackets(payload):
    filtered_text = re.sub(r'\[[^\[\]]*\]', '', payload)
    return filtered_text

def split_words_on_whitespace(payload):
    words = re.split(r'\s+', payload)
    non_empty_words = [word for word in words if len(word) > 0]
    return non_empty_words
