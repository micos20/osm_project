# Wrangle Open Street Map data  <a id="wrangle-open-street-map-data"></a>

__Project documentation__

This text documents the investigations performed on Open Street Map (OSM) raw data extracted from [Overpass query](https://overpass-api.de/query_form.html). We will screen and audit the raw data, perform some cleaning operations and create a SQL database for further investigation of the OSM content. The following points are addressed.   

<a id="table-of-content"></a> 
<p style="font-size: large"> Table of content</p> 

1. [Investigated area](#investigated-area)  
2. [Auditing OSM raw data](#auditing-osm-raw-data)  
 a) [Audit node and way attributes](#audit-node-and-way-attributes)  
 b) [Audit node and way tags](#audit-node-and-way-tags)  
 c) [Audit way nodes references](#audit-way-nodes-references)  
3. [Cleaning operations](#cleaning-operations)   
 a) [Clean weblinks](#clean-weblinks)  
 b) [Clean phone numbers](#clean-phone-numbers)  
4. [SQL Database](#sql-database)  
 a) [Database creation](#database-creation)  
 b) [Database queries](#database-queries)   
5. [Summary](#summary)   
6. [List of references](#list-of-references)    
7. [List of files](#list-of-files)   

## Investigated area <a id="investigated-area"></a>

The investigated region is approximately 35km north of Hamburg, Germany. The [image](#InvestigatedArea_600x474) below shows the extracted region. I selected this area because I've been living here for more than 20 year. I'm actually keen to know how many information and details I are already implemented in the OSM map.

The following overpass query was used to extract the raw data in XML:

```sh
overpass query
(
   node(53.6782,9.6072,53.7988,9.7888);
   <;
);
out meta;
```

![OSM Area: Germany, Schleswig-Hostein, Pinneberg, Elmshorn & Uetersen](https://github.com/micos20/osm_project/blob/master/images/InvestigatedArea_600x474.PNG)

<img src="https://github.com/micos20/osm_project/blob/master/images/InvestigatedArea_600x474.PNG" width = "600" height="474" alt="OSM Area: Germany, Schleswig-Hostein, Pinneberg, Elmshorn & Uetersen" />

<a id="InvestigatedArea_600x474"></a>  
![Investigated area: Germany, Schleswig-Hostein, Pinneberg, Elmshorn & Uetersen](./images/InvestigatedArea_600x474.PNG)

<figure><figcaption style="text-indent:10%">Investigated area: Germany, Schleswig-Hostein, Pinneberg, Elmshorn & Uetersen</figcaption></figure>

<a style="font-size: small; font-style: italic" href=#table-of-content>Back to table of content.</a>

## Auditing OSM raw data  <a id="auditing-osm-raw-data"></a>

To get an overview of the data I first checked some general things regarding the OSM content. I used the the script [*quick_parse_osm.py*](#list-of-files) for this purpose. 
The xml-file contains the following tags:

<p style="text-indent: 20%; font-weight: bold; font-size: small">Overview of tags in OSM raw data:</p>

Tag name | Counts | sub-tags| ref nodes/ members 
--|--|--|--
osm| 1||
note| 1||
meta| 1||
node| 252825| 46546|
way| 51297| 176900| 346424
relation| 614 | 2902| 39735

 ### Audit node and way attributes <a id="audit-node-and-way-attributes"></a>

The python script [*audit_nodes.py*](#list-of-files) is used to audit the node attributes, the script [*audit_ways.py*](#list-of-files) is used to audit way attributes. All attributes are checked for correct data type. All integer types and *datestamp* are checked for range (min, max) and validity (e.g. valid date, all values positive). The nodal coordinates *lat*, *lon* are also checked for correct position (within defined bounding box from overpass query). *Users* are checked for problematic characters.  

All fields show valid data types. The node *id*s range from 131499 to 7869305206, the way *id*s from 4043904 to 842937254.
The coordinates of all nodes are within the bounding box of our investigated region. 
The *uid* for nodes and ways ranges between 50 to 11558570. There are 468 unique users in node tags and 444 users in way tags. There are three user names showing problematic characters.  
<p style="text-indent: 20%; font-weight: bold; font-size: small">Problematic user names:</p>

*uid* | *user* | node/way
--|--|--
6526984 | @mmanuel | node
1041363 | nit@bse | node and way
45059 | &lt;don&gt; | way

The earliest recorded change made to nodes in this data set is `2007-09-10 08:58:41+00:00` and the latest `2020-09-02 18:21:42+00:00`. Way *timestamp*s lay within this range.

 

### Audit node and way tags <a id="audit-node-and-way-tags"></a>

All *tag*s consist of a key/ value pair (*k*/ *v*). The script [*audit_tags.py*](#list-of-files) is used to assess the data. All key/ value pairs are checked for problematic characters.

#### Audit tag keys

The keys in the xml file are colon separated keys like `railway:ref:DBAG`. I use the first part of the key as *type* and the remaining string as *key*. This results for the above mentioned key in: `type=railway` and `key=ref:DBA`. If there is no colon in the key string the *type* is set to 'regular'.

There are 787 different type/ key combinations in the OSM data including 111 unique *type*s. Each *type* has several different *key*s. The list below shows the most prominent *type*s and some exemplary *key* names.

<p style="text-indent: 20%; font-weight: bold; font-size: small">Overview of <em>type/ key</em> combinations including example <em>key</em>s:</p>

Type | n° of keys | Example keys
--|--|--
regular | 320 | 'meter_load', 'loc_name', 'landuse'
railway | 72 | 'signal:speed_limit:speed', 'signal:station_distant', 'position'
destination | 33 | 'colour:to:forward', 'colour:backward', 'colour:text'
recycling | 22 | 'plastic_packaging', 'plastic_bottles', 'waste'
openGeoDB | 16 | 'version', 'type', 'auto_update'
note | 16 | 'stripclub', 'de', 'vacant'
payment | 15 | 'debit_cards', 'ep_geldkarte', 'girocard'
removed | 14 | 'internet_access:fee', 'landuse', 'website'
socket | 14 | 'schuko:output', 'type2:voltage', 'type2_combo:voltage'
fuel | 12 | 'GTL_diesel', 'octane_102', 'biogas'


There are no problematic characters in the type/ key names. Some keys use capital letters or numbers (e.g. `openGeoDB:telephone_area_code`, but this doen't seem to be a problem. 

As the keys are composed of different colon separated names the very same name could occure in different type/ key combinations. If we were to search for websites for example we need to consult at least three different *type*s. The `key=website` can be found in the types *regular*, *contact* and *removed*. In addition websites can be found in *url* keys. Or we might want to look for shops. The `key=shop` can be found in type *regular*, *ref*, *note* and *disused*. We need to consider this fact when we clean the data and query the SQL database later. 

#### Audit tag values  
There are no missing or *NULL* values in the data set. I've found problematic characters for *value* attributes in 86 keys. The table below shows the *key*s (first 10) containing the most problematic *value*s.

<p style="text-indent: 20%; font-weight: bold; font-size: small">Number of problematic <em>value</em>s found in <em>key</em>s:</p>

*key* | problematic *value*s  
--|-- 
website | 450
name | 359  
opening_hours | 191   
phone | 189
ref | 138
email | 79  
fax | 64 
note | 43
backward | 38
operator | 37


The *name* values contain predominantly bus stops or railway items like crossings as can be seen in the output below. I show only an extract of the output of *name* values starting with 'B'. 
```python
print("Checking problematic name values starting with 'B':")
for name in (n for n in pbl_values['name'] if n[0] == 'B'):
    print(name)
```
    ...
    Barmstedt, Markt
    Boje-C.-Steffen-Gemeinschaftsschule Elmshorn
    Barmstedt, Baumschulenweg
    Bevern, Steinfurth
    Barmstedt, Galgenberg
    Bevern, Schmiedekamp
    Bevern, Tannenweg
    Bf. Tornesch
    Bullenkuhlen, Schulweg
    Brücke Elmshorn e.V.
    Bf. Prisdorf (SEV)
    Bevern, Barkhörner Weg
    Barmstedt, Hamburger Straße
    Bi'n Himmel
    Bullenkuhlen, Achterstraße
    Bullenkuhlen, Seether Weg (Mitte)
    Bergmann & Söhne
    Bullendorf, Feuerwehrhaus
    Blumen & Gestaltung Sudeck
    Bevern, Am Gehölz
    Bf. Elmshorn (ZOB)
    Bob's Teeregal
    Barmstedt, Chemnitzstraße
    Berufliche Schule Elmshorn, Europaschule
    Barmstedt, Gymnasium
    Bf. Elmshorn (Holstenplatz)
    BÜ 27 "Wrangelpromenade"
    BÜ 29 "Grenzweg"
    BÜ 28 "Gerlingweg"
    Bevern, Holstein
    B+K Wohnkultur u. Boge/Clasen 
    


The *name* values contain lots of different special characters like `'`, `&`, `"` and `()`. Some of the street names are quoted like `BÜ 27 "Wrangelpromenade"`. The raw xml data for the latter example is given below.
```
 <node id="1239947780" lat="53.7679521" lon="9.6554377" version="5" timestamp="2019-01-18T09:46:14Z" changeset="66420457" uid="677977" user="peter_elveshorn">
    <tag k="crossing:barrier" v="no"/>
    <tag k="name" v="BÜ 27 &quot;Wrangelpromenade&quot;"/>
    <tag k="railway" v="level_crossing"/>
    <tag k="source" v="Bing"/> 
```

Python correctly interprets html metacharaters and translates `&quot;` to `"`. This *value* is later exported into a csv file as: 

`1239947780,name,"BÜ 27 ""Wrangelpromenade""",regular`.   

Double quotes are used by default to escape meta characters by the python csv module. The subsequent SQL import works also perfectly fine as we'll see later. The other meta characters like `&gt;`, `&lt;` and `&amp;` are translated correctly as well.  

Websites by default contain special characters like `:` or `/`. A quick glance at the html links reveals that the links are given in different formats as the following list demonstartes. 

    https://www.vb-piel.de/  
    https://fitness-barmstedt.de  
    www.buongiorno-caffe.de  
    https://www.schnickschnack-shop.de/  
    http://www.bruecke-sh.de/index.php?idm=132  
    https://www.hanssen-for-men.de/  
    http://www.studienkreis.de/elmshorn.html  
    https://www.maass24.de  
    http://www.auszeit-elmshorn.net/  
    www.nur-hier.de
    https://www.mcdonalds.de/restaurant?url=elmshorn-lise-meitner-str-1&/de
    gefluegelhof-neumann.de
 
Some http links omit the `http://` part. Some use secure `https` some not. Many websites use `www`, others not. And some links even integrate http queries. But the most important question is still not answered. Does the link still work or is it broken, has the url moved elsewhere or is it insecure?

I decided to clarify these questions and refer to chapter [Clean weblinks](#clean-weblinks) where we will discuss weblinks in detail.

With telephone number there is an almost similiar issue. The numbers are given in many different formats as can be seen in the list below.

Telephone numbers showing different formats:

    +49 4122-9994713
    +49 4121 91213
    +49 41212611779
    +49 (4123) 92 17 93
    +49/4121/21773
    +49 4121 643-0
    +49 4123 9290577;+49 4123 9222240
    +494121750205

Some numbers divide country code and area codes by white spaces others by `/` or `-`. And sometimes the phone number doesn't contain any delimiters at all as you can see in the last number of the above list. Often the local code is given in parenthesis as this is widely used in Germany. It also happens that the *phone* value contains more than one number. In that case the numbers are separated by `;`. Open street map allows this behavior as stated on [OSM Key:phone wiki](https://wiki.openstreetmap.org/wiki/Key%3Aphone) (see *Parsing phone numbers*).

The cleaning of the phone numbers is described in chapter [Clean phone numbers](#clean-phone-numbers)


As we have seen above addresses can be found in the *regular* keys *ref* or *name* referring to bus stops, street cabinets, post boxes and railway items. Generally the key *addr:...* is used to hold address data like street names, post codes, city, country, housenumber, etc.    

I checked *street* and *postcode* keys for abbreviations and problematic characters. There are 858 street names and 12 valid post codes in the node and way tags. There is not a single abbreviation for `Straße` (street) within the *value*s. The address data looks actually pretty clean. 

### Audit way nodes references <a id="audit-way-nodes-references"></a>

There is no way w/o node references in the data set. All types are okay. 596 ways reference to 6044 nodes which aren't in the data set. These way nodes are outside our investigated region (bounding box).
The function *write_dummy_noodes* (from *audit_ways.py*) is used to create 6044 dummy nodes written to a csv file which we'll import to our SQL database later. The nodes are witten to the file [dummy_nodes.csv](#list-of-files). In addition a node tag for all dummy nodes is written to [dummy_nodes_tags.csv](#list-of-files) containing a *note* key to explain why this node has been created. The *uid* is set to -1 and the *user* to 'dummy'. The coordinates are set to 0.0/0.0 (lon/lat).

First 4 rows of dummy_nodes.csv: 

    id,lat,lon,user,uid,version,changeset,timestamp
    4826498152,0.0,0.0,dummy,-1,1,-1,2020-09-25T00:00:00Z
    1763012935,0.0,0.0,dummy,-1,1,-1,2020-09-25T00:00:00Z
    3823956308,0.0,0.0,dummy,-1,1,-1,2020-09-25T00:00:00Z
    ...

First 4 rows of dummy_nodes_tags.csv:  

    id,key,value,type
    4826498152,note,Way ref dummy node outside bounding box,regular
    1763012935,note,Way ref dummy node outside bounding box,regular
    3823956308,note,Way ref dummy node outside bounding box,regular
    ...
    


 <a style="font-size: small; font-style: italic" href=#table-of-content>Back to table of content.</a>

## Cleaning operations <a id='cleaning-operations'></a>
This chapter will document the cleaning process of weblinks and phone numbers.

### Clean weblinks (including nodes, ways and relations) <a id='clean-weblinks'></a>
We'll identify weblinks in the OSM data set, standardize the weblink format and check if the weblink is valid/ working. On request a JSON file is written which provides a look-up table mapping the current to the corrected weblinks.

The [OSM wiki for website tags](https://wiki.openstreetmap.org/wiki/Key%3Awebsite) provides information and recommendations for the use of *website* keys. A major principle is "*Use as short a URL as possible*". All weblinks should also conform with [RFC1738](https://tools.ietf.org/html/rfc1738#section-3.1). I use the URL schema found on Wikipedia ([URL encoding](https://de.wikipedia.org/wiki/URL-Encoding)) to show the different parts of a weblink.

<p style="text-indent: 20%; font-weight: bold; font-size: small">URL schema:</p>

                            https://maxmuster:geheim@www.example.com:8080/index.html?p1=A&p2=B#ressource
                            \___/   \_______/ \____/ \_____________/ \__/\_________/ \_______/ \_______/
                              |         |       |           |         |       |          |         |
                            schema     user  passphrase   host       port    path      query    fragment


The following general steps are performed to clean the weblinks:
- If possible use secure weblink (*https*)
- Generally user/ password data shouldn't be part of a OSM *website*
- OSM recommends to omit *www* to shorten the link
- Providing the host part only is the most robust and long lasting usage
- Port is optional
- The path is also optional. If the path is broken/ doesn't work the weblink will be shortened to the host part
- Querys should be omitted. I'll keep them if they work



#### Identify weblinks
According OSM weblinks can be found in *website*, *url*, *image* and *wikipedia* keys. I parse the tag keys of the OSM data to check the number of weblinks we find per key. In addition the found link is checked if it is a prober weblink. The python script [*audit_tags.py*](#list-of-files) contain the necessary functions to perform these tasks.

```python
weblinks, badlinks = weblinks_by_key(osm_file)
```
    Found weblinks in:
      website: 322
      wikipedia: 64
      brand:wikipedia: 39
      url: 12
      contact:website: 167
      image: 11
      subject:wikipedia: 3
      related:wikipedia: 2
      removed:website: 1

    Found bad links in:
      wikipedia: 64
      brand:wikipedia: 39
      subject:wikipedia: 3
      related:wikipedia: 2



The *wikipedia* keys don't contain proper weblinks as we can see in the following output,
```python
for i in range(10):
    print(badlinks['wikipedia'][i])
```
    de:Kreis Pinneberg
    de:Elmshorn
    de:Flugplatz Ahrenlohe
    de:Eiche von Barmstedt
    de:Nikolaikirche (Elmshorn)
    de:Hans Hachmann
    de:Uetersener Wasserturm
    de:Krückau
    de:Krückau
    de:Krückau

but *image* keys do:
```python
for i in range(10):
    print(weblinks['image'][i])
```
    https://upload.wikimedia.org/wikipedia/commons/c/c7/Stolperstein_Heinrich_Kastning.png
    https://upload.wikimedia.org/wikipedia/commons/b/be/Stolperstein_Max_Wriedet.png
    https://upload.wikimedia.org/wikipedia/commons/a/aa/Stolperstein_Reinhold_Jürgensen.png
    https://upload.wikimedia.org/wikipedia/commons/9/94/Stolperstein_Max_Maack.png
    https://upload.wikimedia.org/wikipedia/commons/f/f2/Stolperstein_Stanislaus_Pade.png
    https://upload.wikimedia.org/wikipedia/commons/5/5d/Schleswig-Holstein%2C_Tornesch%2C_Naturdenkmal_12-01_NIK_2221.JPG
    https://upload.wikimedia.org/wikipedia/commons/5/5d/Schleswig-Holstein%2C_Tornesch%2C_Naturdenkmal_12-01_NIK_2221.JPG
    https://commons.wikimedia.org/wiki/File:Teehaus_Uetersen.JPG
    http://www.zum-tannenbaum.de/files/bilder/hotel-pension.jpg
    https://commons.wikimedia.org/wiki/File:Heidgraben_Green_Gables.jpg
            

*website*, *contact:website*, *removed:website*, *url* and *image* keys contain weblinks. But are there any other keys containing weblinks? I will check other keys for weblinks using the *weblinks_by_value* function.

```python
weblinks_val = weblinks_by_value(osm_file)
```
    Found weblinks:
      website: 322
      openGeoDB:version: 6
      email: 61
      url: 12
      note:de: 10
      contact:website: 167
      source: 40
      contact:email: 20
      name: 1
      contact:facebook: 2
      image: 11
      internet_access:ssid: 1
      removed:website: 1
      operator: 1
      note: 1
      network: 12

*openGeoDB:version*, *network*, *operator* and *name* do not contain proper links. The others do, like the key *source* as can be seen in the example below.

    source:
    http://www.gas-tankstellen.de
    http://www.kindergarten-tornesch.de
    http://www.kunst-im-auftrag.de/Projekte/Gezeiten-Projekte/Sturmflut-Dalben/sturmflut-dalben.html
    http://www.heimathaus-tornesch.de/


 I also don't consider emails so we end up with the following keys containing weblinks:

- *website*
- *url*
- *image*
- *removed:website*
- *contact:website*
- *source*
- *contact:facebook*
- *internet_access:ssid* 
- *note*



#### How to identify a weblink
You might have asked yourself "*how does he identify weblinks properly?*". Well, this is done by defining the following regular expression:

```python
regex_weblink = re.compile(r'^(https?://)?(www\.)?(.*\.[a-zA-Z]{2,6})($|/{1}.*)$')
```

This regex identifies the *schema*, *host*, *www* and *path* part of an URL and splits the link into these four parts if existant. Let's consider a small example. Imagine we had the following url: *http://www.jugendpflege-uetersen.info/www/02_jugendzentrum/index.php?task=1*

Matching and grouping our regex would result in:

```python
match = regex_weblink.match('http://www.jugendpflege-uetersen.info/www/02_jugendzentrum/index.php?task=1')
for group in match.groups():
    print(group)
```
    http://
    www.
    jugendpflege-uetersen.info
    /www/02_jugendzentrum/index.php?task=1

#### Update weblinks
The function *check_url* is used to check and if necessary to update the URL. On request a look-up table can be written to a JSON file for mapping the current (old) URL with the updated (new) one. 

Invoking this function updates the URLs and shows the follows statistics: 
```python
lut, stats = weblink.check_url(osm_file, output=True, JSON_out='weblink_lut.all_d200923.1.JSON')
```
    Nbr insecure urls:  old/ 260   new/ 164
    Nbr secure urls:    old/ 169   new/ 282
    Nbr missing schemes:   17
    Nbr modified links:     7
    Nbr broken links:      63
    Ndr of doublicates:    40
    
In the current OSM file there are 260 insecure (*http*) and 169 secure (*https*) links. After the update we have 164 insecure and 282 secure links. 17 links without schema are updated. 7 broken links could be fixed by updating the URL *path*. There are still 63 broken/ defect links in the data set. 40 links are doublicates. An exaple of the performed update is given below. 

The weblink [http://www.kruemet.de/unternehmen/filialen/filiale-elmshorn/](http://www.kruemet.de/unternehmen/filialen/filiale-elmshorn/) does not work. The function *check_url* updated the link by exchanging `http` by `https` and by removing `filiale-elmshorn/` from the URL *path*. In addition *www* is removed. The resulting link's now working: [https://kruemet.de/unternehmen/filialen/](https://kruemet.de/unternehmen/filialen/)

**Attention:**  
- Invoking this function on the complete OSM data set is pretty time consuming (~10 minutes) as the function invokes several hundret webpages
- The results might not be exactly reproduceable as the validity of a page might have changed in the meantime
- For this study the file *weblink_lut.all_d200923.1.JSON* is used to incorporate the weblink updates

#### How do we check a weblink

The url check is performed by the *requests* module. The short function that performs the job is shown below. It's part of the wrangle helper functions defined in [*wrangle_hlp.py*](#list-of-files). I've chosen the request type *head* to avoid loading the complete page content. Shorter *timeout*s than 4s increase the number of invalid URLs. It's important to allow redirection. Many (if not most) pages incorporate the *www* term in the *host* part of the URL which we've deleted to comply with the OSM recommendations.  

```python
import requests
def check_weblink(link):
    try:
        r = requests.head(link, timeout=4, allow_redirects=True)        
    except:
        return False    
    return r.status_code == requests.codes.ok
```

Whould be nice to know if there is an even easier and faster way to perfom the URL checks. If you have any suggestions leave a comment an github, please. 


### Clean phone numbers <a id='clean-phone-numbers'></a>

#### General information

The [OSM wiki for *phone* keys](https://wiki.openstreetmap.org/wiki/Key%3Aphone) provies information how phone numbers should look like in OSM data. Generally the phone number should comply with the international standard given in *ITU-T E.164* and should look like `+<country code> <area code> <local number>`. The image below provides some details refgarding the ITU standard.  
<a id="InvestigatedArea_600x474"></a>  
![International_ITU-T_E.164-number_structure_for_geographic_areas](./images/International_ITU-T_E.164-number_structure_for_geographic_areas_400x266.PNG)

<p style="text-indent: 20%; font-weight: bold; font-size: small">Schema of phone numbers in acc. to <em>ITU-T E.164</em></p>  

German area codes have been downloaded from ["*Bundesnetzagentur*"](https://www.bundesnetzagentur.de/DE/Sachgebiete/Telekommunikation/Unternehmen_Institutionen/Nummerierung/Rufnummern/ONRufnr/ON_Einteilung_ONB/ON_ONB_ONKz_ONBGrenzen_node.html) as csv file (*NVONB.INTERNET.20200916.ONB.csv*). In addition German mobile codes have been extracted from [Wikipedia](https://en.wikipedia.org/wiki/Telephone_numbers_in_Germany) and appended manually to this file. These ara codes are used to extract area codes from the OSM file and to check validity of the data. 

For auditing phone numbers we will consult the following keys:
+ phone  
+ phone2  
+ fax
+ contact:phone
+ contact:fax
+ communication:mobile

I dismiss emergency codes in e.g. *regular:emergency_telephone_code* as these do not comply with ITU standard anyway.

#### The results of the phone updates
The python script [*audit_phone.py*](#list-of-files) is used to audit and update phone numbers. Simply invoking *audit_phone* will perform the audits and updates. Below you can find some statistics and important details.  

```python
phnbr, problm, special, areas = audit_phone(osm_file, output=True)
```
    Nbr of phone numbers: 255
    Nbr of unique area codes: 15
    Nbr of numbers containing non-digit characters: 22
    Nbr of problematic numbers (after cleaning): 0
    Problematic numbers:
    []

There are 255 phone numbers in 15 unique area codes in the OSM file. 22 phone numbers did contail special characters. There is no number that couldn't be updated to ITU standard.

Found area codes:  

    Number of found area codes:  15
    Area codes:
    Area code:    151, area name: Deutsche Telekom (GSM/UMTS)
    Area code:    152, area name: Vodafone D2 (GSM/UMTS)
    Area code:    162, area name: Vodafone D2 (GSM/UMTS)
    Area code:    176, area name: o2 Germany (GSM/UMTS)
    Area code:    178, area name: E-Plus (merging into o2 Germany) (GSM/UMTS)
    Area code:     32, area name: National subscriber numbers
    Area code:     40, area name: Hamburg
    Area code:   4101, area name: Pinneberg
    Area code:   4120, area name: Ellerhoop
    Area code:   4121, area name: Elmshorn
    Area code:   4122, area name: Uetersen
    Area code:   4123, area name: Barmstedt
    Area code:   4126, area name: Horst Holstein
    Area code:   4821, area name: Itzehoe
    Area code:   4922, area name: Borkum
    
5 area codes are mobile phone codes. There is also a special code for natinal subscriber numbers. The remaining 9 codes are actual area codes.

Some phone numbers initially containing special characters:

    +49 4122 7107-70
    +494121-4757577
    +49 (4123) 92 17 93
    +49 4121 645-274
    +49 4122-9994713
    +49 4121 4092-0
    +49/4121/21773
    +49 (4123) 68 40 24
    +49 (4123) 68 400
    +49 4121 643-0
    +49 4121 57998-0
    +49 4123 9290577;+49 4123 9222240
    ...

Below you can find an extract of the updated phone numbers:

    Updated phone numbers (before, after):
    ...
    ('+49 4122-9994713', '+49 4122 9994713')
    ('+49 4122 7058', '+49 4122 7058')
    ('+494122402132', '+49 4122 402132')
    ('+49 4122 41776', '+49 4122 41776')
    ('+49 4122 90421170', '+49 4122 90421170')
    ('+49 4123 9369644', '+49 4123 9369644')
    ('+4932221391378', '+49 32 221391378')
    ('+49412244365', '+49 4122 44365')
    ('+49 4121 103 83 30', '+49 4121 1038330')
    ('+49 4121 750205', '+49 4121 750205')
    ...

Even multiple numbers are treated correctly:  
    
    ('+49 4123 9290577;+49 4123 9222240', '+49 4123 9290577;+49 4123 9222240')

Ok, there is actually no update necessary as theses numbers are already ITU conform. 

#### Some code explanation
The function *update_phone* does the actual job of cleaning phone numbers. The tricky part in updating phone numbers is the identification of the area code as area codes in Germany have different length varying from 2 to 5 digits. The above mentioned csv file *NVONB.INTERNET.20200916.ONB.csv* containing all valid German area codes is used to identify the the area code within the *number*. This file is loaded and stored as dict *area_codes*. After stripping off the country code the remaining *number* consists of the *area* and the *subscriber* part. The code below is the actual engine to extract the area code. 

```python
# Extract area code from number
code_found = False
for i in range(2,6):        # Area code consists of 2 to 5 digits
    area = number[:i]       # area equals first i digits of number
    # Iterate over area codes of length i and compare to area extracted from number
    for code in (x for x in area_codes.keys() if len(x) == i):
        if area == code:
            code_found = True
            subscriber = number.replace(area, '')  # Remaining string of number is subscriber part
            break
    if code_found == True: break
# Return False if no area code found
if code_found == False:
    return False
```

This loop iterates over an area code (*area*) length between 2 and 5 digits. In the first run of the loop it assumes the area code to be of *i=2* digits length and compares the code with the valid codes of length *i=2* in the dict *area_codes*. If *area* is found in *area_codes* the remaining part of *number* is the *subscriber* part and the job is done. If *area* is not found the next iteration starts. The area code is assumed to be *i=3* digits and the new *area* is compared to all valid *area_codes* of length *i=3*. This procedure is repeated until a valid area code is found. Otherwise the function will return *False*.


 <a style="font-size: small; font-style: italic" href=#table-of-content>Back to table of content.</a>

## SQL Database <a id='sql-database'></a>

### Database creation <a id='database-creation'></a>

The database schema used to create the SQL database (*osm.db*) can be seen below. The script [*export_OSM_data.py*](#list-of-files) is used create the database structure from OSM raw data and to validate and export each table (shown in the schema below) to a csv file. Subsequently the csv files are imported to the database.

The database is schema looks like:
```sql
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT
);

CREATE TABLE nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
);

CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT
);

CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
);

CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);
```

### Database queries <a id='database-queries'></a>


#### Verify problematic values

values containing ',' are safe by quoting s.b.

    3927715814,name,"Raa-Besenbek, Kirchensteig",regular

uid containing @ char is no problem  

    4806085427,53.7521971,9.6684194,nit@bse,1041363,1,47976980,2017-04-20T16:17:08Z

encoding issue for tag *name:ru*:

      <node id="240036785" lat="53.7532486" lon="9.6524559" version="12" timestamp="2019-03-28T17:34:03Z" changeset="68634953" uid="9451067" user="b-jazz-bot">
    <tag k="name:ru" v="Эльмсхорн"/>

      <way id="286843508" version="2" timestamp="2017-08-03T15:55:23Z" changeset="50812925" uid="28234" user="derandi">
        ...  
        <tag k="addr:city" v="Tornesch"/>
        <tag k="addr:country" v="DE"/>
        <tag k="addr:housenumber" v="25"/>
        <tag k="addr:postcode" v="25436"/>
        <tag k="addr:street" v="Asperhorner Weg"/>
        <tag k="building" v="yes"/>
        <tag k="name" v="Geflügelhof Neumann"/>
        <tag k="website" v="gefluegelhof-neumann.de"/>

No website tag anymore

    286843508,city,Tornesch,addr
    286843508,country,DE,addr
    286843508,housenumber,25,addr
    286843508,postcode,25436,addr
    286843508,street,Asperhorner Weg,addr
    286843508,building,yes,regular
    286843508,name,Geflügelhof Neumann,regular





- number of queries per user

Create user table containing
    uid (pkey), user
    
    
Create changeset table containing
    changeset (pkey), nodes, ways, (relations)
    
I can create a view instead of these two tables

Query users and count assiciated element (node, way) creations. Sort by number of element created.  

Using regex in queries for weblinks and phone numbers



<a style="font-size: small; font-style: italic" href=#table-of-content>Back to table of content.</a>

## List of references  <a id="list-of-references"></a>

The following list shows the consulted references and websites.  

<dl>
<br/>
<dt style="font-style: italic; text-indent: 2%"><a href='https://overpass-api.de/query_form.html'>https://overpass-api.de/query_form.html</a></dt > 
<dd style="text-indent: 4%">
    This weblink is used to extract the OSM raw data.</dd>
<br/>
<dt style="font-style: italic; text-indent: 2%"><a href='https://wiki.openstreetmap.org/wiki/Key%3Awebsite'>https://wiki.openstreetmap.org/wiki/Key%3Awebsite</a></dt > 
<dd style="text-indent: 4%">
    This OSM wiki page provides information and recommendations regarding the usage of <em>website</em> tags.</dd>
<br/>
<dt style="font-style: italic; text-indent: 2%"><a href='https://de.wikipedia.org/wiki/URL-Encoding'>https://de.wikipedia.org/wiki/URL-Encoding</a></dt > 
<dd style="text-indent: 4%">
    URL encoding described on <em>Wikipedia</em>.</dd>    
<br/>
<dt style="font-style: italic; text-indent: 2%"><a href='https://tools.ietf.org/html/rfc1738#section-3'>https://tools.ietf.org/html/rfc1738#section-3</a></dt > 
<dd style="text-indent: 4%">
   RFC1738 - Uniform Resource Locators (URL)</dd>      
<br/>
<dt style="font-style: italic; text-indent: 2%"><a href='https://wiki.openstreetmap.org/wiki/Key%3Aphone'>https://wiki.openstreetmap.org/wiki/Key%3Aphone</a></dt > 
<dd style="text-indent: 4%">
   This OSM wiki page provides information and recommendations regarding the usage of <em>phone</em> tags.</dd>  
<br/>
<dt style="font-style: italic; text-indent: 2%"><a href='https://en.wikipedia.org/wiki/Telephone_numbers_in_Germany'>https://en.wikipedia.org/wiki/Telephone_numbers_in_Germany</a></dt > 
<dd style="text-indent: 4%">
   Wikipedia resource providing information about German area codes for telefone numbers.</dd>     
<br/>
<dt style="font-style: italic; text-indent: 2%"><a href='https://www.bundesnetzagentur.de/DE/Sachgebiete/Telekommunikation/Unternehmen_Institutionen/Nummerierung/Rufnummern/ONRufnr/ON_Einteilung_ONB/ON_ONB_ONKz_ONBGrenzen_node.html'>https://www.bundesnetzagentur.de/DE/Sachgebiete/Telekommunikation/Unternehmen_Institutionen/Nummerierung/Rufnummern/ONRufnr/ON_Einteilung_ONB/ON_ONB_ONKz_ONBGrenzen_node.html</a></dt > 
<dd style="text-indent: 4%">
    German official resource from <em>Bundesnetzagentur</em> for phone numbers and area codes. The csv file downloaded from this page is <em>NVONB.INTERNET.20200916.ONB.csv</em> (see <a href=#list-of-files>List of files</a>). There are regular updates on this page so that the current csv might not be the same.</dd> 
    
    
    
   
   
</dl>

 <a style="font-size: small; font-style: italic" href=#table-of-content>Back to table of content.</a>

## List of files  <a id="list-of-files"></a>

The following list shows python scripts used to assess and clean the OSM raw data. In addition files containing data (csv, JSON) created during auditing and cleaning are mentioned as well. The python scripts can be found in the sub-directory `./scripts/`, data files in the sub-directory `./data/`.

<br/>
<dl> 
<dt style="font-style: italic; text-indent: 2%">wrangle_hlp.py</dt > 
<dd style="text-indent: 4%">
    This script provides helping functions used throughout this investigation. The script is not intended to be run separately.</dd> 
<br/>
<dt style="font-style: italic; text-indent: 2%">quick_parse_osm.py</dt > 
<dd style="text-indent: 4%">
    This script provides some functions to count the tags within the OSM xml file and to count the sub-tags included in <em>node</em>, <em>way</em> and <em>relation</em> tags.</dd> 
<br/> 
<dt style="font-style: italic; text-indent: 2%">audit_nodes.py</dt > 
<dd style="text-indent: 4%">
    This script is used to audit all node fields. Each field has it's own auditing function. The fields <em>uid</em> and <em>user</em> as well as <em>version</em> and <em>changeset</em> are assessed within a single function.</dd> 
<br/>
<dt style="font-style: italic; text-indent: 2%">audit_ways.py</dt > 
<dd style="text-indent: 4%">
    This script is used to audit all way attributes and node references. Each attribute has it's own auditing function. The attribute <em>uid</em> and <em>user</em> as well as <em>version</em> and <em>changeset</em> are assessed within a single function.</dd>
<br/>
<dt style="font-style: italic; text-indent: 2%">audit_tags.py</dt > 
<dd style="text-indent: 4%">
    This script is used to audit node and way tags. It provides functions to audit the keys and the values of node tags. It also provides a function to check street names, post codes and country codes.</dd> 
<br/>
<dt style="font-style: italic; text-indent: 2%">dummy_nodes.csv</dt > 
<dd style="text-indent: 4%">
    This file contains dummy nodes which are referenced by way node references. These nodes are missing in the current OSM data set as they are outside the investigated region.</dd>
<br/>
<dt style="font-style: italic; text-indent: 2%">dummy_nodes_tags.csv</dt > 
<dd style="text-indent: 4%">
    This file contains dummy node tags for nodes outside the investigated region. A <em>note</em> tag is used to explain why these nodes (see <em>dummy_nodes.csv</em>) have been created.</dd> 
<br/>
<dt style="font-style: italic; text-indent: 2%">audit_weblinks.py</dt > 
<dd style="text-indent: 4%">
   This script is used to identify weblinks in the OSM data set, standardize the weblink format and check if the weblink is valid/ working. On request a JSON file is written which provides a look-up table mapping the current to the corrected weblinks.</dd> 
<br/>
<dt style="font-style: italic; text-indent: 2%">weblink_lut.all_d200923.1.JSON</dt > 
<dd style="text-indent: 4%">
   This file contains the mapping of the current URLs to the updates ones. It serves as a look-up table when writing the OSM data to csv files.</dd>     
<br/>
<dt style="font-style: italic; text-indent: 2%">NVONB.INTERNET.20200916.ONB.csv</dt > 
<dd style="text-indent: 4%">
   This file contains German area codes extracted from <a href='https://www.bundesnetzagentur.de/DE/Sachgebiete/Telekommunikation/Unternehmen_Institutionen/Nummerierung/Rufnummern/ONRufnr/ON_Einteilung_ONB/ON_ONB_ONKz_ONBGrenzen_node.html'><em>Bundesnetzagentur</em></a> on 24.9.2020. At the end of the official list some mobile codes are appended manually.</dd>  
<br/>
<dt style="font-style: italic; text-indent: 2%">schema.py</dt > 
<dd style="text-indent: 4%">
   Validation schema used by cerberus module</dd>     
<br/>
<dt style="font-style: italic; text-indent: 2%">export_OSM_data.py</dt > 
<dd style="text-indent: 4%">
   This python script is used to create the SQL database structure, extract the OSM raw data, perform cleaning operations for weblinks and phone numbers, validate the data and export the data/ tables to csv files.</dd>
</dl>


 <a style="font-size: small; font-style: italic" href=#table-of-content>Back to table of content.</a>


```python

```
