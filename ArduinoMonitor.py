#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import time
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

import serial
import serial.tools.list_ports

serial_debug = False

def get_local_json_contents(json_filename):
    """
    Returns the contents of a (local) JSON file

    :param json_filename: the filename (as a string) of the local JSON file
    :returns: the data of the JSON file
    """

    try:
        with open(json_filename) as json_file:
            try:
                data = json.load(json_file)
            except ValueError:
                print('Contents of "' + json_filename + '" are not valid JSON')
                raise
    except IOError:
        print('An error occurred while reading "' + json_filename + '"')
        raise

    return data


def get_json_contents(json_url):
    """
    Return the contents of a (remote) JSON file

    :param json_url: the url (as a string) of the remote JSON file
    :returns: the data of the JSON file
    """

    data = None

    req = Request(json_url)
    try:
        response = urlopen(req).read()
    except HTTPError as e:
        print('HTTPError ' + str(e.code))
    except URLError as e:
        print('URLError ' + str(e.reason))
    else:
        try:
            data = json.loads(response.decode('utf-8'))
        except ValueError:
            print('Invalid JSON contents')
    print(data)
    return data


def find_in_data(ohw_data, name):
    """
    Search in the OpenHardwareMonitor data for a specific node, recursively

    :param ohw_data:    OpenHardwareMonitor data object
    :param name:        Name of node to search for
    :returns:           The found node, or -1 if no node was found
    """
    if ohw_data == -1:
        raise Exception('Couldn\'t find value ' + name + '!')
    if ohw_data['Text'] == name:
        # The node we are looking for is this one
        return ohw_data
    elif len(ohw_data['Children']) > 0:
        # Look at the node's children
        for child in ohw_data['Children']:
            if child['Text'] == name:
                # This child is the one we're looking for
                return child
            else:
                # Look at this children's children
                result = find_in_data(child, name)
                if result != -1:
                    # Node with specified name was found
                    return result
    # When this point is reached, nothing was found in any children
    return -1

def get_hardware_info(ohw_ip, ohw_port, cpu_name, ram_name):
    """
    Get hardware info from OpenHardwareMonitor's web server and format it
    """
    global serial_debug

    # Init arrays
    my_info = {}

    # Get data
    if serial_debug:
        # Read data from response.json file (for debugging)
        data_json = get_local_json_contents('response.json')
    else:
        # Get actual OHW data
        ohw_json_url = 'http://' + ohw_ip + ':' + ohw_port + '/data.json'
        data_json = get_json_contents(ohw_json_url)

    # Get info for CPU Load, and remove ".0 %" from the end
    cpu_data = find_in_data(data_json, cpu_name)
    cpu_load = find_in_data(cpu_data, 'CPU Total')['Value'][:-4]

    my_info['cpu_load'] = cpu_load

    # Get info for RAM, , and remove ".0 %" from the end of each value
    ram_data = find_in_data(data_json, ram_name)
    my_info['ram_load'] = find_in_data(ram_data, 'Memory')['Value'][:-4]
    my_info['ram_used'] = find_in_data(ram_data, 'Used Memory')['Value'][:-3]
    my_info['ram_availb'] = find_in_data(ram_data, 'Available Memory')['Value'][:-3]

    return my_info


def main():
    global serial_debug

    # Load config JSON
    cd = os.path.join(os.getcwd(), os.path.dirname(__file__))
    __location__ = os.path.realpath(cd)
    config = get_local_json_contents(os.path.join(__location__, 'config.json'))

    # Connect to the specified serial port
    serial_port = config['serial_port']
    if serial_port == 'TEST':
        serial_debug = True
    else:
        ser = serial.Serial(serial_port)

    while True:
        # Get current info
        my_info = get_hardware_info(
            config['ohw_ip'],
            config['ohw_port'],
            config['cpu_name'],
            config['ram_name']
        )

        # Add CPU and RAM %
        my_info['cpu_load'] = my_info['cpu_load'] + '%'
        my_info['ram_load'] = my_info['ram_load'] + '%'

        # Send the strings via serial to the Arduino
        arduino_str = \
            my_info['cpu_load'] + ';' + my_info['ram_load'] \
            + ';' + my_info['ram_used'] + ';' + my_info['ram_availb']

        if serial_debug:
            print(arduino_str)
        else:
            ser.write(arduino_str.encode())

        # Wait until refreshing Arduino again
        print(arduino_str)
        time.sleep(2.5)


if __name__ == '__main__':
    main()