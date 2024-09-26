import re
from collections import Counter
from typing import List, Tuple
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import io
import base64

# Загрузка стоп-слов
nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('russian'))

def preprocess_text(text: str) -> str:
    """Предобработка текста: приведение к нижнему регистру и удаление знаков препинания."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text

def remove_stop_words(text: str) -> str:
    """Удаление стоп-слов из текста."""
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]
    return ' '.join(filtered_words)

def get_keywords(text: str, top_n: int = 10) -> List[Tuple[str, float]]:
    """Извлечение ключевых слов с использованием модели из Hugging Face."""
    keyword_extractor = pipeline("feature-extraction", model="distilbert-base-multilingual-cased")
    preprocessed_text = remove_stop_words(preprocess_text(text))
    
    # Извлечение признаков
    features = keyword_extractor(preprocessed_text)
    
    # Преобразование признаков в словарь слово-значение
    word_scores = {word: score.mean() for word, score in zip(preprocessed_text.split(), features[0])}
    
    # Сортировка слов по значению и выбор top_n
    return sorted(word_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

def get_text_statistics(text: str) -> dict:
    """Подсчет статистики текста: количество символов и слов."""
    return {
        'char_count': len(text),
        'word_count': len(text.split())
    }

def generate_word_cloud(text: str) -> str:
    """Генерация облака слов и возврат его в виде строки base64."""
    preprocessed_text = remove_stop_words(preprocess_text(text))
    
    wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=100).generate(preprocessed_text)
    
    # Сохранение изображения в буфер
    img_buffer = io.BytesIO()
    wordcloud.to_image().save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Кодирование изображения в base64
    return base64.b64encode(img_buffer.getvalue()).decode()

def analyze_text(text: str) -> dict:
    """Анализ текста: ключевые слова, статистика и облако слов."""
    keywords = get_keywords(text)
    stats = get_text_statistics(text)
    word_cloud = generate_word_cloud(text)
    
    return {
        'keywords': keywords,
        'statistics': stats,
        'word_cloud': word_cloud
    }

# Пример использования:
if __name__ == "__main__":
    sample_text = """
    Искусственный интеллект - это область информатики, которая занимается созданием интеллектуальных машин, 
    работающих и реагирующих подобно людям. Некоторые из основных видов деятельности, связанных с ИИ, включают 
    распознавание речи, обучение, планирование и решение проблем. Машинное обучение является ключевой 
    технологией в развитии искусственного интеллекта, позволяя системам автоматически улучшаться на основе опыта.
    """
    
    analysis_result = analyze_text(sample_text)
    
    print("Ключевые слова:")
    for word, score in analysis_result['keywords']:
        print(f"{word}: {score:.4f}")
    
    print("\nСтатистика текста:")
    for key, value in analysis_result['statistics'].items():
        print(f"{key}: {value}")
    
    print("\nОблако слов сгенерировано и доступно в формате base64")
    # В реальном приложении вы бы использовали analysis_result['word_cloud'] для отображения изображения