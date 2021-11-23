#!/usr/bin/env python

"""This script pulls completed subjects from the Scribe mongodb for Workflow 3, and writes 
these annotations, coordinates, and text to the workflow database. This data can be used to
create training data for the CRF NLP machine learning process or as ground truth for the
outupt of that process. The full process involves:
- Pull down subjects from mongodb for Workflow 3
- Write business entity annotations to the Annotation, Coordinates, and Text_Value tables
"""

from subprocess import call
import requests
import configparser
import json
import csv
import ndjson
import math
import psycopg2
import psycopg2.extras
from datetime import datetime

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

def groupSubjects(listings):
    """Group business entities by business listing mongo id"""
    grouped = {}
    for l in listings:
        if l['parent_subject_id']['$oid'] in grouped:
            grouped[l['parent_subject_id']['$oid']].append(l)
        else:
            grouped[l['parent_subject_id']['$oid']] = [l]
    return grouped

def getParentId(subjects, id):
    """Get parent listing id for the annotation coordinates and values"""
    for s in subjects:
        if s['_id']['$oid'] == id:
            parent_id = s['meta_data']['id']
            if s['classification_count'] > 2 and s['status'] == 'retired':
                inactive = True
            else:
                inactive = False
    return (parent_id, inactive)

def getTranscription(subjects, id):
    """Get corresponding transcription for a business entity coordinates"""
    transcription = None
    type_map = {'yp3_transcribed_business_name':'business name',
                'yp3_transcribed_business_address':'address',
                'yp3_transcribed_phone_number': 'phone number',
                'yp3_transcribed_see_advertisement': 'see advertisement',
                'yp3_transcribed_other': 'other information',
                'yp3_described_graphic': 'graphic'}
    for s in subjects:
        if 'parent_subject_id' in s:
            if s['parent_subject_id']['$oid'] == id:
                transcription = {}
                for t in type_map.keys():
                    if t == s['type']:
                        key = t
                transcription['text'] = s['data']['values'][0]['value']
                transcription['key'] = type_map[key]
                transcription['text_external_id'] = s['_id']['$oid']
    return transcription

def getEntities(subjects):
    """Get entity coordinates and text from mongo subjects"""
    type_map = {'yp3_business_name':'business name',
                'yp3_business_address':'address',
                'yp3_phone_number': 'phone number',
                'yp3_see_advertisement': 'see advertisement',
                'yp3_other': 'other information',
                'yp3_graphic': 'graphic'}
    entity_types = [x for x in subjects if x['type'] in type_map.keys()]
    #group subjects by parent grouping
    grouped = groupSubjects(entity_types)
    #get data for listings and types (using 'listings' for short here)
    entities_by_listings = []
    for k, v in grouped.items():
        ebl = {}
        ebl['listing_mongo_id'] = k
        ebl['entities'] = []
        for e in v:
            #get the parent listing id and see if it's inactive yet (i.e. all entities have been marked and transcribed)
            parent_id = getParentId(subjects, e['parent_subject_id']['$oid'])
            if parent_id[1] == True:
                entity = {}
                ebl['data_source_id'] = parent_id[0]
                entity['external_id'] = e['_id']['$oid']
                entity['subject_type'] = type_map[e['type']]
                entity['x'] = float(e['data']['x'])
                entity['y'] = float(e['data']['y'])
                entity['height'] = float(e['data']['height'])
                entity['width'] = float(e['data']['width'])
                transcription = getTranscription(subjects, e['_id']['$oid'])
                if transcription is not None:
                    entity['text'] = transcription['text']
                    entity['key'] = transcription['key']
                    entity['text_external_id'] = transcription['text_external_id']
                    ebl['entities'].append(entity)
        entities_by_listings.append(ebl)
    return entities_by_listings

def writeToAnnotationTable(ebl):
    """Write set of listing entities from CS3 to Annotation table for use as training/verification data"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    cs_task = 4
    external_ids = tuple([x['external_id'] for x in ebl['entities']])
    sql = """insert into "Annotation" (source_type, cs_task_id, data_source_id, created_at, subject_type)
            select 'business listing', %s, %s, %s, 'business listing entities'
            where not exists (select "external_id" from "Coordinates" where "external_id" in %s)
            returning id"""
    data = (cs_task, ebl['data_source_id'], datetime.now(), external_ids,)
    try:
        cur.execute(sql, data)
    except:
        conn.rollback()
        cur.execute(sql, data)
    rows = cur.fetchall()
    conn.commit()
    #if new entry, return this id
    if len(rows) > 0:
        id = rows[0]['id']
    #otherwise query for the id based on external_id in Coordinates
    else:
        db = dbconnect()
        cur = db[0]
        conn = db[1]
        sql = """select distinct a."id"
                from "Annotation" a
                join "Coordinates" c
                on a."id" = c."annotation_id"
                where c."external_id" in %s;"""
        data = (external_ids,)
        try:
            cur.execute(sql, data)
        except:
            conn.rollback()
            cur.execute(sql, data)
        rows = cur.fetchall()
        conn.commit()
        id = rows[0]['id']
    return id 

def writeToCoordinatesTable(entity, anno_id):
    """Write listings from CS2 to Coordinate table for use as data sources in CS3"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    sql = """insert into "Coordinates" (x, y, width, height, external_id, 
            annotation_id)
            values (%s, %s, %s, %s, %s, %s)
            on conflict (external_id) do nothing
            returning id;"""
    data = (entity['x'], entity['y'], entity['width'], entity['height'],
           entity['external_id'], anno_id,)
    try:
        cur.execute(sql, data)
    except:
        conn.rollback()
        cur.execute(sql, data)
    rows = cur.fetchall()
    conn.commit()
    #if new entry, return this id
    if len(rows) > 0:
        id = rows[0]['id']
    #otherwise query for the id based on external_id 
    else:
        db = dbconnect()
        cur = db[0]
        conn = db[1]
        sql = """select c."id"
                from "Coordinates" c
                where c."external_id" = %s;"""
        data = (entity['external_id'],)
        try:
            cur.execute(sql, data)
        except:
            conn.rollback()
            cur.execute(sql, data)
        rows = cur.fetchall()
        conn.commit()
        id = rows[0]['id']
    return id

def writeToTextValueTable(key, value, coordinates_id, external_id):
    """For business types, add the transcribed text to the Text_Value table"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    sql = """insert into "Text_Value" (key, value, coordinates_id, external_id)
            values (%s, %s, %s, %s)
            on conflict (external_id) do nothing
            returning id;"""
    data = (key, value, coordinates_id, external_id)
    try:
        cur.execute(sql, data)
    except:
        conn.rollback()
        cur.execute(sql, data)
    rows = cur.fetchall()
    conn.commit()

if __name__ == "__main__":

    #download subjects from mongodb in Workflow 2 to /exports folder
    config = configparser.ConfigParser()
    config.read('../hitl.config')
    pwd = config.get('MONGO', 'Password')
    cmd = 'mongoexport -h localhost --port=27023 -d loop_dev -c subjects -u loop_dev -o ../exports/yp3/subjects.ndjson --forceTableScan'
    call('echo {} | {}'.format(pwd, cmd), shell=True)

    subjects = ndjson.load(open('../exports/yp3/subjects.ndjson', 'r'))
    
    items = [{'id': 'gdcustel.usteledirec00004', 'key': 'Birmingham_1955', 'name': 'Birmingham, Alabama, 1955', 'year': '1955'},
             {'id': 'usteledirec.usteledirec05650', 'key': 'Dubuque_1943', 'name': 'Dubuque, Iowa, 1943', 'year': '1943'},
             {'id': 'gdcustel.usteledirec03932', 'key': 'Colorado_Springs_1954', 'name': 'Colorado Springs, Colorado, 1954', 'year': '1954'},
             {'id': 'gdcustel.usteledirec04986x', 'key': 'Chicago_Czech_Slovak_1939', 'name': 'Chicago Czech and Slovak American, 1939', 'year': '1939'}
            ]
    
    #get all business entities from mongo, grouped by business listing
    entities = getEntities(subjects)
    
    #write entities as annotations to Annotation table
    for e in entities:
        if len(e['entities']) > 0:
            e['annotation_id'] = writeToAnnotationTable(e)
            #write entity coordinates to Coordinates table if not already there
            if 'annotation_id' in e:
                for ent in e['entities']:
                    ent['coordinates_id'] = writeToCoordinatesTable(ent, e['annotation_id'])
                #write text of entities to Text_Value table
                    writeToTextValueTable(ent['key'], ent['text'], ent['coordinates_id'], ent['text_external_id'])

