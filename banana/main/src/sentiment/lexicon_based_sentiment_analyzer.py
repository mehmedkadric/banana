from nltk.tokenize import WhitespaceTokenizer
from unidecode import unidecode


def analyze(txt):
    tokenizer = WhitespaceTokenizer()
    tokenized_txt = tokenizer.tokenize(txt)

    positive_count = count_positive(tokenized_txt)
    negative_count = count_negative(tokenized_txt)
    diff = positive_count - negative_count
    sentiment_score = round(diff / len(tokenized_txt), 2)
    # print(sentiment_score)
    threshold = 0.0
    if sentiment_score > threshold:
        return "Positive"
    elif sentiment_score < -threshold:
        return "Negative"
    else:
        return "Neutral"


def token_counter(path, tokenized_txt):
    lexicon_tokens = []
    with open(path) as f:
        for line in f:
            lexicon_tokens.append(unidecode(line.strip().lower()))
    # counter of lexicon tokens
    cnt = 0

    for token in tokenized_txt:
        if unidecode(token.lower()) in lexicon_tokens:
            cnt += 1
    return cnt


def count_positive(tokenized_txt):
    return token_counter("/Users/mehmed/Desktop/banana/banana/media/lexicons/ba/positive_words_bs.txt", tokenized_txt)


def count_negative(tokenized_txt):
    return token_counter("/Users/mehmed/Desktop/banana/banana/media/lexicons/ba/negative_words_bs.txt", tokenized_txt)

