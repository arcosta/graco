from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import sys

'''
 Scrap for professors from Computing Department of
 Universidade Federal do Rio Grande do Norte/Brazil
'''

baseurl = "https://sigaa.ufrn.br/sigaa/public/programa/equipe.jsf?lc=pt_BR&id=73"


professors=list()

soup =bs(urlopen(baseurl).read())

table = soup.find(id="table_lt")
if not table:
    print("No table found")
    sys.ext(-1)
for tr in table.find_all('tr'):
    if tr['class'] == 'campos':
        continue
    row = tr.find_all('td')
    a_tag = row[4].find('a')
    if a_tag:
        print('%s: %s' %(row[0].text.strip(), a_tag['href']))
        professors.append({"name":row[0].text.strip(), "lattes": a_tag['href']})
    else:
        print('%s: %s' %(row[0].text.strip(), 'x'))
        professors.append({"name":row[0].text.strip(), "lattes": ""})
        
with open("docentes-ufrn.json",'w') as f:
    f.write('[')
    for p in professors:
        f.write(u'{"name":"%s","lattes":"%s"},' % (p['name'],p['lattes']))
    f.write('null]')
        
