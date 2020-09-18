#!/usr/bin/env python
# coding: utf-8

# Import libraries
from wrangle_hlp import get_element, cast_type
from collections import defaultdict
import re


def audit_keys(osm_file, output=False, out_depth=5): 
    lower = re.compile(r'^([a-z]|[_:])*$')
    problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
    keys = defaultdict(set)
    UPPER = set()
    probl_chars = set()

    for node in get_element(osm_file, tags=('node',)):
        for tag in node.iter('tag'):
            k = tag.get('k')
            if not lower.match(k):
                UPPER.add(k)
            if problemchars.search(k):
                probl_chars.add(k)
            if ':' not in k:
                keys['regular'].add(k)
            else:
                type, key = k.split(':', 1)
                keys[type].add(key)

    if output == True:
        print("Number of problematic keys: ", len(probl_chars))
        if len(probl_chars) > 0: 
            i = 0
            print("Problematic keys (first {}): ".format(out_depth))
            for key in probl_chars:
                i += 1
                print("\t", key)
                if i >= out_depth: break
        print("Number of keys not only lower case: ", len(UPPER))
        if len(UPPER) > 0: 
            i = 0
            print("List of keys not only lower case (first {}):".format(out_depth))
            for key in UPPER:
                i += 1
                print("\t", key)
                if i >= out_depth: break
        print("Number of unique node types: ", len(keys))
        if len(keys) > 0: 
            i = 0
            print("List of types followed by number of keys per type plus 3 keys (first {}):".format(out_depth))
            for type in sorted(keys, key=lambda x: len(keys[x]) , reverse=True):
                i += 1
                print("  Type:", type, "| keys:", len(keys[type]), "|", list(keys[type])[:3])
                if i >= out_depth: break       
                
    return UPPER, probl_chars, keys
    
def keys_double(keys, output=False):     
    # Can a regular key be a type?
    double_def = []
    for type in keys.keys():
        if type in keys['regular']: 
            double_def.append(type)
    if output == True:
        print('Type equals "regular" key ', len(double_def), 'times.')
        print('All types that equal a "regular" key:', double_def)
    return double_def
 
 
def check4reg_keys(keys, output=False, out_depth=5):          
    # Do we find 'regular' keys within the keys of other types?
    match_in_other_type = defaultdict(set)
    for key in keys['regular']:
        for type in keys.keys():
            if type == 'regular': continue    # Omit 'regular' type 
            for type_key in keys[type]:
                if key in type_key.split(':'):
                    match_in_other_type[key].add(type + ":" + type_key)  
    
    if output == True:
        print("Number of 'regular' keys found in other types: ", len(match_in_other_type))
        if len(match_in_other_type) > 0: 
            i = 0
            print("Matched keys (first {}): ".format(out_depth))
            for match in match_in_other_type:
                i += 1
                print('-',match,'- found in: ', match_in_other_type[match])
                if i >= out_depth: break
    return match_in_other_type

def unique_keys(keys):
    unique_keys = 0
    for type in keys:
        unique_keys += len(keys[type])
    return unique_keys
    
def audit_values(osm_file, output=False, out_depth=5):
    #problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
    problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\.\t\r\n]')
    splitOnColon = re.compile(r'.*:([^:]*)$')
    probl_chars = defaultdict(set)
    missing_values = defaultdict(set)           # Dict holding missing key values (k) for nodes {node id: (key1, key2, ...)}
    
    for node in get_element(osm_file, tags=('node',)):
        for tag in node.iter('tag'):
            k = tag.get('k')
            # Use last colon separated value only in 'k' to determine the data type
            if ':' in k:
                k = splitOnColon.match(k)[1]     
            v = tag.get('v')
            if v == '' or v == None or v == 'NULL':
                missing_values[node.get('id')].add(tag.get('k'))
            elif problemchars.search(v):
                probl_chars[k].add(v)
             
    if output == True:
        i = 0
        print('Missing values found for', len(missing_values), 'nodes')
        if len(missing_values) > 0: 
            print('List of missing values:', sorted(missing_values, key=lambda x: len(missing_values[x]), reversed=True))
        print('Problematic characters found in', len(probl_chars), 'keys.')
        for key in sorted(probl_chars, key=lambda x: len(probl_chars[x]), reverse=True):
            i += 1 
            print(key+":", len(probl_chars[key]))
            if i >= out_depth: break
            
    return probl_chars, missing_values
    
 
def audit_addr(osm_file, output=False, out_depth=5):
    streets = set()
    postcodes = set()
    
    for node in get_element(osm_file, tags=('node',)):
        for tag in node.iter('tag'): 
            if tag.get('k') == 'addr:street':
                streets.add(tag.get('v'))
            elif tag.get('k') == 'addr:postcode':
                postcodes.add(tag.get('v'))
                
    return streets, postcodes