import time
import os


from utils.contract import DataNft,ERC721Factory, Web3Config, get_address

# TODO - check for all envs
assert os.environ.get("RPC_URL", None), "You must set RPC_URL environment variable"
web3_config = Web3Config(os.environ.get("RPC_URL"), os.environ.get("PRIVATE_KEY"))
owner = web3_config.owner
ocean_address = get_address(web3_config.w3.eth.chain_id,"Ocean")
fre_address = get_address(web3_config.w3.eth.chain_id,"FixedPrice")
factory = ERC721Factory(web3_config)



S_PER_MIN = 60
S_PER_HOUR = 60 * 60
MAX_UINT256 = 2**256 - 1
# for our ganache, have one epoch per minute (every 60 blocks)
base = "ETH"
quote = "USDT"
source = "kraken"
timeframe = '5m'
pair = "ETH/USDT"



s_per_block = 7  # depends on the chain
s_per_epoch = 301
s_per_subscription = 86394
trueval_timeout = 4 * 12 * s_per_epoch

print(f"{s_per_subscription % s_per_block}")
print(f"{s_per_epoch % s_per_block}")


feeCollector = web3_config.w3.to_checksum_address("0x4FF94e326DdA576132b0731333a62427f1611Ca9")
trueval_submiter = web3_config.w3.to_checksum_address("0xAc69154e0C32C99863dA5f717D7D52f202C9A80D")
rate = web3_config.w3.to_wei(3,'ether')
cut = web3_config.w3.to_wei(0.2,'ether')

nft_name = base+"-"+quote+"-"+source+"-"+timeframe
nft_symbol = pair
erc20_name = nft_symbol
erc20_symbol = nft_symbol

nft_data = (
    nft_name,
    nft_symbol,
    1,
    "",
    True,
    owner
)
erc_data = (
    3,
    [erc20_name, erc20_symbol],
    [
        owner,
        owner,
        feeCollector,
        ocean_address,
        ocean_address,
    ],
    [MAX_UINT256, 0, s_per_block, s_per_epoch, s_per_subscription, trueval_timeout],
    [],
)
fre_data = (
    fre_address,
    [ 
        ocean_address,
        owner,
        feeCollector,
        owner
    ],
    [
        18,
        18,
        rate,
        cut,
        1
    ]

)
data_nft_address = factory.createNftWithErc20WithFixedRate(nft_data,erc_data,fre_data)
print(f"Deployed NFT: {data_nft_address}")
data_nft = DataNft(web3_config,data_nft_address)
tx = data_nft.set_data("pair", pair)
print(f"Pait set to {pair} in {tx.hex()}")
tx = data_nft.set_data("base", base)
print(f"base set to {base} in {tx.hex()}")
tx = data_nft.set_data("quote", quote)
print(f"quote set to {quote} in {tx.hex()}")
tx = data_nft.set_data("source", source)
print(f"source set to {source} in {tx.hex()}")
tx = data_nft.set_data("timeframe", timeframe)
print(f"timeframe set to {timeframe} in {tx.hex()}")
tx = data_nft.add_erc20_deployer(trueval_submiter)
print(f"Erc20Deployer set to {trueval_submiter} in {tx.hex()}")
#ddo = {
#    "title": "aaa"
#}
#data_nft.set_ddo(ddo)
