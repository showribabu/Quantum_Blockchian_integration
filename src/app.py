#for flask 
from flask import Flask,request,redirect,render_template

#blockchain
from web3 import Web3,HTTPProvider
import json


#for files
from werkzeug.utils import secure_filename
# import ipfsapi


app=Flask(__name__)


def connect_with_network(wallet):
    web3= Web3(HTTPProvider('127.0.0.1:7545'))
    print('ganache connected')
    
    with open('./build/contracts/network.json') as f:
        artificat_network= json.load(f)
        abi=artificat_network['abi']
        address=artificat_network['networks']['5777']['address']
    contract=web3.eth.contract(abi=abi,address=address)
    
    print('contract selected')
        
    if wallet==0:
        web3.eth.defaultAccount=web3.eth._get_accounts
    else:
        web3.eth.defaultAccount=wallet
    
    print('Account selected')
    
    return web3,contract
        
    

def connect_with_communication(wallet):
    web3= Web3(HTTPProvider('127.0.0.1:7545'))
    print('ganache connected')
    
    if wallet==0:
        print('wallet 0')
        web3.eth.defaultAccount=web3.eth._get_accounts
    else:
        web3.eth.defaultAccount=wallet
    
    print('Account selected')
    
    with open('./build/contracts/communication.json') as f:
        artificat_communication= json.load(f)
        abi=artificat_communication['abi']
        address=artificat_communication['networks']['5777']['address']
    contract=web3.eth.contract(abi=abi,address=address)
    
    print('contract selected')
        

    return web3,contract



@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)









