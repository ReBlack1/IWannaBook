from text_analys.classifiers.classifier import *
from text_analys.mining.tokenizer import Tokenizator


text = """
13-летняя Омайра Санчес стала жертвой трагедии: ее тело застряло в обломках здания,
в результате девочка трое суток простояла по шею в грязи. Ее лицо опухло, руки стали практически белыми,
а глаза налились кровью
"""
text = text.replace(',', '')
text = text.replace('.', '')
words = text.split()
tok = Tokenizator()
classifier = EmotionalClassifier()
for word in words:
    token = tok.get_stat_token_word(word)
    answer = classifier.get_classifier_by_token(token)
    print(word, " : ", answer)
