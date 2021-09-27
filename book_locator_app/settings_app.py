# -*- coding: utf-8 -*-

import json, logging, os


log = logging.getLogger(__name__)


##################################################
## webapp
##################################################

README_URL = os.environ['BK_LCTR__README_URL']

INFO_URL = os.environ['BK_LCTR__README_URL']

LOCATE_LOCATIONS = ['rock', 'sci']

DATA_DIR = os.environ['BK_LCTR__DATA_DIR_PATH']  # data saved from google-sheet
log.debug( f'DATA_DIR, ```{DATA_DIR}``' )


##################################################
## indexer
##################################################

GSHEET_KEY_PATH = os.environ['BK_LCTR__GSHEET_KEY_PATH']

## misleading var names; these are really the spreadsheet keys; a 'gid' represents an individual worksheet of the spreadsheet
ROCK_GID = os.environ['BK_LCTR__ROCK_GID']
SCI_GID = os.environ['BK_LCTR__SCI_GID']
ROCK_CHINESE_GID = os.environ['BK_LCTR__ROCK_CHINESE_GID']
ROCK_JAPANESE_GID = os.environ['BK_LCTR__ROCK_JAPANESE_GID']
ROCK_KOREAN_GID = os.environ['BK_LCTR__ROCK_KOREAN_GID']

## new-2021 g-sheet IDs...
ROCK_GENERAL_SPREADSHEET_ID = os.environ['BK_LCTR__ROCK_SPREADSHEET_ID']
SCI_SPREADSHEET_ID = os.environ['BK_LCTR__SCI_SPREADSHEET_ID']
ROCK_CJK_SPREADSHEET_ID = os.environ['BK_LCTR__CJK_SPREADSHEET_ID']
#---
ROCK_GENERAL_FLOOR_A_WORKSHEET_ID = os.environ['BK_LCTR__ROCK_GENERAL_FLOOR_A_WORKSHEET_ID']
ROCK_GENERAL_FLOOR_B_WORKSHEET_ID = os.environ['BK_LCTR__ROCK_GENERAL_FLOOR_B_WORKSHEET_ID']
ROCK_GENERAL_FLOOR_2_WORKSHEET_ID = os.environ['BK_LCTR__ROCK_GENERAL_FLOOR_2_WORKSHEET_ID']
ROCK_GENERAL_FLOOR_3_WORKSHEET_ID = os.environ['BK_LCTR__ROCK_GENERAL_FLOOR_3_WORKSHEET_ID']
ROCK_GENERAL_FLOOR_4_WORKSHEET_ID = os.environ['BK_LCTR__ROCK_GENERAL_FLOOR_4_WORKSHEET_ID']
#---
SCI_FLOOR_11_WORKSHEET_ID = os.environ['BK_LCTR__SCI_FLOOR_11_WORKSHEET_ID']
SCI_FLOOR_12_WORKSHEET_ID = os.environ['BK_LCTR__SCI_FLOOR_12_WORKSHEET_ID']
SCI_FLOOR_13_WORKSHEET_ID = os.environ['BK_LCTR__SCI_FLOOR_13_WORKSHEET_ID']
#---
CHINESE_WORKSHEET_ID = os.environ['BK_LCTR__CHINESE_WORKSHEET_ID']
JAPANESE_WORKSHEET_ID = os.environ['BK_LCTR__JAPANESE_WORKSHEET_ID']
KOREAN_WORKSHEET_ID = os.environ['BK_LCTR__KOREAN_WORKSHEET_ID']

#---
#---

META_FILEPATH = os.environ['BK_LCTR__META_PICKLE_FILEPATH']

INDEXER_LOG_PATH = os.environ['BK_LCTR__INDEXER_LOG_PATH']


##################################################
## auth
##################################################

# SUPER_USERS = json.loads( os.environ['BK_LCTR__UPER_USERS_JSON'] )
# STAFF_USERS = json.loads( os.environ['BK_LCTR__STAFF_USERS_JSON'] )  # users permitted access to admin
# STAFF_GROUP = os.environ['BK_LCTR__STAFF_GROUP']  # not grouper-group; rather, name of django-admin group for permissions
# TEST_META_DCT = json.loads( os.environ['BK_LCTR__TEST_META_DCT_JSON'] )
# POST_LOGIN_ADMIN_REVERSE_URL = os.environ['BK_LCTR__POST_LOGIN_ADMIN_REVERSE_URL']  # tricky; for a direct-view of a model, the string would be in the form of: `admin:APP-NAME_MODEL-NAME_changelist`
