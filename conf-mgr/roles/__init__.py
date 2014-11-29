"""

This file defines the storage for the roles.


"""
import pkgutil as _pkgutil
from lib.logging import getLogger


_log = getLogger(["roles", "__init__"])

_loaded_roles = []
def _check_load():
    if _loaded_roles:
        return
    _loaded_roles.append("Loaded Roles") # Prevent recursive call.
    loaded = []
    for importer, module_name, is_pkg in _pkgutil.iter_modules(__path__):
        if not is_pkg and importer is not None:
            _log.msg("Loading `%s` module ..." % module_name)
            __import__("%s.%s" % (__name__, module_name))
            _log.msg("Loaded `%s` module." % module_name)
            loaded.append(module_name)

    _log.msg("Loaded the following modules: %r" % loaded)
