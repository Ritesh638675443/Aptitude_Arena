import json
import os
import re
from datetime import date


@__import__("functools").lru_cache(maxsize=1)
def load_questions():
    path = os.path.join(os.path.dirname(__file__), "data", "readysetscores_complete.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fix_math(text):
    if not text:
        return text
    text = re.sub(r'\\\[', '$$', text)
    text = re.sub(r'\\\]', '$$', text)
    text = re.sub(r'\\\(', '$', text)
    text = re.sub(r'\\\)', '$', text)
    return text


def clean_question(text):
    text = text.strip()
    n = len(text)
    for offset in range(-20, 21):
        mid = n // 2 + offset
        if mid <= 0 or mid >= n:
            continue
        first = text[:mid].strip()
        second = text[mid:].strip()
        if first == second:
            text = first
            break
    return fix_math(text)


def clean_text(text):
    return fix_math(text.strip()) if text else text


def get_rank(xp):
    if xp >= 5000: return "🏆 Champion"
    if xp >= 2000: return "⚡ Master"
    if xp >= 1000: return "🌟 Expert"
    if xp >= 400:  return "🚀 Achiever"
    if xp >= 100:  return "🔍 Explorer"
    return "🌱 Beginner"
