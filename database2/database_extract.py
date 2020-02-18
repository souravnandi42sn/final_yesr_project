import json,csv
from collections import defaultdict
flipcart=[]
amazon=[]
flipcart_predict=[]
amazon_predict=[]
amazon_rating=[]
flipcart_most_buyed_prduct_details=[]
def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def getdata():

    with open("flipcart_review_output.json", "r") as read_file:
        data = json.load(read_file)
        l=data["review"]
        for i in l:
            flipcart.append(remove_html_tags(i))

    with open("amazon.json","r") as read_file:
        data=json.load(read_file)
        for i in data[0]["reviews"]:
            amazon.append(i["review_text"])
            amazon_rating.append(int(float(i["review_rating"])))

    with open("amazon_predict.txt","r") as read_file:
        for i in read_file.read():
            if(i in ["T","F"]):
                amazon_predict.append(i)

    with open("Output2.txt","r") as read_file:
        for i in read_file.read():
            if(i in ["T","F"]):
                flipcart_predict.append(i)

    file = 'Flipkart_product_output.csv'
    with open(file) as fh:
        rd = csv.DictReader(fh, delimiter=',')
        for row in rd:
            flipcart_most_buyed_prduct_details.append(row)

    amazon_ratting_avearge=sum(amazon_rating)/len(amazon_rating)
    print("flipcart", flipcart)
    print("amazon", amazon)
    print("amazon_predict", amazon_predict)
    print("flipcart_predict", flipcart_predict)
    print("amazon_ratting_avearge", sum(amazon_rating) / len(amazon_rating))
    print("flipcart_prduct_details", flipcart_most_buyed_prduct_details)

    return flipcart,flipcart_predict,amazon,amazon_predict,amazon_ratting_avearge,flipcart_most_buyed_prduct_details
#flipcart,flipcart_predict,amazon,amazon_predict,amazon_ratting_avearge,flipcart_most_buyed_prduct_details=getdata()


"""
with open('Flipkart_product_output.csv', mode='r') as infile:
    reader = csv.reader(infile)
    with open('coors_new.csv', mode='w') as outfile:
        writer = csv.writer(outfile)
        mydict = {rows[0]:rows[1] for rows in reader}
    print(mydict)
"""