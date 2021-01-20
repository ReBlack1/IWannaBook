from text_analys.classifiers.classifier import *
from text_analys.mining.tokenizer import Tokenizator


tok = Tokenizator()
word = "человек"
token = tok.get_stat_token_word(word)
classifier = PersonClassifier()
answer = classifier.get_classifier_by_token(token)
print(answer)

