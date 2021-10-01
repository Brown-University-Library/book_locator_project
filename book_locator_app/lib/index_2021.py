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
        log.debug( 'starting Indexer.__init__()' )
        self.raw_groups = self.prepare_groups()
        self.spreadsheet_group_json_urls = self.prepare_spreadsheet_urls( self.raw_groups )
        # self.rock_general_floor_a_data = {}
        # self.rock_general_floor_b_data = {}
        # self.rock_general_floor_2_data = {}
        # self.rock_general_floor_3_data = {}
        # self.rock_general_floor_4_data = {}
        # self.sci_floor_11_data = {}
        # self.sci_floor_12_data = {}
        # self.sci_floor_13_data = {}
        # self.chinese_data = {}
        # self.japanese_data = {}
        # self.korean_data = {}

    ## run on __init__() ------------------------

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
                'location_code': 'rock_chinese',
                'spreadsheet_id': settings_app.ROCK_CJK_SPREADSHEET_ID,
                'worksheet_info': [
                    {'id': settings_app.CHINESE_WORKSHEET_ID, 'label': 'rock_chinese' },
                ]
            },
            {
                'location_code': 'rock_japanese',
                'spreadsheet_id': settings_app.ROCK_CJK_SPREADSHEET_ID,
                'worksheet_info': [
                    {'id': settings_app.JAPANESE_WORKSHEET_ID, 'label': 'rock_japanese' },
                ]
            },
            {
                'location_code': 'rock_korean',
                'spreadsheet_id': settings_app.ROCK_CJK_SPREADSHEET_ID,
                'worksheet_info': [
                    {'id': settings_app.KOREAN_WORKSHEET_ID, 'label': 'rock_korean' },
                ]
            },
        ]
        return raw_groups

    def prepare_spreadsheet_urls( self, raw_groups ):
        """ Populates Indexer.spreadsheet_urls on instantiation.
            Creates a list of spreadsheet-url info, with each element of the list having the structure...
            {
                'group_json_urls': [
                    {'worksheet_label': 'rock_general_floor_a', 'worksheet_url': 'https://worksheet-url'},
                    {'worksheet_label': 'rock_general_floor_b', 'worksheet_url': 'https://worksheet-url'},
                    {'worksheet_label': 'rock_general_floor_2',  'worksheet_url': 'https://worksheet-url'},
                    etc.
                    ],
                'location_code': 'rock'
            },
            Called by __init__() """
        log.debug( 'starting prepare_spreadsheet_urls()' )
        assert type( raw_groups ) == list
        log.debug( f'raw_groups, ``{pprint.pformat(raw_groups)}``' )
        spreadsheet_group_json_urls = []
        for group in raw_groups:
            assert type(group) == dict
            worksheet_info_lst = []
            spreadsheet_id = group['spreadsheet_id']
            for worksheet_data_dct in group['worksheet_info']:
                worksheet_id = worksheet_data_dct['id']
                worksheet_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:json&gid={worksheet_id}'
                worksheet_info_dct = { 'worksheet_url': worksheet_url, 'worksheet_label': worksheet_data_dct['label'] }
                worksheet_info_lst.append( worksheet_info_dct )
            dct = {
                'location_code': group['location_code'],
                'group_json_urls': worksheet_info_lst
            }
            spreadsheet_group_json_urls.append( dct )
        return spreadsheet_group_json_urls

    ## managers ---------------------------------

    def process_worksheet_urls( self ):
        """ Loops through worksheet urls.
            Called by main() """
        log.debug( 'starting process_worksheet_urls()' )
        assert type( self.spreadsheet_group_json_urls ) == list
        log.debug( f'self.spreadsheet_group_json_urls, ``{pprint.pformat(self.spreadsheet_group_json_urls)}``' )
        for spreadsheet_info in self.spreadsheet_group_json_urls:
            assert type( spreadsheet_info ) == dict
            for worksheet_info in spreadsheet_info['group_json_urls']:
                assert type( worksheet_info ) == dict
                log.debug( f'worksheet_info, ``{worksheet_info}``' )
                ( label, url ) = ( worksheet_info['worksheet_label'], worksheet_info['worksheet_url'] )
                self.process_worksheet_url( url, label )
        return

    def process_worksheet_url( self, url, label ):
        """ Manages processing of single worksheet.
            Called by process_worksheet_urls() """
        log.debug( 'starting process_worksheet_url()' )
        log.debug( f'label, ``{label}``; url, ``{url}``' )
        assert type( label ) == str
        assert type( url ) == str
        raw_data_dct = self.query_spreadsheet( url, label )
        row_list = self.create_row_data( raw_data_dct, label )
        self.continue_regularly_scheduled_programming( row_list, label )  # hand off to previous code
        # 1/0
        return

    ## meat -------------------------------------

    def query_spreadsheet( self, worksheet_url, label ):
        """ Queries spreadsheet.
            Called by access_worksheet_json() """
        ( jsn_dct, err ) = ( None, None )
        try:
            log.debug( f'querying worksheet, ``{label}``' )
            assert type( worksheet_url ) == str
            assert type( label ) == str
            r = requests.get( worksheet_url )
            content = r.content.decode( 'utf-8' )
            start_string = 'Query.setResponse('
            start_position = content.find( start_string ) + len( start_string )
            end_position = len( ');' )
            jsn_str = content[start_position: -end_position]
            jsn_dct = json.loads( jsn_str )
            # log.debug( f'jsn_dct, ``{pprint.pformat( jsn_dct )}``' )
            assert type( jsn_dct ) == dict
            return jsn_dct
        except:

    def create_row_data( self, raw_data_dct, label ):
        """ Converts self.all_raw_json_data list-data into row-data for each spreadsheet.
            Called by main() """
        log.debug( 'starting create_row_data()' )
        log.debug( f'creating row-data from raw-data from worksheet, ``{label}``' )
        log.debug( f'TEMP- raw_data_dct, ``{pprint.pformat(raw_data_dct)}``' )
        assert type( raw_data_dct ) == dict
        assert type( label ) == str
        log.debug( f'raw_data_dct.keys(), ``{pprint.pformat(raw_data_dct.keys())}``' )
        log.debug( f'raw_data_dct["table"], ``{raw_data_dct["table"]}``' )
        table = raw_data_dct['table']
        assert type( table ) == dict
        log.debug( f'table-keys, ``{pprint.pformat(table.keys())}``' )
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
                    row_dct['aisle'] = cell['v'].strip()
                elif i == 1:
                    row_dct['begin'] = cell['v'].strip()
                elif i == 2:
                    row_dct['end'] = cell['v'].strip()         # /floor/location_code
                elif i == 3:
                    try:
                        row_dct['floor'] = cell['f'].strip()
                    except:
                        row_dct['floor'] = cell['v'].strip()
                elif i == 4:
                    row_dct['location_code'] = cell['v'].strip()
                elif i > 4:
                    break
            row_list.append( row_dct )
        log.debug( f'row_list data for worksheet ``{label}``: ``{pprint.pformat(row_list)}``' )
        assert type( row_list ) == list
        return row_list
        ## end def create_row_data()

    def continue_regularly_scheduled_programming( self, row_list, label ):
        """ temporary place-holder
            Called by process_worksheet_url() """
        log.debug( 'starting temporary continue_regularly_scheduled_programming()' )
        log.debug( f'would be handling processing of worksheet, ``{label}``' )
        pass
        return

    # def organize_json( self ):
    #     """ Converts self.all_raw_json_data list-data into row-data for each spreadsheet.
    #         Called by main() """
    #     log.debug( 'starting organize_json()' )
    #     # log.debug( f'self.all_raw_json_data, ``{pprint.pformat(self.all_raw_json_data)}``' )
    #     # 1/0
    #     assert type( self.all_raw_json_data ) == list
    #     for worksheet in self.all_raw_json_data:
    #         assert type( worksheet ) == dict
    #         log.debug( f'processing worksheet, ``{pprint.pformat(worksheet)}...``' )
    #         log.debug( f'worksheet.keys(), ``{pprint.pformat(worksheet.keys())}``' )
    #         log.debug( f'worksheet["table"], ``{worksheet["table"]}``' )
    #         # 1/0
    #         table = worksheet['table']
    #         assert type( table ) == dict
    #         log.debug( f'table-keys, ``{pprint.pformat(table.keys())}``' )
    #         # 1/0
    #         second_row_table_identifier = table['rows'][2]
    #         log.debug( f'processing table containing, ``{second_row_table_identifier}``' )
    #         row_list = []
    #         for row in table['rows']:
    #             cells = row['c']
    #             first_cell_data = cells[0]['v']
    #             log.debug( f'first_cell_data, ``{first_cell_data}``' )
    #             if first_cell_data == 'aisle':
    #                 continue
    #             row_dct = {
    #                 'aisle': '', 'begin': '', 'end': '', 'floor': '', 'location_code': '' }
    #             for ( i, cell ) in enumerate( cells ):
    #                 if i == 0:
    #                     row_dct['aisle'] = cell['v']
    #                 elif i == 1:
    #                     row_dct['begin'] = cell['v']
    #                 elif i == 2:
    #                     row_dct['end'] = cell['v']         # /floor/location_code
    #                 elif i == 3:
    #                     try:
    #                         row_dct['floor'] = cell['f']
    #                     except:
    #                         row_dct['floor'] = cell['v']
    #                 elif i == 4:
    #                     row_dct['location_code'] = cell['v']
    #                 elif i > 4:
    #                     break
    #             row_list.append( row_dct )
    #         last_entry = row_list[-1]
    #         if last_entry['location_code'].strip() == 'rock':
    #             if last_entry['floor'].strip() == 'A':
    #                 self.rock_general_floor_a_data = row_list
    #             elif last_entry['floor'].strip() == 'B':
    #                 self.rock_general_floor_b_data = row_list
    #             elif last_entry['floor'].strip() == '2':
    #                 self.rock_general_floor_2_data = row_list
    #             elif last_entry['floor'].strip() == '3':
    #                 self.rock_general_floor_3_data = row_list
    #             elif last_entry['floor'].strip() == '4':
    #                 self.rock_general_floor_4_data = row_list
    #         elif last_entry['location_code'].strip() == 'sci':
    #             if last_entry['floor'].strip() == '11':
    #                 self.sci_general_floor_11_data = row_list
    #             elif last_entry['floor'].strip() == '12':
    #                 self.sci_general_floor_12_data = row_list
    #             elif last_entry['floor'].strip() == '13':
    #                 self.sci_general_floor_13_data = row_list
    #         elif last_entry['location_code'].strip() == 'rock chinese':
    #             self.chinese_data = row_list
    #         elif last_entry['location_code'].strip() == 'rock japanese':
    #             self.japanese_data = row_list
    #         elif last_entry['location_code'].strip() == 'rock korean':
    #             self.korean_data = row_list
    #     log.debug( f'self.rock_general_floor_a_data, ``{pprint.pformat(self.rock_general_floor_a_data)}``' )
    #     ## end def organize_json()

    # def access_worksheet_json( self ):
    #     """ Manages spreadsheet queries to gather raw json-data.
    #         Called by main() """
    #     log.debug( 'starting access_worksheet_json()' )
    #     raw_json_data = []
    #     for entry in self.spreadsheet_group_json_urls:
    #         log.debug( f'entry, ``{pprint.pformat(entry)}``' )
    #         assert type(entry) == dict
    #         log.debug( f'processing worksheet urls for `location_code`, ``{entry["location_code"]}``' )
    #         worksheet_urls = entry['group_json_urls']
    #         for worksheet_url in worksheet_urls:
    #             assert type(worksheet_url) == str
    #             jsn_dct = self.query_spreadsheet( worksheet_url )
    #             jsn_dct['queried_url'] = worksheet_url
    #             raw_json_data.append( jsn_dct )
    #         break
    #     # log.debug( f'raw_json_data, ``{raw_json_data}``' )
    #     assert type( raw_json_data ) == list
    #     return raw_json_data

    ## end class Indexer()


## runner ---------------------------------------

def main():
    log.debug( 'starting `def main()`' )
    indexer = Indexer()
    indexer.process_worksheet_urls()

if __name__ == "__main__":
    log.debug( 'starting `if __name__...`' )
    main()
