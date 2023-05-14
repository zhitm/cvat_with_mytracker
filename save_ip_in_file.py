import subprocess

cmd = "ip route get 1.2.3.4 | grep -oP '(?<=src )\S+'  "
output = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).communicate()[0]
ip = output.strip().decode("utf-8")
path = "serverless/common/ip.txt"
f=open(path, 'w')
f.write(ip)
f.close()