#!/usr/bin/env python
# coding: utf-8

# Import libraries
from wrangle_hlp import get_element, cast_type, check_weblink
from collections import defaultdict
import re
import xml.etree.cElementTree as ET
import requests

def weblinks_by_key(osm_file):
    webkeys = {'website', 'url', 'image', 'wikipedia'}      # key containing weblink suggested by OSM
    weblinks = defaultdict(list)                            # Dict containing weblinks
    badlinks = defaultdict(list)                            # Dict containing bad links
    # Regex to match a weblink (intended to identify bad links)
    regex_weblink = re.compile(r'^(https?://)?(www\.)?(.*\.[a-zA-Z]{2,6})($|/{1}.*)$')

    # Parsing the file (only tags)
    for tag in (elm for _, elm in ET.iterparse(osm_file, events=('start', )) if elm.tag == 'tag'):
        if webkeys.intersection(tag.get('k').split(':')):
            weblinks[tag.get('k')].append(tag.get('v'))
            match = regex_weblink.match(tag.get('v'))
            if match == None:
                badlinks[tag.get('k')].append(tag.get('v'))
    
    # Output summary    
    print("Found weblinks in:")
    for key in weblinks:
        print("  " + key + ":", len(weblinks[key]))
    
    print("\nFound bad links in:")
    for key in badlinks:
        print("  " + key + ":", len(badlinks[key]))
    
    return weblinks, badlinks
    
def weblinks_by_value(osm_file):    
    weblinks = defaultdict(list)                # Dict for found weblinks
    # This time we use the regex to identify weblinks in other keys
    regex_weblink = re.compile(r'^(https?://)?(www\.)?(.*\.[a-zA-Z]{2,6})($|/{1}.*)$')

    # Parsing the file (only tags)
    for tag in (elm for _, elm in ET.iterparse(osm_file, events=('start', )) if elm.tag == 'tag'):
        match = regex_weblink.match(tag.get('v'))
        if match != None:
            weblinks[tag.get('k')].append(tag.get('v'))
    
    #Output
    print("Found weblinks:")
    for key in weblinks:
        print("  " + key + ":", len(weblinks[key]))
        
    return weblinks
    
def check_url(osm_file):
    webkeys     = ['website', 'url', 'image', 'removed:website', 'contact:website', 
                   'source', 'contact:facebook', 'internet_access:ssid', 'note']
    regex_weblink = re.compile(r'^(https?://)?(www\.)?(.*\.[a-zA-Z]{2,6})($|/{1}.*)$')
    
    modified_links = []
    broken_links = []
    secure_links = []
    insecure_links = []

    # Parsing the file
    for tag in (elm for _, elm in ET.iterparse(osm_file, events=('start', )) if elm.tag == 'tag'):
        if tag.get('k') in webkeys:
            match = regex_weblink.match(tag.get('v'))
            if match != None:
                old_url = tag.get('v').rstrip('/')
                new_url = update_webkey(match)
                #print(new_url)
            else:
                continue   
            
            if new_url == '':
                broken_links.append(old_url)
                continue
            
            old_sub = regex_weblink.match(old_url).group(4)
            new_sub = regex_weblink.match(new_url).group(4)
            
            if old_sub != new_sub:
                modified_links.append( (new_url, old_url) ) 
            
            if new_url.find('https', 0, 4):
                secure_links.append( (new_url, old_url) )
            else:
                insecure_links.append( (new_url, old_url) )
        
    return secure_links, insecure_links, broken_links, modified_links
        
        
def update_webkey(match):                  
    reg = re.compile(r'/[^/]*$')            
    
    sublink = match.group(4).rstrip("/")
    hostlink = match.group(3)
        
    # check if https works
    url = "https://" + hostlink + sublink
    if check_weblink(url):
        return url
    
    # check for http
    url = "http://" + hostlink + sublink
    print(url)
    if check_weblink(url):
        return url        
    
    # Set prfix of url
    if match.group(1) == "https://":
        prefix = "https://"
    else:   
        url = "https://" + match.group(3)
        if check_weblink(url):
            prefix = "https://"
        else:
            prefix = "http://"
                
    # Modify url subpart and check if link remains broken
    n = len(sublink.lstrip('/').split('/'))
    for _ in range(n):
        sublink = reg.sub('', sublink, 1)
        url = prefix + hostlink + sublink
        if check_weblink(url):
            return url
                
    # Link broken or other problem
    return ''

       