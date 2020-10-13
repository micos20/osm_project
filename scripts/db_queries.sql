SELECT DISTINCT uid, user FROM nodes
WHERE uid > 0
ORDER BY uid;
#> 468 users

# Number of unique users
SELECT uid, user FROM nodes n
WHERE uid > 0
UNION
SELECT uid, user FROM ways w
WHERE uid > 0
#> 570 users

# Create 'user' view
CREATE VIEW users
(uid, user) AS
SELECT uid, user FROM nodes n
WHERE uid > 0
UNION
SELECT uid, user FROM ways w
WHERE uid > 0 

# Show users who created the most nodes
SELECT u.user, count(*) nodes_created FROM users u
INNER JOIN nodes n
ON u.uid = n.uid
GROUP BY u.user
ORDER BY nodes_created DESC
#>
user| nodes_created
OSchlüter	111249
westnordost	42720
Velorep	19256
derandi	8041
Críostaí	6121
GeoMagician	5867
KTim	5376
sundew	3671
Zartbitter	3247
Divjo	3062

# Show users who created the most ways
SELECT u.user, count(*) ways_created FROM users u
INNER JOIN ways n
ON u.uid = n.uid
GROUP BY u.user
ORDER BY ways_created DESC
#>
OSchlüter	24571
westnordost	5990
Velorep	4156
derandi	2070
Críostaí	1248
peter_elveshorn	1030
Zartbitter	912
GeoMagician	817
frantzius2177	535
Divjo	454

# Which user contributed the most changes (nodes, ways)
SELECT uid, user, sum(num) total_elements FROM
(SELECT uid, user, 'NODES' type, count(*) num FROM nodes
WHERE uid > 0
GROUP BY uid
UNION ALL
SELECT uid, user, 'WAYS' type, count(*) num FROM ways
WHERE uid > 0
GROUP BY uid)
GROUP BY uid
ORDER BY total_elements DESC
LIMIT 10
=>
uid	user	total_elements
66904	OSchlüter	135820
1205786	westnordost	48710
1140155	Velorep	23412
28234	derandi	10111
2969228	Críostaí	7369
22646	GeoMagician	6684
75623	KTim	5753
40397	Zartbitter	4159
617520	sundew	3832
63375	Divjo	3516

# Show biggest changesets
SELECT elms.changeset, elms.uid, elms.user, count(*) elements FROM
(SELECT 'NODE' type, id, uid, user, version, changeset, timestamp FROM nodes
WHERE changeset > 0
UNION ALL
SELECT 'WAY' type, id, uid, user, version, changeset, timestamp FROM ways
WHERE changeset > 0) elms
GROUP BY changeset
ORDER BY 4 DESC
LIMIT 10
=>
changeset	uid	user	elements
24006537	1205786	westnordost	1190
25727434	66904	OSchlüter	1136
20068189	66904	OSchlüter	1045
16556423	1205786	westnordost	950
31427045	66904	OSchlüter	888
25837436	66904	OSchlüter	846
24519941	66904	OSchlüter	832
25831448	66904	OSchlüter	820
15071524	1205786	westnordost	799
367847	22646	GeoMagician	781


# Number of changesets and changed elements per user
SELECT cs.uid, cs.user, count(*) nbr_changesets, sum(elements) FROM    
(SELECT elms.changeset, elms.uid, elms.user, count(*) elements FROM
(SELECT 'NODE' type, id, uid, user, version, changeset, timestamp FROM nodes
WHERE changeset > 0
UNION ALL
SELECT 'WAY' type, id, uid, user, version, changeset, timestamp FROM ways
WHERE changeset > 0) elms
GROUP BY changeset) cs
GROUP BY uid
ORDER BY 4 DESC
LIMIT 10
=>
uid	user	nbr_changesets	sum(elements)
66904	OSchlüter	674	135820
1205786	westnordost	477	48710
1140155	Velorep	703	23412
28234	derandi	204	10111
2969228	Críostaí	112	7369
22646	GeoMagician	106	6684
75623	KTim	282	5753
40397	Zartbitter	54	4159
617520	sundew	69	3832
63375	Divjo	38	3516

# Verify results above
SELECT uid, type, number FROM (
SELECT uid, 'nodes' type, count(*) number FROM nodes
WHERE uid=1205786
UNION ALL 
SELECT uid, 'ways' type, count(*) number FROM ways
WHERE uid=1205786)
=>
uid	type	number
1205786	nodes	42720
1205786	ways	5990


# Check problematic user names
SELECT DISTINCT user, uid from nodes
WHERE user LIKE '%@%';
#>
user	uid
nit@bse	1041363
@mmanuel	6526984

# Check latest timestamp
SELECT datetime(timestamp) timestamp, 'NODE' type, id, changeset FROM nodes
WHERE changeset > 0
UNION ALL
SELECT datetime(timestamp) timestamp, 'WAY' type, id, changeset FROM ways
WHERE changeset > 0
ORDER BY timestamp DESC
LIMIT 5;

# Check earliest timestamp
SELECT datetime(timestamp) timestamp, 'NODE' type, id, changeset FROM nodes
WHERE changeset > 0
UNION ALL
SELECT datetime(timestamp) timestamp, 'WAY' type, id, changeset FROM ways
WHERE changeset > 0
ORDER BY timestamp
LIMIT 5;

# Check values from tags containing special characters
SELECT * FROM nodes_tags
WHERE 
id = 1239947780 AND
key = 'name';
=>
id	key	value	type
1239947780	name	BÜ 27 "Wrangelpromenade"	regular

SELECT DISTINCT user FROM users
WHERE 
user REGEXP '[ÄÜÖäüö]';
=>
user
Eckhart Wörner
Lübeck
OSchlüter
Boris Jäger
glühwürmchen
grüni
Jonas Köritz
RüFo
Danny Ralph Cäsar
Robert Röper

SELECT DISTINCT user, uid from nodes
WHERE user LIKE '%@%'
UNION ALL
SELECT DISTINCT user, uid from ways
WHERE user REGEXP '[<>]';
=>
user	uid
nit@bse	1041363
@mmanuel	6526984
<don>	45059

# Create tags VIEW
CREATE VIEW vw_tags
(element, id, key, value, type) AS
SELECT 'NODE' element,
       id,
       key,
       value,
       type
  FROM nodes_tags
UNION ALL
SELECT 'WAY' element,
       id,
       key,
       value,
       type
  FROM ways_tags

# Postcodes counts
SELECT value postcode, count(*) FROM vw_tags
WHERE key LIKE '%postcode%'
GROUP BY value;
=>
postcode	count(*)
25335	5357
25336	4480
25337	4425
25355	2966
25358	269
25365	925
25368	666
25370	39
25373	391
25436	2994
25495	30
25497	4

# Number of destination codes (pretty nesty stuff)
SELECT c.area_code, count(*) frequency FROM
(SELECT *, substr(res, 1, end-1) area_code FROM
(SELECT *, instr(res, ' ') end FROM
(SELECT *, substr(value, pos+1) res FROM
(SELECT *, instr(value, ' ') pos FROM vw_tags
WHERE key IN ('phone', 'phone2', 'fax', 'fax', 'mobile') AND
type IN ('contact', 'communication', 'regular'))))) c
GROUP BY c.area_code
ORDER BY frequency DESC
=>
area_code  frequency
4121       155
4122       43
4123       33
4126       6
4101       4
40         3
4120       3
151        1
152        1
162        1
176        1
178        1
32         1
4821       1
4922       1

# Create changeset View
CREATE VIEW vw_changesets
(changeset, uid) AS
SELECT changeset, uid FROM nodes
UNION
SELECT changeset, uid FROM ways

# Create nodes view
CREATE VIEW vw_nodes
(id, lat, lon, version, changeset, timestamp) AS
SELECT id,
       lat,
       lon,
       version,
       changeset,
       timestamp
  FROM nodes

# Create ways view
CREATE VIEW vw_ways
(id, version, changeset, timestamp) AS
SELECT id,
       version,
       changeset,
       timestamp
  FROM ways



SELECT * FROM vw_tags
WHERE (type = 'amenity' OR key = 'amenity') AND value = 'cafe'
ORDER BY key
=>
element	id	key	value	type
NODE	249752019	amenity	cafe	regular
NODE	270632008	amenity	cafe	regular
NODE	281690707	amenity	cafe	regular
NODE	288893273	amenity	cafe	regular
NODE	291902956	amenity	cafe	regular
NODE	308946646	amenity	cafe	regular
NODE	385287257	amenity	cafe	regular
NODE	416915099	amenity	cafe	regular
NODE	416977988	amenity	cafe	regular
NODE	417459219	amenity	cafe	regular
NODE	490524213	amenity	cafe	regular
NODE	1039130935	amenity	cafe	regular
NODE	1039131878	amenity	cafe	regular
NODE	1039132160	amenity	cafe	regular
NODE	1039237440	amenity	cafe	regular
NODE	1314106748	amenity	cafe	regular
NODE	1314106802	amenity	cafe	regular
NODE	2384582960	amenity	cafe	regular
NODE	2384613411	amenity	cafe	regular
NODE	2833206591	amenity	cafe	regular
NODE	2928174245	amenity	cafe	regular
NODE	2938199403	amenity	cafe	regular
NODE	2944574838	amenity	cafe	regular
NODE	2954932162	amenity	cafe	regular
NODE	2954932182	amenity	cafe	regular
NODE	2955746486	amenity	cafe	regular
NODE	2955746531	amenity	cafe	regular
NODE	2955746532	amenity	cafe	regular
NODE	2955756272	amenity	cafe	regular
NODE	3669263093	amenity	cafe	regular
NODE	3669340850	amenity	cafe	regular
NODE	3677249172	amenity	cafe	regular
NODE	3817744150	amenity	cafe	regular
NODE	3895894037	amenity	cafe	regular
NODE	6651534704	amenity	cafe	regular
NODE	7202870052	amenity	cafe	regular
WAY	117856213	amenity	cafe	regular
WAY	511329270	amenity	cafe	regular

#Show all cafes in the region
SELECT c.element, c.id, n.name, cy.city FROM ( 
SELECT element, id FROM vw_tags
WHERE key = 'amenity' AND value = 'cafe') c
LEFT OUTER JOIN (
SELECT element, id, value name FROM vw_tags
WHERE key='name') n
ON c.id=n.id AND c.element=n.element
LEFT OUTER JOIN (
SELECT element, id, value city FROM vw_tags
WHERE key='city') cy
ON c.id=cy.id AND c.element=cy.element
ORDER BY c.element, c.id 
=>
element id          name                           city
NODE    249752019   Café Langes Mühle              Uetersen
NODE    270632008   Tommy's Eisbar                 Uetersen
NODE    281690707   Café Galerie Schlossgefängnis  Barmstedt
NODE    288893273   Uhlenhoff                      Kölln-Reisiek
NODE    291902956   Rosenhof Kruse	
NODE    308946646   Die Pause	
NODE    385287257   Janny's Eis Cafe	
NODE    416915099   Café Kruschat                  Elmshorn
NODE    416977988   Eis Cafe Südpol	
NODE    417459219   Eis Boutique	
NODE    490524213   	
NODE    1039130935  Jim Coffey	
NODE    1039131878  Diakonie-Cafe	
NODE    1039132160  Café Lykke	
NODE    1039237440  Eis Cafe Vittoria	
NODE    1314106748  Dielen-Café	
NODE    1314106802  Hof-Café	
NODE    2384582960  Keiser Eis	
NODE    2384613411  Bäckerei Eggers	
NODE    2833206591  Eiscafé Südpol                 Barmstedt
NODE    2928174245  In Aller Munde	
NODE    2938199403  Ice Cafe Vittoria	
NODE    2944574838  	
NODE    2954932162  Conny's	
NODE    2954932182  Juli	
NODE    2955746486  Cafe el Pasha	
NODE    2955746531  Smokey's Shisha Bar	
NODE    2955746532  Stadt Cafe	
NODE    2955756272  Buongiorno Caffe               Elmshorn
NODE    3669263093  Cafeteria (LMG)	
NODE    3669340850  Presse Café                    Uetersen
NODE    3677249172  Café Ambiente	
NODE    3817744150  Klinikcafe	
NODE    3895894037  Kaffee Klatsch                 Barmstedt
NODE    6651534704  Kolls	
NODE    7202870052  Cafe Billy's Morgenduft	
WAY	    117856213   Monroe's                       Elmshorn
WAY	    511329270   Plantenhoff Cafe               Groß Nordende




# Show amenities
SELECT value Type, COUNT(*) nbr FROM vw_tags
WHERE key='amenity'
GROUP BY value
ORDER BY nbr DESC
LIMIT 20;
=>
Type	nbr
parking	735
bench	150
recycling	109
post_box	101
restaurant	93
bicycle_parking	65
school	49
fast_food	48
kindergarten	44
vending_machine	40
cafe	38
waste_basket	37
place_of_worship	33
doctors	31
pharmacy	27
bank	25
charging_station	24
fuel	23
social_facility	21
post_office	20


# School names in this region
SELECT id, value school_name FROM vw_tags
WHERE (element = 'NODE' AND key IN ('name') AND id IN
(SELECT id FROM nodes_tags
WHERE (type = 'amenity' OR key = 'amenity') AND value = 'school') )
OR (element = 'WAY' AND key IN ('name') AND id IN
(SELECT id FROM ways_tags
WHERE (type = 'amenity' OR key = 'amenity') AND value = 'school') )
=>
id	school_name
249745398	Birkenallee-Schule
270924683	Musikschule Uetersen
291358158	Geschwister-Scholl-Schule
544839063	Albert-Schweitzer-Schule
2184453482	Grundschule
2617897260	James-Krüss-Schule
7396700196	Schulgelände KGST 1
7396700199	Schulgelände KGST 2
25955952	Elsa-Brändström-Schule
26192122	Grundschule Kaltenweide
27137327	Boje-C.-Steffen-Gemeinschaftsschule Elmshorn
27158095	Astrid-Lindgren-Schule
31905663	Gemeinschaftsschule Langelohe
43339015	Carl-Friedrich-von-Weizsäcker-Gymnasium
45076170	Timm-Kröger-Schule
60362561	Grundschule Klein Nordende
66697249	Erich Kästner Gemeinschaftsschule Elmshorn
97476188	Berufsbildungsstätte Elmshorn
97476193	Wirtschaftsakademie Schleswig-Holstein
114394132	Bismarckschule
117107536	Friedrich-Ebert-Schule
120355661	Geschwister Scholl Schule
120355664	Grundschule Birkenallee
128732878	Grundschule Hainholz
150963562	Freie Waldorfschule Elmshorn
152212101	Raboisenschule
176620426	Erich Kästner Gemeinschaftsschule Elmshorn-Außenstelle Ramskamp
190168715	Berufliche Schule Elmshorn, Europaschule
198334456	Ludwig-Meyn-Schule
203010329	Berufliche Schule Elmshorn, Europaschule
205407747	Paul-Dohrmann-Schule
225037006	Grundschule Hafenstraße
244684458	Johannes Schwennesen Grundschule
263626689	Norddeutsche Fachschule für Gartenbau, Außenstelle Berufliche Schule Elmshorn
265838983	Leibniz Privatschule
268095200	Bilsbek-Schule
272243509	Rosenstadtschule Uetersen
292056271	Grund- und Gemeinschaftsschule Barmstedt
331184624	Grundschule Kölln-Reisiek
348164853	Klaus-Groth-Schule
362139545	Friedrich-Ebert-Schule
450180640	Ĝrundschule Wiepeldorn
470185503	Grundschule Fritz-Reuter-Schule
558268408	Grundschule Heidgraben

5 schools w/o a name

# Count number of nodes and ways
SELECT type, number FROM (
SELECT 'NODES' type, count(*) number FROM nodes
WHERE id>0
UNION ALL
SELECT 'WAYS' type, count(*) number FROM ways);
=>
type	number
NODES	258869
WAYS	51297
