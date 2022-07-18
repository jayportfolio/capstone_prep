from collections import Counter, defaultdict

import nltk
import pandas as pd
from nltk import trigrams

from globalfunction import vv

import pandas as pd
from collections import Counter
from itertools import chain
import wordcloud

data = [
    {"sentence": "Run with dogs, or shoes, or dogs and shoes"},
    {"sentence": "Run without dogs, or without shoes, or without dogs or shoes"},
    {"sentence": "Hold this while I finish writing the python script"},
    {"sentence": "Is this python script written yet, hey, hold this"},
    {"sentence": "Can dogs write python, or a python script?"},
]


def find_ngrams(input_list, n):
    return list(zip(*[input_list[i:] for i in range(n)]))


# df = pd.DataFrame.from_records(data)
df = pd.read_csv(vv.LISTING_ENRICHED_FILE)
df = df[['bullet_points', 'long_description']]
df.dropna(inplace=True)
print(df.head())
df['content'] = df['bullet_points'] + df['long_description']

stop_words = list(wordcloud.STOPWORDS)
stop_words.extend([
    '','-'
])

def get_gram(n, most_frequent=40):
    df['bigrams'] = df['content'].map(lambda x: find_ngrams(x.split(" "), 2))

    # Bigram Frequency Counts
    bigrams = df['bigrams'].tolist()
    print(1, len(bigrams))
    bigrams = list(chain(*bigrams))
    print(2, len(bigrams))
    bigrams = [(x.lower(), y.lower()) for x, y in bigrams]
    print(3, len(bigrams))
    bigrams = [(a, b) for (a, b) in bigrams if a not in stop_words and b not in stop_words]
    print(4, len(bigrams))

    bigram_counts = Counter(bigrams)
    print()
    #print("\n".join(bigram_counts.most_common(40)))
    for each in bigram_counts.most_common(most_frequent):
        print(each)
    return bigram_counts.most_common(most_frequent)

#quit()

df['trigrams'] = df['content'].map(lambda x: find_ngrams(x.split(" "), 3))

# trigram Frequency Counts
trigrams = df['trigrams'].tolist()
print(1, len(trigrams))
trigrams = list(chain(*trigrams))
print(2, len(trigrams))
trigrams = [(x.lower(), y.lower(), z.lower()) for x, y, z in trigrams]
print(3, len(trigrams))
trigrams = [(a, b, c) for (a, b, c) in trigrams if a not in stop_words and b not in stop_words and c not in stop_words]
print(4, len(trigrams))

trigram_counts = Counter(trigrams)
print()
#print("\n".join(trigram_counts.most_common(40)))
for each in trigram_counts.most_common(40):
    print(each)

quit()

data = [
    {"sentence": "Run with dogs, or shoes, or dogs and shoes"},
    {"sentence": "Run without dogs, or without shoes, or without dogs or shoes"},
    {"sentence": "Hold this while I finish writing the python script"},
    {"sentence": "Is this python script written yet, hey, hold this"},
    {"sentence": "Can dogs write python, or a python script?"},
]


def find_ngrams(input_list, n):
    return list(zip(*[input_list[i:] for i in range(n)]))


df = pd.DataFrame.from_records(data)
df['bigrams'] = df['sentence'].map(lambda x: find_ngrams(x.split(" "), 3))
print(df.head())

# Bigram Frequency Counts
bigrams = df['bigrams'].tolist()
bigrams = list(chain(*bigrams))
bigrams = [(x.lower(), y.lower()) for x, y in bigrams]

bigram_counts = Counter(bigrams)
print()
print(bigram_counts.most_common(10))

# [(('dogs,', 'or'), 2),
# (('shoes,', 'or'), 2),
# (('or', 'without'), 2),
# (('hold', 'this'), 2),
# (('python', 'script'), 2),
# (('run', 'with'), 1),
# (('with', 'dogs,'), 1),
# (('or', 'shoes,'), 1),
# (('or', 'dogs'), 1),
# (('dogs', 'and'), 1)]
quit()

sentence = """At eight o'clock on Thursday morning
... Arthur didn't feel very good."""
tokens = nltk.word_tokenize(sentence)
tokens
# ['At', 'eight', "o'clock", 'on', 'Thursday', 'morning',
# 'Arthur', 'did', "n't", 'feel', 'very', 'good', '.']
tagged = nltk.pos_tag(tokens)
tagged[0:6]


# [('At', 'IN'), ('eight', 'CD'), ("o'clock", 'JJ'), ('on', 'IN'),
# ('Thursday', 'NNP'), ('morning', 'NN')]


def train_trigram(lst):
    model = defaultdict(lambda: defaultdict(lambda: 0))
    for sent in lst:
        sent = sent.split()
        for w1, w2, w3 in trigrams(sent, pad_right=True, pad_left=True):
            model[(w1, w2)][w2] += 1
    total_count = 0
    for w1, w2 in model:
        total_count = float(sum(model[(w1, w2)].values()))
        for w3 in model[(w1, w2)]:
            model[(w1, w2)][w3] /= total_count


# Total Sum Of Trigram Probablity Of A Sentence[Returns Float]:


def trigram_counts(word_list):
    tgs = nltk.trigrams(word_list)
    fdist = nltk.FreqDist(tgs)
    d = Counter()
    for k, v in fdist.items():
        d[k] = v
    return d


print(train_trigram(sentence))
trigram_counts(sentence)

df = pd.read_csv(vv.LISTING_ENRICHED_FILE)


def CreateCorpusFromDataFrame(corpusfolder, df):
    for index, r in df.iterrows():
        id = r['bedrooms']
        title = r['bullet_points']
        body = r['long_description']
        category = r['type']
        fname = str(category) + '_' + str(id) + '.txt'
        corpusfile = open(corpusfolder + '/' + fname, 'a')
        corpusfile.write(str(body) + " " + str(title))
        corpusfile.close()


CreateCorpusFromDataFrame('yourcorpusfolder/', df)
print('fin')
