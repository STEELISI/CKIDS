import requests
from configparser import ConfigParser
import json
import pandas as pd
# Keyword Filter, to count the frequency of each keyword and get rid of the common keywords


# Read old kw list
kw = pd.read_csv('v2_CKIDS_keywords.csv', header=None)


config = ConfigParser()
config.read('secrets.ini')
API_ROOT = config['ZENODO_API']['API_ROOT']
ACCESS_KEY = config['ZENODO_API']['ACCESS_TOKEN']

lines = []
for word in kw[0]:
    params = {
        "page": '1',
        "size": '1',
        'q': word,
        'access_token': ACCESS_KEY
    }
    res = requests.get(
        url=API_ROOT + 'records/', params=params)
    # To read the count only
    raw = res.json()
    count = 0
    # If hits
    if raw.get("hits"):
        count = raw["hits"].get("total",0)
    line = (count, word)
    lines.append(line)

# Sort and put lines into a csv folder
lines.sort(reverse=True)
kw2 = pd.DataFrame(lines,columns=['Frequency', 'Word'])
kw2.to_csv('v3_CKIDS_keywords_with_frequency.csv')

# old--brush keywords list
# keyword_data = pd.read_csv('v3_CKIDS_keywords_with_frequency.csv', index_col=0)
# def process_term_list(term_list):
#     term_list2 = []
#     for t in term_list:
#         # remove hyphens
#         if '-' in t:
#             term_list2 += [t.replace('-', ' ')]
#         # separate terms with brackets
#         elif "(" and ")" in t:
#             tt = t.split("(")
#             if tt[0] == '':
#                 term_list2 += [tt[1].replace(")","")]
#             term_list2 += [tt[0].rstrip(" "), tt[1].replace(")","")]
#         else:
#             term_list2 += [t]
#     return term_list2
# term_list = process_term_list(keyword_data['Word'].unique())
# term_list = set(term_list)
# term_list.discard('')
# term_list = sorted(list(term_list))