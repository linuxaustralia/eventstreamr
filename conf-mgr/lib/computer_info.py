__author__ = 'Lee Symes'

"""
This file contains utilities for this computer's information including the current MAC address, IP address and computer
 name.

"""



def computer_ip():
    from subprocess import check_output
    return "IP" # check_output(["ifdata", "-pa", "eth0"]).rstrip()


def computer_hostname():
    from subprocess import check_output
    return check_output(["hostname"]).rstrip()


def computer_mac_address():
    from subprocess import check_output
    return "MAC" # check_output(["ifdata", "-ph", "eth0"]).rstrip()