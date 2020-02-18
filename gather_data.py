from flask import Flask,render_template
import textwrap

app=Flask(__name__)


import json,csv
from collections import defaultdict
amazon_ratting_avearge=0
amazon=[]
flipcart=[]
flipcart_predict=[]
amazon_predict=[]
amazon_rating=[]
flipcart_most_buyed_prduct_details=[]
#ama=defaultdict(list)




def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def return_values():
    with open("amazon_predict.txt","r") as read_file:
        for i in read_file.read():
            if(i in ["T","F"]):
                amazon_predict.append(i)

    with open("flipcart_review_output.json", "r") as read_file:
        data = json.load(read_file)
        l=data["review"]
        for i in l:
            flipcart.append(remove_html_tags(i))

    with open("amazon.json","r") as read_file:
        data=json.load(read_file)
        k=0
        f={}
        for i in data[0]["reviews"]:
            #f["t"]=i["review_text"]
            data=i["review_text"]
            info = (data[:75] + '..') if len(data) > 75 else data
            amazon.append(info)
            #ama[info]=amazon_predict[k]
            k=k+1
            #amazon.append(f)
            amazon_rating.append(int(float(i["review_rating"])))
    #print(ama)





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

    print(flipcart_most_buyed_prduct_details)
    return flipcart,flipcart_predict,amazon,amazon_predict,str(amazon_ratting_avearge*10)+"%","66,239","66%",str(amazon_ratting_avearge*10)+",100",flipcart_most_buyed_prduct_details

"""
#print(amazon)
@app.route('/dash')
def dash():
    return render_template("start.html",flipcarts=flipcart,flipcart_predicts=flipcart_predict,amazons=amazon,amazon_predicts=amazon_predict,per=str(amazon_ratting_avearge*10)+"%",fl_rate="66,239",fl_per="66%",amazon_rating_averages=str(amazon_ratting_avearge*10)+",100",flipcart_most_buyed_prduct_details=flipcart_most_buyed_prduct_details)

if __name__=="__main__":
    app.run(debug=True)
"""