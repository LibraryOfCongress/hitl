#!/usr/bin/env python

"""This script pulls page images and relevant metadata from the workflow database and outputs CSV files of page
subjects for ingest into Scribe Workflow 1. It is assumed that individual page coordinates will have been generated
by the page detection algorithm and written to the Data_Source table for each digital object listed in the items
variable. The full process involves:
- Get source urls for individual images from the IIIF manifest for each item and writing to the source_url column of
the Data_Source table for each digital object image. (Sequence number is not a reliable predictor for image identifier, 
these urls must be pulled directly from the manifest)
- Get metadata from Data_Source table for pages in each item
- Generate the IIIF image url for each based on page image coordinates and write to Data_Source table
- Output CSV files for each item and a CSV file with all items and item-level metadata to the Workflow 1 /subjects
directory

After running this script, run `rake project:load[yellow-pages-1]` in /loop_1 to load new 
page data to Scribe
"""

import requests
import configparser
import json
import csv
import ndjson
import math
import psycopg2
import psycopg2.extras

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

def getPageData(do_id):
    """Get page data for a yellow pages directory (digital object)"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    #need to change a."ml_version_id" to a."subject_type" = 'page'
    sql = """select a.*, c.*, ds.id as "ds_id", ds."name" as "do_name", ds."source_id", ds."source_url"
            from "Coordinates" c
            join "Annotation" a
            on a.id = c."annotation_id"
            join "Data_Source" ds
            on a."data_source_id" = ds.id
            where a."ml_version_id" = 4
            and a."data_source_id" in (select ds1.id
            from "Data_Source" ds1
            join "Data_Source" ds2
            on ds1."parent_id" = ds2."id"
            where ds2."source_id" = %s )
            order by "do_name", "x";"""
    data = (do_id,)
    try:
        cur.execute(sql, data)
    except:
        conn.rollback()
        cur.execute(sql, data)
    rows = cur.fetchall()
    return rows

def makeUrl(data):
    """Make IIIF image url for the business grouping"""
    coords = [math.ceil(float(data['x'])), math.ceil(float(data['y'])), math.ceil(float(data['width'])), math.ceil(float(data['height']))]
    coords = ','.join([str(c) for c in coords])
    url = data['parent_source_image_url'].replace('full', coords)
    return url

def getManifest(item):
    """Get IIIF manifest for the digital object"""
    base = 'https://www.loc.gov/item/{}/manifest.json'
    item = item.split('.')[1]
    url = base.format(item)
    query = requests.get(url)
    manifest = query.json()
    return manifest

def getWebPage(manifest, source_id):
    """Get page url"""
    page = None
    files = manifest['sequences'][0]['canvases']
    for f in files:
        if f['@id'].endswith(source_id.split('.')[1]):
            page = f['related']
    return page

def getSourceUrl(source_id, id):
    """Get source url from IIIF manifest for the collection"""
    manifest = getManifest(id)
    url = getWebPage(manifest, source_id)
    return url

def getPages(do_id):
    "Get page annotation coordinates for all images from a specified yellow pages directory"
    data = getPageData(do_id)
    pages = []
    prev = ''
    for d in data:
        page = {}
        #append 'a' or 'b' for page id depending on R or L, as ordered by x coord in sql query
        if d['source_id'] == prev:
            page['name'] = d['source_id'] + '_b'
        else:
            page['name'] = d['source_id'] + '_a'
        prev = d['source_id']
        page['type'] = 'page'
        page['source_id'] = d['source_id']
        page['source_system'] = 'lc'
        page['source_url'] = ''
        page['source_image_url'] = makeUrl(d)
        page['height'] = float(d['height'])*2
        page['width'] = float(d['width'])*2
        page['x'] = float(d['x'])*2
        page['y'] = float(d['y'])*2
        page['parent_id'] = d['ds_id']
        page['annotation_id'] = d['annotation_id']
        pages.append(page)
    return pages

def getPagesDS(do_id):
    """Get pages from Data_Source table in database, if they already exist there"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    sql = """select page.*, parent."source_url" as "parent_source_url", parent."source_image_url" as "parent_source_image_url"
            from "Data_Source" page
            join "Data_Source" parent
            on page."parent_id" = parent."id"
            where page."type" = 'page'
            and page."parent_id" in (select "id"
            from "Data_Source" image
            where image."parent_id" in (select "id"
            from "Data_Source" item
            where item."source_id" = %s)) 
            order by page."name";"""
    data = (do_id,)
    try:
        cur.execute(sql, data)
    except:
        conn.rollback()
        cur.execute(sql, data)
    rows = cur.fetchall()
    conn.commit()
    pages = []
    order = 1
    for r in rows:
        page = {}
        page['order'] = order
        page['source_image_url'] = makeUrl(r)
        page['width'] = r['width']
        page['height'] = r['height']
        page['id'] = r['id']
        page['name'] = r['name']
        page['source_url'] = r['parent_source_url']
        pages.append(page)
        order += 1
    return pages
    
def writeSourceUrlsToDOs(item_id):
    """Write the LC page source urls from the IIIF manifest to the page in Data_Source table"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    #get all digital object image ids for a digital object
    sql_a = """select image."source_id"
            from "Data_Source" image
            join "Data_Source" parent
            on image."parent_id" = parent."id"
            where image."type" = 'digital object image'
            and parent."source_id" = %s"""
    data_a = (item_id,)
    try:
        cur.execute(sql_a, data_a)
    except:
        conn.rollback()
        cur.execute(sql_a, data_a)
    rows = cur.fetchall()
    #for each image id, get corresponding web page url from IIIF manifest
    for r in rows:
        url = getSourceUrl(r['source_id'], item_id)
        #write source url to Data_Source table for digital object image    
        sql_b = """update "Data_Source" set "source_url" = %s
        where "source_id" = %s
        and "type" = 'digital object image'
        returning id;"""
        data_b = (url, r['source_id'])
        try:
            cur.execute(sql_b, data_b)
        except:
            conn.rollback()
            cur.execute(sql_b, data_b)
        rows = cur.fetchall()
        conn.commit()
    
def writeUrlsToDataSource(p):
    """Write source and source image urls to Data_Source table"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    sql = """update "Data_Source" set (source_image_url, source_url) = (%s, %s)
    where id = %s
    returning id;"""
    data = (p['source_image_url'], p['source_url'], p['id'])
    try:
        cur.execute(sql, data)
    except:
        conn.rollback()
        cur.execute(sql, data)
    rows = cur.fetchall()
    conn.commit()
    
def writeToDataSourceTable(p):
    """Write page data to Data_Source table (if a data source with same name and annotation
    id does not yet exist)"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    sql = """with ins as(insert into "Data_Source" (name, type, source_system, 
            source_id, parent_id, source_url, source_image_url, 
            height, width, x, y, annotation_id)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            on conflict (name, annotation_id) do nothing
            returning id)
            select id from ins
            union all
            select id from "Data_Source"
            select name = %s
            limit  1;"""
    data = (p['name'], p['type'], p['source_system'], 
            p['source_id'], p['parent_id'], p['source_url'], p['source_image_url'], 
            p['height'], p['width'], p['x'], p['y'], p['annotation_id'], p['name'])
    try:
        cur.execute(sql, data)
    except:
        conn.rollback()
        cur.execute(sql, data)
    rows = cur.fetchall()
    conn.commit()
    id = rows[0]['id']
    return id
      
def writePagesToCsv(filename, pages):
    """Write page data to CSV for ingest into scribe Workflow 1"""
    f = open(filename, 'w')
    fieldnames = ['order','file_path','thumbnail','width','height', 'id', 'name', 'source_url']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    order = 1
    for p in pages:
        row = {}
        row['order'] = order
        row['file_path'] = p['source_image_url']
        row['thumbnail'] = p['source_image_url'].replace('pct:50', 'pct:3.125')
        row['width'] = p['width']
        row['height'] = p['height']
        row['id'] = p['id']
        row['name'] = p['name']
        row['source_url'] = p['source_url']
        writer.writerow(row)
        order += 1
    f.close()

def writePageGroupsToCsv(groups):
    """Write page grouping data to CSV for ingest into scribe Workflow 1"""
    filename = '../../loop_1/project/yellow-pages-1/subjects/groups.csv'
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
    #add or remove items to this list as needed. Items will need to have had pages generated and written to the db
    items = [{'id': 'gdcustel.usteledirec00004', 'key': 'Birmingham_1955', 'name': 'Birmingham, Alabama, 1955', 'year': '1955'},
         {'id': 'usteledirec.usteledirec05650', 'key': 'Dubuque_1943', 'name': 'Dubuque, Iowa, 1943', 'year': '1943'},
             {'id': 'gdcustel.usteledirec03932', 'key': 'Colorado_Springs_1954', 'name': 'Colorado Springs, Colorado, 1954', 'year': '1954'},
             {'id': 'gdcustel.usteledirec04986x', 'key': 'Chicago_Czech_Slovak_1939', 'name': 'Chicago Czech and Slovak American, 1939', 'year': '1939'}
        ]
    groups = []
    for i in items:
        group = {}
        group['key'] = 'page_' + i['key']
        group['name'] = i['name']
        group['external_url'] = 'https://www.loc.gov/resource/' + i['id'].replace('gdcustel', 'usteledirec')

        #write source urls to digital objects in Data_Source table
        writeSourceUrlsToDOs(i['id'])
    
        ##if pages are already in DataSource table
        pages = getPagesDS(i['id'])
        #write source_image_url to page in Data_Source table
        for p in pages:
            writeUrlsToDataSource(p)
        
        #write pages to a group csv
        filename = '../../loop_1/project/yellow-pages-1/subjects/group_page_{}.csv'.format(i['key'])
        writePagesToCsv(filename, pages)
        group['cover_image_url'] = pages[0]['source_image_url']
        groups.append(group)
        
    #write groups to csv
    writePageGroupsToCsv(groups)

