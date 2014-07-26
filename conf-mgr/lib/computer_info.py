__author__ = 'Lee Symes'
__doc__ = """
This file contains utilities for this computer's information including the current MAC address, IP address and computer
 name.

"""


def is_production():
    import os
    return os.environ.get("PRODUCTION", False)


def computer_ip():
    from subprocess import check_output
    try:
        return check_output(["ifdata", "-pa", "eth0"]).rstrip()
    except:
        return "Unknown-IP"


def computer_hostname():
    from subprocess import check_output
    try:
        return check_output(["hostname"]).rstrip()
    except:
        return "Unknown-Hostname"


def computer_mac_address():
    from subprocess import check_output
    try:
        return check_output(["ifdata", "-ph", "eth0"]).rstrip()
    except:
        return "AA:BB:CC:DD:EE:FF"


def num_cores():
    from multiprocessing import cpu_count
    return cpu_count()


def load_averages():
    """
    This method calculates the load averages for the past 1, 5 and 15 minutes and returns them as a percentage of the
    total cpu usage. This means that a load of 1.5 on a 2 core cpu will actually return 0.75.
    :return:
    :rtype: tuple(int, int, int)
    """
    from subprocess import check_output

    cmd_output = check_output(["uptime"])
    load = cmd_output.split(":")[-1].strip()
    cores = num_cores()
    # Different `uptime` versions uses `, ` and ` ` to denominate. Be cross platform.
    times = [float(t.strip(", ").strip()) / cores for t in load.split(" ")]
    return times



