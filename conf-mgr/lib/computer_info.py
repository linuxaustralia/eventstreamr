__author__ = 'Lee Symes'
__doc__ = """
Provides untility functions for accessing information about the computer.


"""


def is_production():
    """
    Returns a truthy value if this is being run in production. It checks if the C{PRODUCTION}
    environment variable is defined to be a truthy value.
    """
    import os
    return os.environ.get("PRODUCTION", False)


def computer_ip():
    """
    Returns the computer's IP address by calling C{ifdata}. Otherwise simply returning a constant
    IP address.
    """
    from subprocess import check_output
    try:
        return check_output(["ifdata", "-pa", "eth0"]).rstrip()
    except:
        return "Unknown-IP"


def computer_hostname():
    """
    Returns the computer's name as given by C{hostname}. Otherwise simply returning a constant name.
    """
    from subprocess import check_output
    try:
        return check_output(["hostname"]).rstrip()
    except:
        return "Unknown-Hostname"


def computer_mac_address():
    """
    Returns the computer's MAC address by calling C{ifdata}. Otherwise simply returning a constant
    MAC address.
    """
    from subprocess import check_output
    try:
        return check_output(["ifdata", "-ph", "eth0"]).rstrip()
    except:
        return "AA:BB:CC:DD:EE:FF"


def num_cores():
    """
    Returns the number of CPUs using L{multiprocessing.cpu_count}.
    """
    from multiprocessing import cpu_count
    return cpu_count()


def load_averages():
    """
    This method calculates the load averages for the past 1, 5 and 15 minutes and returns them
    as a percentage of the total CPU usage. This means that a load of 1.5 on a 2 core cpu
    will actually return 0.75.
    """
    from subprocess import check_output

    cmd_output = check_output(["uptime"])
    load = cmd_output.split(":")[-1].strip()
    cores = num_cores()
    # Different `uptime` versions uses `, ` and ` ` to denominate. Be cross platform.
    times = [float(t.strip(", ").strip()) / cores for t in load.split(" ")]
    return times
