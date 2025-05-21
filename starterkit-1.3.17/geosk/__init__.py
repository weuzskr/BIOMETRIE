import os
# __version__ = (1, 2, 0, 'alpha', 6)
__version__ = (1, 3, 17, 'final', 0)

class UnregisteredSKException(Exception):
    pass

def get_version():
    try:
        import geonode.version
        return geonode.version.get_version(__version__)
    except ImportError:
        return ".".join(map(str, __version__[:3]))  # fallback simple sans GeoNode
