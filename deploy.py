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
s_per_block = 1  # depends on the chain
s_per_epoch = 1 * S_PER_MIN
s_per_subscription = 24 * S_PER_HOUR
feeCollector = owner
rate = web3_config.w3.to_wei(2,'ether')
cut = web3_config.w3.to_wei(0.2,'ether')


nft_data = (
    "nft_name",
    "nft_symbol",
    1,
    "",
    True,
    owner
)
erc_data = (
    3,
    ["ETH-USDT", "ETH-USDT"],
    [
        owner,
        owner,
        owner,
        ocean_address,
        ocean_address,
    ],
    [MAX_UINT256, 0, s_per_block, s_per_epoch, s_per_subscription, 30],
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
data_nft.set_data("pair", "ETH/USDT")

ddo = {
    "title": "aaa"
}
data_nft.set_ddo(ddo)
