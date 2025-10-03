import re
from collections import Counter
from nltk.corpus import stopwords

# Example text (Replace with your competitor's page text)
text = """Seattle web design agency creating high-performance, SEO-optimized websites for businesses. Custom development, branding & digital marketing."""

# Remove punctuation & split words
words = re.findall(r'\b\w+\b', text.lower())

# Load common stopwords
stop_words = set(stopwords.words("english"))

# Filter words (remove stop words)
filtered_words = [word for word in words if word not in stop_words]

# Count keyword frequency
keyword_counts = Counter(filtered_words)

# Print most common keywords
print(keyword_counts.most_common(10))
