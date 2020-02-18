import cx_Oracle
import copy

def Articles():
	con = cx_Oracle.connect('system/$Sn8987480720@127.0.0.1/orcl')
	cur = con.cursor()
	cur.execute('select * from questions')
	res = cur.fetchall()
	dict = {}
	qtns = []
	.0
	for i in res:
		dict["id"] = i[0]
		dict["title"] = i[1]
		dict["body"] = i[2][3:len(i[2]) - 3]
		dict["authorid"] = i[3]
		cur.execute('select name from webusers where id=:id', {"id": i[3]})
		dict["name"] = cur.fetchall()[0][0]
		dict["create_date"] = i[4].date()
		qtns.append(dict)
		print(qtns)
	return qtns

def preprocessing(dataset):
	copieddata = copy.deepcopy(dataset)#yahan par "dataset" ka copy banaya gaya h--->"deepcopy" ka isslia upyoag kia gaya h taki koi bhi updation in the "copieddata" mein farak na kare
	print(copieddata)
	copieddata["Momentum_1D"]=copieddata["Close"]-copieddata["Close"].shift(1)  #yeh "copieddata["Close"].shift(1)" wo current "copieddata["Close"]" ke niche wale ko signify kar raha h
	copieddata["RSI"]=copieddata["Momentum_1D"].rolling(center=False, window=14).apply(rsi).fillna(0) #yeh RSI values ke column  ko addkarne ke lia h jo below "rsi" function ke formula se bana h
	print(type(copieddata))#hum upar wale mein rolling function le rahe h jo ekk certain no.s of rows(eg:-window=14) ko considered karta h to derive  a value by applying  function "rsi"
    #yeh fillna(0) use h taki jahan-jahan "NAN" uske jagah "0" dal sake
	datalist=copieddata.values.tolist()
	return (datalist)

##########??????ITERATE KAISE KARE IN THE COPIEDDATA KA VALUES MEIN


#yeh niche wala he "Relative Strength Index' ka nikalne ka kam aata h...
def rsi(values):
	up = values[values > 0].mean()# Avg(PriceUp)/(Avg(PriceUP)+Avg(PriceDown)*100
	down = -1 * values[values < 0].mean()
	return 100 * up / (up + down)

def RelativeStrengthIndex():
	print("hey")
