import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords

# Download stopwords only when they aren't already present
try:
    stopwords.words("english")
except LookupError:
    nltk.download("stopwords")

# -------------------------------------------
# 1. WEB MINING → SCRAPE QUOTES
# -------------------------------------------
URL = "https://quotes.toscrape.com/"
response = requests.get(URL, timeout=30)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

quotes = [q.text.strip() for q in soup.find_all("span", class_="text")]

print("=== SCRAPED QUOTES ===")
for q in quotes:
    print("-", q)

# -------------------------------------------
# 2. TEXT MINING → CLEANING
# -------------------------------------------
text = " ".join(quotes).lower()
text = re.sub(r"[^a-z ]", " ", text)
words = text.split()

stop_words = set(stopwords.words("english"))
filtered = [w for w in words if w not in stop_words and len(w) > 2]

# -------------------------------------------
# 3. TEXT MINING → FIND KEYWORDS
# -------------------------------------------
freq = Counter(filtered)
top_words = freq.most_common(10)

print("\n=== TOP KEYWORDS ===")
for word, count in top_words:
    print(f"{word}: {count}")
