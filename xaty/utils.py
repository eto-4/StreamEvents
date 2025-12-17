# xaty/utils.py
import re
from django import forms

BAD_WORDS = ['puta', 'idiota', 'merda']

def contains_bad_words(msg):
    msg_lower = msg.lower()
    
    for word in BAD_WORDS:
        pattern = rf'\b{re.escape(word)}\b'
        if re.search(pattern, msg_lower):
            return True
    return False

def empty_message(msg):
    if not msg:
        return False
    return True

def outof_length_range(msg):
    if len(msg) > 500:
        return True
    return False