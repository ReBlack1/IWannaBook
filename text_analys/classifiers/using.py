from text_analys.classifiers.classifier import *
from text_analys.mining.tokenizer import Tokenizator


tok = Tokenizator()
word = "подонок"
token = tok.get_stat_token_word(word)
classifier = CruelClassifier()
answer = classifier.get_classifier_by_token(token)
print(answer)

