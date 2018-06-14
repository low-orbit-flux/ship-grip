

import sys
import os
import socket
import time
import re
from pymongo import MongoClient
from daemon import Daemon    # from sander-daemon package
import logging
import logging.handlers


host = "duck-puppy"

PORT = 22000
POLL_INTERVAL = 30   # poll every 30 seconds,  might want to set it to 5 minutes

p_end_connection = re.compile(r'done - got our data')
live_status = {}

handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", "ship-grip-agent.log"))
handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)


def poll_agent(host, checks):
    status = ""
    for i in checks:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, PORT))
            s.send(i.encode('ascii'))
            logging.info("polling....")
            while True:
                status += s.recv(1024)
                if not status:  # agent disconnected, not normal
                    break
                m_end = p_end_connection.search(status)
                if m_end:       # end of message found
                    break       # stop receiving data
                logging.info("stuck")
            s.close()
        except socket.error, msg:
            logging.info("ERROR: " + str(msg))

        if status == "":
            logging.info("ERROR: no heart beat from agent")
        else:
            logging.info(status)
            live_status["disk and raid"] = status

    return status


def poll_loop():
    while True:
        checks = ['disk-status', 'raid-status']
        poll_agent(host, checks)

        time.sleep(POLL_INTERVAL)


def save_alert():
    pass
    #client = MongoClient('localhost', 27017)


def usage():
    output = """
    Usage:
        core start     # start as a service
        core stop      # stop running service"
        core fg        # run in the foreground
        
        
        """
    print output


class MyDaemon(Daemon):
    def run(self):
        poll_loop()


if __name__ == "__main__":

    pid = "/tmp/ship-grip-core.pid"
    md = MyDaemon(pid)

    if len(sys.argv) == 2:
        if sys.argv[1] == "start":
            md.start()
        elif sys.argv[1] == "stop":
            md.stop()
        elif sys.argv[1] == "fg":
            poll_loop()
        else:
            usage()

    else:
        usage()
