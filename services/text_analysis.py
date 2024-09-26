import logging
from collections import Counter
import re
from wordcloud import WordCloud
import io
import base64
from typing import List, Tuple
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
import math
from transformers import pipeline

logger = logging.getLogger(__name__)

sentiment_analyzer = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment")

nltk_resources = ['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
for resource in nltk_resources:
    try:
        nltk.data.find(f'tokenizers/{resource}')
    except LookupError:
        print(f"Downloading {resource}")
        nltk.download(resource, quiet=True)

def analyze_text(text: str) -> dict:
    preprocessed_text = preprocess_text(text)
    words = preprocessed_text.split()
    sentences = sent_tokenize(text)
    
    statistics = {
        'char_count': len(text),
        'word_count': len(words),
        'sentence_count': len(sentences),
        'average_word_length': calculate_average_word_length(words),
        'average_sentence_length': len(words) / len(sentences) if sentences else 0,
        'lexical_diversity': calculate_lexical_diversity(words),
        'readability_score': calculate_readability_score(text),
        'sentiment_score': analyze_sentiment(text),
    }
    
    keywords = get_keywords(text)
    word_cloud = generate_word_cloud(preprocessed_text)
    
    return {
        'statistics': statistics,
        'keywords': keywords,
        'word_cloud': word_cloud
    }

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-zA-Zа-яА-Я\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def calculate_average_word_length(words: List[str]) -> float:
    return sum(len(word) for word in words) / len(words) if words else 0

def calculate_lexical_diversity(words: List[str]) -> float:
    return len(set(words)) / len(words) if words else 0

def calculate_readability_score(text: str) -> float:
    words = text.split()
    sentences = sent_tokenize(text)
    if not words or not sentences:
        return 0
    avg_sentence_length = len(words) / len(sentences)
    avg_syllables_per_word = sum(count_syllables(word) for word in words) / len(words)
    return 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word

def count_syllables(word: str) -> int:
    word = word.lower()
    count = 0
    vowels = 'aeiouyаеёиоуыэюя'
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith('e'):
        count -= 1
    if word.endswith('le'):
        count += 1
    if count == 0:
        count += 1
    return count

def analyze_sentiment(text: str) -> float:
    result = sentiment_analyzer(text[:512])[0]  # Ограничиваем длину текста
    if result['label'] == 'POSITIVE':
        return result['score']
    elif result['label'] == 'NEGATIVE':
        return -result['score']
    else:
        return 0.0

def extract_nouns(text: str) -> List[str]:
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    nouns = [word.lower() for word, pos in tagged if pos.startswith('NN') and len(word) > 2]
    return nouns

def get_keywords(text: str, top_n: int = 10) -> List[Tuple[str, float]]:
    preprocessed_text = preprocess_text(text)
    words = extract_nouns(preprocessed_text)
    words = [word for word in words if word.isalpha() and len(word) > 2]
    
    word_freq = Counter(words)
    total_words = sum(word_freq.values())
    
    word_tf = {word: count / total_words for word, count in word_freq.items()}
    
    return sorted(word_tf.items(), key=lambda x: x[1], reverse=True)[:top_n]

def generate_word_cloud(text: str) -> str:
    logger.info("Generating word cloud")
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    img_buffer = io.BytesIO()
    wordcloud.to_image().save(img_buffer, format='PNG')
    img_buffer.seek(0)
    encoded_image = base64.b64encode(img_buffer.getvalue()).decode()
    logger.info(f"Word cloud image generated, size: {len(encoded_image)} bytes")
    return encoded_image