
import subprocess
import re

disks = ['sda', 'sdb', 'sdc', 'sdd', 'sde']
p_errors = re.compile(r'No Errors Logged')


print( '\n' * 5 + 20 * '=' + '| Disk Status |' + 20 * '=')

for i in disks:
    output = ""
    try:
        output = subprocess.check_output('smartctl -a /dev/' + i, stderr=subprocess.STDOUT, shell=True)
    except:
        pass
    m_errors = None
    m_errors = p_errors.search(output)
    if m_errors:
        print( i + ": OK")
    else:
        print( i + ": ERROR")
#    print(m_errors.group())


print( '\n' * 3 + 20 * '=' + '| Array Status |' + 20 * '=' )

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
    else:
        print("something went wrong...")

print('\n' * 4)
