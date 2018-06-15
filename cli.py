
import sys
import os
import socket
import json
import re

PORT = 11000
p_end_connection = re.compile(r'(.*?)done - got our data')

def core_loop(host):
    status = ""

    prompt = """
    
    
    
    
    
    Commands:
        cache-view       # show current live status
        alert-view       # show any alerts
        alert-watch      # show any alerts, keep updating as they come in
        exit             # to exit the cli
        
    >"""

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, PORT))
        print("connected to " + host + "\n")

        while True:

            command = raw_input(prompt)

            if command == "exit":
                s.close()
                return 0

            s.send(command.encode('ascii'))

            while True:
                status += s.recv(1024)
                if not status:  # core disconnected, not normal
                    print("disconnected ....")
                    s.close()
                    return 1
                m_end = p_end_connection.search(status)
                if m_end:       # end of message found
                    status = m_end.group(1)
                    print(status)
                    break
            raw_input("\n\n\nPress the [any] key to continue.")

    except socket.error, msg:
            print("ERROR: " + str(msg))

    return status


def usage():
    output = """
    Usage:
        cli.py [core hostname/IP]
        """
    print output


if __name__ == "__main__":
    host = ""

    """
        Read hostname from config file
        override that with something on commandline
        
    """
    if os.path.exists("ship_grip_cli.config"):
        f = open("ship_grip_cli.config", "r")
        config_data = f.read()
        f.close()
        config = json.loads(config_data)
        host = config["host"]

    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        usage()

    core_loop(host)
