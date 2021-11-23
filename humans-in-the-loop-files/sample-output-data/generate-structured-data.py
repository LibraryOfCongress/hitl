#!/usr/bin/env python

import configparser
import math
import psycopg2
import psycopg2.extras
import csv
import json

def dbconnect():
    """Connect to the validation database"""
    config = configparser.ConfigParser()
    config.read('..crowdsourcing-data-flow-scripts/hitl.config')
    host = config.get('POSTGRES', 'Host')
    user = config.get('POSTGRES', 'User')
    pw = config.get('POSTGRES', 'Password')
    port = config.get('POSTGRES', 'Port')
    dbs = config.get('POSTGRES', 'Database')
    #fire up the database connection
    conn = psycopg2.connect("dbname='{0}' user='{1}' host='{2}' password='{3}'".format(dbs, user, host, pw))
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    return cur, conn

def getMLData():
    """Get ML-generated business listing entity data and their parent data from the db"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    sql = """select yp.id as "yellow_pages_id", yp."name" as "directory", page."name" as "page", page."source_url", page."source_image_url", page."source_id" as "image_id", page."x" as "page_x", page."y" as "page_y",
            page."width" as "page_width", page."height" as "page_height", ents.*, types."business_type_id", types."value" as "business_type"
            from (select bg.id as "grouping_id", bg."data_source_id", bl.id as "listing_id", a.id as "structured_listing_id", t."key", t."value", bltext."value" as "listing_text", blc."x", blc."y", blc."width", blc."height"
            from "Annotation" a
            join "Coordinates" c
            on a."id" = c."annotation_id"
            join "Text_Value" t
            on c."id" = t."coordinates_id"
            join "Annotation" bl
            on a."parent_id" = bl."id"
            join "Coordinates" blc
            on bl.id = blc."annotation_id"
            join "Text_Value" bltext
            on blc.id = bltext."coordinates_id"
            join "Annotation" bg
            on bl."parent_id" = bg."id"
            where a."ml_version_id" is not null
            and a."subject_type" = 'structured business listing') ents
            join (select bg."id" as "grouping_id", a."id" as "business_type_id", t."key", t."value"
            from "Annotation" a
            join "Coordinates" c
            on a."id" = c."annotation_id"
            join "Text_Value" t
            on c."id" = t."coordinates_id"
            join "Annotation" bg
            on a."parent_id" = bg."id"
            where a."ml_version_id" is not null
            and a."subject_type" = 'business type') types
            on ents."grouping_id" = types."grouping_id"
            join "Data_Source" ocr
            on ents."data_source_id" = ocr.id
            join "Data_Source" page
            on ocr."parent_id" = page.id
            join "Data_Source" image
            on page."parent_id" = image.id
            join "Data_Source" yp
            on image."parent_id" = yp.id
            order by yp.id, page.id, types."grouping_id", ents."listing_id";"""
    try:
        cur.execute(sql,)
    except:
        conn.rollback()
        cur.execute(sql)
    rows = cur.fetchall()
    return rows

def getCSData():
    """Get CS-generated business listing entity data and their parent data from the db"""
    db = dbconnect()
    cur = db[0]
    conn = db[1]
    sql = """select yp.id as "yellow_pages_id", yp."name" as "directory", page."name" as "page", page."source_url", page."source_image_url", page."source_id" as "image_id", page."x" as "page_x", page."y" as "page_y",
            page."width" as "page_width", page."height" as "page_height", ents.*, types."business_type_id", types."value" as "business_type"
            from (select a."id" as "listing_id", l."x", l."y", l."width", l."height", tv."key", tv."value", g.id as "grouping_id", g."parent_id" as "page_id", g."x" as "grouping_x", g."y" as "grouping_y"  
            from "Text_Value" tv
            join "Coordinates" c
            on tv."coordinates_id" = c."id"
            join "Annotation" a
            on c."annotation_id" = a."id"
            join "Data_Source" l
            on a."data_source_id" = l.id
            join "Data_Source" g
            on l."parent_id" = g.id
            where a."subject_type" = 'business listing entities') ents
            join (select g."id" as "grouping_id", a."id" as "business_type_id", tv."key", tv."value"
            from "Text_Value" tv
            join "Coordinates" c
            on tv."coordinates_id" = c."id"
            join "Annotation" a
            on c."annotation_id" = a."id"
            join "Data_Source" g
            on a."data_source_id" = g.id
            where a."subject_type" = 'business type'
            and a."cs_task_id" is not null) types
            on ents."grouping_id" = types."grouping_id"
            join "Data_Source" page
            on ents."page_id" = page.id
            join "Data_Source" image
            on page."parent_id" = image.id
            join "Data_Source" yp
            on image."parent_id" = yp.id
            order by yp.id, page.id, types."grouping_id", ents."listing_id";"""
    try:
        cur.execute(sql,)
    except:
        conn.rollback()
        cur.execute(sql)
    rows = cur.fetchall()
    return rows

def makeCSUrl(listing):
    """Generate IIIF image url for crowdsourced business listings"""
    #split parent url by image id
    image_id = listing['image_id'].split('.')[1]
    base_url = listing['source_image_url'].split(image_id)[0]
    #add business grouping x and y to parent coords and replace width and height
    coords = [math.ceil(float(listing['page_x'])) + math.ceil(float(listing['grouping_x'])/2) + math.ceil(float(listing['x'])),
              math.ceil(float(listing['page_y'])) + math.ceil(float(listing['grouping_y'])/2) + math.ceil(float(listing['y'])),
              math.ceil(float(listing['width'])),
              math.ceil(float(listing['height']))]
    coords = [','.join([str(c) for c in coords])]
    #reconstruct url with new business grouping coords
    after_coords = listing['source_image_url'].split(image_id)[1].split('/')[2:]
    coords.extend(after_coords)
    rest_of_url = '/'.join(coords)
    url = base_url + image_id + '/' + rest_of_url
    return url

def makeUrl(listing):
    """Generate IIIF image url for business listing"""
    #split parent url by image id
    image_id = listing['image_id'].split('.')[1]
    base_url = listing['source_image_url'].split(image_id)[0]
    #add business grouping x and y to parent coords and replace width and height
    coords = [math.ceil(float(listing['page_x']) + float(listing['x'])),
              math.ceil(float(listing['page_y']) + float(listing['y'])),
              math.ceil(float(listing['width'])),
              math.ceil(float(listing['height']))]
    coords = [','.join([str(c) for c in coords])]
    #reconstruct url with new business grouping coords
    after_coords = listing['source_image_url'].split(image_id)[1].split('/')[2:]
    coords.extend(after_coords)
    rest_of_url = '/'.join(coords)
    url = base_url + image_id + '/' + rest_of_url
    return url

def structureByListing(data, source_type):
    listings = {}
    for d in data:
        #start a dict for the listing if it's not yet in listings
        if d['listing_id'] not in listings:
            listing = {}
            listing['directory'] = d['directory']
            listing['page'] = d['page']
            listing['url'] = d['source_url']
            listing['business_type'] = [d['business_type']]
            listing[d['key']] = [d['value']]
            listing['listing_text'] = d['listing_text'] if 'listing_text' in d else None
            if source_type == 'cs':
                listing['listing_image_url'] = makeCSUrl(d)
            else:
                listing['listing_image_url'] = makeUrl(d)
            listings[d['listing_id']] = listing
        #add data to an existing listing
        else:
            #add entity to listing
            #if it already exists, append it to the list
            if d['key'] in listings[d['listing_id']]:
                if d['value'] not in listings[d['listing_id']][d['key']]:
                    listings[d['listing_id']][d['key']].append(d['value'])
            #otherwise add it to the listing
            else:
                listings[d['listing_id']][d['key']] = [d['value']]
            #add business type to listing, if it differs from what's there
            if d['business_type'] not in listings[d['listing_id']]['business_type']:
                listings[d['listing_id']][business_type].append(d['business_type'])
    return listings

def convertToList(listings):
    as_list = []
    for k, v in listings.items():
        v['listing_id'] = k
        as_list.append(v)
    return as_list

def writeToCsv(filename, listings):
    f = open(filename, 'w')
    fieldnames = ['listing_id', 'business_type', 'business_name', 'address', 'phone_number', 'other_information',
                 'see_advertisement', 'graphic', 'directory', 'image_url', 'listing_image_url', 'page', 'full_text']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for l in listings:
        row = {}
        row['listing_id'] = l['listing_id']
        row['business_type'] = ' | '.join(b for b in l['business_type']) if 'business_type' in l else None
        row['business_name'] = ' | '.join(b for b in l['business name']) if 'business name' in l else None
        row['address'] = ' | '.join(b for b in l['address']) if 'address' in l else None
        row['phone_number'] = ' | '.join(b for b in l['phone number']) if 'phone number' in l else None
        row['other_information'] = ' | '.join(b for b in l['other information']) if 'other information' in l else None
        row['graphic'] = ' | '.join(b for b in l['graphic']) if 'graphic' in l else None
        row['see_advertisement'] = ' | '.join(b for b in l['see advertisement']) if 'see advertisement' in l else None
        row['directory'] = l['directory']
        row['image_url'] = l['url']
        row['listing_image_url'] = l['listing_image_url']
        row['page'] = l['page']
        row['full_text'] = l['listing_text']
        writer.writerow(row)
    f.close()

if __name__ == "__main__":

    #get entity listing data from database
    ml_data = getMLData()
    ml_listings = structureByListing(ml_data, 'ml')
    list_ml = convertToList(ml_listings)
    writeToCsv('all_ml_listings.csv', list_ml)
    
    cs_data = getCSData()
    cs_listings = structureByListing(cs_data, 'cs')
    list_cs = convertToList(cs_listings)
    writeToCsv('all_cs_listings.csv', list_cs)
