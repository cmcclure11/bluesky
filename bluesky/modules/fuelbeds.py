"""bluesky.modules.fuelbeds"""

__author__ = "Joel Dubowy"

import logging
import random
from collections import defaultdict

import fccsmap
from fccsmap.lookup import FccsLookUp
from functools import reduce

from bluesky.config import Config

__all__ = [
    'run'
]

__version__ = "0.1.0"

def run(fires_manager):
    """Runs emissions module

    Args:
     - fires_manager -- bluesky.models.fires.FiresManager object
    """
    logging.info("Running fuelbeds module")
    fires_manager.processed(__name__, __version__,
        fccsmap_version=fccsmap.__version__)

    logging.debug('Using FCCS version %s',
        Config.get('fuelbeds', 'fccs_version'))

    for fire in fires_manager.fires:
        with fires_manager.fire_failure_handler(fire):
            if not fire.get('activity'):
                raise ValueError(
                    "Activity information required to look up fuelbeds")

            for a in fire['activity']:
                if not a.get('location'):
                    raise ValueError(
                        "activity location information required to look up fuelbeds")
                # TODO: instead of instantiating a new FccsLookUp and Estimator
                #   for each activity object, create AK and non-AK lookup and
                #   estimator objects that are reused, and set reference to
                #   correct one here
                # TODO: is_alaska from lat,lng, not from 'state'
                lookup = FccsLookUp(is_alaska=a['location'].get('state')=='AK',
                    **Config.get('fuelbeds'))
                Estimator(lookup).estimate(a)

    # TODO: Add fuel loadings data to each fuelbed object (????)
    #  If we do so here, use bluesky.modules.consumption.FuelLoadingsManager
    #  (which should maybe be moved to a common module if to be used here)
    #     fm = FuelLoadingsManager()
    #     for fire in fires_manager.fires:
    #       for fb in get_fuel_loadings():
    #         fb['fuel_loadings'] = fm.get_fuel_loadings(fb['fccs_id'])
    #  Note: probably no need to do this here since we do it in the
    #  consumption module

    fires_manager.summarize(fuelbeds=summarize(fires_manager.fires))

def summarize(fires):
    if not fires:
        return []

    area_by_fccs_id = defaultdict(lambda: 0)
    total_area = 0
    for fire in fires:
        for a in fire['activity']:
            total_area += a['location']['area']
            for fb in a['fuelbeds']:
                area_by_fccs_id[fb['fccs_id']] += (fb['pct'] / 100.0) * a['location']['area']
    summary = [{"fccs_id": fccs_id, "pct": (area / total_area) * 100.0}
        for fccs_id, area in area_by_fccs_id.items()]
    return sorted(summary, key=lambda a: a["fccs_id"])

# TODO: change 'get_*' functions to 'set_*' and chnge fire in place
# rather than return values ???

# According to https://en.wikipedia.org/wiki/Acre, an acre is 4046.8564224 m^2
ACRES_PER_SQUARE_METER = 1 / 4046.8564224  # == 0.0002471053814671653

class Estimator(object):

    def __init__(self, lookup):
        self.lookup = lookup

        # Is this necessary?
        for attr, val in Config.get('fuelbeds').items():
            if attr.startswith('truncation_'):
                setattr(self, attr.replace('truncation_', ''), val)

    def estimate(self, activity_obj):
        """Estimates fuelbed composition based on lat/lng or GeoJSON data.

        If activity_obj['location']['geojson'] is defined, it will look something like
        the following:

            {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [-84.8194, 30.5222],
                            [-84.8197, 30.5209],
                            ...
                            [-84.8193, 30.5235],
                            [-84.8194, 30.5222]
                        ]
                    ]
                ]
            }
        """
        if not activity_obj.get('location'):
            raise ValueError("Insufficient data for looking up fuelbed information")

        fuelbed_info = {}
        if activity_obj['location'].get('shape_file'):
            raise NotImplementedError("Importing of shape data from file not implemented")

        elif activity_obj['location'].get('geojson'):
            fuelbed_info = self.lookup.look_up(activity_obj['location']['geojson'])
            # fuelbed_info['area'] is in m^2
            # TDOO: only use fuelbed_info['area'] if activity_obj['location']['area']
            # isn't already defined?
            if fuelbed_info and fuelbed_info.get('area'):
                activity_obj['location']['area'] = fuelbed_info['area'] * ACRES_PER_SQUARE_METER

        elif activity_obj['location'].get('latitude') and activity_obj['location'].get('longitude'):
            geo_data = {
                "type": "Point",
                "coordinates": [
                    activity_obj['location']['longitude'],
                    activity_obj['location']['latitude']
                ]
            }
            logging.debug("Converted lat,lng to geojson: %s", geo_data)
            fuelbed_info = self.lookup.look_up(geo_data)

        else:
            raise ValueError("Insufficient data for looking up fuelbed information")

        if not fuelbed_info or not fuelbed_info.get('fuelbeds'):
            # TODO: option to ignore failures ?
            raise RuntimeError("Failed to lookup fuelbed information")
        elif Config.get('fuelbeds', 'total_pct_threshold') < abs(100.0 - sum(
                [d['percent'] for d in fuelbed_info['fuelbeds'].values()])):
            raise RuntimeError("Fuelbed percentages don't add up to 100% - {fuelbeds}".format(
                fuelbeds=fuelbed_info['fuelbeds']))

        fuelbeds = [{'fccs_id':f, 'pct':d['percent']}
            for f,d in fuelbed_info['fuelbeds'].items()]

        activity_obj.update(**self._truncate(fuelbeds))

    def _truncate(self, fuelbeds):
        """Sorts fuelbeds by decreasing percentage, and

        Sort fuelbeds by decreasing percentage, use first N fuelbeds that
        reach 90% coverage or 5 count (defaults, both configurable), and
        then adjust percentages of included activity_objs so that total is 100%.
        e.g. if 3 fuelbeds, 85%, 8%, and 7%, use only the first and second,
        and then adjust percentages as follows:
          85% -> 85% * 100 / (100 - 7) = 91.4%
          8% -> 7% * 100 / (100 - 7) = 8.6%
        """
        truncated_fuelbeds = []
        total_pct = 0.0
        # iterate through fuelbeds sorted by pct (decreasing) and then by
        # fccs_id (for deterministic results in the case of equal percentages)
        for i, f in enumerate(sorted(fuelbeds, key=lambda fb: (-fb['pct'], fb['fccs_id']) )):
            truncated_fuelbeds.append(f)
            total_pct += f['pct']

            # if either treshold is None or 0, then don't truncate
            # by that that criterion
            if ((self.percentage_threshold and total_pct >= self.percentage_threshold)
                    or (self.count_threshold and i+1 >= self.count_threshold)):
                break

        # Note: we'll run adjust percentages even if nothing was truncated
        # in case percentages of initial set of fuelbeds don't add up to 100
        # (which should really never happen)

        return {
            "fuelbeds": self._adjust_percentages(truncated_fuelbeds),
            "fuelbeds_total_accounted_for_pct": total_pct
        }

    def _adjust_percentages(self, fuelbeds):
        total_pct = sum([fb['pct'] for fb in fuelbeds])

        if total_pct != 100.0:
            for fb in fuelbeds:
                # divide by total_pct before multiplying by 100 to avoid
                # rounding errors
                fb['pct'] = (fb['pct'] / total_pct) * 100.0
        # else, no adjustment necessary

        # return for convenience
        return fuelbeds
