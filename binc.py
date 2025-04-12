from web3 import Web3
from hexbytes import HexBytes
import pymongo
from datetime import datetime, timedelta, date
import time
import json
from threading import Thread

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
if scan == None:
    blockscancol.insert_one({"id": 1, "startblock": 0, "endblock": 0})
price = pricecol.find_one()
# print(price)
if price == None:
    pricecol.insert_one({"id": 1, "name": "Biten", "symbol": "BTN",
                        "price": "0", "change24": "0", "change1h": "0"})
    
w3 = Web3(Web3.HTTPProvider(config["http_provider"]))
def backgroungdblock():
    while True:
        startblock = blockscancol.find_one({"id": 1})
        endblock = w3.eth.get_block_number()
        try:
            for i in range(startblock["endblock"], endblock):
                bb = w3.eth.get_block(i, True)
                trxlist = []
                block = {
                    "difficulty": bb["difficulty"], "extraData": bb["extraData"].hex(), "gasLimit": bb["gasLimit"],
                    "gasUsed": bb["gasUsed"], "hash": bb["hash"].hex(), "logsBloom": bb["logsBloom"].hex(),
                    "miner": bb["miner"], "mixHash": bb["mixHash"].hex(), "nonce": bb["nonce"].hex(), "number": bb["number"],
                    "parentHash": bb["parentHash"].hex(), "receiptsRoot": bb["receiptsRoot"].hex(),
                    "sha3Uncles": bb["sha3Uncles"].hex(), "size": bb["size"], "stateRoot": bb["stateRoot"].hex(),
                    "timestamp": bb["timestamp"], "totalDifficulty": bb["totalDifficulty"], "transactions": trxlist,
                    "transactionsRoot": bb["transactionsRoot"].hex(), "uncles": bb["uncles"]
                }
                mydict = {"block": block, "number": bb["number"]}
                for i in bb['transactions']:
                    td = {"blockHash": i["blockHash"].hex(), "blockNumber": i["blockNumber"], "from": i["from"],
                    "gas": i["gas"], "gasPrice": i["gasPrice"], "timeStamp": bb["timestamp"], "hash": i["hash"].hex(),
                    "input": "", "nonce": i["nonce"], "to": i["to"], "transactionIndex": i["transactionIndex"],
                    "value": str(i["value"]), "type": i["type"], "chainId": "", "v": i["v"], "r": i["r"].hex(),
                    "s": i["s"].hex(), "gwei": float(i["gasPrice"])/1000000000,
                    "gasFee": (i["gas"]*float(i["gasPrice"]))/1000000000000000000
                    }
                    trxlist.append(td)
                    mytrxobj = {"data": td, "hash": i["hash"].hex(
                    ), "number": bb["number"], "timestamp": datetime.fromtimestamp(bb["timestamp"]).strftime("%Y-%m-%d")}
                    trxfind = transactioncol.find_one({"hash": i["hash"].hex()})
                    if trxfind == None:
                        #print(mytrxobj)
                        transactioncol.insert_one(mytrxobj)
                    else:
                        print("Transaction Exit ")
                blockfind = blockcol.find_one({"number": bb["number"]})
                if blockfind == None:
                    #print(block)
                    print("...inserted block... "+str(bb["number"]))
                    blockcol.insert_one(mydict)
                    blockscancol.update_one({"id": 1}, {"$set": {"endblock": bb["number"]}})
                else:
                    print("Block Exit "+str(bb["number"]))
                    print("......")
                latest()    
        except KeyboardInterrupt:
            print("Shutdown...")
            stop_threads=True
            break
        except BaseException as e:
            print("Connection Error")
            print(str(e))


def latest():
        try:
                bb = w3.eth.get_block('latest', True)
                trxlist = []
                block = {
                    "difficulty": bb["difficulty"], "extraData": bb["extraData"].hex(), "gasLimit": bb["gasLimit"],
                    "gasUsed": bb["gasUsed"], "hash": bb["hash"].hex(), "logsBloom": bb["logsBloom"].hex(),
                    "miner": bb["miner"], "mixHash": bb["mixHash"].hex(), "nonce": bb["nonce"].hex(), "number": bb["number"],
                    "parentHash": bb["parentHash"].hex(), "receiptsRoot": bb["receiptsRoot"].hex(),
                    "sha3Uncles": bb["sha3Uncles"].hex(), "size": bb["size"], "stateRoot": bb["stateRoot"].hex(),
                    "timestamp": bb["timestamp"], "totalDifficulty": bb["totalDifficulty"], "transactions": trxlist,
                    "transactionsRoot": bb["transactionsRoot"].hex(), "uncles": bb["uncles"]
                }
                mydict = {"block": block, "number": bb["number"]}
                for i in bb['transactions']:
                    td = {"blockHash": i["blockHash"].hex(), "blockNumber": i["blockNumber"], "from": i["from"],
                    "gas": i["gas"], "gasPrice": i["gasPrice"], "timeStamp": bb["timestamp"], "hash": i["hash"].hex(),
                    "input": "", "nonce": i["nonce"], "to": i["to"], "transactionIndex": i["transactionIndex"],
                    "value": str(i["value"]), "type": i["type"], "chainId": "", "v": i["v"], "r": i["r"].hex(),
                    "s": i["s"].hex(), "gwei": float(i["gasPrice"])/1000000000,
                    "gasFee": (i["gas"]*float(i["gasPrice"]))/1000000000000000000
                    }
                    trxlist.append(td)
                    mytrxobj = {"data": td, "hash": i["hash"].hex(
                    ), "number": bb["number"], "timestamp": datetime.fromtimestamp(bb["timestamp"]).strftime("%Y-%m-%d")}
                    trxfind = transactioncol.find_one({"hash": i["hash"].hex()})
                    if trxfind == None:
                        print(mytrxobj)
                        transactioncol.insert_one(mytrxobj)
                    else:
                        print("Latest Transaction Exit ")
                blockfind = blockcol.find_one({"number": bb["number"]})
                if blockfind == None:
                    #print(block)
                    print("...Latest block inserted ... "+str(bb["number"]))
                    blockcol.insert_one(mydict)
                else:
                    print("Latest Block Exit "+str(bb["number"]))
                    print("......")
                  
        except KeyboardInterrupt:
            print("Shutdown...")
        except BaseException as e:
            print("Connection Error")
            print(str(e))
        #time.sleep(7)    

backgroungdblock()
#latest()

t1 = Thread(target = backgroungdblock)
t2 = Thread(target = latest)

#t1.start()
#t2.start()