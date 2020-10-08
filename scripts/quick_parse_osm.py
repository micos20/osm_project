#!/usr/bin/env python
# coding: utf-8
"""
Count number of different tags in osm data file
"""
import xml.etree.cElementTree as ET
import wrangle_hlp as wh

def count_tags(filename):
    '''
    Count all tags found in "filename"
    Returns dict containing the tags
    '''
    tags = {}       # dict to store the tags {tag: number}
    for _, elm in ET.iterparse(filename, events=('start', )):
        if elm.tag in tags.keys():
            tags[elm.tag] += 1
        else:
            tags[elm.tag] = 1
    return tags

def count_ways_tags(osm_file):
    '''
    Count way tags found in "filename"
    Returns number of tags
    '''
    way_count = 0
    for way in wh.get_element(osm_file, tags=('way')):
        for tag in way.iter('tag'):
            way_count += 1
    return way_count
    
def count_nodes_tags(osm_file):
    '''
    Count node tags found in "filename"
    Returns number of tags
    '''
    node_count = 0
    for node in wh.get_element(osm_file, tags=('node')):
        for tag in node.iter('tag'):
            node_count += 1
    return node_count
    
def count_relations_tags(osm_file):
    '''
    Count realtions tags found in "filename"
    Returns number of tags
    '''
    relation_count = 0
    for relation in wh.get_element(osm_file, tags=('relation')):
        for tag in relation.iter('tag'):
            relation_count += 1
    return relation_count
    
if __name__ == '__main__':
    '''
    Quick parse the OSM file
    '''
    # osm data files
    # osm_file = '../data/GE_SH_PI_elmshorn_uetersen_k=20.osm'
    # osm_file = '../data/GE_SH_PI_elmshorn_uetersen_k=100.osm'
    osm_file = '../data/GE_SH_PI_elmshorn_uetersen.osm'
        
    print("Number of tags in OSM file:")
    print(count_tags(osm_file))
    print("Number of way tags in OSM file:", count_ways_tags(osm_file) )
    print("Number of node tags in OSM file:", count_nodes_tags(osm_file) )
    print("Number of relation tags in OSM file:", count_relations_tags(osm_file) )
    
