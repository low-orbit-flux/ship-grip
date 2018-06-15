

import sys
import os
import socket
import time
import re
from pymongo import MongoClient
from daemon import Daemon    # from sander-daemon package
import logging
import logging.handlers
import threading
import json

host = "duck-puppy"

PORT = 22000
POLL_INTERVAL = 30   # poll every 30 seconds,  might want to set it to 5 minutes

p_end_connection = re.compile(r'(.*?)done - got our data')
live_status = {}

handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", "ship-grip-agent.log"))
handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)


def poll_agent(host, checks):
    for i in checks:
        status = ""
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
                    status = m_end.group(1)
                    break       # stop receiving data
            s.close()
        except socket.error, msg:
            logging.info("ERROR: " + str(msg))

        if status == "":
            logging.info("ERROR: no heart beat from agent")
        else:
            logging.info("==>")
            logging.info(status)
            logging.info("<==")
            jstatus = json.loads(status)
            logging.info(jstatus)
            live_status[i] = jstatus[i]

    return status


def poll_loop():
    while True:
        checks = ['disk-status', 'raid-status']
        poll_agent(host, checks)

        time.sleep(POLL_INTERVAL)


def save_alert():
    pass
    #client = MongoClient('localhost', 27017)


def cache_view():
    live_status_json = json.dumps(live_status)
    return live_status_json


def alert_view():
    pass
    return ""


def client_command_parse(command):
    command = command.rstrip()
    logging.info("["+command + "]")
    if command == "cache-view":
        output = cache_view()
    elif command == "alert-view":
        output = alert_view()
    else:
        output = "unknown command"
    return output


def client_interface_server_talk(c):
    while True:
        data = c.recv(1024)
        if data:
            logging.info("received a command " + data)
            output = client_command_parse(data)
            c.send(output + "done - got our data")
        else:
            logging.info("client disconnected")
            break


def client_interface_server():
    host = ""
    port = 11000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    logging.info("client socket bound", port)
    s.listen(25)    # queue 25 connection requests before refusing requests
    logging.info("client socket listening")

    while True:
        c, addr = s.accept()    # accept client connection
        logging.info("Client connected :" + str(addr[0]) + ':' + str(addr[1]))
        threading.Thread(target=client_interface_server_talk, args=(c,)).start()
    s.close()


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
        threading.Thread(target=poll_loop).start()
        threading.Thread(target=client_interface_server).start()



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
