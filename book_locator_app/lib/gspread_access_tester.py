"""
Checks gspread google-sheet access.
Usage:
- cd into project directory
- $ source ../env3_bklctr/bin/activate
- $ python3 ./book_locator_app/lib/gspread_access_tester.py
"""

import logging, os, sys

import gspread
from oauth2client.service_account import ServiceAccountCredentials  # py3

## add project path to simplify other imports
assert sys.version_info.major >= 3  # python3 check
sys.path.append( os.environ['BK_LCTR__PROJECT_PATH'] )

from book_locator_app import settings_app


## setup logging
def setup_logging():
    err = None
    try:
        logging.basicConfig(
            filename=settings_app.INDEXER_LOG_PATH,
            level=logging.DEBUG,
            format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
            datefmt='%d/%b/%Y %H:%M:%S'
            )
        # logging.getLogger("oauth2client").setLevel(logging.WARNING)
        log = logging.getLogger( 'book_locator_indexer' )
        log.info( '\nstarting gspread_access_tester.py' )
    except:
        err = hereZZ
        log.exception(  )


META_FILE = settings_app.META_FILEPATH


#
# Setup Google Spreadsheet connection.
#
with open( settings_app.GSHEET_KEY_PATH ) as f:
    json_key_str = f.read()
# log.debug( f'json_key_str, ```{json_key_str}```; type(json_key_str), `{type(json_key_str)}`' )
json_key = json.loads( json_key_str )

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name( settings_app.GSHEET_KEY_PATH, scope )
gc = gspread.authorize(credentials)
log.debug( f'type(gc), ```{type(gc)}```' )
log.debug( f'gc, ```{gc}```' )


# List of gsheets and location codes that we will index.  These
# are the "locatable" locations.
groups = [
    {
        'location_code': 'rock',
        'gid': settings_app.ROCK_GID
    },
    {
        'location_code': 'sci',
        'gid': settings_app.SCI_GID
    },
    {
        'location_code': 'rock-chinese',
        'gid': settings_app.ROCK_CHINESE_GID,
        'worksheet': 'chinese'
    },
    {
        'location_code': 'rock-japanese',
        'gid': settings_app.ROCK_JAPANESE_GID,
        'worksheet': 'japanese'
    },
    {
        'location_code': 'rock-korean',
        'gid': settings_app.ROCK_KOREAN_GID,
        'worksheet': 'korean'
    },
]


def gget(d, k):
    """
    Function to get a cell from the gspread
    and return None rather than an empty string.

    :param d:
    :param k:
    :return:
    """
    val = d.get(k, None)
    if val is None:
        return_val = None
    elif val.strip() == '':
        return_val = None
    else:
        return_val = val
    log.debug( f'return_val, `{return_val}`' )
    return return_val


def build_item(location, begin):
    item = Item(begin, location)
    n = None
    try:
        n = item.normalize()
        log.debug
    except ValueError:
        # print>>sys.stderr, "Can't normalize", location, begin
        # return None
        log.exception( f"Can't normalize 'location', `{location}`, 'begin', `{begin}`" )
    log_message = f'from "location", `{location}` and "begin", `{begin}`; returning normalized_item, `{n}`'
    if n is None:
        log.warning( log_message )
    else:
        log.debug( log_message )
    return n


def make_last_updated_date(raw):
    """
    Turn the Gspread updated date into a python datetime.
    """
    chunked = raw.split('T')
    yr, month, dy = chunked[0].split('-')
    hour, minute, _  = chunked[1].split(':')
    formatted_time = "{}-{}-{} {}:{}".format(yr, month, dy, hour, minute)
    upd = strptime(formatted_time, '%Y-%m-%d %H:%M')
    #Convert to datetime object
    dt = datetime.fromtimestamp(mktime(upd))
    return dt


def load_meta():
    try:
        with open( META_FILE, 'rb' ) as inf:
            info = pickle.load( inf, encoding='bytes' )
            log.debug( f'type(info), `{type(info)}`; info, ```{info}```' )
            return info
    except ( IOError, ValueError ) as e:
        log.exception()
        return None


def get_index_last_updated():
    meta = load_meta()
    if meta is not None:
        return meta.get('updated')


def set_index_last_updated(timestamp=datetime.utcnow()):
    meta = load_meta() or {}
    meta['updated'] = timestamp
    with open(META_FILE, 'wb') as outf:
        pickle.dump(meta, outf)


def check_last_update(worksheet):
    if FORCE_REINDEX is not True:
        spread_updated = make_last_updated_date(worksheet.updated)
        index_updated = get_index_last_updated()
        if (index_updated) and (spread_updated < index_updated):
            log.info(
                "Skipping reindex because spreadsheet updated: {} and last index: {}"\
                .format(spread_updated, index_updated)
            )
            return False
    return True


def index_group(location_code, gid, worksheet):
    log.info( f'location code, ```{location_code}```; gid, ```{gid}```' )
    try:
        spread = gc.open_by_key( gid )
        # log.debug( f'type(spread), `{type(spread)}`' )
        log.debug( f'spread, `{spread}`' )  # will show name and gid
    except Exception as e:
        # logging.error("Error in {}\nMessage: {}".format(gid, e.message))
        log.exception( 'problem accessing spreadsheet' )
        raise e


    # If no worksheet is passed in, get all worksheets in spread.
    log.debug( 'about to get `sheets`' )
    if worksheet is None:
        sheets = spread.worksheets()
    else:
        sheets = [spread.worksheet(worksheet)]

    locate_index = {}
    range_start_list = []

    has_changed = False

    # Go through each sheet and see if it has changed.
    # If any sheet in the set has changed, reindex.
    for worksheet in sheets:
        should_index = check_last_update(worksheet)
        if should_index is True:
            has_changed = True

    if has_changed is False:
        log.info("Skipping location code {}. No data changed.".format(location_code))
        return

    # Actually index the sheet.
    for worksheet in sheets:
        log.info("Indexing worksheet {}".format(worksheet.title))
        for rec in worksheet.get_all_records():
            aisle_meta = rec.copy()
            begin = gget(rec, 'begin')
            if begin is None:
                logging.warning("No begin range")
                continue
            normalized_range_start = build_item(location_code, begin)
            range_start_list.append(normalized_range_start)
            aisle_meta['normalized_start'] = normalized_range_start
            locate_index[normalized_range_start] = aisle_meta

    # Dump the metadata to the file system.
    ld = LocateData(location_code, meta=True)
    ld.dump(locate_index)
    log.debug( 'metadata saved' )

    # Dump the index, which is a sorted listed of normalized call numbers.
    # log.debug( f'type(range_start_list), `{type(range_start_list)}`; range_start_list, ```{pprint.pformat(range_start_list)}```' )
    # range_start_list.sort()  # was generating error because of None elements among the strings
    filtered_range_start_list = [ x for x in range_start_list if x ] # removes None elements before sorting
    filtered_range_start_list.sort()
    ld = LocateData(location_code, index=True)
    ld.dump(filtered_range_start_list)
    log.debug( 'index saved' )


def main():
    for grp in groups:
        log.debug( f'grp, ```{pprint.pformat(grp)}```' )
        index_group(grp['location_code'], grp['gid'], grp.get('worksheet'))
        # break
    set_index_last_updated()
    log.debug( 'indexing complete' )


if __name__ == "__main__":
    main()
