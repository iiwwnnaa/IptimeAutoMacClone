import randmac, requests, os, schedule, time

class iptime:
    def __init__(self):
        self.host = '192.168.0.1' #ipTIME routers ip address
        self.username = 'admin' #Admin username
        self.passwd = '' #Admin password

        self.s = requests.session()
        self.headers ={
            'Referer':f'http://{self.host}/sess-bin/login_session.cgi',
            'User-Agent':'Mozilla/5.0'
        }

    def login(self):
        payload = {
            'init_status':'1',
            'captcha_on':'0',
            'captcha_file':'',
            'username': self.username,
            'passwd': self.passwd,
        }

        res = self.s.post(f'http://{self.host}/sess-bin/login_handler.cgi', headers=self.headers, data=payload).text

        if 'efm_session_id' in res:
            self.efm_session_id = res.split("setCookie('")[1].split("')")[0]

    def chgMac(self):
        newMac = str(randmac.RandMac())
        print("Trying to change mac address to : " + newMac)
        newMac = newMac.split(':')
        payload = {
            'tmenu':'iframe',
            'smenu':'hiddenwansetup',
            'act':'save',
            'ocolor':'',
            'wan':'wan1',
            'ifname':'eth3',
            'nopassword':'0',
            'wan_type':'dynamic',
            'allow_private':'on',
            'hw_dynamic1':newMac[0],
            'hw_dynamic2':newMac[1],
            'hw_dynamic3':newMac[2],
            'hw_dynamic4':newMac[3],
            'hw_dynamic5':newMac[4],
            'hw_dynamic6':newMac[5],
            'hw_conf_dynamic':'on'
        }
        self.headers['Referer'] = f'http://{self.host}/sess-bin/timepro.cgi'
        self.s.post(self.headers['Referer'], headers=self.headers, data=payload, cookies={'efm_session_id':self.efm_session_id})

    def logout(self):
        self.s.get(f'http://{self.host}/sess-bin/login_session.cgi?logout=1', headers=self.headers)

    def pingTest(self):
        time.sleep(5)
        cmd = 'ping -c 1 8.8.8.8'
        flag = os.system(cmd)
        if flag == 0:
            return True
        return False

def job():
    m = iptime()
    m.login()
    while True:
        m.chgMac()
        if m.pingTest():
            print("OK")
            m.logout()
            break
        print("FAILED to connect internet.. retrying")

if __name__ == "__main__":
    schedule.every().day.at('04:00').do(job) # Change Mac Address automatically everyday at 04:00
    while True:
        schedule.run_pending()
        time.sleep(1)