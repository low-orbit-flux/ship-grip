

import sys
import socket
import time
import re

# grab hosts to manage from mongo
# select host
    # poll for status
# discover disks to monitor

PORT = 22000
POLL_INTERVAL = 30   # poll every 30 seconds,  might want to set it to 5 minutes

p_end_connection = re.compile(r'done - got our data')


def poll_agent(host, checks):
    status = ""
    for i in checks:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, PORT))
        s.send(i.encode('ascii'))
        while True:
            status += s.recv(1024)
            if not status:  # agent disconnected, not normal
                break
            m_end = p_end_connection.search(status)
            if m_end:       # end of message found
                break       # stop receiving data
        s.close()
    return status


def poll_loop(host):
    while True:
        checks = ['disk-status', 'raid-status']
        status = poll_agent(host, checks)
        print(status)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":

    if len(sys.argv) == 2:
        host = sys.argv[1]
        poll_loop(host)
    else:
        print("wrong args ...")
