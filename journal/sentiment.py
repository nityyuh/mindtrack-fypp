from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()

def analyse_sentiment(text):
    scores = analyser.polarity_scores(text)
    compound = scores['compound']

    stress_keywords = [
        "stress", "stressed", "stressful", "anxious",
        "anxiety", "nervous", "overwhelmed", "pressure",
        "worried", "panic", "tense", "burnout", "drained",
        "exhausted"
    ]

    negative_keywords = [
        "sad", "down", "upset", "angry", "frustrated", "annoyed",
        "lonely", "tired", "isolated", "hopeless", "unmotivated", 
        "low", "crying", "miserable"
    ]

    positive_keywords = [
        "happy", "excited", "exciting", "calm", 
        "peaceful", "relaxed", "relieved", "grateful",
        "thankful", "motivated", "productive", "good", "great",
        "better", "amazing"
    ]

    text_lower = text.lower()
    words = text_lower.split()

    stress_count = sum(word in words for word in stress_keywords)
    negative_count = sum(word in words for word in negative_keywords)
    positive_count = sum(word in words for word in positive_keywords)

    compound -= 0.08 * stress_count
    compound -= 0.05 * negative_count
    compound += 0.05 * positive_count
    
    compound = max(min(compound, 1),-1)

    if compound >= 0.2:
        label = 'positive'
    elif compound <= -0.2:
        label = 'negative'
    else:
        label = 'neutral'
    
    return label,compound
    