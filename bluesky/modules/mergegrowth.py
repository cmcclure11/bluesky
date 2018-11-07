"""bluesky.modules.mergegrowth"""

__author__ = "Joel Dubowy"

import logging

__all__ = [
    'run'
]

__version__ = "0.1.0"


def run(fires_manager):
    """Merges each fire's growth windows to eliminate overlaps in time.

    Args:
     - fires_manager -- bluesky.models.fires.FiresManager object
    """
    logging.info("Running mergegrowth module")
    fires_manager.processed(__name__, __version__)

    for fire in fires_manager.fires:
        with fires_manager.fire_failure_handler(fire):
            _merge(fire)

def _merge(fire):
    raise NotImplementedError("The Mergegrowth module isn't yet implemented")
