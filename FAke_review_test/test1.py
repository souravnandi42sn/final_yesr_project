import json
flipcart=[]

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


with open("flipcart_review_output.json", "r") as read_file:
    data = json.load(read_file)
    l=data["review"]
    for i in l:
        flipcart.append(remove_html_tags(i))

with open("data2.txt", "w",encoding="utf8") as f:
    for i in flipcart:
        f.writelines(str(i)+"\n")
f.close()