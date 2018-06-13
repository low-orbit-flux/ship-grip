
import sys
import os
import subprocess
import re
import socket
import threading
from daemon import Daemon    # from sander-daemon package
import logging
import logging.handlers


disks = ['sda', 'sdb', 'sdc', 'sdd', 'sde']
p_errors = re.compile(r'No Errors Logged')


handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", "ship-grip-agent.log"))
handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)


def disk_status():
    logging.info('\n' * 5 + 20 * '=' + '| Disk Status |' + 20 * '=')
    status = '\n' * 5 + 20 * '=' + '| Disk Status |' + 20 * '=' + '\n'
    for i in disks:
        output = ""
        try:
            output = subprocess.check_output('smartctl -a /dev/' + i, stderr=subprocess.STDOUT, shell=True)
        except:
            pass
        m_errors = None
        m_errors = p_errors.search(output)
        if m_errors:
            logging.info(i + ": OK")
            status += i + ": OK\n"
        else:
            logging.info(i + ": ERROR")
            status += i + ": ERROR\n"

    return status


def raid_status():
    logging.info('\n' * 3 + 20 * '=' + '| Array Status |' + 20 * '=')
    status = '\n' * 3 + 20 * '=' + '| Array Status |' + 20 * '=' + '\n'
    RAID_arrays = ['md0']
    p_array_status = re.compile(r'State : (.*)')
    for i in RAID_arrays:
        output = ""
        try:
            output = subprocess.check_output('mdadm --detail /dev/' + i, stderr=subprocess.STDOUT, shell=True)
        except:
            pass
        m_array_status = None
        m_array_status = p_array_status.search(output)
        if m_array_status:
            logging.info(m_array_status.group())
            status += m_array_status.group() + "\n"
        else:
            logging.info("ERROR - Something went wrong... Can't parse mdadm output.  Check it manually.")
            status += "Something went wrong... Can't parse mdadm output.  Check it manually.\n"

    return status


def command_parse(command):
    command = command.rstrip()
    logging.info("["+command + "]")
    if command == "disk-status":
        output = disk_status()
    elif command == "raid-status":
        output = raid_status()
    else:
        output = "unknown command"
    return output


def server_talk(c):
    while True:
        data = c.recv(1024)
        if data:
            logging.info("received a command " + data)
            output = command_parse(data)
            c.send(output + "done - got our data")
        else:
            logging.info("client disconnected")
            break


def server():
    host = ""
    port = 22000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    logging.info("socket bound", port)
    s.listen(25)    # queue 25 connection requests before refusing requests
    logging.info("socket listening")

    while True:
        c, addr = s.accept()    # accept client connection
        logging.info("Client connected :" + str(addr[0]) + ':' + str(addr[1]))
        #server_talk(c)
        threading.Thread(target=server_talk, args=(c,)).start()
    s.close()


def usage():
    output = """
    Usage:
        agent start     # start as a service
        agent stop      # stop running service"
        agent fg        # run in the foreground


        """
    print output


class MyDaemon(Daemon):
    """
    Extend the Daemon class so we can override the run method and launch our own server function
    """
    def run(self):
        server()


if __name__ == "__main__":

    pid = "/tmp/ship-grip-agent.pid"
    md = MyDaemon(pid)

    if len(sys.argv) == 2:
        if sys.argv[1] == "start":
            md.start()
        elif sys.argv[1] == "stop":
            md.stop()
        elif sys.argv[1] == "fg":
            server()
        else:
            usage()

    else:
        usage()

