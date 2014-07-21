__author__ = 'lee'
__doc__ = """
This file will contain a lightweight wrapper around `twisted.python.log` to make certain kinds of logging easier and
also allow pre-definition of extra content. This is in preparation for the move to transmitting station logs to the
manager.

This will provide a class that allows:
 - Debug messages that are only output when the `PRODUCTION` environment variable is not set.
 - Simpler logging of error messages
 - The definition of logging location at creation instead of at every log call.

All of these will simply call onto `twisted.python.log` as necessary

It will also be a drop in replace for `from twisted.python import log` by providing a base log instance which can be
imported as: `from lib.logging import log` without any code being changed.
"""