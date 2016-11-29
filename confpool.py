import re
import csv
import pandas as pd
import urllib2
from bs4 import BeautifulSoup

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

site = 'http://www.espn.com/nfl/lines'

req = urllib2.Request(site, headers=hdr)
req.add_header('User-agent', 'Mozilla/5.0 (Linux i686)')
html = urllib2.urlopen(req).read()

table = [('Home','Away','Westgate','BOVADA','BETONLINE','SportsBetting','5Dimes')]

soup = BeautifulSoup(html, 'html.parser')

def home(str):
    home_team = str.split(' at ')[1]
    return home_team

def away(str):
    away_team = str.split(' at ')[0]
    return away_team

list = []
for g in soup.find_all(colspan="4"):
    list_game = []
    games = g.get_text()[:-6].split('-')[0]
    list_game = (str(home(games)),str(away(games)))
    list.append(list_game)

i = 1
points_list = []
for bet in soup.find_all(style="text-align:center;"):
    if bet.get_text()[0] == '-' or bet.get_text()[0] == '+' or bet.get_text()[0] == 'E':
        if bet.get_text() == 'EVEN':
             line = '0'
             favorite = '+'
        else:
            spread = bet.get_text()[1:-16][:5]
            favorite = bet.get_text()[0]
            if favorite == '+':
                line = spread.split('-')
                adv = 'A'
            elif favorite == '-':
                line = spread.split('+')
                adv = 'H'

        def sign(plusminus,string):
            if plusminus == 'H' and string != 0:
                st = string*-1
            else:
                st = string
            return st

        if i == 1:
            point_spread_1 = sign(adv, float(line[0]))
            i += 1
        elif i == 2:
            point_spread_2 = sign(adv, float(line[0]))
            i += 1
        elif i == 3:
            point_spread_3 = sign(adv, float(line[0]))
            i += 1
        elif i == 4:
            point_spread_4 = sign(adv, float(line[0]))
            i += 1
        elif i == 5:
            point_spread_5 = sign(adv, float(line[0]))
            spreads = (point_spread_1, point_spread_2,point_spread_3,point_spread_4,point_spread_5)
            points_list.append(spreads)
            i = 1

def table_join(list1, list2):
    i = 0
    count = len(list1)
    table = [('HOME', 'AWAY', 'LINE1', 'LINE2','LINE3','LINE4','LINE5')]
    while i < count:
        home = list1[i][0]
        away = list1[i][1]
        line1 = list2[i][0]
        line2 = list2[i][1]
        line3 = list2[i][2]
        line4 = list2[i][3]
        line5 = list2[i][4]
        row = (home, away, line1, line2, line3, line4, line5)
        table.append(row)
        i = i+1
    return table

data = table_join(list, points_list)
df = pd.DataFrame(data)
df.columns = df.iloc[0]
df = df[1:]

df['AVERAGE'] = df[["LINE1","LINE2","LINE3","LINE4","LINE5"]].mean(axis=1)
df['ADVANTAGE'] = df['AVERAGE'].apply(lambda x: 'AWAY' if x <= 0.0 else 'HOME' )

df = df[['HOME','AWAY','AVERAGE','ADVANTAGE']]
df['ABS'] = df['AVERAGE'].abs()
df = df.sort_values(by='ABS', ascending=False)
df = df[['AWAY','HOME','ADVANTAGE','AVERAGE']]


print df

