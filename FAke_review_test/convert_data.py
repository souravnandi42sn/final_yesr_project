
import json
from json import dump
import codecs

f=codecs.open("data.txt","w","utf-8")

with open("amazon.json") as json_file:
    data=json.load(json_file)
    for i in data[0]["reviews"]:
        extracted_data=str(i["review_text"])
        #extracted_data = str(i["review_text"])
        dump(extracted_data,f,indent=2)
        f.write('\n')
f.close()
print("completed")
"""
filename="hotelDeceptionTest.txt"
with open(filename, 'r', encoding="utf8") as f:
    for line in f:
        print(type(line))
print("below is for after transformation")
filename="data.txt"
with open(filename, 'r', encoding="utf8") as f:
    for line in f:
        print(type(line))
"""
