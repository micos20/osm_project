# Wrangle Open Street Map data
Explore OSM raw data for educational purpose

The investigated region is approximately 35km north of Hamburg in Germany.
OSM Area: Germany, Schleswig-Hostein, Pinneberg, Elmshorn & Uetersen

Overpass query used to extract Open Street Map raw data in XML
```sh
overpass query
(
   node(53.6782,9.6072,53.7988,9.7888);
   <;
);
out meta;
```

![OSM Area: Germany, Schleswig-Hostein, Pinneberg, Elmshorn & Uetersen](https://github.com/micos20/osm_project/blob/master/images/InvestigatedArea_600x474.PNG)

