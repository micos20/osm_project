#!/usr/bin/env python
# coding: utf-8

# Import libraries
from wrangle_hlp import get_element, cast_type
from collections import defaultdict
import re
import datetime
from datetime import datetime as dt
from dateutil import parser


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')





def audit_node_id(osm_file, output=False):
    ''' 
    Assessing node id
    What are we going to do?
    + cout nodes  
    + check for data type
    + all node ids positive?
    + check for range
    '''
    
    cnt_nodes = 0               # node counter
    false_node_types = []       # array for nodes with wrong id type
    max_node = -1               # initialize max_node
    min_node = 10**100          # initialize min_node

    # Assess node id
    for element in get_element(osm_file, tags=('node',)):
        cnt_nodes += 1
        node_id = element.get('id')
        if not cast_type(node_id, 'int'): 
            false_node_types.append(node_id)
            continue
        node_id = int(node_id)
        if node_id > max_node: max_node = node_id
        if node_id < min_node: min_node = node_id       

    if output == True:
        print("Number of nodes: ", cnt_nodes)
        print("Number of false node id type: ", len(false_node_types))
        if len(false_node_types) > 0: print("False ids: ", false_node_types)
        print("Max node id: ", max_node)
        print("Min node id: ", min_node)
    return {'nbr_nodes': cnt_nodes, 
            'false_node_types': false_node_types,
            'max_nodeId': max_node,
            'min_nodeId': min_node}

def audit_coords(osm_file, minlon, maxlon, minlat, maxlat, output=False):
    '''
    Assessing coordinates
    What are we going to do?
    + check for data type float
    + coords in range of osm API request
    '''

    false_coord_types = []      # List containing false data types for coordinates
    # minlon = 9.6072
    # maxlon = 9.7888
    # minlat = 53.6782
    # maxlat = 53.7988
    outside_bbox = []           # List for nodes outside bounding box

    # Assess node coordinates
    for element in get_element(osm_file, tags=('node',)):
        lon = element.get('lon')
        lat = element.get('lat')
        if not (cast_type(lon, 'float') and cast_type(lon, 'float')): 
            false_coord_types.append((lon, lat))
            continue
        lon = float(lon)
        lat = float(lat)
        if not (minlon <= lon <= maxlon and minlat <= lat <= maxlat): 
            outside_bbox.append({element.get('id'): element})

    if output == True:
        print("Number of false coord types: ", len(false_coord_types))
        if len(false_coord_types) > 0: print("False coord types: ", false_coord_types)
        print("Number of nodes outside bounding box: ", len(outside_bbox))
        if len(outside_bbox) > 0: print("Nodes outside bounding box: ", outside_bbox)
    return {'false_coord_types': false_coord_types,
            'nodes_off_bbox': outside_bbox}
 
 
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
    for element in get_element(osm_file, tags=('node',)):
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
    for element in get_element(osm_file, tags=('node',)):
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
    for element in get_element(osm_file, tags=('node',)):
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
            


