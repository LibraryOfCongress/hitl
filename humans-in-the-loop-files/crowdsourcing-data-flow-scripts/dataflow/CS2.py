#!/usr/bin/env python

"""This script pulls completed subjects from the Scribe mongodb for Workflow 1, writes 
these annotations and coordinates to the workflow database, adds business groupings to the
Data_Source table, then pulls relevant metadata from the workflow database and outputs CSV files 
of business grouping subjects for ingest into Scribe Workflow 2.  The full process involves:
- Pull down subjects from mongodb for Workflow 1
- Write advertisement, business grouping, and telephone tips annotations to the Annotation
and Coordinates tables
- Write business grouping data to Data_Source table (including new IIIF image urls) for use
in Workflow 2
- Get metadata from Data_Source table for business groupings in each item
- Output CSV files with business groupings for each item and a CSV file with all items and
item-level metadata to the Workflow 2 /subjects directory

After running this script, run `rake project:load[yellow-pages-2]` in /loop_2 to load new 
business grouping data to Scribe
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

def groupSubjects(segments):
    """Group subjects by parent page mongo id"""
    grouped = {}
    for s in segments:
        if s['parent_subject_id']['$oid'] in grouped:
            grouped[s['parent_subject_id']['$oid']].append(s)
        else:
            grouped[s['parent_subject_id']['$oid']] = [s]
    return grouped

def getParentId(subjects, id):
    """Get workflow database id for subject parent"""
    for s in subjects:
        if s['_id']['$oid'] == id:
            parent_id = s['meta_data']['id']
    return parent_id

def getSegments(subjects):
    """Get relevant segment subjects from mongodb subjects download"""
    type_map = {'yp1_advertisement':'advertisement',
                'yp1_business_block':'business grouping',
                'yp1_informational':'telephone tip'}
    segments = [x for x in subjects if x['type'] in ['yp1_advertisement', 'yp1_business_block', 'yp1_informational']]
    #group subjects by parent page
    grouped = groupSubjects(segments)
    segments_by_page = []
    for k, v in grouped.items():
        sbp = {}
        sbp['page_mongo_id'] = k
        sbp['segments'] = []
        for s in v:
            segment = {}
            segment['external_id'] = s['_id']['$oid']
            segment['subject_type'] = type_map[s['type']]
            segment['x'] = float(s['data']['x'])
            segment['y'] = float(s['data']['y'])
            segment['height'] = float(s['data']['height'])
            segment['width'] = float(s['data']['width'])
            segment['data_source_id'] = getParentId(subjects, s['parent_subject_id']['$oid'])
            sbp['segments'].append(segment)
        segments_by_page.append(sbp)
    return segments_by_page

def writeToAnnotationTable(segment):
    """Write segments from CS1 to Annotation table for use as data sources in CS2"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    sql = """insert into "Annotation" (source_type, cs_task_id, data_source_id, created_at, subject_type)
            select 'page', 1, %s, %s, %s
            where not exists (select "external_id" from "Coordinates" where "external_id" = %s)
            returning id"""
    data = (segment['data_source_id'], datetime.now(), segment['subject_type'], segment['external_id'])
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
        data = (segment['external_id'],)
        try:
            cur.execute(sql, data)
        except:
            conn.rollback()
            cur.execute(sql, data)
        rows = cur.fetchall()
        conn.commit()
        id = rows[0]['id']
    return id 

def writeToCoordinatesTable(segment):
    """Write segments from CS1 to Coordinate table for use as data sources in CS2"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    sql = """insert into "Coordinates" (x, y, width, height, external_id, 
            annotation_id)
            values (%s, %s, %s, %s, %s, %s)
            on conflict (external_id) do nothing
            returning id;"""
    data = (segment['x'], segment['y'], segment['width'], segment['height'],
           segment['external_id'], segment['annotation_id'])
    try:
        cur.execute(sql, data)
    except:
        conn.rollback()
        cur.execute(sql, data)
    rows = cur.fetchall()
    conn.commit()

def writeToDataSourceTable(bg):
    """Write business groupings from Annotations to Data Source table if they don't already
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

def getBusinessGroupingData(do_id):
    """Get business grouping data from database"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    #get business grouping annotation data and parent data source data for a given digital object id
    sql = """select a.*, c.*, page."id" as "ds_id", image."source_id" as "image_id", page."name" as "parent_name", page."source_url" as "parent_source_url", page."source_image_url" as "parent_source_image_url"
            from "Coordinates" c
            join "Annotation" a
            on a."id" = c."annotation_id"
            join "Data_Source" page
            on a."data_source_id" = page."id"
            join "Data_Source" image
            on page."parent_id" = image."id"
            join "Data_Source" item
            on image."parent_id" = item."id"
            where a."subject_type" = 'business grouping'
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
    """Generate IIIF image url for the business grouping"""
    #split parent url by image id
    image_id = data['image_id'].split('.')[1]
    base_url = data['parent_source_image_url'].split(image_id)[0]
    #get parent coords
    parent_coords = data['parent_source_image_url'].split(image_id)[1].split('/')[1]
    parent_coords = parent_coords.split(',')
    #add business grouping x and y to parent coords and replace width and height
    coords = [int(parent_coords[0]) + math.ceil(float(data['x'])),
              int(parent_coords[1]) + math.ceil(float(data['y'])),
              math.ceil(float(data['width'])),
              math.ceil(float(data['height']))]
    coords = [','.join([str(c) for c in coords])]
    #reconstruct url with new business grouping coords
    after_coords = parent_coords = data['parent_source_image_url'].split(image_id)[1].split('/')[2:]
    coords.extend(after_coords)
    rest_of_url = '/'.join(coords)
    url = base_url + image_id + '/' + rest_of_url
    return url

def getBusinessGroupings(do_id):
    """Get business grouping data from database and structure for insert in Data_Source
    and CSV files for CS2 workflow"""
    groupings_data = getBusinessGroupingData(do_id)
    groupings = []
    for g in groupings_data:
        grouping = {}
        #append x, y coords to parent name to create grouping name
        grouping['name'] = g['parent_name'] + '_bg_' + str(g['x']) + '-' + str(g['y'])
        grouping['type'] = 'business grouping'
        grouping['source_id'] = g['image_id']
        grouping['source_system'] = 'lc'
        grouping['source_url'] = g['parent_source_url']
        #may need to adjust coordinates to be relative to full image instead of page
        grouping['source_image_url'] = makeUrl(g)
        grouping['height'] = float(g['height'])*2
        grouping['width'] = float(g['width'])*2
        grouping['x'] = float(g['x'])*2
        grouping['y'] = float(g['y'])*2
        grouping['parent_id'] = g['ds_id']
        grouping['annotation_id'] = g['annotation_id']
        grouping['external_id'] = g['external_id']
        groupings.append(grouping)
    return groupings

def getBusinessGroupingDataSourceId(bg):
    """Get business grouping Data_Source id from database"""
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

def writeGroupingsToCsv(filename, groupings):
    """Write business grouping data to CSV for ingest into scribe Workflow 2"""
    f = open(filename, 'w')
    fieldnames = ['order','file_path','thumbnail','width','height', 'id', 'name', 'source_url']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    order = 1
    for g in groupings:
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
    """Write business grouping group data to CSV for ingest into scribe Workflow21"""
    filename = '../../loop_2/project/yellow-pages-2/subjects/groups.csv'
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

    #download subjects from mongodb in Workflow 1 to /exports folder
    config = configparser.ConfigParser()
    config.read('../hitl.config')
    pwd = config.get('MONGO', 'Password')
    cmd = 'mongoexport -h localhost -d loop_dev -c subjects -u loop_dev -o ../exports/yp1/subjects.ndjson --forceTableScan'
    call('echo {} | {}'.format(pwd, cmd), shell=True)

    subjects = ndjson.load(open('../exports/yp1/subjects.ndjson', 'r'))

    items = [{'id': 'gdcustel.usteledirec00004', 'key': 'Birmingham_1955', 'name': 'Birmingham, Alabama, 1955', 'year': '1955'},
         {'id': 'usteledirec.usteledirec05650', 'key': 'Dubuque_1943', 'name': 'Dubuque, Iowa, 1943', 'year': '1943'},
             {'id': 'gdcustel.usteledirec03932', 'key': 'Colorado_Springs_1954', 'name': 'Colorado Springs, Colorado, 1954', 'year': '1954'},
             {'id': 'gdcustel.usteledirec04986x', 'key': 'Chicago_Czech_Slovak_1939', 'name': 'Chicago Czech and Slovak American, 1939', 'year': '1939'}
        ]
    #get all segment subjects from mongo, grouped by page
    segments = getSegments(subjects)
    
    #write segments as annotations to Annotation table
    for seg in segments:
        for s in seg['segments']:
            s['annotation_id'] = writeToAnnotationTable(s)
            #write segment coordinates to Coordinates table if not already there
            if 'annotation_id' in s:
                writeToCoordinatesTable(s)
                
    #get business grouping annotations from Annotation and Coordinates table for each item
    groups = []
    for i in items:
        group = {}
        group['key'] = 'grouping_' + i['key']
        group['name'] = i['name']
        group['external_url'] = 'https://www.loc.gov/resource/' + i['id']
        business_groupings = getBusinessGroupings(i['id'])
        if len(business_groupings) > 0:
            #write business groupings to Data_Source table if it doesn't exist
            for bg in business_groupings:
                writeToDataSourceTable(bg)
            #get Data_Source ids for business groupings
            for bg in business_groupings:
                bg['id'] = getBusinessGroupingDataSourceId(bg)
            #generate group CSV files for scribe workflow 2 ingest
            filename = '../../loop_2/project/yellow-pages-2/subjects/group_grouping_{}.csv'.format(i['key'])
            writeGroupingsToCsv(filename, business_groupings)
            group['cover_image_url'] = business_groupings[0]['source_image_url']
            groups.append(group)

    #write groups to csv
    writeGroups(groups)

