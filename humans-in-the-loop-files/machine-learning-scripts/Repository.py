import psycopg2
import configparser
from Annotation import Annotation
from DataSource import DataSource
from TextValue import TextValue
from Coordinate import Coordinate
from datetime import datetime

class Repository:

    def get_data_source_pages(self):
        conn = None
        to_return = list()
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'select * from "Data_Source" d where "source_system" = \'ml\''
            sql += 'and exists ( select * from "Annotation" a where "subject_type" = \'page\' and "ml_version_id" is not null and a."id" = d."annotation_id" ) ' 
            sql += 'and not exists (select * from "Annotation" a where "source_type" = \'page\' and "subject_type" = \'page ocr\' and a."data_source_id" = d."id" );'
            cur.execute(sql)

            row = cur.fetchone()
    
            while row is not None:
                to_return.append(self.parse_data_sources(row))
                row = cur.fetchone()

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return to_return

    def get_ml_process_id(self, name):
        conn = None
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'select id FROM public."ML_Process" where name = %s' 
            cur.execute(sql, (name,))

            row = cur.fetchone()
    
            if row is not None:
                id = int(row[0])
                return id

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return 0

    def get_ml_version_id(self, process_id, version):
        conn = None
        
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'select id FROM public."ML_Version" where ml_process_id = %s and version_number = %s;' 
            
            cur.execute(sql, (process_id, version))

            row = cur.fetchone()
    
            if row is not None:
                return int(row[0])

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return 0

    def insert_ml_version(self, ml_process_id, version_number):
            conn = None
            try:
                params = self.config()
                conn = psycopg2.connect(**params)
                cur = conn.cursor()

                sql = 'INSERT INTO public."ML_Version"(ml_process_id, version_number, date_time)' 
                sql += ' VALUES(%s, %s, %s)'
                sql += ' returning id;'
                cur.execute(sql, (ml_process_id, version_number, datetime.now()))
                id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                return id
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
            finally:
                if conn is not None:
                    conn.close()
            return 0

    def get_coordinates(self, annotation_id):
        conn = None
        to_return = list()
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'SELECT id, x, y, width, height, annotation_id FROM public."Coordinates" where annotation_id=' + str(annotation_id) + ';' 
            
            cur.execute(sql)

            row = cur.fetchone()
    
            while row is not None:
                rec = self.parse_coordinates(row)
                to_return.append(rec)
                row = cur.fetchone()

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return to_return

    def insert_coordinates(self, coordinate: Coordinate):
        conn = None
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'INSERT INTO public."Coordinates"(x, y, width, height, annotation_id)' 
            sql += ' VALUES(%s, %s, %s, %s, %s)'
            sql += ' returning id;'
            cur.execute(sql, (coordinate.x, coordinate.y, coordinate.width, coordinate.height, coordinate.annotation_id))
            id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return id
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return 0

    def insert_text_value(self, textvalue):
        conn = None
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'INSERT INTO public."Text_Value"(key, value, coordinates_id, external_id)' 
            sql += ' VALUES(%s, %s, %s, %s)'
            sql += ' returning id;'
            cur.execute(sql, (textvalue.key, textvalue.value, textvalue.coordinates_id, textvalue.external_id))
            id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return id
        except (Exception, psycopg2.DatabaseError) as error:
            print("ERROR")
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return 0

    def parse_coordinates(self, row):
        rec = Coordinate()
        rec.id = row[0]
        rec.x = int(row[1])
        rec.y = int(row[2])
        rec.width = int(row[3])
        rec.height = int(row[4])
        rec.annotation_id = row[5]
        return rec

    # Data Source
    def insert_data_source(self, datasource: DataSource):
        conn = None
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'INSERT INTO public."Data_Source"(name, type, source_system, source_id, parent_id, source_url, source_image_url, height, width, location, annotation_id, x, y)' 
            sql += 'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            #sql += ' VALUES (\'' + str(datasource.name) + '\', \'' + str(datasource.type) + '\', \'' + str(datasource.source_system) + '\',\''+ str(datasource.source_id)  +'\',\'' + str(datasource.parent_id) + ', \''+ str(datasource.source_url) + '\', \''+str(datasource.source_image_url)+'\', '+str(datasource.height)+', '+str(datasource.width)+', \''+str(datasource.location) + '\')'

            sql += ' returning id;'
            cur.execute(sql, (datasource.name, datasource.type, datasource.source_system, datasource.source_id, datasource.parent_id, datasource.source_url, datasource.source_image_url, datasource.height, datasource.width, datasource.location, datasource.annotation_id, datasource.x, datasource.y))
            id = cur.fetchone()[0]
            
            conn.commit()
            cur.close()
            return id
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return 0

    def get_data_source(self, id):
        conn = None
        rec = None
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'SELECT id, name, type, source_system, source_id, parent_id, source_url, source_image_url, height, width, location, x, y FROM public."Data_Source" where id=' + str(id) + ';' 
            
            cur.execute(sql)

            row = cur.fetchone()
    
            if row is not None:
                rec = self.parse_data_sources(row)

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return rec

    def get_data_source_with_ocr(self):
        conn = None
        to_return = list()
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'SELECT id, name, type, source_system, source_id, parent_id, source_url, source_image_url, height, width, location, x, y '
            sql += ' from "Data_Source" d'
            sql += ' where exists ('
            sql += '  select * from "Data_Source" o'
            sql += '  where o."parent_id" = d."id" and "type" = \'page OCR\''
            sql += ');' 
            
            cur.execute(sql)

            row = cur.fetchone()
    
            while row is not None:
                rec = self.parse_data_sources(row)
                to_return.append(rec)
                row = cur.fetchone()

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return to_return

    def get_text_value(self, coordinates_id):
            conn = None
            to_return = None
            try:
                params = self.config()
                conn = psycopg2.connect(**params)
                cur = conn.cursor()

                sql = 'SELECT id, key, value, coordinates_id, external_id FROM public."Text_Value"  '
                sql += ' where coordinates_id =' + str(coordinates_id) + ';'
                
                cur.execute(sql)

                row = cur.fetchone()
        
                if row is not None:
                    to_return = self.parse_text_value(row)

                cur.close()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
            finally:
                if conn is not None:
                    conn.close()
            return to_return

    def get_group_business_type_annotation(self, parent_id):
        conn = None
        rec = None
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'SELECT id, source_type, ml_version_id, cs_task_id, data_source_id, confidence, subject_type, created_at, parent_id'
            sql += ' from "Annotation"'
            sql += ' where subject_type = \'business type\' and ml_version_id is not null and parent_id = \'' + str(parent_id) + '\''
            sql += ';' 
            
            cur.execute(sql)

            row = cur.fetchone()

            if row is not None:
                rec = self.parse_annotations(row)

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return rec

    def get_page_ocr_annotations(self):
        conn = None
        to_return = list()
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'SELECT id, source_type, ml_version_id, cs_task_id, data_source_id, confidence, subject_type, created_at, parent_id'
            sql += ' from "Annotation" a'
            sql += ' where source_type = \'page ocr\' and ml_version_id is not null and subject_type = \'business listing\''
            sql += ' and not exists (select * from "Annotation" a1 where a1.data_source_id = a.data_source_id and subject_type = \'structured business listing\')'
            sql += ';' 
            
            cur.execute(sql)

            row = cur.fetchone()

            while row is not None:
                rec = self.parse_annotations(row)
                to_return.append(rec)
                row = cur.fetchone()

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return to_return

    def update_location(self, id, location):
        conn = None
        to_return = list()
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'UPDATE "Data_Source"'
            sql += ' SET location = \'' + location + '\''
            sql += ' WHERE id = ' + str(id)
            sql += ';' 
            
            cur.execute(sql)
            
            conn.commit()

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return to_return
            
    def get_text_value_business_listing(self):
        conn = None
        to_return = list()
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'SELECT id, name, type, source_system, source_id, parent_id, source_url, source_image_url, height, width, location, x, y '
            sql += ' from "Data_Source" d'
            sql += ' where exists ('
            sql += '  select * from "Data_Source" o'
            sql += '  where o."parent_id" = d."id" and "type" = \'page OCR\''
            sql += ');' 
            
            cur.execute(sql)

            row = cur.fetchone()
    
            while row is not None:
                rec = self.parse_data_sources(row)
                to_return.append(rec)
                row = cur.fetchone()

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return to_return

    def get_data_sources_to_process(self):
            conn = None
            to_return = list()
            try:
                params = self.config()
                conn = psycopg2.connect(**params)
                cur = conn.cursor()

                sql = 'SELECT id, name, type, source_system, source_id, parent_id, source_url, source_image_url, height, width, location FROM public."Data_Source" where type=\'digital object image\' and parent_id is not null' 
                
                cur.execute(sql)

                row = cur.fetchone()
        
                while row is not None:
                    rec = self.parse_data_sources(row)
                    to_return.append(rec)
                    row = cur.fetchone()

                cur.close()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
            finally:
                if conn is not None:
                    conn.close()
            return to_return
    def get_data_source_for_annotation(self, annotation_id):
                conn = None
                to_return = list()
                try:
                    params = self.config()
                    conn = psycopg2.connect(**params)
                    cur = conn.cursor()

                    sql = 'SELECT id, name, type, source_system, source_id, parent_id, source_url, source_image_url, height, width, location, x, y FROM public."Data_Source" where annotation_id=' + str(annotation_id) + ' and parent_id is not null' 
                    
                    cur.execute(sql)

                    row = cur.fetchone()
            
                    if row is not None:
                        rec = self.parse_data_sources(row)
                        return rec

                    cur.close()
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                finally:
                    if conn is not None:
                        conn.close()
                return to_return
    def parse_data_sources(self, row):
    #name, type, source_system, source_id, parent_id, source_url, source_image_url, height, width, location
        rec = DataSource()
        rec.id = row[0]
        rec.name = row[1]
        rec.type = row[2]
        rec.source_system = row[3]
        rec.source_id = row[4]
        rec.parent_id = row[5]
        rec.source_url = row[6]
        rec.source_image_url = row[7]
        rec.height = row[8]
        rec.width = row[9]
        rec.location = row[10]
        rec.x = row[11]
        rec.y = row[12]
        return rec
    
    def parse_text_value(self, row):
    #id, key, value, coordinates_id, external_id
        rec = TextValue()
        rec.id = row[0]
        rec.key = row[1]
        rec.value = row[2]
        rec.coordinates_id = row[3]
        rec.external_id = row[4]
        return rec

    # Annotations
    def insert_annotation(self, annotation: Annotation):
        conn = None
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'INSERT INTO public."Annotation"(source_type, ml_version_id, cs_task_id, data_source_id, confidence, subject_type, created_at, parent_id)' 
            #sql += ' VALUES (\'' + str(annotation.source_type) + '\', ' + str(annotation.ml_version_id) + ', ' + str(annotation.cs_task_id) + ',\''+ str(annotation.data_source_id)  +'\',\'' + str(annotation.confidence) + '\', \''+str(annotation.subject_type_id)+'\', \''+str(annotation.created_at) + '\')'
            
            sql += 'VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
            #sql += ' VALUES (\'' + str(datasource.name) + '\', \'' + str(datasource.type) + '\', \'' + str(datasource.source_system) + '\',\''+ str(datasource.source_id)  +'\',\'' + str(datasource.parent_id) + ', \''+ str(datasource.source_url) + '\', \''+str(datasource.source_image_url)+'\', '+str(datasource.height)+', '+str(datasource.width)+', \''+str(datasource.location) + '\')'

            sql += ' returning id;'

            cur.execute(sql, (annotation.source_type, annotation.ml_version_id, annotation.cs_task_id, annotation.data_source_id, annotation.confidence, annotation.subject_type, annotation.created_at, annotation.parent_id))

            conn.commit()

            id = cur.fetchone()[0]

            cur.close()
            return id
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return 0

    def get_annotations(self, data_source_id):
        conn = None
        to_return = list()
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'SELECT id, source_type, ml_version_id, cs_task_id, data_source_id, confidence, subject_type, created_at, parent_id FROM public."Annotation" WHERE data_source_id=' + data_source_id + ';'
           
            cur.execute(sql)

            row = cur.fetchone()
    
            if row is not None:
                rec = self.parse_annotations(row)
                to_return.append(rec)
                row = cur.fetchone()

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return to_return

    def get_business_listing_annotations(self):
        conn = None
        to_return = list()
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'SELECT id, source_type, ml_version_id, cs_task_id, data_source_id, confidence, subject_type, created_at, parent_id '
            sql += 'from "Annotation" '
            sql += ' where subject_type = \'business listing entities\' and cs_task_id is not null;'
            cur.execute(sql)

            row = cur.fetchone()
    
            while row is not None:
                rec = self.parse_annotations(row)
                to_return.append(rec)
                row = cur.fetchone()

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return to_return

    def get_page_annotations(self):
        conn = None
        to_return = list()
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'SELECT id, source_type, ml_version_id, cs_task_id, data_source_id, confidence, subject_type, created_at, parent_id FROM public."Annotation" WHERE subject_type=\'page\';'
           
            cur.execute(sql)

            row = cur.fetchone()
    
            while row is not None:
                rec = self.parse_annotations(row)
                to_return.append(rec)
                row = cur.fetchone()

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return to_return

    def get_ad_annotations(self, data_source_id):
        conn = None
        to_return = list()
        try:
            params = self.config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            sql = 'SELECT id, source_type, ml_version_id, cs_task_id, data_source_id, confidence, subject_type, created_at, parent_id FROM public."Annotation" WHERE subject_type=\'ad\' and data_source_id = ' +  str(data_source_id) + ';'
           
            cur.execute(sql)

            row = cur.fetchone()
    
            while row is not None:
                rec = self.parse_annotations(row)
                to_return.append(rec)
                row = cur.fetchone()

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return to_return
    def parse_annotations(self, row):
        rec = Annotation()
        rec.id = row[0]
        rec.source_type = row[1]
        rec.ml_version_id = row[2]
        rec.cs_task_id = row[3]
        rec.data_source_id = row[4]
        rec.confidence = row[5]
        rec.subject_type = row[6]
        rec.created_at = row[7]
        rec.parent_id = row[8]
        return rec

    def config(self, filename='database.ini', section='postgresql'):
        # create a parser
        parser = configparser.ConfigParser()
        # read config file
        parser.read(filename)
    
        # get section, default to postgresql
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    
        return db