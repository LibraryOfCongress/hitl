#!/usr/bin/env python

"""This script pulls completed subjects from the Scribe mongodb for Workflow 2, writes 
these annotations, coordinates, and text to the workflow database, adds business listings to the
Data_Source table, then pulls relevant metadata from the workflow database and outputs CSV files 
of business listing subjects for ingest into Scribe Workflow 3.  The full process involves:
- Pull down subjects from mongodb for Workflow 2
- Write business type and listing annotations to the Annotation, Coordinates, and Text_Value tables
- Write business listing data to Data_Source table (including new IIIF image urls) for use
in Workflow 3
- Get metadata from Data_Source table for business listings in each item
- Output CSV files with business listings for each item and a CSV file with all items and
item-level metadata to the Workflow 3 /subjects directory

After running this script, run `rake project:load[yellow-pages-3]` in /loop_3 to load new 
business listing data to Scribe
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
    """Group business types and listings by business grouping mongo id"""
    grouped = {}
    for l in listings:
        if l['parent_subject_id']['$oid'] in grouped:
            grouped[l['parent_subject_id']['$oid']].append(l)
        else:
            grouped[l['parent_subject_id']['$oid']] = [l]
    return grouped

def getParentId(subjects, id):
    """Get database id for parent business grouping"""
    for s in subjects:
        if s['_id']['$oid'] == id:
            parent_id = s['meta_data']['id']
    return parent_id

def getTranscription(subjects, id):
    """Get corresponding transcription for a business type coordinates"""
    transcription = None
    for s in subjects:
        if 'parent_subject_id' in s:
            if s['parent_subject_id']['$oid'] == id:
                transcription = {}
                if 'yp3_business_type_main' in s['data']['values'][0]:
                    transcription['business_type_text'] = s['data']['values'][0]['yp3_business_type_main']
                if 'yp3_business_type_reference' in s['data']['values'][0]:
                    transcription['business_type_ref_text'] = s['data']['values'][0]['yp3_business_type_reference']
                transcription['text_external_id'] = s['_id']['$oid']
    return transcription

def getListingsAndTypes(subjects):
    """Get relevant business listing and type subjects from mongodb subjects download"""
    type_map = {'yp3_business_listing':'business listing',
                'yp3_business_type':'business type'}
    listings_types = [x for x in subjects if x['type'] in ['yp3_business_listing', 'yp3_business_type']]
    #group subjects by parent grouping
    grouped = groupSubjects(listings_types)
    #get data for listings and types (using 'listings' for short here)
    listings_by_groupings = []
    for k, v in grouped.items():
        lbg = {}
        lbg['grouping_mongo_id'] = k
        lbg['listings'] = []
        for l in v:
            listing = {}
            listing['external_id'] = l['_id']['$oid']
            listing['subject_type'] = type_map[l['type']]
            listing['x'] = float(l['data']['x'])
            listing['y'] = float(l['data']['y'])
            listing['height'] = float(l['data']['height'])
            listing['width'] = float(l['data']['width'])
            listing['data_source_id'] = getParentId(subjects, l['parent_subject_id']['$oid'])
            #check if business types have been transcribed and only add them to the list if they have been
            if l['type'] == 'yp3_business_type':
                transcription = getTranscription(subjects, l['_id']['$oid'])
                if transcription is not None:
                    listing['text'] = {}
                    if 'business_type_text' in transcription:
                        listing['text']['business_type_text'] = transcription['business_type_text']
                    if 'business_type_ref_text' in transcription:
                        listing['text']['business_type_ref_text'] = transcription['business_type_ref_text']
                    listing['text_external_id'] = transcription['text_external_id']
                    if len(listing['text']) > 0:
                        lbg['listings'].append(listing)
            #add the business listings to the list
            else:
                lbg['listings'].append(listing)
        listings_by_groupings.append(lbg)
    return listings_by_groupings

def writeToAnnotationTable(listing):
    """Write listings from CS2 to Annotation table for use as data sources in CS3"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    if listing['subject_type'] == 'business listing':
        cs_task = 2
    else:
        cs_task = 3
    sql = """insert into "Annotation" (source_type, cs_task_id, data_source_id, created_at, subject_type)
            select 'business grouping', %s, %s, %s, %s
            where not exists (select "external_id" from "Coordinates" where "external_id" = %s)
            returning id"""
    data = (cs_task, listing['data_source_id'], datetime.now(), listing['subject_type'], listing['external_id'],)
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
        sql = """select a."id"
                from "Annotation" a
                join "Coordinates" c
                on a."id" = c."annotation_id"
                where c."external_id" = %s;"""
        data = (listing['external_id'],)
        try:
            cur.execute(sql, data)
        except:
            conn.rollback()
            cur.execute(sql, data)
        rows = cur.fetchall()
        conn.commit()
        id = rows[0]['id']
    return id 

def writeToCoordinatesTable(listing):
    """Write listings from CS2 to Coordinate table for use as data sources in CS3"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    sql = """insert into "Coordinates" (x, y, width, height, external_id, 
            annotation_id)
            values (%s, %s, %s, %s, %s, %s)
            on conflict (external_id) do nothing
            returning id;"""
    data = (listing['x'], listing['y'], listing['width'], listing['height'],
           listing['external_id'], listing['annotation_id'],)
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
        data = (listing['external_id'],)
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

def writeToDataSourceTable(bg):
    """Write business listings from Annotations to Data Source table if they don't already
    exist"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    sql = """insert into "Data_Source" (name, type, source_system, 
            source_id, parent_id, source_url, source_image_url, 
            height, width, x, y, annotation_id)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            on conflict (annotation_id) do nothing
            returning id;"""
    data = (bg['name'], bg['type'], bg['source_system'], 
            bg['source_id'], bg['parent_id'], bg['source_url'], bg['source_image_url'], 
            bg['height'], bg['width'], bg['x'], bg['y'], bg['annotation_id'])
    try:
        cur.execute(sql, data)
    except:
        conn.rollback()
        cur.execute(sql, data)
    rows = cur.fetchall()
    conn.commit()

def getBusinessListingData(do_id):
    """Get business listing data from database"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    #get business listing annotation data and parent data source data for a given digital object id
    sql = """select a.*, c.*, g."id" as "ds_id", image."source_id" as "image_id", g."name" as "parent_name", g."source_url" as "parent_source_url", g."source_image_url" as "parent_source_image_url"
            from "Coordinates" c
            join "Annotation" a
            on a."id" = c."annotation_id"
            join "Data_Source" g
            on a."data_source_id" = g."id"
            join "Data_Source" page
            on g."parent_id" = page."id"
            join "Data_Source" image
            on page."parent_id" = image."id"
            join "Data_Source" item
            on image."parent_id" = item."id"
            where a."subject_type" = 'business listing'
            and a."cs_task_id" is not null
            and item."source_id" = %s;"""
    data = (do_id,)
    try:
        cur.execute(sql, data)
    except:
        conn.rollback()
        cur.execute(sql, data)
    rows = cur.fetchall()
    return rows

def makeUrl(data):
    """Generate IIIF image url for business listing"""
    #split parent url by image id
    image_id = data['image_id'].split('.')[1]
    base_url = data['parent_source_image_url'].split(image_id)[0]
    #get parent coords
    parent_coords = data['parent_source_image_url'].split(image_id)[1].split('/')[1]
    parent_coords = parent_coords.split(',')
    #add business grouping x and y to parent coords and replace width and height
    coords = [int(parent_coords[0]) + math.ceil(float(data['x'])/2),
              int(parent_coords[1]) + math.ceil(float(data['y'])/2),
              math.ceil(float(data['width'])/2),
              math.ceil(float(data['height'])/2)]
    coords = [','.join([str(c) for c in coords])]
    #reconstruct url with new business grouping coords
    after_coords = parent_coords = data['parent_source_image_url'].split(image_id)[1].split('/')[2:]
    coords.extend(after_coords)
    rest_of_url = '/'.join(coords)
    url = base_url + image_id + '/' + rest_of_url
    return url


def getBusinessListings(do_id):
    """Get business listing data from database and structure for insert in Data_Source
    and CSV files for CS3 workflow"""
    listings_data = getBusinessListingData(do_id)
    listings = []
    for g in listings_data:
        listing = {}
        #append x, y coords to parent name to create grouping name
        listing['name'] = g['parent_name'] + '_bg_' + str(g['x']) + '-' + str(g['y'])
        listing['type'] = 'business listing'
        listing['source_id'] = g['image_id']
        listing['source_system'] = 'lc'
        listing['source_url'] = g['parent_source_url']
        #may need to adjust coordinates to be relative to full image instead of page
        listing['source_image_url'] = makeUrl(g)
        listing['height'] = float(g['height'])/2
        listing['width'] = float(g['width'])/2
        listing['x'] = float(g['x'])/2
        listing['y'] = float(g['y'])/2
        listing['parent_id'] = g['ds_id']
        listing['annotation_id'] = g['annotation_id']
        listing['external_id'] = g['external_id']
        listings.append(listing)
    return listings

def getBusinessListingDataSourceId(bg):
    """Get business listing Data_Source id from database"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    #get id based on annotation_id
    sql = """select id
            from "Data_Source"
            where "annotation_id" = %s;"""
    data = (bg['annotation_id'],)
    try:
        cur.execute(sql, data)
    except:
        conn.rollback()
        cur.execute(sql, data)
    rows = cur.fetchall()
    id = rows[0]['id']
    return id

def writeGroupingsToCsv(filename, listings):
    f = open(filename, 'w')
    fieldnames = ['order','file_path','thumbnail','width','height', 'id', 'name', 'source_url']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    order = 1
    for g in listings:
        row = {}
        row['order'] = order
        row['file_path'] = g['source_image_url']
        row['thumbnail'] = g['source_image_url'].replace('pct:50', 'pct:3.125')
        row['width'] = g['width']
        row['height'] = g['height']
        row['id'] = g['id']
        row['name'] = g['name']
        row['source_url'] = g['source_url']
        writer.writerow(row)
        order += 1
    f.close()
    
def writeGroups(groups):
    filename = '../../loop_3/project/yellow-pages-3/subjects/groups.csv'
    f = open(filename, 'w')
    fieldnames = ['key','name','description','cover_image_url','external_url','meta_data_1','retire_count']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for v in groups:
        row = {}
        row['key'] = v['key']
        row['name'] = v['name']
        # row['cover_image_url'] = v['cover_image_url']
        row['cover_image_url'] = ''
        row['external_url'] = v['external_url']
        row['retire_count'] = 1
        writer.writerow(row)
    f.close()

if __name__ == "__main__":

    #download subjects from mongodb in Workflow 2 to /exports folder
    config = configparser.ConfigParser()
    config.read('../hitl.config')
    pwd = config.get('MONGO', 'Password')
    cmd = 'mongoexport -h localhost --port=27020 -d loop_dev -c subjects -u loop_dev -o ../exports/yp2/subjects.ndjson --forceTableScan'
    call('echo {} | {}'.format(pwd, cmd), shell=True)

    subjects = ndjson.load(open('../exports/yp2/subjects.ndjson', 'r'))

    items = [{'id': 'gdcustel.usteledirec00004', 'key': 'Birmingham_1955', 'name': 'Birmingham, Alabama, 1955', 'year': '1955'},
             {'id': 'usteledirec.usteledirec05650', 'key': 'Dubuque_1943', 'name': 'Dubuque, Iowa, 1943', 'year': '1943'},
             {'id': 'gdcustel.usteledirec03932', 'key': 'Colorado_Springs_1954', 'name': 'Colorado Springs, Colorado, 1954', 'year': '1954'},
             {'id': 'gdcustel.usteledirec04986x', 'key': 'Chicago_Czech_Slovak_1939', 'name': 'Chicago Czech and Slovak American, 1939', 'year': '1939'}
            ]
    #get all business listing and type subjects from mongo, grouped by business grouping
    listings = getListingsAndTypes(subjects)
    
    #write listings as annotations to Annotation table
    for li in listings:
        for l in li['listings']:
            l['annotation_id'] = writeToAnnotationTable(l)
            #write listings coordinates to Coordinates table if not already there
            if 'annotation_id' in l:
                l['coordinates_id'] = writeToCoordinatesTable(l)
            #write text to Text_Value table if listing is a business type
            if l['subject_type'] == 'business type':
                for k, v in l['text'].items():
                    writeToTextValueTable(k, v, l['coordinates_id'], l['text_external_id'])
    
    #get business listing annotations from Annotation and Coordinates table for each item
    groups = []
    for i in items:
        group = {}
        group['key'] = 'listings_' + i['key']
        group['name'] = i['name']
        group['external_url'] = 'https://www.loc.gov/resource/' + i['id']
        business_listings = getBusinessListings(i['id'])
        if len(business_listings) > 0:
            #write business listings to Data_Source table if it doesn't exist
            for bl in business_listings:
                writeToDataSourceTable(bl)
            #get Data_Source ids for business listings
            for bl in business_listings:
                bl['id'] = getBusinessListingDataSourceId(bl)
            #generate group CSV files for scribe workflow 3 ingest
            filename = '../../loop_3/project/yellow-pages-3/subjects/group_listings_{}.csv'.format(i['key'])
            writeGroupingsToCsv(filename, business_listings)
            group['cover_image_url'] = business_listings[0]['source_image_url']
            groups.append(group)

    #write groups to csv
    writeGroups(groups)

