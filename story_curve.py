import re

import altair as alt
import bottleneck as bn
import numpy as np
import pandas as pd

w_tmp = pd.read_csv('labMTwordsEn-english.csv', header=None)
s_tmp = pd.read_csv('labMTscores-english.csv', header=None)
w_tmp.columns = ['word']
s_tmp.columns = ['score']

word_sentiment_s = pd.concat([w_tmp, s_tmp], axis=1).set_index('word')['score']
# word_sentiment_s = pd.read_csv('AFINN-en-165.txt', delimiter='\t', header=None).set_index(0)[1]


def story_curve(story, n=None):
    def is_empty(s):
        return (s == '') or str.isspace(s)

    def stutter(counts):
        return np.concatenate([np.tile(c, c) for c in counts])

    def sentiment_score(word):
        return word_sentiment_s.loc[word] if word in word_sentiment_s else 0

    def mean_abs_sentiment(sentiment):
        return np.mean(np.abs(sentiment))

    story = story.replace('’', "'")
    ipara = 0
    words = []
    for p in re.split('\n', story):
        if is_empty(p):
            continue
        ipara += 1
        isent = 0
        for sentence in re.split('\.|!|\?', p):
            if is_empty(sentence):
                continue
            isent += 1
            words.extend([(ipara, isent, w) for w in re.split(' |—', sentence.lower().translate(
                str.maketrans('', '', '"#$%&\()*+,-/:;<=>@[\\]^_`{|}~“”'))) if w != ''])

    df = pd.DataFrame(data=words, columns=['paragraph', 'sentence', 'word'])
    df['pos'] = df.index.values
    df['len'] = df['word'].str.len()

    df['words_per_sentence'] = stutter(df.groupby(['paragraph', 'sentence'])['word'].count())
    df['words_per_paragraph'] = stutter(df.groupby('paragraph')['word'].count())
    df['sentiment'] = [sentiment_score(word) for word in df['word']]
    df['sentiment'] -= df['sentiment'].mean()
    mas = mean_abs_sentiment(df['sentiment'])
    df['sentiment_s'] = df['sentiment'] / mas

    if n is None:
        n = max(1, int(len(df) / 6))

    df_ = pd.DataFrame(
        {'sentiment': bn.move_mean(df['sentiment_s'], window=n, min_count=n)[n - 1:],
         # 'abs_sent': bn.move_mean(df['sentiment_s'].abs(), window=n, min_count=n)[n - 1:],
         # 'word_len': bn.move_mean(df['len'], window=n, min_count=n)[n - 1:],
         # 'words_p_sent': bn.move_mean(df['words_per_sentence'], window=n, min_count=n)[n - 1:],
         # 'words_p_para': bn.move_mean(df['words_per_paragraph'], window=n, min_count=n)[n - 1:]
         })
    df_['word'] = df_.index
    
    return mas, df_, n


def make_viz(df, n):
    # df = pd.DataFrame(data={'sentiment': sentiment,
    #                         'word':  np.arange(0, len(sentiment), int(n/10))})
    line = alt.Chart(df.loc[::int(n/10)]).mark_line().encode(x='word', y='sentiment').properties(
        width=737,
        height=400)
    # points = alt.Chart(df).mark_point().encode(x='word', y='sentiment')
    # chart = line + points
    return line.to_dict()
