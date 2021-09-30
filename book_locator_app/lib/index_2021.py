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


## Row ------------------------------------------

# class Row():

#     def __init__( self ):
#         log.debug( 'starting Row.__init__()' )
#         self.aisle = ''
#         self.begin = ''
#         self.end = ''
#         self.floor = ''
#         self.location_code = ''

#     ## end class Row()


## Indexer --------------------------------------

class Indexer():

    def __init__( self ):
        log.debug( 'starting Indexer.__init__()' )
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
                jsn_dct = self.query_spreadsheet( worksheet_url )
                jsn_dct['queried_url'] = worksheet_url
                raw_json_data.append( jsn_dct )
            break
        # log.debug( f'raw_json_data, ``{raw_json_data}``' )
        assert type( raw_json_data ) == list
        return raw_json_data

    def organize_json( self ):
        """ Converts self.all_raw_json_data list-data into row-data for each spreadsheet.
            Called by main() """
        log.debug( 'starting organize_json()' )
        # log.debug( f'self.all_raw_json_data, ``{pprint.pformat(self.all_raw_json_data)}``' )
        # 1/0
        assert type( self.all_raw_json_data ) == list
        for worksheet in self.all_raw_json_data:
            assert type( worksheet ) == dict
            log.debug( f'processing worksheet, ``{pprint.pformat(worksheet)}...``' )
            log.debug( f'worksheet.keys(), ``{pprint.pformat(worksheet.keys())}``' )
            log.debug( f'worksheet["table"], ``{worksheet["table"]}``' )
            # 1/0
            table = worksheet['table']
            assert type( table ) == dict
            log.debug( f'table-keys, ``{pprint.pformat(table.keys())}``' )
            # 1/0
            second_row_table_identifier = table['rows'][2]
            log.debug( f'processing table containing, ``{second_row_table_identifier}``' )
            row_list = []
            for row in table['rows']:
                cells = row['c']
                first_cell_data = cells[0]['v']
                log.debug( f'first_cell_data, ``{first_cell_data}``' )
                if first_cell_data == 'aisle':
                    continue
                row_dct = {
                    'aisle': '', 'begin': '', 'end': '', 'floor': '', 'location_code': '' }
                for ( i, cell ) in enumerate( cells ):
                    if i == 0:
                        row_dct['aisle'] = cell['v']
                    elif i == 1:
                        row_dct['begin'] = cell['v']
                    elif i == 2:
                        row_dct['end'] = cell['v']         # /floor/location_code
                    elif i == 3:
                        try:
                            row_dct['floor'] = cell['f']
                        except:
                            row_dct['floor'] = cell['v']
                    elif i == 4:
                        row_dct['location_code'] = cell['v']
                    elif i > 4:
                        break
                row_list.append( row_dct )
            last_entry = row_list[-1]
            if last_entry['location_code'].strip() == 'rock':
                if last_entry['floor'].strip() == 'A':
                    self.rock_general_floor_a_data = row_list
                elif last_entry['floor'].strip() == 'B':
                    self.rock_general_floor_b_data = row_list
                elif last_entry['floor'].strip() == '2':
                    self.rock_general_floor_2_data = row_list
                elif last_entry['floor'].strip() == '3':
                    self.rock_general_floor_3_data = row_list
                elif last_entry['floor'].strip() == '4':
                    self.rock_general_floor_4_data = row_list
            elif last_entry['location_code'].strip() == 'sci':
                if last_entry['floor'].strip() == '11':
                    self.sci_general_floor_11_data = row_list
                elif last_entry['floor'].strip() == '12':
                    self.sci_general_floor_12_data = row_list
                elif last_entry['floor'].strip() == '13':
                    self.sci_general_floor_13_data = row_list
            elif last_entry['location_code'].strip() == 'rock chinese':
                self.chinese_data = row_list
            elif last_entry['location_code'].strip() == 'rock japanese':
                self.japanese_data = row_list
            elif last_entry['location_code'].strip() == 'rock korean':
                self.korean_data = row_list
        log.debug( f'self.rock_general_floor_a_data, ``{pprint.pformat(self.rock_general_floor_a_data)}``' )
        ## end def organize_json()

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
        jsn_dct = json.loads( jsn_str )
        # log.debug( f'jsn_dct, ``{pprint.pformat( jsn_dct )}``' )
        return jsn_dct

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
                'worksheet_info': [
                    {'id': settings_app.ROCK_GENERAL_FLOOR_A_WORKSHEET_ID, 'label': 'rock_general_floor_a' },
                    {'id': settings_app.ROCK_GENERAL_FLOOR_B_WORKSHEET_ID, 'label': 'rock_general_floor_b' },
                    {'id': settings_app.ROCK_GENERAL_FLOOR_2_WORKSHEET_ID, 'label': 'rock_general_floor_2' },
                    {'id': settings_app.ROCK_GENERAL_FLOOR_3_WORKSHEET_ID, 'label': 'rock_general_floor_3' },
                    {'id': settings_app.ROCK_GENERAL_FLOOR_4_WORKSHEET_ID, 'label': 'rock_general_floor_4' }
                ]
            },
            {
                'location_code': 'sci',
                'spreadsheet_id': settings_app.SCI_SPREADSHEET_ID,
                'worksheet_info': [
                    {'id': settings_app.SCI_FLOOR_11_WORKSHEET_ID, 'label': 'sci_floor_11' },
                    {'id': settings_app.SCI_FLOOR_12_WORKSHEET_ID, 'label': 'sci_floor_12' },
                    {'id': settings_app.SCI_FLOOR_13_WORKSHEET_ID, 'label': 'sci_floor_13' },
                ]
            },
            {
                'location_code': 'rock-chinese',
                'spreadsheet_id': settings_app.ROCK_CJK_SPREADSHEET_ID,
                'worksheet_info': [
                    {'id': settings_app.CHINESE_WORKSHEET_ID, 'label': 'rock_chinese' },
                ]
            },
            {
                'location_code': 'rock-japanese',
                'spreadsheet_id': settings_app.ROCK_CJK_SPREADSHEET_ID,
                'worksheet_info': [
                    {'id': settings_app.JAPANESE_WORKSHEET_ID, 'label': 'rock_japanese' },
                ]
            },
            {
                'location_code': 'rock-korean',
                'spreadsheet_id': settings_app.ROCK_CJK_SPREADSHEET_ID,
                'worksheet_info': [
                    {'id': settings_app.KOREAN_WORKSHEET_ID, 'label': 'rock_korean' },
                ]
            },
        ]
        return raw_groups

    # def prepare_groups( self ):
    #     """ Populates Indexer.groups on instantiation.
    #         Called by __init__() """
    #     log.debug( 'starting prepare_groups()' )
    #     raw_groups = [
    #         {
    #             'location_code': 'rock',
    #             'spreadsheet_id': settings_app.ROCK_GENERAL_SPREADSHEET_ID,
    #             'worksheet_ids': [
    #                 settings_app.ROCK_GENERAL_FLOOR_A_WORKSHEET_ID,
    #                 settings_app.ROCK_GENERAL_FLOOR_B_WORKSHEET_ID,
    #                 settings_app.ROCK_GENERAL_FLOOR_2_WORKSHEET_ID,
    #                 settings_app.ROCK_GENERAL_FLOOR_3_WORKSHEET_ID,
    #                 settings_app.ROCK_GENERAL_FLOOR_4_WORKSHEET_ID,
    #             ]
    #         },
    #         {
    #             'location_code': 'sci',
    #             'spreadsheet_id': settings_app.SCI_SPREADSHEET_ID,
    #             'worksheet_ids': [
    #                 settings_app.SCI_FLOOR_11_WORKSHEET_ID,
    #                 settings_app.SCI_FLOOR_12_WORKSHEET_ID,
    #                 settings_app.SCI_FLOOR_13_WORKSHEET_ID,
    #             ]
    #         },
    #         {
    #             'location_code': 'rock-chinese',
    #             'spreadsheet_id': settings_app.ROCK_CJK_SPREADSHEET_ID,
    #             'worksheet_ids': [
    #                 settings_app.CHINESE_WORKSHEET_ID,
    #             ]
    #         },
    #         {
    #             'location_code': 'rock-japanese',
    #             'spreadsheet_id': settings_app.ROCK_CJK_SPREADSHEET_ID,
    #             'worksheet_ids': [
    #                 settings_app.JAPANESE_WORKSHEET_ID,
    #             ]
    #         },
    #         {
    #             'location_code': 'rock-korean',
    #             'spreadsheet_id': settings_app.ROCK_CJK_SPREADSHEET_ID,
    #             'worksheet_ids': [
    #                 settings_app.KOREAN_WORKSHEET_ID,
    #             ]
    #         },
    #     ]
    #     return raw_groups

    ## end class Indexer()


## runner ---------------------------------------

def main():
    log.debug( 'starting `def main()`' )
    indexer = Indexer()
    log.debug( f'indexer.spreadsheet_group_json_urls, ``{pprint.pformat(indexer.spreadsheet_group_json_urls)}``' )
    indexer.all_raw_json_data = indexer.access_worksheet_json()
    indexer.all_worksheet_data = indexer.organize_json()
    # indexer.populate_worksheet_data()

if __name__ == "__main__":
    log.debug( 'starting `if __name__...`' )
    main()
