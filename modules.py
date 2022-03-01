from imports import *

def timeStamped(fname, fmt='%Y-%m-%d-%H-%M-%S_{fname}'):
    return datetime.datetime.now().strftime(fmt).format(fname=fname)

def log():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S.%f')[:-3]
    return("[{}] ".format(st))

def runlog(entry):
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S.%f')[:-3]
    return("[Attempt {}][{}] ".format(entry,st))

def random_generator(size=11, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def file_len(fname):
    global i
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    try:
        return i + 1
    except NameError:
        return 0

def twocap(x, apikey, pageurl, googlekey):

    token = 'RESPONSE_TOKEN_HERE'

    params = {
        'key':apikey,
        'method':'userrecaptcha',
        'googlekey':googlekey,
        'pageurl':pageurl,
        'json':1
    }

    r = requests.post('http://2captcha.com/in.php', params=params)
    jsonA = json.loads(r.text)
    id = jsonA['request']
    #print(Fore.RED + "[Attempt {}]".format(x) + log() + "2CAP Solve ID: " + id)

    getParams = {
        'key':apikey,
        'action':'get',
        'id':id,
        'json':1
    }

    status = 0
    while status == 0:
        time.sleep(3)
        r = requests.get('http://2captcha.com/res.php', params=getParams)
        jsonB = json.loads(r.text)
        status = jsonB['status']
        token = jsonB['request']
        if "ERROR" in token:
            print(Fore.RED + "[Attempt {}]".format(x) + log() + "Captcha unsolvable. This entry will fail.")
            break
        elif "NOT_READY" in token:
            pass
        elif "ERROR" and "NOT READY" not in token:
            print(Fore.RED + "[Attempt {}]".format(x) + log() + token)

    print(Fore.CYAN + "[Attempt {}]".format(x) + log() + "Captcha response returned from 2CAP.")
    return token

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def runerror(errormsg):
    traceback.print_exc()
    print (Fore.RED + errormsg)
    input("Program crashed; press Enter to exit")
    exit()

def crashed(x):
    f = open("crashlogs.txt","a+")
    f.write(runlog(x) + "---------------- STANLEY#0001 --------------\n")
    f.write(traceback.format_exc() + "\n")
    f.write(runlog(x) + "---------------- STANLEY#0001 --------------\n")
    f.close()

def load_config():
    try:
        with open('config.json') as json_data:
            config = json.load(json_data)
        print(Fore.GREEN + log() + "Loaded config.")
    except:
        runerror("There was an error loading your config. Please check your config.")
    return config

def load_proxies():
    ips = []
    users = []
    passwds = []
    try:
        with open('proxies.txt', 'r') as f:
            for line in f:
                pr = line.strip()
                m = re.search(r'^(.*)\:(.*)\:(.*)\:(.*)$', pr)
                n = re.search(r'^(.*)\:(.*)$', pr)
                if m:
                    #print('user: ' + m.group(3))
                    #proxies[scheme + m.group(1)] = scheme + m.group(3) + ':' + m.group(4) + '@' + m.group(1) + ':' + m.group(2)
                    ips.append(m.group(1) + ':' + m.group(2))
                    users.append(m.group(3))
                    passwds.append(m.group(4))
                else:
                    ips.append(n.group(1) + ':' + n.group(2))
                    users.append(None)
                    passwds.append(None)
    except:
        runerror("There was an error loading your proxies file. Please check your proxies.")

    dict = {"ips":ips,"users":users,"passwds":passwds}
    return dict


def sel_headless_prep():
    try:
        options = Options()
        prefs = {'profile.managed_default_content_settings.images':2}
        options.add_experimental_option("prefs", prefs)
        options.add_argument('log-level=3')
        options.add_argument('--disable-gpu')
        options.headless = True
    except:
        runerror("There was an error setting chromedriver configs.")
    return options

def sel_hidden_prep():
    try:
        options = Options()
        prefs = {'profile.managed_default_content_settings.images':2}
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--log-level=3")
        options.add_argument('window-size=0x0')
        options.add_argument('--window-position=10000,0')
    except:
        runerror("There was an error setting chromedriver configs.")
    return options

def proxy_prep(x, ips, users, passwds):
    if users[x]: #it is userpass
        http_proxy  = "http://{}:{}@{}".format(users[x],passwds[x],ips[x])
        https_proxy = "https://{}:{}@{}".format(users[x],passwds[x],ips[x])
    else:
        http_proxy  = "http://{}".format(ips[x])
        https_proxy = "https://{}".format(ips[x])

    proxyDict = {
      "http":http_proxy,
      "https":https_proxy
    }
    return proxyDict

#if test_proxy(x): continue
def test_proxy(x, ips, users, passwds):
    if users[x]: #it is userpass
        http_proxy  = "http://{}:{}@{}".format(users[x],passwds[x],ips[x])
        https_proxy = "https://{}:{}@{}".format(users[x],passwds[x],ips[x])
    else:
        http_proxy  = "http://{}".format(ips[x])
        https_proxy = "https://{}".format(ips[x])

    proxyDict = {
      "http":http_proxy,
      "https":https_proxy
    }
    try:
        requests.head('https://httpbin.org/get', proxies=proxyDict, timeout=10)
        return False
    except:
        return True

def gen_email(x, config):
    try:
        if config["catchall"] == "":
            email = config["gmail"] + "+" + str(random.randint(100000,999999)) + "@gmail.com"
        elif config["gmail"] == "":
            email = random_generator() + "@" + config["catchall"]
        #print(Fore.CYAN + runlog(x) + "Generated email: {}".format(email))
    except:
        runerror("There was an error generating the entry email. Please check your config.")
    return email

def gen_name(x,config):
    try:
        if config["randomName"] == True:
            fname = names.get_first_name()
            lname = names.get_last_name()
            name = fname + " " + lname
        elif config["randomMiddleName"] == True:
            fname = config["firstName"] + " " + names.get_first_name()
            lname = config["lastName"]
            name = fname + " " + lname
        else:
            fname = config["firstName"]
            lname = config["lastName"]
            name = fname + " " + lname
        print(Fore.CYAN + runlog(x) + "Generated name: {}".format(name))
    except:
        runerror("There was an error generating the entry name. Please message stanley#0001 on Discord.")
    name_dict = {
        "fname":fname,
        "lname":lname,
        "name":name
    }
    return name_dict

#region = us, eu, singa, jap, or `url`
def gen_phone(x,config,region):
    try:
        if 'doverstreetmarket' in region and "singapore" in region or region == "singa":
            if config["randomPhone"] == True: #singapore
                phone = str("9" + str(random.randint(1000000,9999999)))
            else:
                phone = config["phone"]
        elif 'doverstreetmarket' in region and "ginza" in region or region == "jap":
            if config["randomPhone"] == True: #japan
                phone = str("042" + str(random.randint(1000000,9999999)))
            else:
                phone = config["phone"]
        elif 'doverstreetmarket' in region and "london" in region or region == 'eu':
            if config["randomPhone"] == True: #uk
                phone = str("0207946" + str(random.randint(1000,9999)))
            else:
                phone = config["phone"]
        else:
            if config["randomPhone"] == True: #american
                phone = str("415" + str(random.randint(1000000,9999999)))
            else:
                phone = config["phone"]

        if phone == config["phone"]:
            print(Fore.CYAN + runlog(x) + "Using configured phone number: {}".format(phone))
        else:
            print(Fore.CYAN + runlog(x) + "Generated phone number: {}".format(phone))
    except:
        runerror("There was an error generating the entry phone number. Please message stanley#0001 on Discord.")
    return phone

def gen_style(x, config, *stylelist):
    try:
        if stylelist[0] and config["style"] == stylelist[0]:
            style = config["style"]
        elif stylelist[1] and config["style"] == stylelist[1]:
            style = config["style"]
        elif stylelist[2] and config["style"] == stylelist[2]:
            style = config["style"]
        elif stylelist[3] and config["style"] == stylelist[3]:
            style = config["style"]
        elif stylelist[4] and config["style"] == stylelist[4]:
            style = config["style"]
        elif stylelist[5] and config["style"] == stylelist[5]:
            style = config["style"]
        elif stylelist[6] and config["style"] == stylelist[6]:
            style = config["style"]
        elif stylelist[7] and config["style"] == stylelist[7]:
            style = config["style"]
        elif stylelist[8] and config["style"] == stylelist[8]:
            style = config["style"]
        elif stylelist[9] and config["style"] == stylelist[9]:
            style = config["style"]
        else:
            style = 'no style selected'
        print(Fore.CYAN + runlog(x) + "Selected style: {}".format(style))
    except:
        runerror("There was an error generating the entry style. Please message stanley#0001 on Discord.")

def gen_size(x, config):
    try:
        #size info generation
        """
        szdict = {
            '4.5':'23.5',
            '5':'23.5',
            '5.5':'24',
            '6':'24',
            '6.5':'24.5',
            '7':'25',
            '7.5':'25.5',
            '8':'26',
            '8.5':'26.5',
            '9':'27',
            '9.5':'27.5',
            '10':'28',
            '10.5':'28.5',
            '11':'29',
            '12':'29.5'
        }
        """

        if str(config["size"]) == 'RANDOM':
            sz = random.choice(config["sizeRange"])
        else:
            sz = str(config["size"])
        #size = 'US {} ({} CM)'.format(sz, szdict[sz])
        #size = 'UK {}'.format(sz)
        size = sz
        print(Fore.CYAN + runlog(x) + "Selected size: {}".format(size))
    except:
        runerror("There was an error generating the entry size. Please check your config.")
    return size

def gen_instagram(x, config):
    try:
        if config["randomInstagram"]:
            rand = random.randint(1,4)
            if rand == 1:
                insta = names.get_first_name() + str(random.randint(0,99))
            elif rand == 2:
                insta = names.get_first_name() + names.get_last_name()
            elif rand == 3:
                insta = names.get_last_name() + str(random.randint(0,99))
            elif rand == 4:
                insta = ''.join(random.choice(string.ascii_letters) for i in range(5))
        else:
            insta = config["instagram"]
        print(Fore.CYAN + runlog(x) + "Generated Instagram: {}".format(insta))
    except:
        runerror("There was an error generating the entry Instagram handle. Please check your config.")
    return insta

def gen_address1(x, config):
    try:
        if config["address1Random"]:
            addy = ''.join(random.choice(string.ascii_letters) for i in range(3)) + " " + config["address1"]
        else:
            addy = config["address1"]
        print(Fore.CYAN + runlog(x) + "Generated address 1: {}".format(addy))
    except:
        runerror("There was an error generating address 1. Please check your config.")
    return addy

def gen_address2(x, config):
    try:
        if config["address2Random"]:
            addy2list = ['Apartment ', 'Suite ', 'Occupant ', 'Resident ', 'APT ']
            addy = random.choice(addy2list) + str(random.randint(1,99))
        else:
            addy = ''
        print(Fore.CYAN + runlog(x) + "Generated address 2: {}".format(addy))
    except:
        runerror("There was an error generating address 2. Please check your config.")
    return addy
