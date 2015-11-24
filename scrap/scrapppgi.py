#!/usr/bin/python
from bs4 import BeautifulSoup
from urllib.request import urlopen
import sys, re

print("Iniciando parser da página de docentes")


class Researcher:
        def __init__(self, name='', email='', lattesurl=''):
                self.name = name
                self.email = email
                self.lattesurl = lattesurl
                
        def __repr__(self):
                return '{"name": "' + self.name + '", "email": "' + self.email + '", "lattesurl": "' + self.lattesurl + '"}\n'

try:
	pagina = urlopen("http://ppgi.unb.br/curso/docentes")
except Exception as e:
        print("Erro ao ler a pagina %s", str(e))
        sys.exit(1)
	

# Inicia o parse s
soup = BeautifulSoup(pagina)
docentes = list()

tabela_docentes = soup.find_all(attrs={"class":"docentes"})

contador = 1
for docente in tabela_docentes[0].find_all(attrs={"style":"background-color: #d8e8e9;"}):
	links = docente.find_all("a")
	nome = links[0]
	lattes = links[1]['href']
	email = links[2].text.replace(" [at] ","@")

	docentes.append(Researcher(nome.text, email, lattes))
	#print("%i - Nome: %s - %s\nCV: %s\n" % (contador,nome.text, email, lattes))
	contador += 1
print(docentes)

f = open("docentes.json",'w')
f.write(docentes.__str__())
f.close()
