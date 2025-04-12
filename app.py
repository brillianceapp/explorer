from web3 import Web3
from hexbytes import HexBytes
import pymongo
from datetime import datetime, timedelta, date
from flask import Flask, render_template, url_for, request, redirect, flash, current_app, session, jsonify
#from flask_socketio import SocketIO
import json
import requests
from flask_cors import CORS
import blocksmith

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'fdddddddsdfdcvxawyyrsmdjyowqadetcsdddd'
#socketio = SocketIO(app)

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient[config["dbname"]]
blockcol = mydb["blocks"]
transactioncol = mydb["transaction"]
blockscancol = mydb["blockscan"]
pricecol = mydb["price"]

scan = blockscancol.find_one()
#print(scan)
#C:\Users\mdans\AppData\Local\MongoDBCompass\MongoDBCompass.exe

if scan == None:
    blockscancol.insert_one({"id": 1, "startblock": 0, "endblock": 0})
price = pricecol.find_one()
# print(price)
if price == None:
    pricecol.insert_one({"id": 1, "name": "Biten", "symbol": "BTN",
                        "price": "0", "change24": "0", "change1h": "0"})

	

try:
   w3 = Web3(Web3.HTTPProvider(config["http_provider"]))
   print(w3.is_connected())
except:
    print("ws error")   
						


@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html',title=config["networt_name"]+" | Explorer",name=config["coinName"],symbol=config["symbol"],networt_name=config["networt_name"],rpc=config["http_provider"],ws=config["ws_provider"],networtid=config["networkid"],baseBlockReward=config["baseBlockReward"])

@app.route('/blocks', methods=["POST", "GET"])
def blocks():
    return render_template('blocks.html',title=config["networt_name"]+" | All Blocks",name=config["coinName"],symbol=config["symbol"],networt_name=config["networt_name"],rpc=config["http_provider"],ws=config["ws_provider"],networtid=config["networkid"],baseBlockReward=config["baseBlockReward"])

@app.route('/txs', methods=["POST", "GET"])
def txss():
    return render_template('alltrx.html',title=config["networt_name"]+" | All Transactions",name=config["coinName"],symbol=config["symbol"],networt_name=config["networt_name"],rpc=config["http_provider"],ws=config["ws_provider"],networtid=config["networkid"],baseBlockReward=config["baseBlockReward"])

@app.route('/txsPending', methods=["POST", "GET"])
def pendingtxss():
    return render_template('pendingtrx.html',title=config["networt_name"]+" | Pending Transactions",name=config["coinName"],symbol=config["symbol"],networt_name=config["networt_name"],rpc=config["http_provider"],ws=config["ws_provider"],networtid=config["networkid"],baseBlockReward=config["baseBlockReward"])

@app.route('/block/<block>', methods=["POST", "GET"])
def blockid(block):
    return render_template('blockview.html',title=config["networt_name"]+" | Blocks #"+block,block=block,name=config["coinName"],symbol=config["symbol"],networt_name=config["networt_name"],rpc=config["http_provider"],ws=config["ws_provider"],networtid=config["networkid"],baseBlockReward=config["baseBlockReward"])

@app.route('/tx/<hash>', methods=["POST", "GET"])
def trxhash(hash):
    return render_template('trx.html',title=config["networt_name"]+" | Transaction Hash (TxHash) "+hash,hash=hash,name=config["coinName"],symbol=config["symbol"],networt_name=config["networt_name"],rpc=config["http_provider"],ws=config["ws_provider"],networtid=config["networkid"],baseBlockReward=config["baseBlockReward"])

@app.route('/address/<address>', methods=["POST", "GET"])
def addressget(address):
    return render_template('address.html',title=config["networt_name"]+" | Address "+address,address=address,name=config["coinName"],symbol=config["symbol"],networt_name=config["networt_name"],rpc=config["http_provider"],ws=config["ws_provider"],networtid=config["networkid"],baseBlockReward=config["baseBlockReward"])                          

@app.route('/rpc', methods=["POST", "GET"])
def rpcinfo():
    return render_template('rpc.html',title=config["networt_name"]+" | RPC Info ",config=config,name=config["coinName"],symbol=config["symbol"],networt_name=config["networt_name"],rpc=config["http_provider"],ws=config["ws_provider"],networtid=config["networkid"],baseBlockReward=config["baseBlockReward"])                          

@app.route('/api-docs', methods=["POST", "GET"])
def apidocs():
    return render_template('api-docs.html',title=config["networt_name"]+" | API Docs Info",config=config,name=config["coinName"],symbol=config["symbol"],networt_name=config["networt_name"],rpc=config["http_provider"],ws=config["ws_provider"],networtid=config["networkid"],baseBlockReward=config["baseBlockReward"])                          

@app.route('/peer', methods=["POST", "GET"])
def peer():
    r = str(w3.net.peer_count)
    return r

@app.route('/api/priceupdate', methods=["POST", "GET"])
def priceupdate():
    try:
        r = requests.get(config["coinpaprika"])
        data =  r.json()
        hour = float(data["quotes"]["USD"]["percent_change_1h"])
        day = float(data["quotes"]["USD"]["percent_change_24h"])
        priceval = float(data["quotes"]["USD"]["price"])
        newvalues = { "$set": { "price": priceval, "change24": day, "change1h": hour } }
        pricecol.update_one({"id":1},newvalues)
        return jsonify({"status":"success","name": config["coinName"],"symbol": config["symbol"], "data": newvalues["$set"], "csupply": config["csupply"], "supply": config["supply"] })
    except BaseException as e:
        print(str(e))
        return jsonify({ "status": "Failed" })
    
@app.route('/api/getrpc', methods=["POST", "GET"])
def getrpc():
    pr = pricecol.find_one({"id":1})
    return jsonify({
        "rpc-http": config["http_provider"],
        "rpc-socket": config["ws_provider"],
        "network-id": config["networkid"],
        "networt-name": config["networt_name"],
        "coin-name": config["coinName"],
        "symbol": config["symbol"],
        "decimal": config["decimal"],
        "price": pr["price"],
        "change24": pr["change24"],
        "change1h": pr["change1h"],
        "test_network":config["test_network"]
      })

@app.route('/api/getgasprice', methods=["POST", "GET"])
def priceget():
    try:
        pr = pricecol.find_one({"id":1})
        r = w3.eth.gas_price
        return jsonify({
        "gwei": r / 1000000000, "gweidecimal": r, "eth": r * 21000 / 1000000000000000000,
        "price": pr['price'], "change1h": pr["change1h"], "change24": pr["change24"], "supply": config["supply"], 
        "csupply": config["csupply"],"name": config["coinName"],"symbol": config["symbol"]
      })
    except:
        pr = pricecol.find_one({"id":1})
        return jsonify({
        "gwei": 1, "gweidecimal": 0, "eth": 0,
        "price": pr['price'], "change1h": pr["change1h"], "change24": pr["change24"], "supply": config["supply"], 
        "csupply": config["csupply"],"name": config["coinName"],"symbol": config["symbol"]
      })


@app.route('/api/block/<blocks>', methods=["POST", "GET"])
def block(blocks):
        # arg = request.args
        # "arg":arg.get("name")
        type(blocks)
        if len(blocks)<60:
            blocks=hex(int(blocks))
        try:
            bb = w3.eth.get_block(blocks, True)
            trxlist = []
            uncles=[]
            blockd =[{
                "difficulty": bb["difficulty"], "extraData": bb["extraData"].hex(), "gasLimit": bb["gasLimit"],
                "gasUsed": bb["gasUsed"], "hash": bb["hash"].hex(), "logsBloom": bb["logsBloom"].hex(),
                "miner": bb["miner"], "mixHash": bb["mixHash"].hex(), "nonce": bb["nonce"].hex(), "number": bb["number"],
                "parentHash": bb["parentHash"].hex(), "receiptsRoot": bb["receiptsRoot"].hex(),
                "sha3Uncles": bb["sha3Uncles"].hex(), "size": bb["size"], "stateRoot": bb["stateRoot"].hex(),
                "timestamp": bb["timestamp"], "totalDifficulty": bb["totalDifficulty"], "transactions": trxlist,
                "transactionsRoot": bb["transactionsRoot"].hex(), "uncles": uncles
            }]
            for u in bb["uncles"]:
                uncles.append(u.hex())
            print(bb['transactions'])    
            for i in bb['transactions']:
                td = {"blockHash": i["blockHash"].hex(), "blockNumber": i["blockNumber"], "from": i["from"].lower(),
                    "gas": i["gas"], "gasPrice": i["gasPrice"],"timeStamp":bb["timestamp"],"hash": i["hash"].hex(), 
                    "input": i["input"],"nonce": i["nonce"], "to": i["to"].lower(), "transactionIndex": i["transactionIndex"],
                    "value": str(i["value"]), "type": i["type"], "chainId": "", "v": i["v"], "r": i["r"].hex(),
                    "s": i["s"].hex(), "gwei": float(i["gasPrice"])/1000000000,
                    "gasFee": (i["gas"]*float(i["gasPrice"]))/1000000000000000000
                }
                trxlist.append(td)
            return jsonify(blockd)
        except BaseException as e:
            print("Connection Error") 
            print(str(e))
            return jsonify([])


@app.route('/api/blocks', methods=["POST", "GET"])
def allblocks():
    arg = request.args
    limits = 50
    sorts = -1
    page = 0
    data=[]
    if arg.get("limit")!="" and arg.get("limit") !=None:
        limits=int(arg.get("limit"))

    if arg.get("page")!="" and arg.get("page") !=None:
        page=(int(arg.get("page"))-1)*limits

    if arg.get("sort") !="" and arg.get("sort") !=None:
        if arg.get("sort")=="desc":
            sorts=-1
        else:
            sorts=1      
           
    try:
        val = blockcol.find().sort([('number', sorts)]).skip(page).limit(limits) 
        for i in val:
            bb = i["block"]
            #print(i["block"]["totalDifficulty"])
            uncles=[]
            blockd ={
                "difficulty": bb["difficulty"], "extraData": bb["extraData"], "gasLimit": bb["gasLimit"],
                "gasUsed": bb["gasUsed"], "hash": bb["hash"], "logsBloom": bb["logsBloom"],
                "miner": bb["miner"], "mixHash": bb["mixHash"], "nonce": bb["nonce"], "number": bb["number"],
                "parentHash": bb["parentHash"], "receiptsRoot": bb["receiptsRoot"],
                "sha3Uncles": bb["sha3Uncles"], "size": bb["size"], "stateRoot": bb["stateRoot"],
                "timestamp": bb["timestamp"], "totalDifficulty": bb["totalDifficulty"], "transactions": bb["transactions"],
                "transactionsRoot": bb["transactionsRoot"], "uncles": uncles
            }
            for u in bb["uncles"]:
                uncles.append(u.hex())
            data.append(blockd)  
            #print(i)
            print("")
        print(data)    
        print("")
        print("")
        return jsonify(data)   
    except BaseException as e:
        print("Connection Error") 
        print(str(e))
        return jsonify([])
           
 
        

@app.route('/api/trxs', methods=["POST", "GET"])
def alltrx():
    arg = request.args
    limits = 50
    sorts = -1
    page = 0
    data=[]
    if arg.get("limit")!="" and arg.get("limit") !=None:
        limits=int(arg.get("limit"))

    if arg.get("page")!="" and arg.get("page") !=None:
        page=(int(arg.get("page"))-1)*limits

    if arg.get("sort") !="" and arg.get("sort") !=None:
        if arg.get("sort")=="desc":
            sorts=-1
        else:
            sorts=1    
    try:        
        val = transactioncol.find().sort([('number', sorts)]).skip(page).limit(limits) 
        for i in val:
            data.append(i["data"])    
        return jsonify(data)
    except BaseException as e:
        print("Connection Error") 
        print(str(e))
        return jsonify([])

@app.route('/api/latest-block', methods=["POST", "GET"])
def blocklatest():
        try:
            bb = w3.eth.get_block("latest", True)
            trxlist = []
            uncles=[]
            blockd =[{
                "difficulty": bb["difficulty"], "extraData": bb["extraData"].hex(), "gasLimit": bb["gasLimit"],
                "gasUsed": bb["gasUsed"], "hash": bb["hash"].hex(), "logsBloom": bb["logsBloom"].hex(),
                "miner": bb["miner"], "mixHash": bb["mixHash"].hex(), "nonce": bb["nonce"].hex(), "number": bb["number"],
                "parentHash": bb["parentHash"].hex(), "receiptsRoot": bb["receiptsRoot"].hex(),
                "sha3Uncles": bb["sha3Uncles"].hex(), "size": bb["size"], "stateRoot": bb["stateRoot"].hex(),
                "timestamp": bb["timestamp"], "totalDifficulty": bb["totalDifficulty"], "transactions": trxlist,
                "transactionsRoot": bb["transactionsRoot"].hex(), "uncles": uncles
            }]
            for u in bb["uncles"]:
                uncles.append(u.hex())
            for i in bb['transactions']:
                td = {"blockHash": i["blockHash"].hex(), "blockNumber": i["blockNumber"], "from": i["from"].lower(),
                    "gas": i["gas"], "gasPrice": i["gasPrice"],"timeStamp":bb["timestamp"],"hash": i["hash"].hex(), 
                    "input": i["input"],"nonce": i["nonce"], "to": i["to"].lower(), "transactionIndex": i["transactionIndex"],
                    "value": str(i["value"]), "type": i["type"], "chainId": "", "v": i["v"], "r": i["r"].hex(),
                    "s": i["s"].hex(), "gwei": float(i["gasPrice"])/1000000000,
                    "gasFee": (i["gas"]*float(i["gasPrice"]))/1000000000000000000
                }
                trxlist.append(td)
            return jsonify(blockd)
        except BaseException as e:
            print("Connection Error") 
            print(str(e))
            return jsonify([])


@app.route('/api/block-count', methods=["POST", "GET"])
def blockcount():
    try:
       return jsonify({"number":w3.eth.get_block_number()})
    except:
        return jsonify([])   

@app.route('/api/block-countdb', methods=["POST", "GET"])
def blockcountdb():
    result = blockcol.count_documents({})
    return jsonify({"result":result})

@app.route('/api/trx-countdb', methods=["POST", "GET"])
def trxcountdb():
    result = transactioncol.count_documents({})
    return jsonify({"result":result})

@app.route('/api/trx/<hash>', methods=["POST", "GET"])
def trxone(hash):
        try:
            i = w3.eth.get_transaction(hash)
            td = {"blockHash": i["blockHash"].hex(), "blockNumber": i["blockNumber"], "from": i["from"],
                    "gas": i["gas"], "gasPrice": i["gasPrice"],"hash": i["hash"].hex(), 
                    "input": "","nonce": i["nonce"], "to": i["to"], "transactionIndex": i["transactionIndex"],
                    "value": str(i["value"]), "type": i["type"], "chainId": "", "v": i["v"], "r": i["r"].hex(),
                    "s": i["s"].hex(), "gwei": float(i["gasPrice"])/1000000000,
                    "gasFee": (i["gas"]*float(i["gasPrice"]))/1000000000000000000
                }
            return jsonify([td])
        except BaseException as e:
            print("Connection Error") 
            print(str(e))
            return jsonify([])

@app.route('/api/trx-count', methods=["POST", "GET"])
def trxcount():
    result = transactioncol.distinct("hash")
    return jsonify({ "trx": len(result), "status": "Query Success" })

@app.route('/api/pending-trx', methods=["POST", "GET"])
def trxpending():
    pending_tx_filter = w3.eth.filter('pending')
    pending_tx = pending_tx_filter.get_new_entries()
    return jsonify(pending_tx)

@app.route('/api/trx-chart', methods=["POST", "GET"])
def trxchart():
    data = []
    tDate = datetime.now()
    fromdate1 = tDate - timedelta(days = 14)
    todate1 = tDate + timedelta(days = 1)
    fromdate = fromdate1.strftime("%Y-%m-%d")
    todate = todate1.strftime("%Y-%m-%d") 
    res = transactioncol.find({"timestamp": {"$gt": fromdate,"$lt": todate}})
    for i in list({ra["timestamp"]: ra for ra in res}.values()):
        result = transactioncol.count_documents({"timestamp":i["timestamp"]})     
        data.append({"time":i["timestamp"],"value":result})
    return jsonify(data)


@app.route('/api/account/<address>', methods=["POST", "GET"])
def account(address):
        address = address.lower()
        address = blocksmith.EthereumWallet.checksum_address(address)
        try:
            rs = w3.eth.get_balance(address)
            bal = {
                "status": "Success",
                "balance": rs / 1000000000000000000,
                "decimalBalance": rs
                }
            return jsonify(bal)
        except BaseException as e:
            print("Connection Error") 
            print(str(e))
            bal = {
                "status": "Failed",
                "balance": "",
                "decimalBalance": ""
                }
            return jsonify(bal)   

@app.route('/api/account/trx/<address>', methods=["POST", "GET"])
def accounttrx(address):
    address = address.lower()
    address = blocksmith.EthereumWallet.checksum_address(address)
    trx = []
    val = transactioncol.find({"$or": [{ "data.from": address},{ "data.to": address }] }).sort("number", -1)
    for i in val:
       if i["data"]["from"] == address or i["data"]["to"]==address:
            trx.append(i["data"])
    datareturn = {
        "status": "Success",
        "address": address,
        "trx": list({v['hash']:v for v in trx}.values())
      }        
    return jsonify(datareturn)

@app.route('/api/supply', methods=["POST", "GET"])
def supply():
    return jsonify({"result":config["supply"]})

@app.route('/api/csupply', methods=["POST", "GET"])
def csupply():
    return jsonify({"result":config["csupply"]})


if __name__=="__main__":
    #socketio.start_background_task(backgroungdblock)
    #socketio.run(app,host='localhost', port=5000,debug=True)
    app.run(host='0.0.0.0',port=5001,debug=False,use_reloader=True,threaded= True)