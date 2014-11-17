Running Python files using twisted
----------------------------------

Just add `#!/usr/bin/env python` at the top of the file then to run simply:

    reactor.spawnProcess(<<ProcessProtocol Instance>>, "path/to/script.py", ["path/to/script.py", ...])

Where the `cwd` is the current directory of the current python process.
This will also work with `.sh` files that also have the `#!` at the top.


http://krondo.com/wp-content/uploads/2009/08/twisted-intro.html#post-2345
