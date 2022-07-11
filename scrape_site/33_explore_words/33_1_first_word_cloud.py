# Python program to generate WordCloud

# importing all necessary modules
import json

from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pd


import sys

sys.path.append('../../globalfunction')  # setting path
import globalfunction.vv as vv  # importing

# Reads 'Youtube04-Eminem.csv' file
#df = pd.read_csv(r"Youtube04-Eminem.csv", encoding="latin-1")
df = pd.read_csv(vv.LISTING_ENRICHED_FILE, encoding="latin-1")

df['CONTENT'] = df['bullet_points'] + df['long_description']
#quit()

comment_words = ''
stopwords = set(STOPWORDS)

stopwords.add('property')
stopwords.update(['offer','make','benefit','range','please','sale','need','use',
                  'give','help','guide price','offer','â','purchase',
                  'order','home','book','ensure','may','buy','note','tested',
                  'well','enjoy','confirm','brochure'
                  ])
#stopwords.update(['svg','camera','sold stc','stc','brochure'
#                  'read','read more','read morea','offer'],'floorplan','purchase')

# iterate through the csv file
for val in df.CONTENT:

    # typecaste each val to string
    val = str(val)

    # split the value
    tokens = val.split()

    # Converts each token into lowercase
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()

    comment_words += " ".join(tokens) + " "

wordcloud = WordCloud(width=800, height=800,
                      background_color='white',
                      stopwords=stopwords,
                      #min_word_length=5,
                      normalize_plurals=True,
                      min_font_size=10).generate(comment_words)

# plot the WordCloud image
plt.figure(figsize=(8, 8), facecolor=None)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad=0)

plt.show()

print(df.columns)

#print(wordcloud.process_text())
wordcloud_words = wordcloud.words_
print(wordcloud_words)


def write_json_pretty(convert_file, data):
    convert_file.write(json.dumps(data, indent=4))


with open(vv.WORDCLOUD_FILE, 'w') as convert_file:
    write_json_pretty(convert_file, wordcloud_words)
