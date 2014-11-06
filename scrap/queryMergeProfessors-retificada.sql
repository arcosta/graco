MATCH (a:Author)-[r:AUTHORING]-(p:Article)
RETURN a.name, count(r) AS connections
ORDER BY connections DESC
LIMIT 10


START n = node(*)
MATCH n-[r:colleagues]->c
WHERE n.type? = 'person' and has(n.name)
RETURN n.name, count(r) AS connections
ORDER BY connections DESC

MATCH (a:Author)-[r:AUTHORING]-(p:Article)
where toInt(p.ano) > 2010
RETURN a.name, count(r) AS connections
ORDER BY connections DESC
LIMIT 10


MATCH (p:Article) 
RETURN p.nomePeriodico,count(*) as ocorrencias 
ORDER BY ocorrencias DESC

MATCH (a)
WHERE a.name='Eskil'
RETURN a.array, filter(x IN a.array WHERE length(x)= 3)



The Journal of the Acoustical Society of America	20
IEEE Transactions on Image Processing	14
IEEE Transactions on Signal Processing	10
Electronic Notes in Theoretical Computer Science	7
IEICE Transactions on Fundamentals of Electronics, Communications and Computer Science	7
International journal of computer science and network security	6
IEEE Transactions on Circuits An Systems for Video Technology	6
IEEE Signal Processing Letters	6
Journal of Pla University of Science and Technology (Natural Science Edition)	5
Journal of the Brazilian Air Transportation Research Society	5


The Journal of the Acoustical Society of America	0001-4966	2013	20
IEEE Transactions on Image Processing	1057-7149	2013	14
IEEE Transactions on Signal Processing	1053-587X	2013	10
IEICE Transactions on Fundamentals of Electronics, Communications and Computer Science	0916-8508	2013	7
IEEE Transactions on Circuits An Systems for Video Technology	1051-8215	2013	6
IEEE Signal Processing Letters	1070-9908	2013	6
Genetics and Molecular Research	1676-5680	2013	4
Cluster Computing	1386-7857	2013	4
Lecture Notes in Computer Science	0302-9743	2004	4
IEICE Transactions on Information and Systems	0916-8532	2013	4


MATCH (a:Author)--(p:Article)--(b:Author) 
RETURN a,b,p


Curriculos que faltam
Fernanda Lima | K4796351U9 
Marcio da Costa Perreira Brandao | K4783453J2
Ricardo Pezzoul Jacobi | K4781781Y6
Priscila America Solis M. Barreto | K4762270T3