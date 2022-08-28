import requests
import json
import time
import datetime
import webbrowser
import sys
import getopt

# ideas
# -----
# only look at certain traits (rare vault-x)
  # me only gives rarity number in listings api, can i pull traits from howrare? or ME? and
  #  do it per NFT that's listed new, so don't have to parse the whole collection
  #  /tokens/:token_mint
# large floor discripencies (floor is 1 and next highest is 5)
# large trait floor discrepencies (floor is 1 and next highest is 5)

USAGE = "me-listings.py --collection <collection> --floorLimit <floorLimit> [--devnet]"


def parse(args):
    options, arguments = getopt.getopt(
        args, # Arguments
        'hc:f:d', # Short option definitions
        ["help", "collection=", "floorMax=", "devnet"]) # Long option definitions
    devnet = False
    collection = None
    floorMax = None
    for o, a in options:
        if o in ("-h", "--help"):
            print("1")
            print(USAGE)
            sys.exit()
        if o in ("-d", "--devnet"):
            devnet = True
        if o in ("-c", "--collection"):
            collection = a
        if o in ("-f", "--floorMax"):
            floorMax = float(a)
    return devnet, collection, floorMax

# api.py start


def getStats(api, collection):
    statsUrl = requests.get(f"{api}/v2/collections/{collection}/stats")
    return json.loads(statsUrl.text)


def getListedCount(statsData):
    listedCount = 0
    if ("listedCount" in statsData):
        listedCount = statsData["listedCount"]
    return listedCount


def getFloorPrice(statsData):
    return statsData["floorPrice"] / 1000000000.0


def getLatestListings(api, collection, offset, limit):
    listingsUrl = requests.get(f"{api}/v2/collections/{collection}/listings?offset={offset}&limit={limit}")
    return json.loads(listingsUrl.text)


# api.py end


def findListings(api, collection, floorMax):
    statsData = getStats(api, collection)
    listedCount = getListedCount(statsData)
    floorPrice = getFloorPrice(statsData)

    print("Listed: " + str(listedCount))
    print("FP: " + str(floorPrice))

    # increase limit if high listing rate
    listingsLimit = 5 # number of items to return
    listingsOffset = listedCount - listingsLimit # number of items to skip

    prevChecked = []
    while True:
        listingsData = getLatestListings(api, collection, listingsOffset, listingsLimit)

        for listing in listingsData:
            tokenMint = listing["tokenMint"]
            if not tokenMint in prevChecked:
                if listing["price"] <= floorMax: # TODO pass this filter in? include or exclude trait
                    print("opening: " + "https://magiceden.io/item-details/" + tokenMint)
                    # webbrowser.open_new_tab("https://magiceden.io/item-details/" + listing["tokenMint"])
                prevChecked.append(tokenMint)
            print("Checking listing...")
            time.sleep(2)
        
        print("Waiting...")
        time.sleep(60)


def main() -> None:
    args = sys.argv[1:]
    print(args)
    if not args:
        print("4")
        raise SystemExit(USAGE)
    devnet, collection, floorLimit = parse(args)

    print("devnet " + str(devnet))
    print("collection " + collection)
    print("floor limit " + str(floorLimit))

    api = "http://api-mainnet.magiceden.dev"
    if (devnet):
        api = api.replace("mainnet", "devnet")

    findListings(api, collection, floorLimit)


if __name__ == "__main__":
   main()
