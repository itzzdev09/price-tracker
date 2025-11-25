import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
import nltk

# Download NLTK stopwords (only first time)
nltk.download('stopwords')
from nltk.corpus import stopwords

# -------------------------------------------
# 1. WEB MINING → SCRAPE NEWS HEADLINES
# -------------------------------------------
URL = "https://www.hindustantimes.com/latest-news"
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

# Collect all headlines
headlines = [h.text.strip() for h in soup.find_all("h3")]

print("=== SCRAPED HEADLINES ===")
for h in headlines:
    print("-", h)

# -------------------------------------------
# 2. TEXT MINING → CLEANING & TOKENIZATION
# -------------------------------------------
text = " ".join(headlines)  # combine all headlines

# Clean text
text = re.sub(r"[^A-Za-z ]", " ", text).lower()
words = text.split()

# Remove stopwords
stop_words = set(stopwords.words("english"))
filtered_words = [w for w in words if w not in stop_words and len(w) > 2]

# -------------------------------------------
# 3. TEXT ANALYTICS → WORD FREQUENCY
# -------------------------------------------
freq = Counter(filtered_words)
top_words = freq.most_common(10)

print("\n=== TOP KEYWORDS (TEXT MINING) ===")
for word, count in top_words:
    print(f"{word}: {count}")

