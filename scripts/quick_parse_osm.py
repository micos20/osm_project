#!/usr/bin/env python
# coding: utf-8
"""
Count number of different tags in osm data file
"""
import xml.etree.cElementTree as ET
import wrangle_hlp as wh

def count_tags(filename):
    tags = {}       # dict to store the tags {tag: number}
    for _, elm in ET.iterparse(filename, events=('start', )):
        if elm.tag in tags.keys():
            tags[elm.tag] += 1
        else:
            tags[elm.tag] = 1
    return tags

def count_ways_tags(osm_file):
    way_count = 0
    for way in wh.get_element(osm_file, tags=('way')):
        for tag in way.iter('tag'):
            way_count += 1
    return way_count
    
def count_nodes_tags(osm_file):
    node_count = 0
    for node in wh.get_element(osm_file, tags=('node')):
        for tag in node.iter('tag'):
            node_count += 1
    return node_count