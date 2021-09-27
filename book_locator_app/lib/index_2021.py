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
        self.groups = self.prepare_groups()

    def prepare_groups( self ):
        groups = [
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
        return groups


    ## end class Indexer()


## runner ---------------------------------------

def main():
    log.debug( 'starting `def main()`' )
    indexer = Indexer()
    log.debug( f'groups, ``{pprint.pformat( indexer.groups )}``' )

if __name__ == "__main__":
    log.debug( 'starting `if __name__...`' )
    main()
