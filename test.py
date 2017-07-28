from google.cloud import language

client = language.Client()
text = "I love nature"
document = client.document_from_text(text)
sentiment_response = document.analyze_sentiment()
sentiment = sentiment_response.sentiment
print(sentiment.score)
