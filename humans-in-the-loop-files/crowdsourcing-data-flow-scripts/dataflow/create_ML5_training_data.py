#!/usr/bin/env python
# coding: utf-8

"""This script pulls business entity data from the workflow database and generates markdown
files for use as training data in the CRF NLP process. """

import configparser
import math
import psycopg2
import psycopg2.extras
from datetime import date
import datetime

def dbconnect():
    """Connect to the validation database"""
    config = configparser.ConfigParser()
    config.read('../hitl.config')
    host = config.get('POSTGRES', 'Host')
    user = config.get('POSTGRES', 'User')
    pw = config.get('POSTGRES', 'Password')
    port = config.get('POSTGRES', 'Port')
    dbs = config.get('POSTGRES', 'Database')
    #fire up the database connection
    conn = psycopg2.connect("dbname='{0}' user='{1}' host='{2}' password='{3}'".format(dbs, user, host, pw))
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    return cur, conn

def getEntities():
    """Get business listing entity data and their parent annotation ids from the db"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    sql = """select a."id" as "annotation_id", tv."key", tv."value", c.* 
            from "Text_Value" tv
            join "Coordinates" c
            on tv."coordinates_id" = c."id"
            join "Annotation" a
            on c."annotation_id" = a."id"
            where a."subject_type" = 'business listing entities'
            and "cs_task_id" is not null
            order by a."id";"""
    try:
        cur.execute(sql,)
    except:
        conn.rollback()
        cur.execute(sql)
    rows = cur.fetchall()
    return rows
    
def entitiesByListing(entities):
    """Group entities from database by annotation id"""
    groups = {}
    for e in entities:
        if e['annotation_id'] not in groups:
            groups[e['annotation_id']] = []
            entity = {}
            for k, v in e.items():
                if k != ['annotation_id']:
                    entity[k] = v
            groups[e['annotation_id']].append(entity)
        else:
            entity = {}
            for k, v in e.items():
                if k != ['annotation_id']:
                    entity[k] = v
            groups[e['annotation_id']].append(entity)
    grouped = []
    for g, v in groups.items():
        new_group = {'annotation_id':g,
                    'entities':v}
        grouped.append(new_group)
    return grouped

def sortBoxes(boxes):
    """Calculate coordinates for each box and sort in reading order"""
    for ent in boxes:
        ent['xmin'] = float(ent['x'])
        ent['ymin'] = float(ent['y'])
        ent['width'] = float(ent['width'])
        ent['height'] = float(ent['height'])
        ent['xmax'] = ent['xmin'] + ent['width']
        ent['ymax'] = ent['ymin'] + ent['height']
    num_boxes = len(boxes)
    # sort from top to bottom and left to right
    sorted_boxes = sorted(boxes, key=lambda x: (x['ymin'], x['xmin']))
    _boxes = list(sorted_boxes)
    # for j in range:
    # check if the next neighbour box x coordinates is greater then the current box x coordinates if not swap them.
    # repeat the swaping process to a threshold iteration and also select the threshold 
    #MAY NEED TO ADJUST THIS THRESHOLD
    threshold_value_y = 25
    for i in range(5):
        for i in range(num_boxes - 1):
            if abs(_boxes[i + 1]['ymin'] - _boxes[i]['ymin']) < threshold_value_y and (_boxes[i + 1]['xmin'] < _boxes[i]['xmin']):
                tmp = _boxes[i]
                _boxes[i] = _boxes[i + 1]
                _boxes[i + 1] = tmp
    return _boxes
    
def toMarkdown(entities):
    """Convert entities to markdown"""
    md_string = []
    for e in entities:
        if e['key'] != 'graphic':
            ent = '- [{0}]({1})'.format(e['value'], e['key'].replace(' ', '_'))
            md_string.append(ent)
    if len(md_string) > 2:
        md_string = ' '.join(md_string)
    else:
        md_string = None
    return md_string

def getNewVersion():
    """Create a new ML version in ML_Version table and return the version number"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    #get latest version number
    sql1 = """select max(version_number) as vn
            from "ML_Version"
            where ml_process_id = 5;
            """
    try:
        cur.execute(sql1,)
    except:
        conn.rollback()
        cur.execute(sql1,)
    rows = cur.fetchall()
    #if no existing version, version number is 1.0.0, else version number + 1
    if rows[0]['vn'] is None:
        vn = '1.0.0'
    else:
        vn = str(int(rows[0]['vn'].split('.')[0]) + 1) + '.0.0'
    #create a new version in the ML_Version table with the new version number
    cur = db[0]
    conn = db[1]
    sql2 = """insert into "ML_Version" (ml_process_id, version_number, date_time)
            values (5, %s, %s)
            returning id;"""
    data = (vn, datetime.datetime.utcnow(),)
    try:
        cur.execute(sql2, data)
    except:
        conn.rollback()
        cur.execute(sql2, data)
    rows = cur.fetchall()
    conn.commit()
    id = rows[0]['id']
    return (id, vn)

def writeToTrainingDataset(filename, vn):
    """Write dataset path and ml_version_id to Training_Dataset table"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    sql = """insert into "Training_Dataset" (ml_version_id, path)
            values (%s, %s)
            returning id;"""
    data = (vn, filename,)
    try:
        cur.execute(sql, data)
    except:
        conn.rollback()
        cur.execute(sql, data)
    rows = cur.fetchall()
    conn.commit()
    
def writeToTrain(annotation_id, vn):
    """Write annotation_id and ml_version_id for each annotation in the training set to Train table"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    sql = """insert into "Train" (ml_version_id, annotation_id)
            values (%s, %s)
            returning id;"""
    data = (vn, annotation_id,)
    try:
        cur.execute(sql, data)
    except:
        conn.rollback()
        cur.execute(sql, data)
    rows = cur.fetchall()
    conn.commit()

def outputMarkdown(entities, filename):
    """Output markdown text as a markdown file"""
    f = open(filename, 'w')
    for e in entities:
        if e['train'] is not None:
            f.write(e['train'] + '\n')
    f.close()

if __name__ == "__main__":

    #get entities from database
    entities = getEntities()
    grouped_ents = entitiesByListing(entities)
    for e in grouped_ents:
        sorted_ents = sortBoxes(e['entities'])
        e['train'] = toMarkdown(sorted_ents)

    #get latest version number and insert into ML_Version, returning id and version number (x.0.0)
    version = getNewVersion()

    filename = '../training/CRF_training_data_{}.md'.format(version[1])

    #write dataset into Training_Dataset table
    path = filename.replace('../', '')
    writeToTrainingDataset(path, version[0])

    #write annotations with ml_version_id to Train table
    for e in grouped_ents:
        if e['train'] is not None:
            writeToTrain(e['annotation_id'], version[0])

    #output md file
    data = outputMarkdown(grouped_ents, filename)

