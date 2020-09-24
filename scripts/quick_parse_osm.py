#!/usr/bin/env python
# coding: utf-8
"""
Count number of different tags in osm data file
"""
import xml.etree.cElementTree as ET

def count_tags(filename):
    tags = {}       # dict to store the tags {tag: number}
    for _, elm in ET.iterparse(filename, events=('start', )):
        if elm.tag in tags.keys():
            tags[elm.tag] += 1
        else:
            tags[elm.tag] = 1
    return tags
    