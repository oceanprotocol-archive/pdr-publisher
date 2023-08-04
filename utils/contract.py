import json
import os
import glob
import time
import hashlib

from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_keys import KeyAPI
from eth_keys.backends import NativeECCBackend

from pathlib import Path
from web3 import Web3, HTTPProvider, WebsocketProvider
from web3.logs import STRICT, IGNORE, DISCARD, WARN

from web3.middleware import construct_sign_and_send_raw_middleware
from os.path import expanduser

import artifacts  # noqa
import addresses # noqa

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
keys = KeyAPI(NativeECCBackend)


class Web3Config:
    def __init__(self, rpc_url: str, private_key: str):
        self.rpc_url = rpc_url

        if rpc_url is None:
            raise ValueError("You must set RPC_URL environment variable")

        if private_key is None:
            raise ValueError("You must set PRIVATE_KEY environment variable")

        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        if private_key is not None:
            if not private_key.startswith("0x"):
                raise ValueError("Private key must start with 0x hex prefix")
            self.account: LocalAccount = Account.from_key(private_key)
            self.owner = self.account.address
            self.private_key = private_key
            self.w3.middleware_onion.add(
                construct_sign_and_send_raw_middleware(self.account)
            )

class ERC721Factory:
    def __init__(self, config: Web3Config,chain_id=None):
        if not chain_id:
            chain_id = config.w3.eth.chain_id
        address = get_address(chain_id,"ERC721Factory")
        if not address:
            raise ValueError("Cannot figure out ERC721Factory address")
        self.contract_address = config.w3.to_checksum_address(address)
        self.contract_instance = config.w3.eth.contract(
            address=config.w3.to_checksum_address(address),
            abi=get_contract_abi("ERC721Factory"),
        )
        self.config = config
    
    def createNftWithErc20WithFixedRate(self,NftCreateData, ErcCreateData,FixedData):
#            gasPrice = self.config.w3.eth.gas_price
            call_params = {
                "from": self.config.owner,
                "gasPrice": 100000000000,
            }

            tx = self.contract_instance.functions.createNftWithErc20WithFixedRate(
                NftCreateData, ErcCreateData,FixedData
            ).transact(call_params)
            receipt = self.config.w3.eth.wait_for_transaction_receipt(tx)
            if receipt['status']!=1:
                raise ValueError(f"createNftWithErc20WithFixedRate failed in {tx.hex()}")
            #print(receipt)
            logs = self.contract_instance.events.NFTCreated().process_receipt(receipt,errors=DISCARD)
            return logs[0]['args']['newTokenAddress']

class DataNft:
    def __init__(self, config: Web3Config, address: str):
        self.contract_address = config.w3.to_checksum_address(address)
        self.contract_instance = config.w3.eth.contract(
            address=config.w3.to_checksum_address(address),
            abi=get_contract_abi("ERC721Template"),
        )
        self.config = config
    
    def set_data(self, field_label,field_value,wait_for_receipt=True):
        """Set key/value data via ERC725, with strings for key/value"""
        field_label_hash = Web3.keccak(text=field_label)  # to keccak256 hash
        field_value_bytes = field_value.encode()  # to array of bytes
#        gasPrice = self.config.w3.eth.gas_price
        call_params = {
                "from": self.config.owner,
                "gasPrice": 100000000000,
                "gas": 100000
        }
        tx = self.contract_instance.functions.setNewData(field_label_hash, field_value_bytes).transact(call_params)
        if wait_for_receipt:
            self.config.w3.eth.wait_for_transaction_receipt(tx)
        return tx
    
    def add_erc20_deployer(self,address,wait_for_receipt=True):
#        gasPrice = self.config.w3.eth.gas_price
        call_params = {
                "from": self.config.owner,
                "gasPrice": 100000000000,
        }
        tx = self.contract_instance.functions.addToCreateERC20List(self.config.w3.to_checksum_address(address)).transact(call_params)
        if wait_for_receipt:
            self.config.w3.eth.wait_for_transaction_receipt(tx)
        return tx
    
    def set_ddo(self,ddo,wait_for_receipt=True):
#        gasPrice = self.config.w3.eth.gas_price
        call_params = {
                "from": self.config.owner,
                "gasPrice": 100000000000,
        }
        js = json.dumps(ddo)
        stored_ddo=Web3.to_bytes(text=js)
        tx = self.contract_instance.functions.setMetaData(
            1,
            '',
            str(self.config.owner),
            bytes([0]),
            stored_ddo,
            Web3.to_bytes(hexstr=hashlib.sha256(js.encode("utf-8")).hexdigest()),
            []
        ).transact(call_params)
        if wait_for_receipt:
            self.config.w3.eth.wait_for_transaction_receipt(tx)
        return(tx)

def get_address(chain_id,contract_name):
        network = get_addresses(chain_id)
        if not network:
            raise ValueError(f"Cannot figure out {contract_name} address")
        address = network.get(contract_name)
        return address

def get_addresses(chain_id):

    address_filename = os.getenv("ADDRESS_FILE")
    path = None
    if address_filename:
        path = Path(address_filename)
    else:
        path = Path(str(os.path.dirname(addresses.__file__))+"/address.json")
    
    if not path.exists():
        raise TypeError("Cannot find address.json")

    with open(path) as f:
        data = json.load(f)
    for name in data:
        network = data[name]
        if network['chainId']==chain_id:
            return network
    return None

def get_contract_abi(contract_name):
    """Returns the abi for a contract name."""
    path = get_contract_filename(contract_name)

    if not path.exists():
        raise TypeError("Contract name does not exist in artifacts.")

    with open(path) as f:
        data = json.load(f)
        return data["abi"]


def get_contract_filename(contract_name):
    """Returns abi for a contract."""
    contract_basename = f"{contract_name}.json"

    # first, try to find locally
    address_filename = os.getenv("ADDRESS_FILE")
    path = None
    if address_filename:
        address_dir = os.path.dirname(address_filename)
        root_dir = os.path.join(address_dir, "..")
        os.chdir(root_dir)
        paths = glob.glob(f"**/{contract_basename}", recursive=True)
        if paths:
            assert len(paths) == 1, "had duplicates for {contract_basename}"
            path = paths[0]
            path = Path(path).expanduser().resolve()
            assert (
                path.exists()
            ), f"Found path = '{path}' via glob, yet path.exists() is False"
            return path
    # didn't find locally, so use use artifacts lib
    path = os.path.join(os.path.dirname(artifacts.__file__), "", contract_basename)
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise TypeError(f"Contract '{contract_name}' not found in artifacts.")
    return path
