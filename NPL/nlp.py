import re
import string

# Função para garantir o download das stopwords
def get_stopwords(language='portuguese'):
    try:
        from nltk.corpus import stopwords
        return set(stopwords.words(language))
    except LookupError:
        import nltk
        nltk.download('stopwords')
        from nltk.corpus import stopwords
        return set(stopwords.words(language))

# Função principal de pré-processamento
def preprocess_tweet(
    text,
    language='portuguese',
    use_stemming=True,
    keep_hashtags=False
):
    # 1. Stopwords
    STOPWORDS = get_stopwords(language)
    # 2. Remove emojis
    text = text.encode('ascii', 'ignore').decode('ascii')
    # 3. Normalização de caixa
    text = text.lower()
    # 4. Remover URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    # 5. Extrair hashtags se necessário
    hashtags = re.findall(r'#(\w+)', text) if keep_hashtags else []
    # 6. Remover menções e hashtags do texto
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    # 7. Remover "RT" (retweets)
    text = re.sub(r'\brt\b', '', text)
    # 8. Remover pontuação e números
    text = text.translate(str.maketrans('', '', string.punctuation + string.digits))
    # 9. Remover espaços extras
    text = re.sub(r'\s+', ' ', text).strip()
    # 10. Tokenização
    tokens = text.split()
    # 11. Normalizar repetições de letras (ex: "amoooo" -> "amoo")
    tokens = [re.sub(r'(.)\1{2,}', r'\1\1', word) for word in tokens]
    # 12. Remover stopwords
    tokens = [word for word in tokens if word not in STOPWORDS]
    # 13. Stemming (opcional)
    if use_stemming and language == 'portuguese':
        try:
            from nltk.stem import RSLPStemmer
            stemmer = RSLPStemmer()
            tokens = [stemmer.stem(word) for word in tokens]
        except LookupError:
            import nltk
            nltk.download('rslp')
            from nltk.stem import RSLPStemmer
            stemmer = RSLPStemmer()
            tokens = [stemmer.stem(word) for word in tokens]
    # 14. Adiciona hashtags como tokens se necessário
    if keep_hashtags:
        tokens.extend(hashtags)
    return tokens

# Exemplo de uso
if __name__ == "__main__":
    tweets = [
        "RT @usuario: O TweetFinder é #incrível! Veja em https://github.com #busca",
        "Amei o novo recurso do TweetFinder!!! 😍😍 #top #busca",
        "RT RT RT Muito bom esse sistema, parabéns equipe!!! @amigo"
    ]

# Para uma lista de tweets hipotética
    for i, tweet in enumerate(tweets):
        tokens = preprocess_tweet(tweet, keep_hashtags=True)
        print(f"Tweet {i}: {tokens}")
