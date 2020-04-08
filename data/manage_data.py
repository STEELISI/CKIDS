import re
with open("doc_keys.csv", "r") as f:
    data = [d.strip()[:-1] for d in f.readlines()]
    print(data)
    s = set()
    for string in data:
        s.add(re.sub('\.\d*', '', string, 1))
    print(s)