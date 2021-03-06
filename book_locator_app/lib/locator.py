# -*- coding: utf-8 -*-

"""
- Loads datafile (produced via cronjob that accesses a googledoc-sheet),
- Gets a normalized callnumber.
- Looks up the normalized callnumber in the loaded data.
- Returns location info.
"""

import bisect, json, logging, os, pprint

from book_locator_app import settings_app
from book_locator_app.lib.normalizer import Item  # TODO: call the normalizer webservice


log = logging.getLogger(__name__)


class ServiceLocator():
    """
    Class for use in web app or script calling locator
    repeatedly.
    """

    def __init__(self):
        self.locations = ['sci', 'rock', 'rock-chinese', 'rock-korean', 'rock-japanese']
        for loc in self.locations:
            try:
                setattr(
                    self,
                    "{}_index".format(loc),
                    LocateData(loc, index=True).load()
                )
                setattr(
                    self,
                    "{}_meta".format(loc),
                    LocateData(loc, meta=True).load()
                 )
            except IOError:
                log.exception( f'Could not load meta or index for ```{loc}```.' )
                # log.error("Could not load meta or index for {}.".format(loc))

    def _data(self, normalized, location):
        log.debug( f'normalized param, `{normalized}`; location param, `{location}`' )
        index = getattr(self, "{}_index".format(location))
        log.debug( f'index, `{index}`' )
        meta = getattr(self, "{}_meta".format(location))
        log.debug( f'meta, `{meta}`' )
        position = bisect.bisect(index, normalized)
        log.debug( f'position, `{position}`' )
        meta_key = index[position - 1]
        log.debug( f'meta_key, `{meta_key}`' )
        loc_data = meta.get(meta_key)
        log.debug( f'loc_data returned, ```{loc_data}```' )
        return loc_data

    def run(self, callnumber, location):
        """ Prepares location information.
            Called by views.map() """
        if location not in self.locations:
            log.debug("Location not in possbile locations.")
        # lower case location
        location = location.strip().lower()
        # upcase call numbers
        callnumber = callnumber.strip().upper()
        try:
            # normalized_callnumber = brown.normalize(callnumber, location).upper()
            item = Item( callnumber, location )
            normalized_callnumber = item.normalize().upper()
        except AttributeError:
            log.info("Could not normalize callnumber {}.".format(callnumber))
            return None
        loc_data = self._data(normalized_callnumber, location)
        located = False
        if loc_data is not None:
            located = True
        aisle = loc_data.get('aisle').upper()
        location_dct = {
            'floor': str(loc_data.get('floor')).upper(),
            'aisle': aisle,
            # For display we will split out aisle and side.
            'display_aisle': "".join(aisle[:-1]),
            # Side is included in aisle as last character.
            'side': aisle[-1].upper(),
            'location': location,
            #Flag as to whether this item was found.
            'located': located,
            }
        log.debug( f'location_dct, ```{pprint.pformat(location_dct)}```' )
        return location_dct

        ## end def run()

    ## end class ServiceLocator


class LocateData(object):

    def __init__(self, location, index=False, meta=False):
        log.debug( f'location, `{location}`; index, `{index}`; meta, `{meta}`' )
        if (index is False) and (meta is False):
            raise Exception("Either index or meta must be true")
        self.location = location
        if index is True:
            self.prefix = 'index'
        else:
            self.prefix = 'meta'

    def _data_filename(self, prefix):
        fn = "{}_{}.json".format(self.location, self.prefix)
        log.debug( f'filename, ```{fn}```' )
        filepath = os.path.join(settings_app.DATA_DIR, fn)
        log.debug( f'filepath, ```{filepath}```' )
        return filepath

    # def dump(self, data):
    #     fn = self._data_filename(self.location)
    #     with open(fn, 'wb') as pfile:
    #         json.dump(data, pfile)
    #     return True

    def dump(self, data):
        fn = self._data_filename(self.location)
        with open( fn, 'w' ) as pfile:
            json.dump( data, pfile, indent=2 )
        return True

    def load(self):
        fn = self._data_filename(self.location)
        with open(fn) as pfile:
            data = json.load(pfile)
        return data
