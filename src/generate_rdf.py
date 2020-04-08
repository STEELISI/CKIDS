# in creator.name:
#   - replace . with " "
#   - Split by , to get 1 author. Eg: Doe, John > John Doe, Copeland, Edwin Bingham -> Edwin Bingham Copeland
#   - handle initials and "," and combine it to the same name. Eg: Conelin, G. E. -> G E Conelin
#   - Split by , to get multiple authors. Eg: Nitin Arora1, Nikhil Srivastava2, Sai Sagar Peri3, Sumit Kumar4 & Alaknanda Ashok5
#   - Split by &/and.. to get multiple authors with same affiliation
#   - find and remove numbers. Eg: Sanjeev Kumar Dwivedi*1 and Ankur Singh Bist2 -> Sanjeev Kumar Dwivedi, Ankur Singh Bist
#   - find and remove special characters. Eg: Sanjeev Kumar Dwivedi*1 -> Sanjeev Kumar Dwivedi
#   - handle symbols in different languages. Eg: (Rivera, César), (Brandtzæg, Petter), (Krpo-Ćetković, Jasmina), (Radujković, Branko M.), (Šundić, Danijela)
#   - remove Ms., Mrs., Mr. etc. 
#     Keep Dr. etc.
#   - handle multiple languages. Eg: डा ॅ0 भावना ग्रोवर दुआ
#   - handle HTML tags in place of string
#   - handle placeholder names. Eg: Ancient Indian and Tibetian scholars
#   - handle NULL entries. Eg: &Na;, &Na;


# to parse human names
from nameparser import HumanName

n = HumanName("Conelin, G. E.")
# <HumanName : [
# 	title: ''
# 	first: 'G.'
# 	middle: 'E.'
# 	last: 'Conelin'
# 	suffix: ''
# 	nickname: ''
# ]>


# to parse organization addresses
from postal.parser import parse_address

parse_address('College of Cybersecurity, Sichuan University, Chengdu 610065, China')
# [('college of cybersecurity sichuan university', 'house'), ('chengdu', 'city'), ('610065', 'postcode'), ('china', 'country')]


# to generate a hash based on name
import hashlib
s = "Fang Yong"
hash_value = int(hashlib.md5(s.encode('utf-8')).hexdigest(), 16)
hash_value = hashlib.sha224(s.encode('utf-8')).hexdigest()