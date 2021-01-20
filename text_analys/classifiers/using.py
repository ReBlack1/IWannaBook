from text_analys.classifiers.classifier import CruelClassifier
from text_analys.mining.tokenizer import Tokenizator


tok = Tokenizator()
word = "сук"
token = tok.get_stat_token_word(word)
classifier = CruelClassifier()
answer = classifier.get_classifier_by_token(token)
print(answer)

