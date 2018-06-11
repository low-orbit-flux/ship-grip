
import subprocess
import re
import socket
#from _thread import *
import threading

disks = ['sda', 'sdb', 'sdc', 'sdd', 'sde']
p_errors = re.compile(r'No Errors Logged')


def disk_status():
    print('\n' * 5 + 20 * '=' + '| Disk Status |' + 20 * '=')
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
            print(i + ": OK")
            status += i + ": OK\n"
        else:
            print(i + ": ERROR")
            status += i + ": ERROR\n"
    #    print(m_errors.group())
    return status


def raid_status():
    print('\n' * 3 + 20 * '=' + '| Array Status |' + 20 * '=')
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
            print(m_array_status.group())
            status += m_array_status.group() + "\n"
        else:
            print("Something went wrong... Can't parse mdadm output.  Check it manually.")
            status += "Something went wrong... Can't parse mdadm output.  Check it manually.\n"

    return status


def command_parse(command):
    command = command.rstrip()
    print("["+command + "]")
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
            print("received a command")
            output = command_parse(data)
            c.send(output + "done - got our data")
        else:
            print("client disconnected")
            break


def server():
    host = ""
    port = 22000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket bound", port)
    s.listen(25)    # queue 25 connection requests before refusing requests
    print("socket listening")

    while True:
        c, addr = s.accept()    # accept client connection
        print("Client connected :" + str(addr[0]) + ':' + str(addr[1]))
        #server_talk(c)
        threading.Thread(target=server_talk, args=(c,)).start()
    s.close()


if __name__ == "__main__":
    server()