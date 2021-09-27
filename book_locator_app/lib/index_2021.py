## initial imports ------------------------------

import os, sys
assert sys.version_info.major >= 3
sys.path.append( os.environ['BK_LCTR__PROJECT_PATH'] )
from book_locator_app import settings_app  # requires above path to be set


## rest of imports ------------------------------

import logging, pprint


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
        log.debug( 'starting ``__init__()' )
        self.raw_groups = self.prepare_groups()
        self.spreadsheet_group_json_urls = self.prepare_spreadsheet_urls( self.raw_groups )

    def prepare_spreadsheet_urls( self, raw_groups ):
        """ Populates Indexer.spreadsheet_urls on instantiation.
            Called by __init__() """
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
    log.debug( f'raw_groups, ``{pprint.pformat( indexer.raw_groups )}``' )
    log.debug( f'spreadsheet_group_json_urls, ``{pprint.pformat( indexer.spreadsheet_group_json_urls )}``' )

if __name__ == "__main__":
    log.debug( 'starting `if __name__...`' )
    main()
