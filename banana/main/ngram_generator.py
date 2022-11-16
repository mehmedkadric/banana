import nltk
import pandas as pd
import psycopg2
from nltk import ngrams


if __name__ == "__main__":
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="mehmed",
        password="")

    sql = "SELECT comment_content FROM main_comment;"
    dat = pd.read_sql_query(sql, conn)
    i = 0

    for comment in dat["comment_content"]:
        NGRAMS = ngrams(sequence=nltk.word_tokenize(comment), n=2)
        for grams in NGRAMS:
            print(grams)
        i = i + 1
        if i == 10:
            break