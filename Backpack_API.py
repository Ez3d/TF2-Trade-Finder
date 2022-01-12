import requests
from bs4 import BeautifulSoup
import json

import time

key_usd = 1.68
key_ref = 43
killstreak_tier = 1
slots = ['melee', 'primary', 'secondary']
# Max Key Price
max_price = 40
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                     'Chrome/84.0.4147.125 Safari/537.36'}


for i in range(3):
    print('Killstreak Tier ' + str(killstreak_tier) + ' ------------------------------------------------------')
    time_start = time.time()
    for slot in slots:
        page = 1
        history = []
        end = False
        print('Searching ' + slot + ' weapons...')
        while True:
            backpack_url = 'https://backpack.tf/api/classifieds/search/v1'
            parameters = {'key': '5f3f298ce2ca3e69ec16543f',
                          'intent': 'buy',
                          'page_size': 30,
                          'slot': slot,
                          'quality': 11,
                          'australium': 'no',
                          'killstreak_tier': killstreak_tier,
                          'page': page}

            backpack_page = requests.get(backpack_url, params=parameters)
            backpack_json = backpack_page.json()
            requests_time = time.time()

            # filters sell listings
            listings = backpack_json['sell']['listings']

            if len(listings) < 30:
                end = True

            for listing in listings:
                # Backpack --------------------------------------------------------
                # Item name
                item = listing['item']['name']
                # skips repeats and skins
                if item in history or '(' in item or 'Botkiller' in item:
                    continue
                history.append(item)

                # Price
                key_price = 0
                metal_price = 0
                if 'usd' in listing['currencies']:
                    continue
                if 'metal' in listing['currencies']:
                    metal_price = listing['currencies']['metal']
                if 'keys' in listing['currencies']:
                    key_price = listing['currencies']['keys']
                price = key_price + metal_price / float(key_ref)
                # skips expensive listings
                if price > max_price:
                    end = True
                    print('max_price exceeded')
                    break

                # defIndex
                defIndex = str(listing['item']['defindex'])

                # Marketplace Scrape ----------------------------------------------------
                marketplace_url = 'https://marketplace.tf/items/tf2/' + defIndex + ';11;kt-' + str(killstreak_tier)
                marketplace_page = requests.get(marketplace_url, headers=headers)

                marketplace_soup = str(BeautifulSoup(marketplace_page.content, 'html.parser'))
                if 'currently no buy orders' in marketplace_soup:
                    continue

                a = marketplace_soup.index('Active Buy Orders')
                sell_price = float(marketplace_soup[marketplace_soup.index('<td>', a) + 5: marketplace_soup.index('</td>', a)])

                # Calculations --------------------------------------------------------
                profit = sell_price * 0.9 - price * key_usd

                if profit > 0.1:
                    print('\n' + '----------------------------------------------')
                    print(item)
                    print('defIndex: ' + defIndex)
                    print('Buy price: ' + str(price) + ' keys')
                    print('Sell price: $' + str(sell_price))
                    print('Profit: $' + str(round(profit, 2)))
                    base_name = item[item.index('Killstreak') + 11:]
                    if ' ' in base_name:
                        base_name = base_name.replace(' ', '%20')
                    if '\'' in base_name:
                        base_name = base_name.replace('\'', '%27')
                    print('URL: ' + 'https://backpack.tf/classifieds?item=' + base_name + '&quality=11&tradable=1&craftable=1&australium=-1&killstreak_tier=' + str(killstreak_tier))
                    print('----------------------------------------------' + '\n')

            if end:
                break
            # print('Scanned Page ' + str(page))
            page += 1
            time_end = time.time()
            if time_end - requests_time < 2:
                time.sleep(2 - (time_end - requests_time))
            # print('Time Elapsed: ' + str(round(time_end - time_start, 2)))

    killstreak_tier += 1