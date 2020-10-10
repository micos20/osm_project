#!/usr/bin/env python
# coding: utf-8

# Import libraries
from wrangle_hlp import get_element, cast_type
from collections import defaultdict
import re

def audit_keys(osm_file, output=False, out_depth=5): 
    '''
    Audit node keys from OSM raw data
    Returns all node keys in osm_file, problematic keys and keys containing capital letters.
    '''
    # Regex matching lower characters or colons or underscore
    lower = re.compile(r'^([a-z]|[_:])*$')
    # Regex matching special/ problematic characters
    problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
    # Dict containig node keys. Structure: {type: {key1, key2, key3, ...}}
    keys = defaultdict(set)
    # Set containing all keys matching regex 'lower'
    UPPER = set()
    # Set containing the keys with problematic characters
    probl_chars = set()

    # Assess node tags
    for node in get_element(osm_file, tags=('node','way')):
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
    
    # Print output if requested by 'output' attribute
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
    ''' 
    Checks if type variable is also found in 'keys' of 'regular' type
    Input: keys dict (containing types and set of keys) returned by audit_keys function
    Returns list of 
    '''
    double_def = []
    for type in keys.keys():
        if type in keys['regular']: 
            double_def.append(type)
    if output == True:
        print('Type equals "regular" key ', len(double_def), 'times.')
        print('All types that equal a "regular" key:', double_def)
    return double_def
 
def check4reg_keys(keys, output=False, out_depth=5):          
    '''
    Do we find 'regular' keys within the keys of other types?
    Input: keys dict (containing types and set of keys) returned by audit_keys function
    Returns dict containing 
    '''
    # Initialize return dict
    match_in_other_type = defaultdict(set)
    
    for key in keys['regular']:               # Iterate over keys in type regular
        for type in keys.keys():              # Iterate over types
            if type == 'regular': continue    # Omit 'regular' type 
            for type_key in keys[type]:       # Iterate over set of keys
                if key in type_key.split(':'):
                    match_in_other_type[key].add(type + ":" + type_key)  
    
    # Print output if requested by 'output' attribute
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
    '''
    Return number of unique keys
    Input: keys dict (containing types and set of keys) returned by audit_keys function
    '''
    unique_keys = 0
    for type in keys:
        unique_keys += len(keys[type])
    return unique_keys
    
def audit_values(osm_file, output=False, out_depth=5):
    '''
    Audit node tag values
    Input: osm_file
    Returns dict containing problematic and missing values
    '''
    # Regex matching lower characters or colons or underscore
    problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\.\t\r\n]')
    #problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
    #Regex splitting strings on colons
    splitOnColon = re.compile(r'.*:([^:]*)$')
    
    probl_chars = defaultdict(set)              # Dict for values with problematic characters
    missing_values = defaultdict(set)           # Dict holding missing key values (k) for nodes {node id: (key1, key2, ...)}
    
    for node in get_element(osm_file, tags=('node','way')):
        for tag in node.iter('tag'):
            k = tag.get('k')
            # Use last colon separated value only in 'k' to determine the data type
            if ':' in k:
                k = splitOnColon.match(k)[1]     
            v = tag.get('v')
            # Check for missing values
            if v == '' or v == None or v == 'NULL':
                missing_values[node.get('id')].add(tag.get('k'))
            elif problemchars.search(v):
                probl_chars[k].add(v)
             
    # Print output if requested by 'output' attribute
    if output == True:
        i = 0
        print('Missing values found for', len(missing_values), 'nodes')
        if len(missing_values) > 0: 
            print('List of missing values:', sorted(missing_values, key=lambda x: len(missing_values[x]), reversed=True))
        print('Problematic characters found in', len(probl_chars), 'keys.')
        print('List of values with problematic characters:')
        for key in sorted(probl_chars, key=lambda x: len(probl_chars[x]), reverse=True):
            i += 1 
            print(key+":", len(probl_chars[key]))
            if i >= out_depth: break
            
    return probl_chars, missing_values
    
 
def audit_addr(osm_file, output=False, out_depth=5):
    '''
    Audit addresses (street names and post codes)
    Returns set of streets and set of post codes
    '''
    streets = set()
    postcodes = set()
    
    for node in get_element(osm_file, tags=('node','way')):
        for tag in node.iter('tag'): 
            if tag.get('k') == 'addr:street':
                streets.add(tag.get('v'))
            elif tag.get('k') == 'addr:postcode':
                postcodes.add(tag.get('v'))
                
    return streets, postcodes
    
if __name__ == '__main__':
    # osm data files
    # osm_file = '../data/GE_SH_PI_elmshorn_uetersen_k=20.osm'
    # osm_file = '../data/GE_SH_PI_elmshorn_uetersen_k=100.osm'
    osm_file = '../data/GE_SH_PI_elmshorn_uetersen.osm'
    
    # audit node keys
    _, __, keys = audit_keys(osm_file, output=True, out_depth=10)
    print("Print keys of type 'TMC'", keys['TMC'])
    print("Number of unique keys:", unique_keys(keys))
    print("\n")
    print("Doublicate keys check")
    keys_double(keys, output=True);
    check4reg_keys(keys, output=True, out_depth=10);
    
    print("\n")
    pbl_values, missing_values = audit_values(osm_file, output=True, out_depth=20)
    # Print name values starting with B
    print("\n")
    print("Checking problematic name values starting with 'B':")
    for name in (n for n in pbl_values['name'] if n[0] == 'B'):
        print(name)
    
    # Address auditing
    streets, postcodes = audit_addr(osm_file)
    print("\n")
    print("Number of streets in node tags (addr:street): ", len(streets))
    print("Number of post codes in node tags (addr:postcode): ", len(postcodes))
    print("\n")
    print("Street names containing string 'St': ")
    for street in streets:
        if 'St' in street:
            print(street)


    
    