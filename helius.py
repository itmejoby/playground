import requests
import json
import time
import sys
import config

# a scratchpad for trying out their api

# TODO
#   handle arguments better
#   filter for different types of txs
#   pagination

# NOTE
#   divide by 100000000 to get the actual value

apiUrl = "https://api.helius.xyz/v0"
apiKey = config.heliusApiKey
apiKeySuffix = f"api-key={apiKey}"


def main() -> None:
    queryType = sys.argv[1]

    eventType = sys.argv[2]

    id = sys.argv[3]

    if queryType == "tx":
        result = getTransaction(id)

        prettyPrint(result)
    elif queryType == "nfts":
        nftAddresses = id.split(",") # input should be comma separated

        result = getNftMetadata(nftAddresses)

        print(result) # todo prettyPrint doesn't handle lists -> 'list' object has no attribute 'dumps'
    elif queryType == "addr":
        if eventType == "tx":
            result = getAddrTransactions(id)

            printDescriptions(result)
        elif eventType == "nft":
            result = getNfts(id)

            printDescriptions(result)
        elif eventType == "nft-events":
            result = getNftEvents(id)

            printDescriptions(result)
        elif eventType == "bal":
            result = getBalances(id)

            prettyPrint(result)
        elif eventType == "names":
            result = getNames(id)

            prettyPrint(result)
    else:
        print(f"unknown query type {queryType}")   


def callHelius(url, jsonPayload):
    if (jsonPayload is None):
        response = requests.get(url)
    else:
        response = requests.post(url, json=jsonPayload)
    return json.loads(response.text) 


def printDescriptions(json):
    tabStr = "\t"
    newLineStr = "\n"

    for entry in json:
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry["timestamp"]))
        print(ts + tabStr + entry["description"] + newLineStr + tabStr + "^ " + entry["signature"])

def prettyPrint(json):
    print(json.dumps(result, indent=2))


# https://docs.helius.xyz/api-reference/enhanced-transactions-api/parse-transaction-s
def getTransaction(txId):
    print(f"pulling tx {txId}")

    txUrlPrefix = apiUrl + "/transactions"
    url = f"{txUrlPrefix}/{txId}/?{apiKeySuffix}"

    return callHelius(url)


# https://docs.helius.xyz/api-reference/enhanced-transactions-api/transaction-history
def getAddrTransactions(addr):
    return getAddrEvents(addr, "transactions")


# https://docs.helius.xyz/api-reference/nft-api/nft-portfolio
def getNfts(addr):
    return getAddrEvents(addr, "nfts")


# https://docs.helius.xyz/api-reference/nft-api/nft-portfolio
def getNftMetadata(nftAddresses):
    print(f"pulling tokens")

    urlPrefix = apiUrl + "/tokens/metadata"
    url = f"{urlPrefix}/?{apiKeySuffix}"

    jsonPayload = { 'mintAccounts': nftAddresses }

    return callHelius(url, jsonPayload)


# https://docs.helius.xyz/api-reference/nft-api/nft-events
def getNftEvents(addr):
    return getAddrEvents(addr, "nft-events")


# https://docs.helius.xyz/api-reference/name-api/name-lookup
def getNames(addr):
    return getAddrEvents(addr, "names")


# https://docs.helius.xyz/api-reference/balances-api
def getBalances(addr):
    return getAddrEvents(addr, "balances")


# generic function to hit the /addresses APIs
def getAddrEvents(addr, eventType):
    print(f"grabbing {eventType} from {addr}")

    addrUrlPrefix = apiUrl + "/addresses"
    url = f"{addrUrlPrefix}/{addr}/{eventType}/?{apiKeySuffix}"

    return callHelius(url)


if __name__ == "__main__":
   main()
