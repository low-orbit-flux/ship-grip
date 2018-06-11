
import subprocess


sites = ['google.com', 'reddit.com']
for i in sites:
    output = subprocess.check_output( "echo | openssl s_client -connect " + i + ":443 2>/dev/null  | openssl x509 -noout -dates|grep -i notAfter", stderr=subprocess.STDOUT, shell=True )
    print(i + " " + output)

