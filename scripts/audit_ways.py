#!/usr/bin/env python
# coding: utf-8

# Import libraries
from wrangle_hlp import get_element, cast_type
from collections import defaultdict
import re
import datetime
from datetime import datetime as dt
from dateutil import parser
import xml.etree.cElementTree as ET

def audit_way_id(osm_file, output=False):
    ''' 
    Assessing way id
    What are we going to do?  
    + check for data type
    + all node ids positive?
    + check for range
    '''  
    false_way_types = []       # array for ways with wrong id type
    max_way_id = -1               # initialize max way id
    min_way_id = 10**100          # initialize min way id

    # Assess way id
    for element in get_element(osm_file, tags=('way',)):
        way_id = element.get('id')
        if not cast_type(way_id, 'int'): 
            false_way_types.append(way_id)
            continue
        way_id = int(way_id)
        if way_id > max_way_id: max_way_id = way_id
        if way_id < min_way_id: min_way_id = way_id       

    # Output
    if output == True:
        print("Number of false way id type: ", len(false_way_types))
        if len(false_way_types) > 0: print("False ids: ", false_waye_types)
        print("Max way id: ", max_way_id)
        print("Min way id: ", min_way_id)
    
    return {'false_way_types': false_way_types,
            'max_way_Id': max_way_id,
            'min_way_Id': min_way_id}

def audit_users(osm_file, output=False):
    '''
    Assessing users
    What are we going to do with the user name and uid?
    + check uid for data type int
    + check uid for range (min, max)
    + number of unique uids
    + uid, name always consistent?
    + check user name for critical characters
    '''
    min_uid = 10**100           # Initialize min_uid
    max_uid = -100              # Initialize max_uid
    wrong_uid_type = []         # List for wrong uid types
    users = defaultdict(set)    # Dict of all contributing users, format: {uid: (name1, name2, ...)}
    PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\.\t\r\n]')     # Definition of problematic characters
    probl_names = set()         # Set for all problematic names

    # Assess node users
    for element in get_element(osm_file, tags=('way',)):
        uid = element.get('uid')
        uname = element.get('user')
        if not cast_type(uid, 'int'): 
            wrong_uid_type.append(element.get('id'), element.get('uid'))
            continue
        uid = int(uid)
        if uid > max_uid: max_uid = uid
        if uid < min_uid: min_uid = uid  
        users[uid].add(uname)
        match = PROBLEMCHARS.search(uname)
        if match: probl_names.add((uid, uname))
        
    if output == True:
        print("Number of wrong uid type: ", len(wrong_uid_type))
        if len(wrong_uid_type) > 0: print("Wrong uid types: ", wrong_uid_type)
        print("Max user id: ", max_uid)
        print("Min_user id: ", min_uid)
        print("Number of unique users: ", len(users))
        print("Number of inconsistent uid/ name combinations: ", len( [id for id in users.keys() if len(users[id]) > 1] ) )
        print("Number of problematic user names: ", len(probl_names))
        print("List of problematic user names: ", probl_names)

    return {'wrong_uid_type': wrong_uid_type,
            'min_uid': min_uid,
            'max_uid': max_uid,
            'unique_users': users,
            'probl_names': probl_names}
 
 
def audit_version_chset(osm_file, output=False):
    '''
    Assessing version and changeset
    What are we going to do?
    + check version and changeset for data type int
    + check version and changeset for range (min, max)
    + number of unique changesets
    + number of unique versions
    '''
    
    false_types = []        # List for all invalid data types found
    max_version = -1        # Initialize max_version
    min_version = 10**100   # Initialize min_version
    max_chset = -1          # Initialize max changeset id
    min_chset = 10**100     # Initialize min_changeset id
    changesets = set()      # Set for unique changesets

    # Assess version and changeset
    for element in get_element(osm_file, tags=('way',)):
        version = element.get('version')
        chset = element.get('changeset')
        if not cast_type(version, 'int'): 
            false_types.append({'type': 'version', 'version': version, 'node_id': element.get('id')})
            continue
        if not cast_type(chset, 'int'): 
            false_types.append({'type': 'changeset', 'changeset': chset, 'node_id': element.get('id')})    
            continue   
        version = int(version)
        chset = int(chset)
        if version > max_version: max_version = version
        if version < min_version: min_version = version
        if chset > max_chset: max_chset = chset
        if chset < min_chset: min_chset = chset
        changesets.add(chset)
        
    if output == True:
        print("Number of falsy types: ", len(false_types))
        if len(false_types) > 0: print("False types: ", false_types)
        print("Max version: ", max_version)
        print("Min version: ", min_version)
        print("Max changeset id: ", max_chset)
        print("Min changeset id: ", min_chset)
        print("Number of unique changesets: ", len(changesets))

    return {'false_types': false_types,
            'changesets': changesets,
            'max_version': max_version,
            'min_version': min_version,
            'max_chset': max_chset,
            'min_chset': min_chset }


def audit_timestamp(osm_file, output=False):
    '''
    Assessing timestamp
    What are we going to do?
    + check timestamp for data type datetime
    + check for range (min, max)
    '''
    
    no_date = []            # List for wrong data types
    earliest = parser.parse('2200-01-01T00:00:00Z')   # Initialize min date
    latest = parser.parse('1900-01-01T00:00:00Z')     # Initialize max date

    # Assess timestamp
    for element in get_element(osm_file, tags=('way',)):
        timestamp = element.get('timestamp')
        if not cast_type(timestamp, 'date'): 
            no_date.append((element.get('id'), timestamp))
            continue
        timestamp = parser.parse(timestamp)
        
        if timestamp > latest: latest = timestamp
        if timestamp < earliest: earliest = timestamp

    if output == True:
        print("Number of wrong date types: ", len(no_date))
        if len(no_date) > 0: print("List of wrong date types: ", no_date)
        print("Earliest date: ", earliest)
        print("Latest date: ", latest)

    return {'no_date': no_date,
            'earliest': earliest,
            'latest': latest}
            
def audit_way_nodes(osm_file, output=False):
    '''
    Auditing way_nodes
    - type is int?
    - referenced node exists?
    '''
    
    false_types = []                    # List for all invalid data types found
    node_list = defaultdict(int)        # dict holding all node ids in dataset
    ref_node_not_found = set()          # Set of ref nodes witch aren't in the dataset
    ways_ref_mis = defaultdict(set)     # Ways affected by missing ref nodes
    ways_wo_ref = []                    # List for ways w/o any referenced node found in dataset
    
    # Fill 'node_list' with all node tag ids in dataset
    for node in (elm for _, elm in ET.iterparse(osm_file, events=('start', )) if elm.tag == 'node'):
        node_list[node.get('id')] = 1
        
    # Checks on way nodes
    for element in get_element(osm_file, tags=('way',)):
        pos = 0
        any_refNode_found = False
        for way_nd in element.iter('nd'):
            node_ref = way_nd.get('ref')
            # Check data type
            if not cast_type(node_ref, 'int'): 
                false_types.append({'way_id': element.get('id'),
                                    'node_ref': node_ref,
                                    'position': pos})
                continue
            # Check if referenced node is in node_list (in the dataset)
            if node_list[way_nd.get('ref')] != 1:           # If node not found ...
                ref_node_not_found.add(way_nd.get('ref'))   # add the node id to ref_node_not_found
                ways_ref_mis[element.get('id')].add(pos)    # add way element to way_ref_mis 
            else: any_refNode_found = True      # There is at least one ref node found  
            pos += 1    
        if not any_refNode_found:                   # If there is no ref node found for this way ... 
            ways_wo_ref.append(element.get('id'))   # add way to this list
    
    # Just output
    if output == True:
        print("Number of falsy types: ", len(false_types))
        if len(false_types) > 0: print("False types: ", false_types)
        print("N° of missing references: ", len(ref_node_not_found))
        print("N° of ways affected by missing references: ", len(ways_ref_mis)) 
        print("N° of ways w/o any referenced node found:", len(ways_wo_ref))
        if len(ways_wo_ref) > 0: print("Way ids w/o reference nodes found:", ways_wo_ref)
        
    return false_types, ref_node_not_found, ways_ref_mis, ways_wo_ref

