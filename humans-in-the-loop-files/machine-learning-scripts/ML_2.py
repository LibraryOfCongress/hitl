# Iterate through image data sources 
# Identify pages and advertisements, store as data sources, annotations, and coordinates in the database

from Repository import Repository
from Identifier import Identifier
from datetime import datetime

def main():
    repo = Repository()
    conf = repo.config(filename='database.ini', section='ml')
    data_sources = repo.get_data_sources_to_process()
    identifier = Identifier()
    identifier.identify_pages(data_sources)
    identifier.identify_ads()
        

if __name__ == "__main__":
    main()