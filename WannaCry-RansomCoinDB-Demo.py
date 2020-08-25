import requests
import locale
import pandas as pd
import matplotlib.pyplot as plt
import tlsh
import tqdm
plt.style.use('ggplot')


'''Put your api key here'''
api_key = "insert_your_64_hex_char_api_key_here"

'''Say you looked up one BTC address of Wannacry, and found:
13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94
So you fetch it from RansomCoinDB.'''
response = requests.get(
    'https://ransomcoindb.concinnity-risks.com/api/v2/bin2btc/btc/13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94?limit=1000',
    headers={'accept': 'application/json','x-api-key': api_key},
)
if response.json() == {'detail': "Could not validate the provided credentials. Please get in contact with the admins of this site in order get your API key. In the meantime ask 'aaron@lo-res.org' for BETA testing."}:
    print('You appear to be using an expired API key or forget to set it up in the variable above.')
    exit()
df = pd.DataFrame.from_dict(response.json())
df.to_csv('Binaries-with-13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94.csv')
RansomAccounts = set([])

'''Now we use every hash we found associated with that BTC address to see
to see what other BTC addresses we can find'''
print('Finding other associated BTC Accounts')
for j in tqdm.tqdm(df.sha256):
    response = requests.get(
        'https://ransomcoindb.concinnity-risks.com/api/v2/bin2btc/sha256/'+j,
        headers={'accept': 'application/json','x-api-key': api_key},
    )
    if response:
        for k in response.json():
            RansomAccounts.add(k['btc'])
    else:
        print('An error has occurred while searching by hash:'+j)
        print(response.status_code)

'''Then we use those accounts to see how many binaries they appear in'''
print('Finding other binaries from all associated BTC accounts')
for l in tqdm.tqdm(RansomAccounts):
    response = requests.get(
        'https://ransomcoindb.concinnity-risks.com/api/v2/bin2btc/btc/'+l,
        headers={'accept': 'application/json','x-api-key': api_key},
    )
    df = pd.DataFrame.from_dict(response.json())
    df.to_csv('Binaries-with-'+l+'.csv')
    count = 0
    if response:
        for m in response.json():
            count += 1
        print('Account '+l+' appears in '+str(count)+' samples.')
    else:
        print('An error has occurred while esearching by BTC address:'+l)
        print(response.status_code)

'''Then we see how much money they made'''
print('Calculating the money made in each of those BTC accounts')
for n in RansomAccounts:
        response = requests.get(
            'https://ransomcoindb.concinnity-risks.com/api/v2/txns/btc/'+n+'?limit=1000',
            headers={'accept': 'application/json','x-api-key': api_key},
        )
        trx_data = pd.DataFrame.from_dict(response.json())
        #print(trx_data.columns)
        trx_data.to_csv(n+'-Transactions.csv',index=False)
        USD = 0
        txn_count = 0
        timestamps = []
        if response:
            for o in response.json():
                #print(o)
                #Because BTC accounts "pay themselves" when they get change
                if o['source'] != o['dest']:
                    USD += o['usd']
                    txn_count += 1
                    timestamps.append(o['timestamp'])
            print('Account '+n+' made $'+'{:20,.2f}'.format(USD)+' US Dollars.')
            print('Across '+str(txn_count)+' transactions (occurrences).')
        else:
            print('An error has occurred while summing amounts by account:'+n)
            print(response.status_code)

'''Everything we just did, is now a API Endpoint: pivot/by/btc'''
response = requests.get('https://ransomcoindb.concinnity-risks.com/api/v2/pivot/by/btc/13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94?currency=usd&limit=1000',
    headers={'accept': 'application/json','x-api-key': api_key},
)
print('Everything we just did, is now a API Endpoint: pivot/by/btc')
trx_function_data = pd.DataFrame.from_dict(response.json())
print(trx_function_data)

'''Let us go back to TLSH though to show you some magic'''
wcry_bindist = []
for i in df.tlsh:
    for j in df.tlsh:
        if i != j:
            wcry_bindist.append(tlsh.diffxlen(i,j))

print('Let us look for new information with binary distance tricks.')
print('A good threshold for this set of binaries would be: '+str(sum(wcry_bindist)/len(wcry_bindist)))
print('Min distance is: '+str(min(wcry_bindist)))
print('Max distance is: '+str(max(wcry_bindist)))
print('Thus further work could identify similar malware based on the TLSH distance, even if it does not have the BTC addresses within it.')
