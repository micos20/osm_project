# Wrangle Open Street Map data
__Project Logbook__


```python
%cd D:\Users\michael\Google Drive\DataAnalyst\Udacity\Project_2\data
```

    D:\Users\michael\Google Drive\DataAnalyst\Udacity\Project_2\data
    


```python
import audit_nodes as nodes
import audit_nodeTags as nodeTags
import audit_ways as ways
import audit_wayTags as wayTags
import audit_weblinks as weblink
import audit_phone as phone
import re
from quick_parse_osm import count_tags, count_ways_tags, count_nodes_tags
```

Overpass query used to extract Open Street Map raw data in XML

```sh
overpass query
(
   node(53.6782,9.6072,53.7988,9.7888);
   <;
);
out meta;
```


```python
# Save coordinates of bounding box
minlongitude = 9.6072
maxlongitude = 9.7888
minlatitude = 53.6782
maxlatitude = 53.7988
```

<img src="images/InvestigatedArea.png" width = "600" height="474" alt="OSM Area: Germany, Schleswig-Hostein, Pinneberg, Elmshorn & Uetersen" />

![InvestigatedArea_600x474.PNG](attachment:InvestigatedArea_600x474.PNG)

Issue with reduced data files
```
  <node changeset="73875873" id="249711938" lat="53.7043716" lon="9.7212653" timestamp="2019-08-29T10:42:18Z" uid="66904" user="OSchlüter" version="2" /><node changeset="51229458" id="249718764" lat="53.6813232" lon="9.6561567" timestamp="2017-08-18T10:57:22Z" uid="1854009" user="richard23" version="3" />
```

```
  <node changeset="73875873" id="249711938" lat="53.7043716" lon="9.7212653" timestamp="2019-08-29T10:42:18Z" uid="66904" user="OSchlüter" version="2" />
  <node changeset="51229458" id="249718764" lat="53.6813232" lon="9.6561567" timestamp="2017-08-18T10:57:22Z" uid="1854009" user="richard23" version="3" />
```

Solved by applying regex to data files using replacement function in notepad++ 

*search string:*   ```/>(<node.*)```   
*replace string:*  ```/>\n  \1```


```python
# osm data files
#osm_file = '../data/GE_SH_PI_elmshorn_uetersen_k=20.osm'
#osm_file = '../data/GE_SH_PI_elmshorn_uetersen_k=100.osm'
osm_file = 'GE_SH_PI_elmshorn_uetersen.osm'
```


```python

```

## General overview of dataset


```python
print(count_tags(osm_file))
```

    {'osm': 1, 'note': 1, 'meta': 1, 'node': 252825, 'tag': 226348, 'way': 51297, 'nd': 346424, 'relation': 614, 'member': 39735}
    


```python
count_ways_tags(osm_file)
```




    176900




```python
count_nodes_tags(osm_file)
```




    46546



### Assessing nodes


#### Assessing node id field 
What are we going to do?
+ cout nodes  
+ check for data type
+ all node ids positive?
+ check for range


```python
nodes.audit_node_id(osm_file, output=True);
```

    Number of nodes:  252825
    Number of false node id type:  0
    Max node id:  7869305206
    Min node id:  131499
    

### Assessing coordinates
What are we going to do?
+ check for data type float
+ coords in range of osm API request



```python
nodes.audit_coords(osm_file, minlon=minlongitude, maxlon=maxlongitude, minlat=minlatitude, maxlat=maxlatitude, output=True);
```

    Number of false coord types:  0
    Number of nodes outside bounding box:  0
    

### Assessing users
What are we going to do with the user name and uid?
+ check uid for data type int
+ check uid for range (min, max)
+ number of unique uids
+ uid, name always consistent?
+ check user name for critical characters


```python
nodes.audit_users(osm_file, output=True);
```

    Number of wrong uid type:  0
    Max user id:  11558570
    Min_user id:  697
    Number of unique users:  468
    Number of inconsistent uid/ name combinations:  0
    Number of problematic user names:  2
    List of problematic user names:  {(6526984, '@mmanuel'), (1041363, 'nit@bse')}
    

### Assessing version and changeset
What are we going to do?
+ check version and changeset for data type int
+ check version and changeset for range (min, max)
+ number of unique changesets


```python
nodes.audit_version_chset(osm_file, output=True);
```

    Number of falsy types:  0
    Max version:  40
    Min version:  1
    Max changeset id:  90318548
    Min changeset id:  23959
    Number of unique changesets:  5236
    

### Assessing timestamp
What are we going to do?
+ check timestamp for data type datetime
+ check for range (min, max)


```python
nodes.audit_timestamp(osm_file, output=True);
```

    Number of wrong date types:  0
    Earliest date:  2007-09-10 08:58:41+00:00
    Latest date:  2020-09-02 18:21:42+00:00
    

---

## Audit node tags

What we will check:
+ how many different types of keys do we have?
+ Are they all lower case?
+ How may colon keys do we have?
+ Do we have keys, values with problematoc characters?
+ Do we have 'regular' keys wich are also types?
+ Do we find 'regular' keys within the keys of other types?

### Audit keys


```python
_, __, keys = nodeTags.audit_keys(osm_file, output=True, out_depth=10);
```

    Number of problematic keys:  0
    Number of keys not only lower case:  39
    List of keys not only lower case (first 10):
    	 socket:type2:voltage
    	 openGeoDB:location
    	 openGeoDB:community_identification_number
    	 socket:type2_combo:voltage
    	 communication:800mhz
    	 TMC:cid_58:tabcd_1:LocationCode
    	 openGeoDB:telephone_area_code
    	 railway:ref:DBAG
    	 openGeoDB:layer
    	 openGeoDB:type
    Number of unique node types:  74
    List of types followed by number of keys per type plus 3 keys (first 10):
      Type: regular | keys: 207 | ['layer', 'type', 'motorcar']
      Type: railway | keys: 68 | ['signal:station_distant:form', 'signal:speed_limit_distant:form', 'signal:speed_limit']
      Type: recycling | keys: 22 | ['plastic', 'batteries', 'clothes']
      Type: openGeoDB | keys: 16 | ['is_in', 'license_plate_code', 'type']
      Type: socket | keys: 14 | ['type2', 'schuko', 'chademo']
      Type: removed | keys: 13 | ['internet_access', 'description', 'payment:telephone_cards']
      Type: payment | keys: 13 | ['credit_cards', 'ep_geldkarte', 'diners_club']
      Type: note | keys: 12 | ['vending', 'opening_hours', 'de']
      Type: fire_hydrant | keys: 9 | ['type', 'couplings', 'flow_rate']
      Type: seamark | keys: 8 | ['type', 'small_craft_facility:category', 'bridge:category']
    


```python
keys['TMC']
```




    {'cid_58:tabcd_1:Class',
     'cid_58:tabcd_1:Direction',
     'cid_58:tabcd_1:LCLversion',
     'cid_58:tabcd_1:LocationCode',
     'cid_58:tabcd_1:NextLocationCode',
     'cid_58:tabcd_1:PrevLocationCode'}




```python
nodeTags.unique_keys(keys)
```




    503




```python
nodeTags.keys_double(keys, output=True);
```

    Type equals "regular" key  26 times.
    All types that equal a "regular" key: ['railway', 'source', 'crossing', 'name', 'ref', 'brand', 'wheelchair', 'traffic_signals', 'amenity', 'note', 'capacity', 'internet_access', 'traffic_sign', 'shelter', 'species', 'genus', 'building', 'voltage', 'social_facility', 'location', 'healthcare', 'fixme', 'memorial', 'parking', 'operator', 'surveillance']
    


```python
nodeTags.check4reg_keys(keys, output=True, out_depth=10);
```

    Number of 'regular' keys found in other types:  44
    Matched keys (first 10): 
    - layer - found in:  {'openGeoDB:layer'}
    - type - found in:  {'aerodrome:type', 'surveillance:type', 'health_facility:type', 'lift_gate:type', 'openGeoDB:type', 'tower:type', 'railway:signal:electricity:type', 'slipway:type', 'mast:type', 'camera:type', 'pillar:type', 'post_office:type', 'operator:type', 'seamark:type', 'siren:type', 'building:type', 'fire_hydrant:type', 'pole:type', 'memorial:type'}
    - email - found in:  {'contact:email'}
    - diameter - found in:  {'fire_hydrant:diameter'}
    - website - found in:  {'contact:website', 'removed:website'}
    - shop - found in:  {'ref:shop:num', 'disused:shop'}
    - covered - found in:  {'removed:covered'}
    - location - found in:  {'openGeoDB:location', 'fire_hydrant:location'}
    - voltage - found in:  {'socket:type2:voltage', 'socket:chademo:voltage', 'socket:type2_combo:voltage'}
    - collection_times - found in:  {'note:collection_times', 'removed:collection_times'}
    


```python
#lookup_key(keys, 'number')
```

### Audit values 


```python
pbl_values, missing_values = nodeTags.audit_values(osm_file, output=True, out_depth=100)
```

    Missing values found for 0 nodes
    Problematic characters found in 58 keys.
    name: 255
    website: 187
    ref: 129
    opening_hours: 127
    phone: 98
    email: 37
    route_ref: 36
    fax: 28
    collection_times: 28
    note: 20
    description: 18
    text: 16
    vacant: 14
    operator: 13
    states: 11
    is_in: 8
    fixme: 7
    exact: 7
    source: 7
    position: 6
    image: 6
    de: 5
    level: 4
    url: 4
    voltage: 4
    speed: 4
    created_by: 3
    brand: 3
    flow_capacity: 3
    LCLversion: 2
    auto_update: 2
    cuisine: 2
    traffic_sign: 2
    facebook: 2
    inscription: 2
    stripclub: 2
    housenumber: 2
    species: 2
    street: 2
    postal_code: 1
    version: 1
    lines: 1
    vending: 1
    ele: 1
    bus_lines: 1
    frequency: 1
    maxheight: 1
    end_date: 1
    output: 1
    speciality: 1
    maxweight: 1
    psv_type: 1
    date: 1
    start_date: 1
    flow_rate: 1
    memorial: 1
    ssid: 1
    height: 1
    


```python
pbl_values['date']
```

 Problematic 'name' values:
 'BÜ 27 "Wrangelpromenade"',
 'BÜ 28 "Gerlingweg"',
 'BÜ 29 "Grenzweg"',
 
---    
     <node id="1239947780" lat="53.7679521" lon="9.6554377" version="5" timestamp="2019-01-18T09:46:14Z" changeset="66420457" uid="677977" user="peter_elveshorn">
        <tag k="crossing:barrier" v="no"/>
        <tag k="name" v="BÜ 27 &quot;Wrangelpromenade&quot;"/>
        <tag k="railway" v="level_crossing"/>
        <tag k="source" v="Bing"/> 

ends up in  

    1239947780,name,"BÜ 27 ""Wrangelpromenade""",regular
    
from csv module:

    Dialect.doublequote
    Controls how instances of quotechar appearing inside a field should themselves be quoted. When True, the character is doubled. When False, the escapechar is used as a prefix to the quotechar. It defaults to True. 
    On output, if doublequote is False and no escapechar is set, Error is raised if a quotechar is found in a field.

---
    
      <node id="2938199401" lat="53.7529133" lon="9.6523618" version="4" timestamp="2017-10-28T08:45:01Z" changeset="53311848" uid="677977" user="peter_elveshorn">
        <tag k="level" v="0"/>
        <tag k="name" v="H&amp;M"/>
        <tag k="opening_hours" v="Mo-Fr 09:30-19:00, Sa 09:30-18:00"/>
        <tag k="shop" v="clothes"/>
        <tag k="wheelchair" v="yes"/>


Some bus stops are written this way: 

    <tag k="name" v="Kibek/Franzosenhof"/>
or this way:

    <tag k="name" v="Heidgraben, Schulstraße"/>

    
      <node id="1762479438" lat="53.7417519" lon="9.7079270" version="7" timestamp="2017-02-21T23:34:00Z" changeset="46290297" uid="5191883" user="Danny Ralph Cäsar">
        <tag k="bus" v="yes"/>
        <tag k="highway" v="bus_stop"/>
        <tag k="name" v="Kibek/Franzosenhof"/>
        <tag k="network" v="HVV"/>
        <tag k="operator" v="Storjohann Stadtverkehr (Die Linie Gmbh)"/>
        <tag k="wheelchair" v="yes"/>
        
      <node id="1711687688" lat="53.7048090" lon="9.6810489" version="3" timestamp="2015-12-29T23:10:53Z" changeset="36252719" uid="617520" user="sundew">
    <tag k="bus" v="yes"/>
    <tag k="highway" v="bus_stop"/>
    <tag k="name" v="Heidgraben, Schulstraße"/>
    <tag k="public_transport" v="platform"/>
    <tag k="route_ref" v="6667"/>
    <tag k="shelter" v="yes"/>

Websites with "www." and "https://"

    'https://www.vb-piel.de/',
    'https://fitness-barmstedt.de/'
    'www.buongiorno-caffe.de',
    
And key 'url' is the same as website

Opening hours many different formats

    '"verschieden"',
    '24/7',
    'Feb-Dec: Su[1], Su[3] 14:00-17:00 || "nach Vereinbarung"',
    'Fr 08:00-13:00; Sa-Th off',
    'Fr-Mo,We 14:00-18:00; Tu,Th off',
    'Mo 09:00-12:30; Tu-Fr 09:00-12:30,14:30-18:00; Sa 10:00-13:00',
    'Mo 18:00-21:00; Tu 19:30-21:00; We 17:00-20:30; Th 09:30-11:00, 18:30-20:00; Fr 10:00-11:15',
    'Mo, Fr 09:00-12:30, 14:30-16:00; Tu, Th 09:00-12:30, 14:30-18:00; We 09:00-12:30',

Telephone numbers different types:

    +49 4122-9994713
    +49 4121 91213
    +49 41212611779
    +49 (4123) 92 17 93
    +49/4121/21773
    +49 4121 643-0
    +49 4123 9290577;+49 4123 9222240
    +494121750205




Addresses can often be found are often in the single keys 'ref' or 'name' referring to bus stops, street cabinets or post boxes 

    <tag k="ref" v="Adenauerdamm / Schumacherstraße, 25336 Elmshorn"/> 

    <node id="1370916239" lat="53.7589708" lon="9.6444597" version="9" timestamp="2018-11-25T11:29:24Z" changeset="64864523" uid="66904" user="OSchlüter">
    <tag k="man_made" v="street_cabinet"/>
    <tag k="operator" v="Stadtwerke Elmshorn"/>
    <tag k="power" v="substation"/>
    <tag k="ref" v="Amsel Str. 1 82"/>
    <tag k="street_cabinet" v="power"/>
    <tag k="substation" v="minor_distribution"/>
        
    <node id="276478119" lat="53.7392863" lon="9.6796004" version="9" timestamp="2019-11-28T22:44:20Z" changeset="77700460" uid="617520" user="sundew">
    <tag k="amenity" v="post_box"/>
    <tag k="check_date" v="2019-11-24"/>
    <tag k="collection_times" v="Mo-Fr 17:30; Sa 12:45"/>
    <tag k="operator" v="Deutsche Post"/>
    <tag k="ref" v="Adenauerdamm / Schumacherstraße, 25336 Elmshorn"/>       



```python
pbl_values['name']
```

Two types of 'ref's: 1 addresses 2 bus lines, power tower numbers 

Do I need to preserve html entities like `&quot;` or `&lt;` for meta characters? Python automatically recognizes and decodes them to metacharacters.

#### Audit address data


```python
streets, postcodes = nodeTags.audit_addr(osm_file)
```


```python
len(streets)
```


```python
len(postcodes)
```


```python
postcodes
```


```python
for street in streets:
    if 'Str.' in street: print('match')
```

There are no abbreviations for "Staße" or "Weg". Address data looks pretty clean for node tags. Postal code is also valid.

# Audit Ways


```python
ways.audit_way_id(osm_file, output=True);
```


```python
ways.audit_users(osm_file, output=True);
```

    <way id="304346561" version="3" timestamp="2019-01-15T12:13:31Z" changeset="66330006" uid="45059" user="&lt;don&gt;">


```python
ways.audit_version_chset(osm_file, output=True);
```

    Number of falsy types:  0
    Max version:  81
    Min version:  1
    Max changeset id:  90220517
    Min changeset id:  66459
    Number of unique changesets:  4613
    


```python
ways.audit_timestamp(osm_file, output=True);
```

    Number of wrong date types:  0
    Earliest date:  2008-01-11 15:28:22+00:00
    Latest date:  2020-09-01 04:46:59+00:00
    

### Audit way nodes references

What are we going to check:

- Do we have referenced nodes witch aren't in this dataset?
- Do we have ways without a ref node in the dataset. --> We might want to delete these items.


```python
false_type, not_refs, lost_ways, lostways = ways.audit_way_nodes(osm_file, output=True, write_dummys=False);
```


```python
len(lost_ways)
```

6044 referenced nodes are missing in the dataset. 596 ways are affected. I will create dummy nodes for the SQL database.


```python

```

### Audit Way Tags


```python
from wrangle_hlp import lookup_key
```


```python
_, __, keys = wayTags.audit_keys(osm_file, output=True, out_depth=20);
```

    Number of problematic keys:  0
    Number of keys not only lower case:  16
    List of keys not only lower case (first 20):
    	 fuel:GTL_diesel
    	 fuel:octane_95
    	 fuel:e85
    	 TMC:cid_58:tabcd_1:LCLversion
    	 fuel:octane_98
    	 osmarender:renderName
    	 TMC:cid_58:tabcd_1:Class
    	 fuel:e10
    	 CEMT
    	 fuel:octane_102
    	 toll:N3
    	 TMC:cid_58:tabcd_1:LocationCode
    	 old_name2
    	 fuel:HGV_diesel
    	 phone2
    	 fuel:octane_100
    Number of unique way types:  73
    List of types followed by number of keys per type plus 3 keys (first 20):
      Type: regular | keys: 242 | ['layer', 'long_name', 'rural']
      Type: destination | keys: 33 | ['ref:backward', 'symbol:to:forward', 'ref:to:lanes:forward']
      Type: recycling | keys: 16 | ['glass_bottles', 'batteries', 'plastic']
      Type: building | keys: 12 | ['type', 'use', 'design:note']
      Type: fuel | keys: 12 | ['octane_100', 'biogas', 'e10']
      Type: cycleway | keys: 10 | ['right', 'left', 'left:segregated']
      Type: addr | keys: 9 | ['city', 'postcode', 'country']
      Type: note | keys: 8 | ['water', 'opening_hours', 'de']
      Type: roof | keys: 8 | ['levels', 'material', 'direction']
      Type: parking | keys: 8 | ['condition:area', 'condition:left:capacity', 'condition:both']
      Type: railway | keys: 7 | ['lzb', 'pzb', 'radio']
      Type: service | keys: 7 | ['bicycle:rental', 'bicycle:diy', 'bicycle:second_hand']
      Type: source | keys: 6 | ['maxspeed', 'maxspeed:forward', 'overtaking']
      Type: maxspeed | keys: 6 | ['type', 'variable', 'forward']
      Type: turn | keys: 4 | ['lanes', 'forward', 'lanes:backward']
      Type: oneway | keys: 4 | ['conditional', 'foot', 'motor_vehicle']
      Type: contact | keys: 4 | ['phone', 'fax', 'email']
      Type: seamark | keys: 4 | ['type', 'harbour:category', 'small_craft_facility:category']
      Type: department | keys: 4 | ['small', 'airpressure', 'archery']
      Type: name | keys: 3 | ['de', 'etymology:wikidata', 'en']
    


```python
lookup_key(keys, 'phone')
```




    ['regular:phone',
     'regular:phone2',
     'contact:phone',
     'communication:mobile_phone']




```python
lookup_key(keys, 'fax')
```




    ['regular:fax', 'contact:fax']




```python
lookup_key(keys, 'mobil')
```




    ['regular:snowmobile', 'communication:mobile_phone']




```python
keys['contact']
```




    {'email', 'fax', 'phone', 'website'}




```python
keys['tele']
```




    set()



For auditing phone numbers we will consult the following keys:
+ phone  
+ phone2  
+ fax
+ contact:phone
+ contact:fax
+ communication:mobile
+ 


```python
lookup_key(keys, 'lane')
```




    ['regular:lanes',
     'lanes:backward',
     'lanes:forward',
     'turn:lanes',
     'turn:lanes:backward',
     'turn:lanes:forward',
     'destination:ref:to:lanes:forward',
     'destination:ref:lanes:backward',
     'destination:symbol:lanes:backward',
     'destination:symbol:lanes:forward',
     'destination:ref:to:lanes:backward',
     'destination:ref:lanes:forward',
     'destination:lanes:backward',
     'destination:lanes:forward',
     'parking:lane:right',
     'parking:lane:both',
     'parking:lane:left',
     'parking:lane',
     'bicycle:lanes:forward',
     'vehicle:lanes:forward']




```python
wayTags.unique_keys(keys)
```




    484




```python
wayTags.keys_double(keys, output=True);
```

    Type equals "regular" key  41 times.
    All types that equal a "regular" key: ['lanes', 'turn', 'destination', 'note', 'source', 'cycleway', 'maxspeed', 'overtaking', 'railway', 'oneway', 'priority_road', 'name', 'surface', 'workrules', 'maxweight', 'hgv', 'brand', 'toilets', 'building', 'parking', 'bicycle', 'motor_vehicle', 'capacity', 'wheelchair', 'operator', 'disused', 'footway', 'sidewalk', 'service', 'access', 'healthcare', 'bridge', 'vehicle', 'fee', 'social_facility', 'traffic_sign', 'ref', 'crossing', 'heritage', 'area', 'cemetery']
    


```python
wayTags.check4reg_keys(keys, output=True, out_depth=10);
```

    Number of 'regular' keys found in other types:  40
    Matched keys (first 10): 
    - email - found in:  {'contact:email'}
    - type - found in:  {'ship:type', 'operator:type', 'seamark:type', 'health_facility:type', 'piste:type', 'building:type', 'maxspeed:type', 'tower:type'}
    - area - found in:  {'parking:condition:area'}
    - website - found in:  {'contact:website'}
    - surface - found in:  {'cycleway:left:surface', 'footway:surface', 'cycleway:surface'}
    - shop - found in:  {'note:shop', 'disused:shop'}
    - hgv - found in:  {'maxspeed:hgv', 'source:maxspeed:hgv'}
    - overtaking - found in:  {'source:overtaking'}
    - capacity - found in:  {'parking:condition:left:capacity'}
    - ref - found in:  {'destination:ref:to', 'destination:ref:forward', 'destination:ref:to:forward', 'destination:ref:to:backward', 'destination:ref:to:lanes:forward', 'destination:ref:lanes:forward', 'destination:ref', 'railway:ref', 'destination:ref:lanes:backward', 'destination:ref:to:lanes:backward', 'destination:ref:backward'}
    


```python

```

### Audit way tag values


```python
pbl_values, missing_values = wayTags.audit_values(osm_file, output=True, out_depth=100)
```

    Missing values found for 0 nodes
    Problematic characters found in 84 keys.
    website: 171
    name: 101
    contact:website: 96
    opening_hours: 73
    phone: 73
    email: 31
    fax: 27
    source: 26
    operator: 25
    destination:backward: 21
    note: 21
    destination: 18
    contact:phone: 18
    destination:forward: 17
    turn:lanes:forward: 14
    addr:housenumber: 14
    created_by: 13
    turn:lanes:backward: 12
    turn:lanes: 12
    contact:email: 12
    maxspeed:conditional: 9
    ref: 9
    width: 9
    contact:fax: 9
    maxweight: 7
    brand: 7
    maxheight: 6
    level: 6
    fixme: 5
    sport: 5
    description: 5
    height: 5
    url: 5
    destination:lanes:backward: 4
    voltage: 4
    image: 4
    destination:lanes:forward: 4
    addr:street: 4
    note:name: 3
    destination:symbol: 3
    traffic_sign: 3
    roof:height: 3
    lines: 2
    note:vacant: 2
    wheelchair:description: 2
    surface: 2
    wikipedia: 2
    old_name: 2
    destination:colour:back: 1
    destination:colour:text: 1
    axle_load: 1
    meter_load: 1
    maxweight:conditional: 1
    TMC:cid_58:tabcd_1:LCLversion: 1
    frequency: 1
    hgv:conditional: 1
    lit: 1
    bicycle:conditional: 1
    motor_vehicle:conditional: 1
    roof:colour: 1
    brand:wikipedia: 1
    destination:symbol:backward: 1
    note:water: 1
    amenity: 1
    short_name: 1
    cuisine: 1
    service_times: 1
    wires: 1
    thw:lv: 1
    building:design:note: 1
    seamark:small_craft_facility:category: 1
    note:access: 1
    note:de: 1
    start_date: 1
    fee:conditional: 1
    oneway:conditional: 1
    seamark:name: 1
    comment: 1
    phone2: 1
    addr:housename:note: 1
    note:shop: 1
    cables: 1
    bus_lines: 1
    destination:symbol:lanes:forward: 1
    


```python
for key, values in ((x, pbl_values[x.lstrip('regular:')]) for x in lookup_key(keys, 'phone')):
    print(key, values, "\n")
```

    regular:phone {'+494121 93232', '+49 4121 50606', '+49 4123 2247', '+49 4122 2902', '+49 4126 2073', '+49 4123 9290577;+49 4123 9222240', '+49 4121 25455', '+49 4121 40940', '+49 4123 9295530', '+49 4121 461360', '+49 4121 77575', '+49 4121 87777', '+49 4121 50820', '+49 4123 8098436', '+49 4121 6440', '+49 4121 438121', '+49 162 6937120', '+49 4121 65432', '+49 4121 24256', '+49 4126 396010', '+49 4122 45050', '+49 4121 476860', '+49 4123 92300', '+49 4121 50773', '+49 4121 5796730', '+494121 94062', '+49 4122 54631', '+4915122377000', '+49 4121 45670', '+49 4121-82526', '+49 4121 4638510', '+49 4126 1274', '+49 4121 7807788', '+49/4121/21773', '+49 4121 233900', '+49 4123 4183', '+49 4121 482325', '+49 4121 6450', '+49 4121 50108', '+49 4121 45750', '+49 4121 5510', '+49 4121-78578', '+49412120511', '+49 4121 2623390', '+49 4121 45680', '+49 4121 643-0', '+49 4120 1500', '+49 4122 958031', '+49 4121 840014', '+49 4121 452373', '+49 4121 294-2150', '+49 (4123) 68 400', '+49 4121 7011220', '+49 4121 77878', '+49 4121 78537', '+49 4122 52612', '+49 4101 8548482', '+49 4122 460230', '+49 4121 21120', '+49 4121 4092-0', '+49 4123 2055', '+49 176 34 52 2724', '+49 4121 459990', '+49 4121 76172', '+49 4121 93113', '+49 4121 62696', '+49 4121 73206', '+49 4121 62885', '+49 4101 85666-0', '+49 4120 909760', '+49 4121 798 0', '+49 4121 72778', '+49 4121 470328'} 
    
    regular:phone2 {'+49 4122 460260'} 
    
    contact:phone {'+494121571157', '+494121572550', '+494121571800', '+49 40 2000 1090 00', '+494121571400', '+49 4121 70089-0', '+494121572300', '+49 4121 482150', '+49 4121 57998-0', '+49 4123 6880', '+49 4121-91213', '+49 4121 4619180', '+494121262430', '+49 4123 3295', '+49 4121 492279', '+49 4121 74553', '+494121572000', '+49 4121 85445'} 
    
    communication:mobile_phone set() 
    
    


```python
for key, values in ((x, pbl_values[x.lstrip('regular:')]) for x in lookup_key(keys, 'website')):
    print(key, values, "\n")
```

    regular:website {'www.moinbohne.de', 'http://www.pferdeklinik-hell-zeeuw.de', 'http://www.baeckerei-rohwer.de/#plink', 'www.bruecke-sh.de/', 'https://www.alsan.de/', 'https://gshainholz.lernnetz.de/', 'http://www.satec-baumaschinen.de/', 'gefluegelhof-neumann.de', 'www.htbg.de', 'http://www.fussspezialist-bornholdt.de/', 'https://www.nikolai-elmshorn.de/', 'www.ses-bahn.de', 'http://www.preuss-elektro.de', 'http://www.die-gruene-suchmaschine.de/Adresseintrag/97427-Tornesch-Hofladen-Meyer.html', 'https://baumschule-stahl.de', 'https://www.stadtwerke-elmshorn.de', 'https://www.premio.de/', 'https://www.lays-loft.de/', 'https://www.dsfotos.de/', 'https://www.fleischerei-fock.de/', 'http://www.sibirien.de/', 'https://www.kiga-zipfelmuetze.de/', 'http://www.segler-verein-elmshorn.de/', 'http://www.lights-events.de/', 'https://perspektive-jugendhilfe.de/', 'https://www.hachmann.de/', 'https://www.kibek.de/', 'https://www.steengmbh.de/', 'http://www.thomaskirche-elmshorn.de/', 'http://www.restaurant-sanmarino.de', 'https://kuehl-elmshorn.de/', 'http://www.toeverhuus.de', 'http://www.theoalbers.de', 'https://www.haus-godewind-elmshorn.de/', 'http://www.heilig-geist-wedel.de/pfarrei/uetersen/', 'www.eisvittoria.de/', 'https://www.koehler-fahrzeugbau.de/', 'http:\\\\www.horstmühle1.de', 'http://kuehl-elmshorn.de/', 'https://www.kuechencentrum-potschien.de/', 'https://www.daenischesbettenlager.de/', 'https://www.alarm-tec.de/', 'https://www.beckmann-feuerungsbau.de', 'https://www.heinrich-uhl.de/', 'http://simian-ales.com', 'https://www.mundfein.de/', 'https://www.thw-elmshorn.de/', 'https://www.emmausgemeinde-elmshorn.de/', 'http://www.praxisamhogenkamp.de', 'http://www.dittchenbuehne.de', 'https://www.interharz-deutschland.de/', 'https://www.reisegmbh.de/', 'https://www.crossfitelmshorn.com', 'http://hamann-holz.de', 'https://fc-elmshorn.de/', 'http://www.elektro-kelting.de', 'http://www.fahrrad-burmeister.de/', 'http://tankstelle.aral.de/tankstelle/tornesch/lise-meitner-allee-3/13136400', 'https://www.pfarreihlmartin.de', 'http://www.baeckerei-rohwer.de/', 'https://www.friedenskirchengemeinde-elmshorn.de/', 'http://guter-hirte.de/', 'http://www.gaertnerei-geisler.de/', 'http://www.seegarten-barmstedt.de', 'https://www.frs-tornesch.com', 'http://www.baumschule-lehmann.de', 'https://www.bellandris-rostock.de/', 'https://www.regiokliniken.de/leistungsspektrum/klinikum-elmshorn.html', 'http://www.kruemet.de/unternehmen/filialen/filiale-elmshorn/', 'www.awostromhaus.de', 'http://www.pflanzen-lohmann.de', 'www.asb-pinneberg-steinburg.de', 'protected.de', 'http://www.wsv-uetersen.de/', 'https://www.auto-strassburg.de/', 'https://www.baumschuledirekt.de/', 'https://www.klostersande.com', 'https://www.pieper-metallbau-gmbh.de/', 'http://www.rkish.de/', 'http://www.schaedlich-boethern.de', 'http://www.baeckerei-rohwer.de', 'https://www.autowerkstatt-barmstedt.de', 'www.gaertnerei-sievers.de', 'https://www.appel-elmshorn.de/', 'http://www.geruestbau-mohrdieck.de', 'https://www.sr-metallbau.com/', 'https://www.allround-planen.de/', 'https://www.gartenderhorizonte.de/', 'http://www.kostuemverleih-froschkoenig.de/', 'http://thormaehlen-landmaschinen.de/', 'www.tischlerei-harry-jeske.de', 'www.blanck-baumschule.de', 'https://www.paul-groth.com/', 'https://www.zimmerei-schamper.de/', 'https://www.dhl.de/de.html', 'https://fernsehmohr.de/', 'http://thomasbeton.de/', 'http://www.kinderhaus-elmshorn.net', 'http://www.berner-international.de/', 'https://www.mcdonalds.de/restaurant?url=elmshorn-lise-meitner-str-1&/de', 'http://www.feuerwehr-tornesch.de/ortswehr-ahrenlohe', 'https://www.mecotec.info', 'https://www.mixmarkt.eu/de/germany/maerkte/37/', 'https://www.aventer.biz/', 'http://www.ist-elmshorn.de', 'http://www.doellinghareico.de/', 'http://www.shuttle.eu/', 'https://www.zimmerei-hartz.de/', 'https://www.fillandroll.de/', 'https://www.svog-elmshorn.de', 'http://www.holsteingrill.de', 'http://autolackierer-bergner.de/', 'http://www.nord-soft.de', 'https://www.dannwisch.de/', 'https://www.toom-baumarkt.de/mein-markt/details/elmshorn/', 'https://www.bahl-gaerten.de/', 'http://www.sc-polymer.com/', 'https://www.friedenskirchengemeinde-elmshorn.de/kindergaerten', 'http://www.energieberatung-leuschner.de', 'www.eb-werbesysteme.de', 'http://www.salon-warthoefer.de', 'https://www.pape-rahn.de/', 'http://www.hansa-ventilatorenbau.de/', 'https://www.kellner-treppen.de/', 'http://semmelhaack-logistik.de/', 'https://www.reiter-apotheke.de/', 'https://www.die-power-pfoten.de/', 'https://markttreff-sh.de/de/markttreff-heidgraben', 'https://www.das-netzcafe.de/', 'https://www.regiokliniken.de/leistungsspektrum/pflege-und-betreuung/johannis-hospiz-ggmbh.html', 'http://zur-ellerhooper-linde.de', 'https://www.waehling-bestattungen.de', 'https://www.thiespropeller.de/', 'https://www.kindergarten-die-kleinen-biber-bevern.de', 'https://www.stadttheater-elmshorn.de/', 'https://www.ihk-schleswig-holstein.de/servicemarken/ueber_uns/vor_ort/geschaeftsstellen_kiel/anfahrtsbeschreibung-ihk-elmshorn/1354770', 'https://pflanzen-oase.regional.de/', 'https://www.rewe.de/', 'https://www.voltrad.de/', 'https://www.tctornesch.de/', 'http://www.bohn-segel.de/', 'tischlerei-holzfeind.de', 'http://www.niebuhrelmshorn.de/', 'https://www.zum-tannenbaum.de/', 'https://www.feuerwehr-kiebitzreihe.de/', 'https://www.kremerglismann.de/', 'http://www.pbe-electronic.de/', 'www.stenzel-feinwerktechnik.de', 'https://birkenhain.eatbu.com/', 'https://www.honda-rein.de/', 'https://www.erc09.de/', 'https://kunstraum.kirstenpetersen.de', 'http://www.astrids-hundeschule.de', 'https://www.rewe.de/marktseite/barmstedt-stadt/541786/rewe-markt-marktstrasse-2-10/', 'http://thw-barmstedt.de/', 'https://www.regio-pflege.de/home.html', 'https://www.muk-elmshorn.de/', 'https://www.regaflex.de/', 'http://www.wse-elmshorn.de', 'http://www.victor-international.com', 'http://www.veloflex.de/', 'http://www.rix-tiefbau.de', 'http://www.jahnckes-messeservice.de/', 'www.schuetzenverein-tornesch.de', 'https://de-de.facebook.com/Restaurant-Caf%C3%A9-Bar-Monroes-856835947708698/', 'www.feuerwehr-klein-offenseth-sparrieshoop.de', 'https://www.wak-sh.de/', 'https://www.rs-uetersen.lernnetz.de/', 'https://www.littau-gmbh.de', 'https://www.shop-ar.de/', 'https://www.veloskop.info/'} 
    
    contact:website {'http://www.biernatzki.de/', 'http://www.jim-gmbh.de/', 'http://www.jamil-automobile.de/', 'http://von-roenne-shop.com', 'http://www.lenggenhager-bestattungen.de/', 'http://www.gebrueder-asmussen.de/', 'http://www.ebisautos.de/', 'http://www.gc-gruppe.de/de/unternehmen/arens-stitz/locations/abex-koelln-reisiek-bei-elmshorn', 'http://oehlers.de/', 'http://www.stueben-muehle.de', 'http://www.luechau.de/standorte/elmshorn/', 'http://www.loeffler-kartonagen.de/', 'http://www.fliesen-baas.de/', 'http://gorra-krause.de/', 'http://www.auras-metallbau.de/', 'http://www.dbl-ahrens.de', 'http://www.viereck.com', 'https://www.aldi-nord.de/tools/filialen-und-oeffnungszeiten/schleswig-holstein/elmshorn/wedenkamp-9-b.html', 'http://www.hotel-royal-elmshorn.de/', 'http://www.fritz-bootsmotoren.de', 'http://www.knutzen.de/', 'http://www.ramelow.com/haeuser/elmshorn.php', 'http://www.gehrls-elmshorn.de/', 'http://www.exler-lackiertechnik.de/', 'http://www.flora-elmshorn.de/', 'http://www.seifert-automobile.de', 'http://www.modellbahn-elmshorn.de/', 'http://www.gruening-elmshorn.de/', 'http://www.kunze-ladenbau.de', 'http://www.depla-messebau.de/', 'http://www.timm-gravuren.de/', 'http://www.keradent.de/', 'http://www.kiga-klein-nordende.de/', 'http://www.warnsholz.de/', 'http://www.ntg-online.com/', 'http://www.kerkamm.com', 'https://www.cmtechnologies.de/', 'http://www.ch-fitness.de/', 'http://www.jawoll.de/', 'http://www.ofenhaus-elmshorn.de', 'https://www.kerkamm-markenhaus.de/', 'http://www.fachklinik-bokholt.de', 'http://www.hiplo.de', 'http://www.awo-pflege-sh.de/', 'http://vgr-gruppe.de/', 'https://www.amt-rantzau.de/', 'http://www.hein-glaserei.de/', 'http://www.bergmann-soehne.de/', 'http://thw-barmstedt.de', 'http://www.cza.de/', 'https://www.futterhaus.de/service/filialen/elmshorn-sibirien/', 'http://www.blw-aktuell.de/Bezirke/Unterbezirke-Hamburg/Elmshorn', 'http://www.boerger-anlagenbau.de/', 'http://www.waldkindergarten-elmshorn.de/', 'http://vab-vakuum.de/', 'http://deg-dach.de/standorte/standorte/deg-elmshorn-koelln-reisiek/', 'https://www.hellermanntyton.de', 'http://sued.kiapartner.de/', 'http://www.toukon.de/', 'http://www.autohaus-elmshorn.de/', 'http://www.faw.de/', 'http://www.volvo-pinneberg.de/', 'http://www.autozentrum-henneberg.de/', 'http://www.autohaus-tiedemann.de/', 'http://lieth19.de/', 'http://www.mount-everest-tea.de', 'http://www.marktpassage-elmshorn.de/', 'http://www.erbst-metallbau.de/', 'http://www.wickersheim-maschinenbau.de', 'http://jess-coaching.de/', 'http://www.keller-feinwerktechnik.de/', 'http://www.hbt-kg.de/', 'http://www.niebuhr-elmshorn.de', 'http://www.kgv-elmshorn.de', 'http://www.ltc-elmshorn.de/', 'http://www.zoohaus-elmshorn.de/', 'http://www.zoller-elektrotechnik.de/', 'http://www.nordhausen-elmshorn.de', 'http://www.autoglas-elmshorn.de/', 'http://www.gewerbehof-offenau.de/', 'http://www.thw-elmshorn.de', 'http://www.akrus.de', 'http://www.meusel-hydraulik.de/', 'http://www.egger-im-buero.de/', 'http://www.capol.de', 'http://www.klauslorenz.de', 'http://www.hell-kayser.de/', 'http://mail-marketing-service.de/', 'http://www.lebenshilfe-online.de/', 'http://www.landahl.de/', 'http://www.kuehl-arbeitsbuehnen.de/', 'http://www.endochoice.de/', 'http://dreid.de', 'http://www.rehaforum.de/', 'http://www.ebe-elmshorn.de/', 'http://www.opelkroeger.de'} 
    
    


```python
for key, values in ((x, pbl_values[x.lstrip('regular:')]) for x in lookup_key(keys, 'name')):
    print(key, values, "\n")
```

    regular:long_name set() 
    
    regular:old_name {'Kurbad W. Güthe', 'Kraft Foods; Mondelēz International'} 
    
    regular:reg_name set() 
    
    regular:loc_name set() 
    
    regular:alt_name set() 
    
    regular:short_name {'cce.'} 
    
    regular:noname set() 
    
    regular:official_name set() 
    
    regular:old_name2 set() 
    
    regular:name {'Boje-C.-Steffen-Gemeinschaftsschule Elmshorn', 'J.-P.-Lange-Straße', "McDonald's-Kundenparkplatz", 'Holstendorf (Gem. Seester)', 'Soziale Projekte e.V. Gemeinnützige Organisation', 'Kiefer&Zehner', 'Gorra & Krause', 'May & Olde', "Hartz'sche Wiese", 'Evangelischer Kindergarten St. Nikolai', 'Wolfsteller & Wulff', 'IDS Internet-Dienstleistung-Service S.B.', 'Mail Boxes Etc.', 'Kleingärtnerverein Elmshorn e.V.', "Ebi's Autos", 'Fahrrad - Service J. Struckmeyer', "Op'n Knüll", 'Maria-S.-Merian-Straße', "Lay's Loft", 'Tankschutz J. Meier GmbH', 'Dr. med. dent. Rolf Junge', 'Wasser-Sportverein-Elmshorn e. V.', 'SHBB / LBV Landwirtschaftlicher Buchführungsverband', 'Berufliche Schule Elmshorn, Europaschule', 'Besucherparkplatz des HdB, AWO', 'jess.PT Lounge', 'Elmshorner Schützengilde v. 1653 e.V.', 'Heidgrabener Sportverein e.V.', "Martina's Bastelparadies", 'S&C Polymer', 'P&R Steindammpark', 'Tierklinig Dr. Hell / Dr. Zeeuw', "Yvonne's Frisörstudio", 'Premio Reifen+Autoservice', 'Bf. Elmshorn (ZOB)', "Meyer's Hof", 'Dr. Schroff-Weg', "Monroe's", 'Johs. Auras Stahlbau', 'Inghild Drews, Dr. Manfred Drews', "McDonald's", 'Hillmann & Ploog GmbH', 'Gebr. Schmidt', 'P+R Tornesch', 'Agentur für Arbeit, BIZ, Jugendberufsagentur', 'Brücke Elmshorn e.V.', 'Holstendorf (Gem. Klein Nordende)', 'Schädlich + Böthern Treppenbau', 'Heuer, der Elbbäcker', "Up'n Feld", 'Synentec, AC-Solution', 'Kindel & Wetzel', 'Landahl & Baumann Spielwaren GmbH', 'Mr. Grande', "Grüne Kugel - Lescow's Pflanzenwelt", 'J.-H.-Fehrs-Weg', "Bi'n Himmel", 'F. Brackmann-Gräf & F. Gräf', 'Sch.', 'Elmshorner Männer-Turnverein von 1860 e. V.', 'Sattlerei Krüger, Rollator Laden', 'Brunsbüttel - Hamburg/Nord', 'A.T.U', 'Wessels + Müller Fahrzeugteile und mehr', 'DLRG Barmstedt e.V.', 'Ev.-Luth. Kindertagesstätte Garten Eden', 'Gebr. Pries', 'Loll Feinmechanik GmbH / Loll Mechatronik GmbH', 'E. Sander', 'E.-L.-Meyn-Straße', 'Elmshorner Ruder-Club von 1909 e.V.', 'St. Nikolai', 'Norddeutsche Fachschule für Gartenbau, Außenstelle Berufliche Schule Elmshorn', 'Karl H. Bartels GmbH Maschinenhersteller', 'Reitstall Perau/Jacobs', 'Amt für Kultur und Weiterbildung, Volkshochschule', 'E&B', 'D. Thun Bauunternehmung', 'Kreisjugendring Pinneberg e.V.', 'Ev. Kindergarten Bugenhagen', 'Nutracorp GmbH & Co. KG', 'Arens & Stitz', 'Katholische Kindertageseinrichtung St. Marien', 'Döllinghareico GmbH & Co. KG', 'türkisch islamischer Kulturverein e.V. Elmshorn', 'B+K Wohnkultur u. Boge/Clasen', 'Tierschutz Verein Elmshorn und Umgebung e.V.', "Rock 'n' Bowl", 'Schützenverein Tornesch v. 1954 e.V', 'Forum Baltikum-Dittchenbühne e.V.', 'Segler Verein Elmshorn e.V.', 'Mail + Marketing Service', 'Autoport Finck & Claus', 'Tennisclub Tornesch e.V.', 'JA. Schuldt Baumschulen', 'Nordhausen Bad & Heizung', 'Islamisches Bildungs- und Integrationszentrum e.V.', 'Cramer + Cramer 2 C Möbelfabrik', 'Lawn-Tennis-Club Elmshorn e.V.', 'Fill & Roll', 'Splendid Drinks G+L Elmshorn'} 
    
    note:name {'es gibt kein offizielles Straßenschild vor Ort, an einem Stromverteiler der in der Straße steht wird die Straße mit "b" geschrieben, woanders mit "p"', 'Der reg_name, sowie ggf. der loc_name sind dem zugehörigen Wikipediaartikel entnommen.', '"Töpferstube" ist über dem Eingang eingraviert'} 
    
    source:name set() 
    
    name:de set() 
    
    name:etymology:wikidata set() 
    
    name:en set() 
    
    addr:housename:note set() 
    
    addr:housename set() 
    
    disused:name set() 
    
    seamark:name {'Segler Verein Elmshorn e.V.'} 
    
    


```python
for key, values in ((x, pbl_values[x.lstrip('regular:')]) for x in lookup_key(keys, 'addr')):
    print(key, values, "\n")
```

    addr:city set() 
    
    addr:postcode set() 
    
    addr:country set() 
    
    addr:housenumber set() 
    
    addr:street set() 
    
    addr:suburb set() 
    
    addr:housename:note set() 
    
    addr:interpolation set() 
    
    addr:housename set() 
    
    


```python
for key, values in ((x, pbl_values[x.lstrip('regular:')]) for x in lookup_key(keys, 'opening')):
    print(key, values, "\n")
```

    regular:opening_hours {'Mo-Fr 09:00-19:00, Sa 09:00-16:00', 'Mo-Th 07:00-18:00; Fr 07:00-16:00; Sa 08:00-12:00', 'Mo-Fr 07:00-12:00, Mo-Th 13:00-17:00, Fr 13:00-15:00', '"Nur nach Terminvereinbarung."', 'Mo-Fr 09:00-12:00, Tu-Fr 14:00-18:00', 'Tu-Sa 17:00-22:00; Su 11:00-21:00; Mo off', 'Mo,We-Fr 10:00-18:00; Sa 09:00-13:00', 'Mo-Fr 09:00-18:00; Sa 09:00-12:30; PH off', 'Mo-Fr 13:00-18:00; Sa 09:00-13:00', 'Mo,Tu,We,Th 08:00-15:30, Fr 08:00-12:00, "Nach Vereinbarung"', 'Mo-Sa 11:00-22:30, Su 12:00-22:30', 'We-Su 12:00+', 'Mo-Fr 09:30-18:30; Sa 09:30-14:00', 'Mo-Fr 09:00-12:00,14:00-18:00; Sa 09:00-14:00', 'Mo-Fr 9:00-18:00; Sa 9:00-12:30', 'Mo-Fr 09:30-19:00, Sa 09:30-16:00', 'Mo-Fr 09:00-16:00; Sa 09:00-13:00', 'Mo-Fr 10:00-12:00,16:00-18:00', 'Mo-Sa 11:00-23:00; Su,PH 12:00-23:00', 'Mo-Sa 08:00-20:00; PH off', 'Mo-Fr 05:00-18:00; Sa 05:00-12:00; Su 08:00-11:00', 'Mo-Fr 09:00-19:00; Sa 09:00-18:00', '24/7', 'Mo-Fr 10:00-20:00; Sa 09:30-20:00', 'Mo-Fr 9:00-12:30,14:00-18:30; Sa 09:00-13:00; PH off', 'We 14:00-17:00; Su 10:00-12:00', 'Mo-Fr 08:00-19:00; Sa 09:00-14:00', 'Mo-Fr 08:00-18:30, Sa 08:00-13:00', 'Mo-Fr 08:00-18:30; Sa 08:00-12:30', '"Laut Website derzeit nur geschlossen\u200b Veranstaltungen."', 'Mo-We 10:00-18:30; Th 10:00-19:30; Fr 10:00-18:30; Sa 10:00-14:00', 'Mo-Th 07:00-17:00; Fr 07:00-14:00', 'Mo 07:00-12:30; Tu-Fr 07:00-18:30; Sa 07:00-12:00', 'Mo-Fr 08:00-18:00; Sa 09:00-13:00', 'Tu,Fr 09:00-11:00,15:00-18:00', 'Mo,Tu,We,Fr 08:00-12:30,14:00-18:00; Th 08:00-12:30; Sa 09:00-13:00; PH off', 'Mo-Fr 8:30-19:00, Sa 9:30-16:00', 'Mo-Fr 09:00-19:00; Sa 09:00-16:00; PH off', 'Sep-May: Mo,Tu,Th,Fr 06:30-21:00, Sep-May: We 09:00-21:00, Sep-May: Sa,Su,PH 08:00-19:00', 'Mo-Fr 09:00-19:00; Sa 09:00-18:00; Su,PH 11:00-16:00', 'Mo-Fr 06:00-18:00; Sa 06:00-12:00; Su 07:00-12:00', 'Mo-Th 08:00-20:00; Fr 08:00-22:00; Sa 08:00-20:00', 'Mo-Fr 07:00-18:30, Sa 07:00-13:00; PH off', '"Hallenzeiten werden für Vereine und Veranstaltungen durch die Stadt Elmshorn vergeben."', 'Mo-Tu 08:30-12:30, 14:30-16:00; We 08:30-12:30; Th 08:30-12:30, 14:30-18:00; Fr 08:30-12:30, 14:30-16:00', 'Mo,Tu,Th 08:30-18:00, We,Fr 08:30-16:00', 'Mo-Fr 05:00-18:00, Sa 05:00-12:30, Su 08:00-11:00', 'Mo-Th 08:00-20:00; Fr 08:00-22:00; Sa 08:00-20:00; PH off', 'Mo-Fr 09:00-12:00,14:00-18:00; Sa 10:00-13:00', 'Mo-Fr 06:00-21:00; Sa 07:00-21:00; Su 08:00-21:00', 'Mo-Fr 10:00-19:00; Sa 10:00-16:00', 'Mo-Sa 17:00-24:00, Su 12:00-15:00,17:00-24:00', 'Mo-Fr 09:30-18:30, Sa 09:30-18:00', '"nach Trainingszeiten der Vereine"', 'Mo-Th 09:00-01:00, Fr,Sa 09:00-03:00, Su 10:00-01:00', 'Mo-Tu 12:30-18:00; Th-Fr 12:30-18:00; Sa 9:00-12:30; Su 10:00-12:00', 'Mo-Fr 09:00-19:00; Sa 09:00-16:00', 'Mo-Fr 11:00-21:00, Sa-Su 11:30-21:00', 'Mo,Th 08:30-18:00, Tu,We,Fr 08:30-16:00', 'Mo-Fr 07:00-17:00; Sa 07:00-14:00', 'Mo-Fr 06:00-22:00; Sa,Su 07:00-22:00', 'Mo-Fr 07:00-18:30; Sa 07:00-13:00', 'Jan-Feb: Mo-Fr 13:00-17:00, Sa 9:00-13:00;Mar-Dec: Mo-Fr 9:00-18:00, Sa 9:00-14:00;Dec 04-Dec 17: Su 10:00-17:00', 'Apr-Sep: Mo-Su,PH 10:00-20:00', 'Mo-Su,PH 06:30-23:00', 'Mo-Su,PH 06:00-22:00', 'Mo-Fr 08:00-21:00; PH closed', 'Mo-Fr 08:00-12:30, Mo-Th 13:00-17:00', 'Mo-Fr 09:00-18:00; Sa 09:00-14:00', 'Mo-Fr 09:30-19:00, Sa 09:30-18:00; PH off', 'Tu-Fr 09:00-12:00,14:00-18:00; Sa 09:00-12:00', 'Sa-Th 00:00-23:59; Fr 00:00-08:00, 13:00-23:59', 'Mo-Sa 07:00-20:00; PH off'} 
    
    note:opening_hours set() 
    
    


```python
for key, values in ((x, pbl_values[x.lstrip('regular:')]) for x in lookup_key(keys, 'mobile')):
    print(key, values, "\n")
```

    regular:snowmobile set() 
    
    communication:mobile_phone set() 
    
    


```python
street, postcode, coutries = wayTags.audit_addr(osm_file)
```


```python
len(street)
```




    833




```python
street
```




    {'Aalkamp',
     'Abbau',
     'Achtern Hoff',
     'Achtern Hollernbusch',
     'Achtern Knick',
     'Achtern Ollerloh',
     'Achterskamp',
     'Achterstraße',
     'Adenauerdamm',
     'Adolfstraße',
     'Adolph-Kolping-Straße',
     'Agnes-Karll-Allee',
     'Ahornallee',
     'Ahornring',
     'Ahornweg',
     'Ahrenloher Straße',
     'Ahrenloher Weg',
     'Akazienweg',
     'Albert-Hirsch-Straße',
     'Albert-Johannsen-Straße',
     'Albert-Schweitzer-Straße',
     'Allee',
     'Alma-Mahler-Weg',
     'Altendeich',
     'Altendeichsweg',
     'Altenmühlen',
     'Alter Markt',
     'Alter Schulweg',
     'Alter Sportplatz',
     'Alter Steig',
     'Am Bast',
     'Am Beek',
     'Am Besenbeker Moor',
     'Am Bleichgraben',
     'Am Brahm',
     'Am Butterberg',
     'Am Deich',
     'Am Dornbusch',
     'Am Düwelsknick',
     'Am Eckerholz',
     'Am Eggernkamp',
     'Am Eiskeller',
     'Am Erlengrund',
     'Am Felde',
     'Am Fischteich',
     'Am Fliederbusch',
     'Am Forst',
     'Am Friedhof',
     'Am Fuchsberg',
     'Am Gemeindezentrum',
     'Am Grünen Wald',
     'Am Kamp',
     'Am Karpfenteich',
     'Am Maisacker',
     'Am Markt',
     'Am Moor',
     'Am Park',
     'Am Raaer Moor',
     'Am Radebrooksbach',
     'Am Redder',
     'Am Rosengarten',
     'Am Rosenhof',
     'Am Schäferfeld',
     'Am Schäferhof',
     'Am Schützenplatz',
     'Am Seepferdchen',
     'Am Seeth',
     'Am Sender',
     'Am Steinberg',
     'Am Teich',
     'Am Wald',
     'Am Wasserwerk',
     'Am Wiesengrund',
     'Am Wischhof',
     'Am alten Sportplatz',
     'Amalie-Schoppe-Weg',
     'Amandastraße',
     'Amselstraße',
     'Amselweg',
     'An der Autobahn',
     'An der Bahn',
     'An der Bundesstraße',
     'An der Heide',
     'An der Hofkoppel',
     'An der Kirche',
     'An der Klosterkoppel',
     'An der Kämpe',
     'An der Oberau',
     'An der Ost-West-Brücke',
     'An der Post',
     'An der Schule',
     'An der Tannenkoppel',
     'An der alten Mühle',
     'Anne-Frank-Straße',
     'Anne-Frank-Weg',
     'Annette-von-Droste-Hülshoff-Straße',
     'Ansgarstraße',
     'Apenrader Straße',
     'Asperhorner Weg',
     'Auenland',
     'Auf dem Flidd',
     'August-Bebel-Platz',
     'August-Christen-Straße',
     'Austraße',
     'Auweg',
     'Auwisch',
     'Bachstraße',
     'Bahnhofstraße',
     'Barkhörner Weg',
     'Barlachring',
     'Barmstedter Straße',
     'Barmstedter Wohld',
     'Bauerweg',
     'Baumschulenweg',
     'Baumschulweg',
     'Beekenblick',
     'Beeklohe',
     'Beethovenstraße',
     'Bei der Alten Mühle',
     'Bei der Alten Post',
     'Beim Reihergehölz',
     'Bekenreihe',
     'Bentkrögener Straße',
     'Bergkoppel',
     'Bergstraße',
     'Bergtwiete',
     'Berliner Straße',
     'Bertha-von-Suttner-Ring',
     'Bertha-von-Suttner-Straße',
     'Bertolt-Brecht-Ring',
     'Beselerstraße',
     'Besenbek',
     'Besenbeker Straße',
     'Besenheide',
     'Bettina-von-Arnim-Straße',
     'Bi de Möhl',
     'Bi de Schünkoppel',
     'Biernatzkistraße',
     'Binsenweg',
     'Birkenallee',
     'Birkengrund',
     'Birkenstieg',
     'Birkenweg',
     'Bismarckstraße',
     'Bleekerstraße',
     'Blücherstraße',
     'Bockelpromenade',
     'Boizenburger Weg',
     'Bokholter Damm',
     'Bookhorstweg',
     'Bornbarg',
     'Bornhöftstraße',
     'Bornkamp',
     'Borstelweg',
     'Botterhörn',
     'Brahmsstraße',
     'Bredenmoorweg',
     'Breiter Weg',
     'Breslauer Straße',
     'Brunnenallee',
     'Brunnenstraße',
     'Brunnenweg',
     'Buchentwiete',
     'Buchenweg',
     'Buchsbaumweg',
     'Bullendorf',
     'Bullendorfer Weg',
     'Bundesstraße',
     'Bundesstraße 5',
     'Burdiekstraße',
     'Busch',
     'Buschkamp',
     'Buschweg',
     'Bussardweg',
     'Butendiek',
     'Böttcherweg',
     'Bültenweg',
     'Bürgermeister-Diercks-Straße',
     'Bürgermeister-Tesch-Straße',
     'Carl-Zeiss-Straße',
     'Carlo-Schmid-Weg',
     'Catharinenstraße',
     'Charlotte-Niese-Weg',
     'Chemnitzstraße',
     'Christa-Wehling-Weg',
     'Christian-Junge-Straße',
     'Clara-Schumann-Weg',
     'Claus-Hinrich-Dieck-Straße',
     'Claus-Reumann Weg',
     'Dachsweg',
     'Dahl',
     'Daimlerstraße',
     'Damm',
     'Dannwisch',
     'Danziger Straße',
     'Deepentwiete',
     'Dehlerweg',
     'Dethlefsenstraße',
     'Diamantstraße',
     'Diertgahren',
     'Dietrich-Bonhoeffer-Straße',
     'Dohrmannweg',
     'Dorfstraße',
     'Dovenmühlen',
     'Dr. Schroff-Weg',
     'Drei Eichen',
     'Dreieichen',
     'Drosselgasse',
     'Drosselkamp',
     'Drosselweg',
     'Dünenweg',
     'Düsterlohe',
     'E.-L.-Meyn-Straße',
     'Eckermannstraße',
     'Ede-Menzler-Weg',
     'Eggerstedtsberg',
     'Eichendorffweg',
     'Eichenhof',
     'Eichenkamp',
     'Eichenstieg',
     'Eichenweg',
     'Eichhörnchenweg',
     'Eichstraße',
     'Elbinger Straße',
     'Elfenstieg',
     'Elisabeth-Selbert-Straße',
     'Ellerngrund',
     'Elmshorner Straße',
     'Emil-Nolde-Straße',
     'Ergliring',
     'Erhardweg',
     'Erich-Ollenhauer-Weg',
     'Erich-Schulz-Weg',
     'Erlengrund',
     'Erlenweg',
     'Ernst-Abbe-Straße',
     'Ernst-Barlach-Straße',
     'Ernst-Behrens-Straße',
     'Eschenweg',
     'Esinger Straße',
     'Esinger Weg',
     'Esmarchstraße',
     'Falkenweg',
     'Fanny-Mendelssohn-Straße',
     'Farmers Ring',
     'Fasanenstieg',
     'Fasanenweg',
     'Faunstieg',
     'Feenstieg',
     'Fehrsstraße',
     'Feldfurth',
     'Feldstraße',
     'Ferdinand-Hanssen-Weg',
     'Finaleweg',
     'Finkenburg',
     'Finkenstieg',
     'Finkenweg',
     'Fischerweg',
     'Flamweg',
     'Fliederweg',
     'Florapromenade',
     'Forellenring',
     'Franz-Marc-Straße',
     'Friedensallee',
     'Friedenstraße',
     'Friedhofstraße',
     'Friedlandstraße',
     'Friedrich-Engels-Straße',
     'Friedrich-Naumann-Weg',
     'Friedrichstraße',
     'Fritz-Erler-Weg',
     'Fritz-Höger-Ring',
     'Fritz-Lau-Weg',
     'Fritz-Reuter-Straße',
     'Fritz-Reuter-Weg',
     'Fritz-Straßmann-Straße',
     'Fritz-Thiedemann-Weg',
     'Fröbelstraße',
     'Fuchsberger Allee',
     'Fuchsberger Damm',
     'Förn Sandweg',
     'Förstkamp',
     'Gadebuschweg',
     'Galgenberg',
     'Gartenecke',
     'Gartenkamp',
     'Gartenstraße',
     'Gartenweg',
     'Gebrüderstraße',
     'Geelbeksdamm',
     'Geestkamp',
     'Gerberstraße',
     'Gerhard-Schröder-Straße',
     'Gerhardstraße',
     'Gerlingweg',
     'Geschwister-Scholl-Straße',
     'Ginsterweg',
     'Glasenberg',
     'Glashofkamp',
     'Godewindweg',
     'Goethestraße',
     'Goldbekstraße',
     'Gooskamp',
     'Gorch-Fock-Straße',
     'Grauer Esel',
     'Grenzstraße',
     'Grenzweg',
     'Grotkamp',
     'Große Gärtnerstraße',
     'Großendorfer Straße',
     'Großer Kamp',
     'Großer Moorweg',
     'Großer Sand',
     'Großer Wulfhagen',
     'Grönlandstraße',
     'Gustav-Heinemann-Straße',
     'Gärtnerstraße',
     'Gärtnerweg',
     'Haberkamp',
     'Habichtweg',
     'Haderslebener Straße',
     'Hafenstraße',
     'Haferkamp',
     'Haidmoor',
     'Hainholter Schooltwiete',
     'Hainholz',
     'Hainholzer Damm',
     'Hainholzer Schulstraße',
     'Hamburger Straße',
     'Hamsterweg',
     'Handwerkerallee',
     'Hanredder',
     'Hans-Böckler-Straße',
     'Hans-Dössel-Weg',
     'Hasenbusch',
     'Hasenkamp',
     'Hasenstieg',
     'Hasentwiete',
     'Hasenweg',
     'Hasweg',
     'Hauen',
     'Hauptstraße',
     'Hauskoppel',
     'Hausweide',
     'Hebbelplatz',
     'Hebbelstraße',
     'Hedwig-Kreutzfeldt-Weg',
     'Heederbrook',
     'Heidesiedlung',
     'Heideweg',
     'Heidgrabener Weg',
     'Heidkamp',
     'Heidkoppel',
     'Heidkoppelweg',
     'Heidmühlenweg',
     'Heidweg',
     'Heimstättenstraße',
     'Heinrich-Böll-Straße',
     'Heinrich-Hauschildt-Straße',
     'Heinrich-Hertz-Straße',
     'Heinrich-Wagner-Straße',
     'Heinrich-von-Brentano-Weg',
     'Heinrichstraße',
     'Helene-Wessel-Straße',
     'Helgoländer Straße',
     'Hellweg',
     'Hellwieser Chaussee',
     'Hemdinger Straße',
     'Henry-Dunant-Ring',
     'Hermann-Ehlers-Weg',
     'Hermann-Löns-Weg',
     'Hermann-Sudermann-Allee',
     'Hermann-Weyl-Straße',
     'Hermelinweg',
     'Heussweg',
     'Hinter den Eichen',
     'Hinterstraße',
     'Hochfeldstraße',
     'Hof Bokhorst',
     'Hof Hanredder',
     'Hofweg',
     'Hogenkamp',
     'Hohe Lieth',
     'Holstendorf',
     'Holstenplatz',
     'Holstenring',
     'Holstenstraße',
     'Holunderstraße',
     'Holunderweg',
     'Holzweg',
     'Horster Landstraße',
     'Horstheider Weg',
     'Horstmühle',
     'Hoyerstraße',
     'Hypatia-Straße',
     'Högertwiete',
     'Hörnweg',
     'Höseleck',
     'Höselweg',
     'Hülsenkoppel',
     'Iltisweg',
     'Im Busch',
     'Im Feld',
     'Im Grünen Tale',
     'Im Hauen',
     'Im Köllner Feld',
     'Im Wiesengrund',
     'Im Winkel',
     'In de Hörn',
     'Ingeborg-Bachmann-Weg',
     'Ingwer-Paulsen-Straße',
     'Irena-Sendler-Straße',
     'Jahnstraße',
     'Jittkamp',
     'Jochen-Klepper-Straße',
     'Johannesstraße',
     'Julius-Leber-Straße',
     'Jungfer-Telsche-Weg',
     'Justus-von-Liebig-Straße',
     'Jägerstraße',
     'Jündewatter Straße',
     'Jürgen-Siemsen-Straße',
     'Jürgenstraße',
     'Kahlkes Weg',
     'Kalberhörn',
     'Kaltenhof',
     'Kaltenweide',
     'Kampstraße',
     'Kantstraße',
     'Karkhorst',
     'Karl-Carstens-Ring',
     'Karl-Ernst-Levy-Weg',
     'Karlsbader Straße',
     'Kassbeerentwiete',
     'Kastanieneck',
     'Kastanienhof',
     'Kastanienring',
     'Kastanienweg',
     'Katharinenstraße',
     'Kiebitzreiher Chaussee',
     'Kieferneck',
     'Kiefernstieg',
     'Kiefernweg',
     'Kieleck',
     'Kirchenstieg',
     'Kirchenstraße',
     'Kirschbaumweg',
     'Klaus-Groth-Promenade',
     'Klaus-Groth-Straße',
     'Klein-Nordender-Weg',
     'Kleine Gärtnerstraße',
     'Kleiner Moorweg',
     'Kleiststraße',
     'Klosterdamm',
     'Klosterhof',
     'Klostersande',
     'Knelltwiete',
     'Kokoschkaweg',
     'Konrad-Struve-Straße',
     'Koppeldamm',
     'Kortenhagen',
     'Kreuzmoor',
     'Kreuzweg',
     'Krittelmoor',
     'Kruck',
     'Krumme Straße',
     'Krummer Weg',
     'Krögers Kuhle',
     'Krückauweg',
     'Krützkamp',
     'Kuhberg',
     'Kuhlenkamp',
     'Kuhlenstraße',
     'Kuhlenweg',
     'Kummerfelder Weg',
     'Kurt-Tucholsky-Weg',
     'Kurt-Wagener-Straße',
     'Kurzenmoor',
     'Kurzenmoorer Chaussee',
     'Käppen-Meyn-Platz',
     'Käthe-Kollwitz-Allee',
     'Käthe-Kollwitz-Platz',
     'Käthe-Mensing-Straße',
     'Köhnholz',
     'Köllner Chaussee',
     'Köllner Weg',
     'Königsberger Straße',
     'Königstraße',
     'Küsterkamp',
     'Lander',
     'Lange Straße',
     'Langelohe',
     'Langenmoor',
     'Lauenberg',
     'Lehmhörn',
     'Lehmkuhlen',
     'Lerchenfeld',
     'Lerchenstraße',
     'Lerchenweg',
     'Lessingstraße',
     'Libellenbogen',
     'Liebermannweg',
     'Lieth',
     'Liether Feldstraße',
     'Liether Moor',
     'Liether Ring',
     'Liethmoor',
     'Ligusterweg',
     'Liliencronstraße',
     'Lilienstraße',
     'Lindenallee',
     'Lindenstraße',
     'Lindentwiete',
     'Lindenweg',
     'Lise-Meitner-Allee',
     'Lise-Meitner-Straße',
     'Lohe',
     'Loheisterweg',
     'Lohkamp',
     'Lohmannweg',
     'Lornsenstraße',
     'Lotusblüte',
     'Louis-Mendel-Straße',
     'Louise-Schroeder-Ring',
     'Louise-Schroeder-Straße',
     'Ludwig-Meyn-Straße',
     'Ludwigsluster Weg',
     'Luise-Schenck-Weg',
     'Lupinenweg',
     'Lusbarg',
     'Luswinkel',
     'Lutzhorner Landstraße',
     'Lönsweg',
     'Lütt Bookhorstweg',
     'Lütt Heid',
     'Magnus-Weidemann-Weg',
     'Maienbrook',
     'Marderstieg',
     'Margarethenstraße',
     'Maria-Dettmann-Weg',
     'Marie-Curie-Straße',
     'Marie-Juchacz-Straße',
     'Marktstraße',
     'Martin-Niemöller-Straße',
     'Mathilde-Röben-Straße',
     'Matthias-Kahlke-Promenade',
     'Matthias-Kruse-Straße',
     'Max-Beckmann-Platz',
     'Max-Liebermann-Straße',
     'Max-Planck-Straße',
     'Max-Planck-Straße 825335 -Sibirien',
     'Max-Slevogt-Straße',
     'Mehlbeerenweg',
     'Meisenweg',
     'Melkstroot',
     'Memeler Straße',
     'Merian-Straße',
     'Merlinweg',
     'Meteorstraße',
     'Meßhorn',
     'Meßtorffstraße',
     'Mildred-Scheel-Weg',
     'Missener Straße',
     'Missentwiete',
     'Mittelskamp',
     'Mittelweg',
     'Moltkestraße',
     'Mommsenstraße',
     'Moordamm',
     'Moorkamp',
     'Moorreger Weg',
     'Moortwiete',
     'Moorweg',
     'Morthorststraße',
     'Mozartstraße',
     'Mühlenberg',
     'Mühlendamm',
     'Mühlenkamp',
     'Mühlenstraße',
     'Mühlenweg',
     'Nappenhorn',
     'Nappenhorner Koppel',
     'Neue Straße',
     'Neuendeicher Weg',
     'Neuenkamp',
     'Neuenkampsweg',
     'Neukoppel',
     'Neut',
     'Nibelungenring',
     'Niedernmoorstraße',
     'Nils-Alwall-Weg',
     'Nixenring',
     'Noldering',
     'Nordender Weg',
     'Norderstraße',
     'Offenau',
     'Offenauer Weg',
     'Oha',
     'Ohlekamp',
     'Ohlenhoff',
     'Olekamp',
     'Olen Kamp',
     'Ollerlohstraße',
     'Ollnsstraße',
     'Op de Högt',
     'Op de Loh',
     "Op'n Knüll",
     'Ortbrookweg',
     'Ossenpadd',
     'Osterfeld',
     'Osterloher Weg',
     'Ostlandring',
     'Otto-Hahn-Straße',
     'Panjestraße',
     'Panzerberg',
     'Papenhöhe',
     'Pappelweg',
     'Parallelstraße',
     'Parkstraße',
     'Parkweg',
     'Pastor-Boldt-Straße',
     'Pastorendamm',
     'Paul-Junge-Straße',
     'Paul-Klee-Straße',
     'Paul-Löbe-Weg',
     'Paula-Modersohn-Becker-Weg',
     'Peltzerberg',
     'Peter-Boldt-Straße',
     'Peter-Kölln-Straße',
     'Peter-Meyn-Straße',
     'Peterstraße',
     'Pfahlweg',
     'Pferdekoppel',
     'Philosophenweg',
     'Pinnauring',
     'Pinneberger Landstraße',
     'Pinneberger Straße',
     'Plinkstraße',
     'Pommernstraße',
     'Pracherdamm',
     'Prinzendamm',
     'Prisdorfer Straße',
     'Prisdorfer Weg',
     'Probstendamm',
     'Querweg',
     'Raboisenstraße',
     'Rampskamper Weg',
     'Ramskamp',
     'Rantzau',
     'Rantzauweg',
     'Rathausstraße',
     'Redderkamp',
     'Redderlohe',
     'Reeperbahn',
     'Rehmkestraße',
     'Rehstieg',
     'Reichenstraße',
     'Reichsbundstraße',
     'Reihergrund',
     'Reinhold-Maier-Weg',
     'Reisieker Weg',
     'Rethfelder Ring',
     'Rethfelder Straße',
     'Retinastraße',
     'Reuterstraße',
     'Reventlowstraße',
     'Richard-Drews-Weg',
     'Riesenweg',
     'Ringstraße',
     'Robbenschlägerweg',
     'Robert-Bosch-Straße',
     'Roggenkamp',
     'Roggenweg',
     'Roonstraße',
     'Rosenhof',
     'Rosenstraße',
     'Rosenweg',
     'Rostock-Koppel',
     'Rostocker Straße',
     'Rotdornstieg',
     'Rotenlehm',
     'Rudolf-Diesel-Straße',
     'Rudolf-Kinau-Weg',
     'Rudolf-Maaßen-Weg',
     'Saarlandhof',
     'Sandberg',
     'Sandfohrt',
     'Sandhöhe',
     'Sandkamp',
     'Sandkoppel',
     'Sandweg',
     'Saßnitzring',
     'Schanzenstraße',
     'Schattenskamp',
     'Schilfweg',
     'Schillerstraße',
     'Schinkelstraße',
     'Schleusengraben',
     'Schlickumstraße',
     'Schloburger Weg',
     'Schlottweg',
     'Schlurrehm',
     'Schmiedekamp',
     'Schmiedskamp',
     'Schneiderkamp',
     'Schooltwiete',
     'Schubertstraße',
     'Schulkoppel',
     'Schulsteig',
     'Schulstraße',
     'Schulweg',
     'Schumacherstraße',
     'Schusterring',
     'Schwalbenweg',
     'Schweriner Weg',
     'Schäferweg',
     'Schönaich-Carolath-Straße',
     'Schützenstraße',
     'Schützenweg',
     'Seerosenring',
     'Seestraße',
     'Seether Straße',
     'Seether Weg',
     'Seminarstraße',
     'Sendefunkstelle',
     'Sibiren',
     'Sibirien',
     'Sielberg',
     'Siethwender Chaussee',
     'Slevogtweg',
     'Sommers Weg',
     'Sompweg',
     'Sonneck',
     'Sophienstraße',
     'Spargelkoppel',
     'Spargelweg',
     'Speelwark Padd',
     'Sperberweg',
     'Spitzerfurth',
     'Spitzweg',
     'Spökerdamm',
     'Stabeltwiete',
     'Stargarder Straße',
     'Steertkamp',
     'Steindamm',
     'Steinfurth',
     'Sternberger Straße',
     'Stettiner Straße',
     'Stormstraße',
     'Straatkoppel',
     'Stralsunder Straße',
     'Strawinskystraße',
     'Stubbenhuk',
     'Sägeberg',
     'Süderstraße',
     'Tannengrund',
     'Tannenhof',
     'Tannenstieg',
     'Tannenweg',
     'Tantaus Allee',
     'Teichweg',
     'Theodor-Storm-Allee',
     'Theodor-Storm-Straße',
     'Thiensen',
     'Thiensener Weg',
     'Thomas-Mann-Straße',
     'Thujaweg',
     'Tilsiter Weg',
     'Timm-Kröger-Straße',
     'Tondernstraße',
     'Tornescher Weg',
     'Toschlag',
     'Turnstraße',
     'Tütenweg',
     'Uetersener Straße',
     'Uferkamp',
     'Uhlenhorst',
     'Uhuweg',
     'Ulmenweg',
     "Up'n Feld",
     'Utweg',
     'Verbindungsweg',
     'Von-Aspern-Straße',
     'Vordersteig',
     'Vorm Dickenbusch',
     'Vormstegen',
     'Vossbarg',
     'Voßkuhlen',
     'Wacholderweg',
     'Wachsbleicherweg',
     'Waldstraße',
     'Waldweg',
     'Walfängerstraße',
     'Walter-Wilkins-Straße',
     'Wassermühlenstraße',
     'Wasserstraße',
     'Weberstraße',
     'Wedenkamp',
     'Weg am Spitzerfurth',
     'Weidendamm',
     'Weidenstieg',
     'Weidenstraße',
     'Weidenweg',
     'Weidkamp',
     'Wenzel-Hablik-Straße',
     'Werner-von-Siemens-Straße',
     'Westerstraße',
     'Wieren',
     'Wiesengrund',
     'Wilfried-Mohr-Straße',
     'Wilhelm-Busch-Weg',
     'Wilhelm-Eckmann-Weg',
     'Wilhelm-Schildhauer-Straße',
     'Wilhelmshöhe',
     'Wilhelmstraße',
     'Wisch',
     'Wismarring',
     'Wittenberger Straße',
     'Wittstocker Straße',
     'Wrangelpromenade',
     'Wulfstwiete',
     'Zanderbogen',
     'Zempiner Weg',
     'Ziegeleiweg',
     'Zingstweg',
     'Zum Horster Graben',
     'Zum Krückaupark',
     'Zum Stoppelfeld',
     'Zur Aussicht',
     'Zur Heide',
     'Zur Heidmühle',
     'Zur Schlangenau',
     'Zur Sielwiese'}




```python
for s in street:
    if '.' in s or 'Str' in s or 'W ' in s:
        print(s)
```

    Königsberger Straße
    Strawinskystraße
    Peter-Boldt-Straße
    Marie-Juchacz-Straße
    Ingwer-Paulsen-Straße
    Gustav-Heinemann-Straße
    Ernst-Behrens-Straße
    Wilhelm-Schildhauer-Straße
    Hypatia-Straße
    Robert-Bosch-Straße
    Bertha-von-Suttner-Straße
    Missener Straße
    Anne-Frank-Straße
    Martin-Niemöller-Straße
    Seether Straße
    Hermann-Weyl-Straße
    Louis-Mendel-Straße
    Sternberger Straße
    Justus-von-Liebig-Straße
    Lange Straße
    Werner-von-Siemens-Straße
    Friedrich-Engels-Straße
    Ludwig-Meyn-Straße
    Gerhard-Schröder-Straße
    Rostocker Straße
    Breslauer Straße
    Bürgermeister-Tesch-Straße
    Haderslebener Straße
    Esinger Straße
    Uetersener Straße
    Von-Aspern-Straße
    Jürgen-Siemsen-Straße
    Besenbeker Straße
    Pastor-Boldt-Straße
    Wittenberger Straße
    Timm-Kröger-Straße
    Straatkoppel
    Walter-Wilkins-Straße
    Fanny-Mendelssohn-Straße
    August-Christen-Straße
    Geschwister-Scholl-Straße
    Peter-Meyn-Straße
    Franz-Marc-Straße
    Elisabeth-Selbert-Straße
    Dr. Schroff-Weg
    Pinneberger Straße
    Albert-Johannsen-Straße
    Ernst-Abbe-Straße
    Danziger Straße
    Carl-Zeiss-Straße
    Max-Planck-Straße
    Irena-Sendler-Straße
    Mathilde-Röben-Straße
    Wilfried-Mohr-Straße
    Hamburger Straße
    Barmstedter Straße
    Hans-Böckler-Straße
    Memeler Straße
    Großendorfer Straße
    Wittstocker Straße
    Paul-Klee-Straße
    Apenrader Straße
    Bürgermeister-Diercks-Straße
    Heinrich-Hauschildt-Straße
    Stettiner Straße
    Lise-Meitner-Straße
    Jündewatter Straße
    Neue Straße
    Konrad-Struve-Straße
    Claus-Hinrich-Dieck-Straße
    Bettina-von-Arnim-Straße
    Matthias-Kruse-Straße
    Christian-Junge-Straße
    Karlsbader Straße
    Marie-Curie-Straße
    Otto-Hahn-Straße
    Kurt-Wagener-Straße
    Helgoländer Straße
    Adolph-Kolping-Straße
    Stralsunder Straße
    E.-L.-Meyn-Straße
    Helene-Wessel-Straße
    Ernst-Barlach-Straße
    Heinrich-Böll-Straße
    Theodor-Storm-Straße
    Bentkrögener Straße
    Louise-Schroeder-Straße
    Schönaich-Carolath-Straße
    Elmshorner Straße
    Julius-Leber-Straße
    Fritz-Straßmann-Straße
    Prisdorfer Straße
    Annette-von-Droste-Hülshoff-Straße
    Paul-Junge-Straße
    Albert-Schweitzer-Straße
    Rethfelder Straße
    Heinrich-Wagner-Straße
    Fritz-Reuter-Straße
    Max-Planck-Straße 825335 -Sibirien
    Jochen-Klepper-Straße
    Krumme Straße
    Rudolf-Diesel-Straße
    Wenzel-Hablik-Straße
    Ahrenloher Straße
    Elbinger Straße
    Merian-Straße
    Emil-Nolde-Straße
    Käthe-Mensing-Straße
    Thomas-Mann-Straße
    Gorch-Fock-Straße
    Klaus-Groth-Straße
    Heinrich-Hertz-Straße
    Berliner Straße
    Stargarder Straße
    Peter-Kölln-Straße
    Dietrich-Bonhoeffer-Straße
    Max-Slevogt-Straße
    Hemdinger Straße
    Max-Liebermann-Straße
    Albert-Hirsch-Straße
    

Pretty clean data 


```python
len(postcode)
```




    12




```python
postcode
```




    {'25335',
     '25336',
     '25337',
     '25355',
     '25358',
     '25365',
     '25368',
     '25370',
     '25373',
     '25436',
     '25495',
     '25497'}




```python
coutries
```




    {'DE'}




```python
keys['TMC']
```




    {'cid_58:tabcd_1:Class',
     'cid_58:tabcd_1:LCLversion',
     'cid_58:tabcd_1:LocationCode'}




```python
{'cid_58:tabcd_1:Class',
 'cid_58:tabcd_1:Direction',
 'cid_58:tabcd_1:LCLversion',
 'cid_58:tabcd_1:LocationCode',
 'cid_58:tabcd_1:NextLocationCode',
 'cid_58:tabcd_1:PrevLocationCode'}
```




    {'cid_58:tabcd_1:Class',
     'cid_58:tabcd_1:Direction',
     'cid_58:tabcd_1:LCLversion',
     'cid_58:tabcd_1:LocationCode',
     'cid_58:tabcd_1:NextLocationCode',
     'cid_58:tabcd_1:PrevLocationCode'}




```python

```

## Audit weblinks (including nodes, ways and relations)

bad weblinks
+ protected.de  
+ `http:\\\\www.horstmühle1.de`  

Open Street Map suggest the following tags to look for weblinks ('website', 'url', 'image', 'wikipedia')


```python
weblinks, badlinks = weblink.weblinks_by_key(osm_file);
```

Examples for bad links found in key *wikipedia*


```python
for i in range(1):
    print(badlinks['wikipedia'][i])
```

#### Example how regex works


```python
regex_weblink = re.compile(r'^(https?://)?(www\.)?(.*\.[a-zA-Z]{2,6})($|/{1}.*)$')
match = regex_weblink.match('http://www.jugendpflege-uetersen.info/www/02_jugendzentrum/index.php?task=1')
```


```python
for group in match.groups():
    print(group)
```

Weblinks are in: 
+ website  
+ url  
+ contact:website  
+ image  +
+ removed:website  +

No weblink found in wikipedia tags.


##### Searching for for further weblinks in tag values


```python
weblink.weblinks_by_value(osm_file);
```

Don't use:              email, openGeoDB:version, contact:email, operator, network  
Use:                    website, url, contact:website, image, removed:website  
Use with pattern check: source, contact:facebook, internet_access:ssid, note   


### Checking weblinks


```python
lut, stats = weblink.check_url(osm_file, output=True, JSON_out='weblink_lut.JSON')
```

http://www.kruemet.de/unternehmen/filialen/filiale-elmshorn/
Link does not work

converted to: https://kruemet.de/unternehmen/filialen/  
removed 'filiale-elmshorn/' : now works  
removed www  
switched to https: works  




```python
stats['modified links']
```

https://de.wikipedia.org/wiki/Uniform_Resource_Identifier

      foo://example.com:8042/over/there?name=ferret#nose
      \_/   \______________/\_________/ \_________/ \__/
       |           |            |            |        |
    scheme     authority       path        query   fragment
       |   _____________________|__
      / \ /                        \
      urn:example:animal:ferret:nose

https://de.wikipedia.org/wiki/URL-Encoding

    https://maxmuster:geheim@www.example.com:8080/index.html?p1=A&p2=B#ressource
    \___/   \_______/ \____/ \_____________/ \__/\_________/ \_______/ \_______/
      |         |       |           |         |       |          |         |
    Schema      |    Kennwort      Host      Port    Pfad      Query    Fragment
 

### Auditing phone numbers

For auditing phone numbers we will consult the following keys:
+ phone  
+ phone2  
+ fax
+ contact:phone
+ contact:fax
+ communication:mobile

Don't use 
'regular:emergency_telephone_code'

Area codes taken from: https://en.wikipedia.org/wiki/Telephone_numbers_in_Germany

spaces should separate country code, area code and local number.

![International%20ITU-T%20E.164-number%20structure%20for%20geographic%20areas_400x266.PNG](attachment:International%20ITU-T%20E.164-number%20structure%20for%20geographic%20areas_400x266.PNG)

    phone=+<country code> <area code> <local number>, following the ITU-T E.123 and the DIN 5008 pattern

%cd D:\Users\michael\Google Drive\DataAnalyst\Udacity\Project_2\data
import audit_nodes as nodes
import audit_nodeTags as nodeTags
import audit_ways as ways
import audit_wayTags as wayTags
import audit_weblinks as weblink
import audit_phone as phone
import re
from quick_parse_osm import count_tags


```python
regex_phone = re.compile(r'^(\+\d{2,3}) *(\d{2,5}) *(\d+)$')
```


```python
phnbr, problm, special, areas = phone.audit_phone(osm_file, output=True)
```

    Nbr of phone numbers: 255
    Nbr of uniqie area codes: 15
    Nbr of numbers containing non-digit characters: 22
    Nbr of problematic numbers (after cleaning): 0
    Problematic numbers:
    []
    


```python
areas
```




    {('151', 'Deutsche Telekom (GSM/UMTS)'),
     ('152', 'Vodafone D2 (GSM/UMTS)'),
     ('162', 'Vodafone D2 (GSM/UMTS)'),
     ('176', 'o2 Germany (GSM/UMTS)'),
     ('178', 'E-Plus (merging into o2 Germany) (GSM/UMTS)'),
     ('32', 'National subscriber numbers'),
     ('40', 'Hamburg'),
     ('4101', 'Pinneberg'),
     ('4120', 'Ellerhoop'),
     ('4121', 'Elmshorn'),
     ('4122', 'Uetersen'),
     ('4123', 'Barmstedt'),
     ('4126', 'Horst Holstein'),
     ('4821', 'Itzehoe'),
     ('4922', 'Borkum')}




```python
special
```

Before -> After 
('+49 (4123) 52 54', '+49 4123 5254'),


'+49 4123 9290577;+49 4123 9222240' doublicate phone tag is allowed by OSM an considered in code

How to normalize the phone numbers:
+ replace special characters in phone numbers with whitespace  
+ split number by withespaces  
+ check country calling code
    - statrts with + or 00
    - which countries
+ check area code (gold standard, country specific)
+ clean-up rest of number


```python

```

# Create Database


```python
from export_OSM_data import process_map
```


```python
%cd D:\Users\michael\Google Drive\DataAnalyst\Udacity\Project_2\data
#osm_file = '../data/GE_SH_PI_elmshorn_uetersen_k=100.osm'
osm_file = '../data/GE_SH_PI_elmshorn_uetersen.osm'

```


```python
process_map(osm_file, validate=True)
```

values containing ',' are safe by quoting s.b.

    3927715814,name,"Raa-Besenbek, Kirchensteig",regular

uid containing @ char is no problem  

    4806085427,53.7521971,9.6684194,nit@bse,1041363,1,47976980,2017-04-20T16:17:08Z


```python

```


```python

```

encoding issue for tag *name:ru*:

      <node id="240036785" lat="53.7532486" lon="9.6524559" version="12" timestamp="2019-03-28T17:34:03Z" changeset="68634953" uid="9451067" user="b-jazz-bot">
    <tag k="name:ru" v="Эльмсхорн"/>


```python
%cd D:\Users\michael\Google Drive\DataAnalyst\Udacity\Project_2\data
```


```python
import audit_nodes as nodes
import audit_nodeTags as nodeTags
import audit_ways as ways
import audit_wayTags as wayTags
import audit_weblinks as weblink
import audit_phone as phone
import re
from quick_parse_osm import count_tags
import wrangle_hlp as wh
```


```python
data = wh.read_JSON('weblink_lut.JSON')
```


```python
data['gefluegelhof-neumann.de'] is False
```


```python
data
```


```python

```

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

    <node id="1435290834" ....
    <tag k="phone" v="+494121-4757577"/>
    
Became:

    1435290834,phone,+49 4121 4757577,regular


```python

```

# Database queries
- number of queries per user

Create user table containing
    uid (pkey), user
    
    
Create changeset table containing
    changeset (pkey), nodes, ways, (relations)
    
I can create a view instead of these two tables

Query users and count assiciated element (node, way) creations. Sort by number of element created.  

Using regex in queries for weblinks and phone numbers




```python

```


```python

```


```python

```


```python

```
