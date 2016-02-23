from bs4 import BeautifulSoup as bs
from urllib.request import urlopen

tiposProf = ['CO', 'PE', 'PA']
endProf="Universidade Federal de Minas Gerais, Instituto de Ciências Exatas"

docentes=list()

for tpProf in tiposProf:
    soup =bs(urlopen('https://www.dcc.ufmg.br/pos/pessoas/professores2.php?tipo=%s' % tpProf).read())
    profTbl=soup.find_all(attrs={'valign':'top','class':'td_sub_conteudo'})

    
    indice=1
    for profCell in profTbl:
        try:
            if tpProf == 'PE':
                docentes.append('"name":"' + profCell.strong.text + '"')
                print("Professor "+tpProf+" ("+str(indice)+"): " + profCell.strong.text)
                indice +=1
        except:
            pass

f = open("docentes-ufmg.json","w")
f.write('[')
for i in docentes:
    f.write("{%s}," % i)
    
f.write('null]')
f.close()