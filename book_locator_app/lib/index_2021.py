## initial imports ------------------------------

import os, sys
assert sys.version_info.major >= 3
sys.path.append( os.environ['BK_LCTR__PROJECT_PATH'] )
from book_locator_app import settings_app  # requires above path to be set


## rest of imports ------------------------------

import json, logging, pprint
import requests


## rest of setup --------------------------------

## setup logging
logging.basicConfig(
    filename=settings_app.INDEXER_LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S'
    )
log = logging.getLogger( 'book_locator_indexer' )
log.info( '\n\nstarting index_2021.py...' )


## Indexer --------------------------------------

class Indexer():

    def __init__( self ):
        log.debug( 'starting __init__()' )
        self.raw_groups = self.prepare_groups()
        self.spreadsheet_group_json_urls = self.prepare_spreadsheet_urls( self.raw_groups )
        self.all_raw_json_data = []
        self.rock_general_floor_a_data = {}
        self.rock_general_floor_b_data = {}
        self.rock_general_floor_2_data = {}
        self.rock_general_floor_3_data = {}
        self.rock_general_floor_4_data = {}
        self.sci_floor_11_data = {}
        self.sci_floor_12_data = {}
        self.sci_floor_13_data = {}
        self.chinese_data = {}
        self.japanese_data = {}
        self.korean_data = {}

    def access_worksheet_json( self ):
        """ Manages spreadsheet queries to gather raw json-data.
            Called by main() """
        log.debug( 'starting access_worksheet_json()' )
        raw_json_data = []
        for entry in self.spreadsheet_group_json_urls:
            log.debug( f'entry, ``{pprint.pformat(entry)}``' )
            assert type(entry) == dict
            log.debug( f'processing worksheet urls for `location_code`, ``{entry["location_code"]}``' )
            worksheet_urls = entry['group_json_urls']
            for worksheet_url in worksheet_urls:
                assert type(worksheet_url) == str
                jsn_obj = self.query_spreadsheet( worksheet_url )
                raw_json_data.append( jsn_obj )
            break
        # log.debug( f'raw_json_data, ``{raw_json_data}``' )
        return raw_json_data

    def query_spreadsheet( self, worksheet_url ):
        """ Queries spreadsheet.
            Called by access_worksheet_json() """
        log.debug( f'querying worksheet_url, ``{worksheet_url}``' )
        assert type( worksheet_url ) == str
        r = requests.get( worksheet_url )
        content = r.content.decode( 'utf-8' )
        start_string = 'Query.setResponse('
        start_position = content.find( start_string ) + len( start_string )
        end_position = len( ');' )
        jsn_str = content[start_position: -end_position]
        jsn_obj = json.loads( jsn_str )
        log.debug( f'jsn_obj, ``{pprint.pformat( jsn_obj )}``' )
        return jsn_obj

    def prepare_spreadsheet_urls( self, raw_groups ):
        """ Populates Indexer.spreadsheet_urls on instantiation.
            Called by __init__() """
        log.debug( 'starting prepare_spreadsheet_urls()' )
        assert type( raw_groups ) == list
        spreadsheet_group_json_urls = []
        for group in raw_groups:
            assert type(group) == dict
            spreadsheet_id = group['spreadsheet_id']
            json_urls = []
            for worksheet_id in group['worksheet_ids']:
                json_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:json&gid={worksheet_id}'
                json_urls.append( json_url )
            dct = {
                'location_code': group['location_code'],
                'group_json_urls': json_urls
            }
            spreadsheet_group_json_urls.append( dct )
        return spreadsheet_group_json_urls

    def prepare_groups( self ):
        """ Populates Indexer.groups on instantiation.
            Called by __init__() """
        log.debug( 'starting prepare_groups()' )
        raw_groups = [
            {
                'location_code': 'rock',
                'spreadsheet_id': settings_app.ROCK_GENERAL_SPREADSHEET_ID,
                'worksheet_ids': [
                    settings_app.ROCK_GENERAL_FLOOR_A_WORKSHEET_ID,
                    settings_app.ROCK_GENERAL_FLOOR_B_WORKSHEET_ID,
                    settings_app.ROCK_GENERAL_FLOOR_2_WORKSHEET_ID,
                    settings_app.ROCK_GENERAL_FLOOR_3_WORKSHEET_ID,
                    settings_app.ROCK_GENERAL_FLOOR_4_WORKSHEET_ID,
                ]
            },
            {
                'location_code': 'sci',
                'spreadsheet_id': settings_app.SCI_SPREADSHEET_ID,
                'worksheet_ids': [
                    settings_app.SCI_FLOOR_11_WORKSHEET_ID,
                    settings_app.SCI_FLOOR_12_WORKSHEET_ID,
                    settings_app.SCI_FLOOR_13_WORKSHEET_ID,
                ]
            },
            {
                'location_code': 'rock-chinese',
                'spreadsheet_id': settings_app.ROCK_CJK_SPREADSHEET_ID,
                'worksheet_ids': [
                    settings_app.CHINESE_WORKSHEET_ID,
                ]
            },
            {
                'location_code': 'rock-japanese',
                'spreadsheet_id': settings_app.ROCK_CJK_SPREADSHEET_ID,
                'worksheet_ids': [
                    settings_app.JAPANESE_WORKSHEET_ID,
                ]
            },
            {
                'location_code': 'rock-korean',
                'spreadsheet_id': settings_app.ROCK_CJK_SPREADSHEET_ID,
                'worksheet_ids': [
                    settings_app.KOREAN_WORKSHEET_ID,
                ]
            },
        ]
        return raw_groups

    ## end class Indexer()


## runner ---------------------------------------

def main():
    log.debug( 'starting `def main()`' )
    indexer = Indexer()
    log.debug( f'indexer.spreadsheet_group_json_urls, ``{pprint.pformat(indexer.spreadsheet_group_json_urls)}``' )
    indexer.all_raw_json_data = indexer.access_worksheet_json()
    # indexer.populate_worksheet_data()

if __name__ == "__main__":
    log.debug( 'starting `if __name__...`' )
    main()
