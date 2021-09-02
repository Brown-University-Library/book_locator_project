"""
Checks gspread google-sheet access.
Usage:
- cd into project directory
- $ source ../env3_bklctr/bin/activate
- $ python3 ./book_locator_app/lib/gspread_access_tester.py
"""

import json, logging, os, sys

import gspread
from oauth2client.service_account import ServiceAccountCredentials  # py3

## add project path to simplify other imports
assert sys.version_info.major >= 3  # python3 check
sys.path.append( os.environ['BK_LCTR__PROJECT_PATH'] )

from book_locator_app import settings_app


## setup logging
logging.basicConfig(
    filename=settings_app.INDEXER_LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S'
    )
# logging.getLogger("oauth2client").setLevel(logging.WARNING)
log = logging.getLogger( 'book_locator_indexer' )
log.info( '\n\nstarting gspread_access_tester.py' )


def setup_spreadsheet_connection():
    """
    This works, returning a gspread client -- which is part of my confusion.
    When things things around the middle of August, I assumed it was because some authentication mechanism had changed.
    """
    try:
        with open( settings_app.GSHEET_KEY_PATH ) as f:
            json_key_str = f.read()
            # log.debug( f'json_key_str, ```{json_key_str}```; type(json_key_str), `{type(json_key_str)}`' )
        json_key = json.loads( json_key_str )
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name( settings_app.GSHEET_KEY_PATH, scope )
        gc = gspread.authorize(credentials)
        assert type(gc) == gspread.client.Client
        return gc
    except:
        err = 'problem connecting to spreadsheet'
        log.exception( err )
        raise Exception( err )


def process_worksheet( gc ):
    """
    This fails on accessing the spreadsheet.
    [Also note that below (commented out), I tried the open_by_url() method.]
    The failure is a gspread "RequestError", with a 404 status code and a server response of:
      "Sorry, unable to open the file at this time. Please check the address and try again."
    (I've confirmed that the key is correct; the spreadsheet is accessible via a browser.)
    """
    try:
        assert type(gc) == gspread.client.Client
        KEY = os.environ['BK_LCTR__GSPREAD_CHECKER_KEY']
        assert type(KEY) == str, type(KEY)
        spread = gc.open_by_key( KEY )
        # sheets = spread.worksheets()
        # for worksheet in sheets:
        #     log.info( f'worksheet-title, ``{worksheet.title}``' )
    except:
        err = 'problem processing worksheets'
        log.exception( err )
        raise Exception( err )

# def process_worksheet( gc ):
#     try:
#         assert type(gc) == gspread.client.Client
#         URL = os.environ['BK_LCTR__GSPREAD_CHECKER_URL']
#         assert type(URL) == str, type(URL)
#         spread = gc.open_by_url( URL )
#         # sheets = spread.worksheets()
#         # for worksheet in sheets:
#         #     log.info( f'worksheet-title, ``{worksheet.title}``' )
#     except:
#         err = 'problem processing worksheets'
#         log.exception( err )
#         raise Exception( err )


def main():
    log.debug( 'starting main()' )
    gc = setup_spreadsheet_connection()
    assert type(gc) == gspread.client.Client
    process_worksheet( gc )
    return


if __name__ == "__main__":
    main()
