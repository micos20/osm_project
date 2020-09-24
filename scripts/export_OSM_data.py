#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema
from audit_phone import update_phone
from audit_weblinks import lookup_webink
from wrangle_hlp import get_element, validate_element, UnicodeDictWriter, read_JSON

# Set path to OSM data sets
OSM_PATH = '../data/GE_SH_PI_elmshorn_uetersen_k=100.osm'   # reduced data set
# OSM_PATH = '../data/GE_SH_PI_elmshorn_uetersen.osm'       # complete data set

# Set path for csv output
NODES_PATH = "../data/nodes.csv"
NODE_TAGS_PATH = "../data/nodes_tags.csv"
WAYS_PATH = "../data/ways.csv"
WAY_NODES_PATH = "../data/ways_nodes.csv"
WAY_TAGS_PATH = "../data/ways_tags.csv"

# Import validation schema
SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\.\t\r\n]')

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []

    # collect tags from node or way elements
    for tag in element.iterfind("tag"):
        k = tag.get('k')
        # if problem_chars.search(k): continue        
        tag_dict = {}
        tag_dict['id'] = element.get('id')
        if ':' not in k:
            tag_dict['key'] = k
            tag_dict['type'] = default_tag_type
        else:
            tag_dict['type'], tag_dict['key'] = k.split(':', 1)

        tag_dict['value'] = tag.get('v')  
        tags.append(tag_dict)    
     
    # collect node attributes
    if element.tag == 'node':
        # Fill node attibute dict
        for name in node_attr_fields:
            if element.get(name):
                node_attribs[name] = element.get(name)
            else:
                print(element.tag, element.get('id'), 'has no', element.get(name))
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        # Fill way attibute dict
        for name in way_attr_fields:
            if element.get(name):
                way_attribs[name] = element.get(name)
            else:
                print(element.tag, element.get('id'), 'has no', element.get(name))
        # Fill node reference dict
        pos = 0
        for ref_node in element.iterfind('nd'):
            node_dict = {}
            node_dict['id'] = element.get('id')
            node_dict['node_id'] = ref_node.get('ref')
            node_dict['position'] = pos
            pos += 1
            way_nodes.append(node_dict)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)