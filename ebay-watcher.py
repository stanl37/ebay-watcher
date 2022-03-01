from imports import *
from modules import *

class logger:
    lock = threading.Lock()

def startup():
    global entries

    clear()
    print(Fore.RED + r"""███████╗████████╗ █████╗ ███╗   ██╗██╗     ███████╗██╗   ██╗
██╔════╝╚══██╔══╝██╔══██╗████╗  ██║██║     ██╔════╝╚██╗ ██╔╝
███████╗   ██║   ███████║██╔██╗ ██║██║     █████╗   ╚████╔╝
╚════██║   ██║   ██╔══██║██║╚██╗██║██║     ██╔══╝    ╚██╔╝     #0001
███████║   ██║   ██║  ██║██║ ╚████║███████╗███████╗   ██║
╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝ """ + "\n")

    print(Fore.CYAN + r"""			   /~\   Welcome!
                          (O O) _/
                          _\=/_
          ___            /  _  \
         / ()\          //|/.\|\\
       _|_____|_       ||  \_/  ||
      | | === | |      || |\ /| ||
      |_|  O  |_|       # \_ _/ #
       ||  O  ||          | | |
       ||__*__||          | | |
      |~ \___/ ~|         []|[]
      /=\ /=\ /=\         | | |
______[_]_[_]_[_]________/_]_[_\_____""" + "\n")

    thread()

def thread():
    prod_link = ""
    while(not prod_link.startswith("http")):
        prod_link = input("What link do you want to watch? ").strip()
        if(not prod_link.startswith("http")):
            print("Hold up, that doesn't make sense. Let's try again.")

    watches = 0
    while(watches == 0):
        in_watches = input("How many accounts do you want to watch the page? ")
        try:
            watches = int(in_watches)
        except:
            print("That's not a number! Try again.")

    threads = config["threads"]
    """threads = 0
    while(threads == 0):
        in_threads = input("How many threads do you want to run? ")
        try:
            threads = int(in_threads)
        except:
            print("That's not a number! Try again.")"""

    ask = input("\nBegin watching? [Y/N] ")
    if ask.lower() == "y":
        print("Starting {} threads...".format(threads))
        clear()

        with ThreadPoolExecutor(max_workers=int(threads)) as executor:
            for x in range(watches):
                future = executor.submit(watch, (x), (prod_link), (watches))

        print("\nAll entries completed.")
    else:
        sys.exit()

def watch(x, prod_link, watches):
    with logger.lock: print(Fore.CYAN + runlog(x) + "Starting browser...")

    reg_link = 'https://reg.ebay.com/reg/PartialReg'

    try:
        if test_proxy(x, ips, users, passwds):
            with logger.lock: print(Fore.RED + runlog(x) + 'Proxy did not work.')
            return
        else:
            with logger.lock: print(Fore.CYAN + runlog(x) + 'Proxy works, continuing.')

        options = Options()
        prefs = {'profile.managed_default_content_settings.images':2}
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--log-level=3")
        options.add_argument('window-size=0x0')
        options.add_argument('--window-position=10000,10000')

        #if config to use proxies, set proxy server
        if config["useProxies"]:
            options.add_argument("--proxy-server=http://{}".format(ips[x]))

        #if proxy is user:pass, add proxy extension
        if users[x]:
            options.add_extension('Proxy Auto Auth.crx')

        #if proxy is ip auth or no proxy, headless
        if not users[x]:
            options.add_argument('--disable-gpu')
            options.headless = True

        driver = webdriver.Chrome(options=options)
        driver.set_window_size(0,0)
        driver.set_window_position(10000,10000)

        if config["useProxies"]:
            with logger.lock: print(Fore.CYAN + runlog(x) + "Initialized browser with proxy: {}".format(ips[x]))
        else:
            with logger.lock: print(Fore.CYAN + runlog(x) + "Initialized browser without proxy.")

        if users[x]:
            driver.get("chrome-extension://ggmdpepbjljkkkdaklfihhngmmgmpggp/options.html")
            driver.find_element_by_id("login").send_keys(users[x])
            driver.find_element_by_id("password").send_keys(passwds[x])
            driver.find_element_by_id("retry").clear()
            driver.find_element_by_id("retry").send_keys("2")
            driver.find_element_by_id("save").click()
            with logger.lock: print(Fore.CYAN + runlog(x) + "Set proxy username and password.")

        driver.get(reg_link)

        if 'Create an account' not in driver.page_source:
            with logger.lock:
                print(Fore.RED + runlog(x) + 'Failed to load account registration page, most likely Distil protection.'.format(x))
                with open('failHTMLS/' + timeStamped('registration-block.html'),'w+') as f:
                    f.write(driver.page_source)
                    f.close()
            driver.quit()
            return
        else:
            with logger.lock: print(Fore.CYAN + runlog(x) + "Loaded account registration page.")

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "firstname")))
        except:
            with logger.lock:
                print(Fore.RED + runlog(x) + 'Failed to find account information fields.')
                with open('failHTMLS/' + timeStamped('registration-field-fail.html'),'w+') as f:
                    f.write(driver.page_source)
                    f.close()
            driver.quit()
            return

        driver.find_element_by_id('firstname').send_keys(names.get_first_name())
        driver.find_element_by_id('lastname').send_keys(names.get_last_name())
        with logger.lock: email = gen_email(x, config)
        driver.find_element_by_id('email').send_keys(email)
        driver.find_element_by_id('PASSWORD').send_keys(config['accountPassword'])

        disabled = True
        while disabled == True:
            btndisabled = BeautifulSoup(driver.page_source, "lxml").find("button", {"id": "ppaFormSbtBtn"}).get('disabled')
            if btndisabled != 'disabled':
                disabled = False

        driver.find_element_by_id('ppaFormSbtBtn').click()
        with logger.lock: print(Fore.CYAN + runlog(x) + "Submitted account data.")

        driver.get(prod_link)
        with logger.lock: print(Fore.CYAN + runlog(x) + "Loaded product page.")
        watch_link = BeautifulSoup(driver.page_source, "lxml").find("div", {"id": "vi-atl-lnk"}).a["href"]
        with logger.lock: print(Fore.CYAN + runlog(x) + "Pulled watch link.")
        driver.get(watch_link)
        driver.get(watch_link)
        with logger.lock: print(Fore.CYAN + runlog(x) + "Loaded watch link.")

        if 'Saved in your' in driver.page_source:
            with logger.lock: print(Fore.GREEN + runlog(x) + 'Product added to watchlist of account: {}'.format(email))
        else:
            with logger.lock: print(Fore.RED + runlog(x) + 'Failure adding product to watchlist of account: {}'.format(email))

        driver.quit()
        return

    except:
        print(traceback.print_exc())

if __name__ == "__main__":
    try:
        whitelist = requests.get('https://docs.google.com/spreadsheets/d/1cHDYgw_MzTTkM_EMn-SOdqPiqMtnt_qRBQKblibnTOA/edit?usp=sharing').text
        ip = requests.get('https://api.ipify.org').text

        if ip in whitelist:

            datet = '2019-07-23'
            ExpirationDate = datetime.datetime.strptime(datet,"%Y-%m-%d").date()
            now = datetime.date.today()
            if ExpirationDate >= now:
                try:
                    requests.packages.urllib3.disable_warnings()

                    config = load_config()

                    if config["useProxies"]:
                        proxies = load_proxies()
                        ips = proxies["ips"]
                        users = proxies["users"]
                        passwds = proxies["passwds"]

                    try:
                        os.mkdir('failHTMLS')
                    except:
                        pass

                    startup()

                except Exception:
                    runerror("The script encountered an unhandled Exception. Please message stanley#0001 on Discord.")
            else:
                print(Fore.RED + r"""███████╗████████╗ █████╗ ███╗   ██╗██╗     ███████╗██╗   ██╗
        ██╔════╝╚══██╔══╝██╔══██╗████╗  ██║██║     ██╔════╝╚██╗ ██╔╝
        ███████╗   ██║   ███████║██╔██╗ ██║██║     █████╗   ╚████╔╝
        ╚════██║   ██║   ██╔══██║██║╚██╗██║██║     ██╔══╝    ╚██╔╝     #0001
        ███████║   ██║   ██║  ██║██║ ╚████║███████╗███████╗   ██║
        ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝ """ + "\n")

                print("The raffle this script was designed for has closed. Feel free to message stanley#0001 on Discord if a new raffle has opened!")
                input()
                sys.exit()

        else:
            clear()
            print(Fore.RED + r"""███████╗████████╗ █████╗ ███╗   ██╗██╗     ███████╗██╗   ██╗
    ██╔════╝╚══██╔══╝██╔══██╗████╗  ██║██║     ██╔════╝╚██╗ ██╔╝
    ███████╗   ██║   ███████║██╔██╗ ██║██║     █████╗   ╚████╔╝
    ╚════██║   ██║   ██╔══██║██║╚██╗██║██║     ██╔══╝    ╚██╔╝     #0001
    ███████║   ██║   ██║  ██║██║ ╚████║███████╗███████╗   ██║
    ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝ """ + "\n")

            print(Fore.CYAN + r"""      .--..--..--..--..--..--.
        .' \  (`._   (_)     _   \
      .'    |  '._)         (_)  |
      \ _.')\      .----..---.   /
      |(_.'  |    /    .-\-.  \  |
      \     0|    |   ( O| O) | o|
       |  _  |  .--.____.'._.-.  |      Your IP address is not authorized.
       \ (_) | o         -` .-`  |        DM stanley#0001 with your IP.
        |    \   |`-._ _ _ _ _\ /          Your IP is: {}
        \    |   |  `. |_||_|   |
        | o  |    \_      \     |     -.   .-.
        |.-.  \     `--..-'   O |     `.`-' .'
      _.'  .' |     `-.-'      /-.__   ' .-'
    .' `-.` '.|='=.='=.='=.='=|._/_ `-'.'
    `-._  `.  |________/\_____|    `-.'
       .'   ).| '=' '='\/ '=' |
       `._.`  '---------------'
               //___\   //___\
                 ||       ||
                 ||_.-.   ||_.-.
                (_.--__) (_.--__)""".format(ip) + "\n")


            input()
            sys.exit()
    except:
        clear()
        print(Fore.RED + r"""███████╗████████╗ █████╗ ███╗   ██╗██╗     ███████╗██╗   ██╗
██╔════╝╚══██╔══╝██╔══██╗████╗  ██║██║     ██╔════╝╚██╗ ██╔╝
███████╗   ██║   ███████║██╔██╗ ██║██║     █████╗   ╚████╔╝
╚════██║   ██║   ██╔══██║██║╚██╗██║██║     ██╔══╝    ╚██╔╝     #0001
███████║   ██║   ██║  ██║██║ ╚████║███████╗███████╗   ██║
╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝ """ + "\n")

        print(Fore.CYAN + r"""      .--..--..--..--..--..--.
    .' \  (`._   (_)     _   \
  .'    |  '._)         (_)  |
  \ _.')\      .----..---.   /
  |(_.'  |    /    .-\-.  \  |
  \     0|    |   ( O| O) | o|
   |  _  |  .--.____.'._.-.  |      There was an issue reaching the IP database.
   \ (_) | o         -` .-`  |               Please DM stanley#0001.
    |    \   |`-._ _ _ _ _\ /                   Error code: {}
    \    |   |  `. |_||_|   |
    | o  |    \_      \     |     -.   .-.
    |.-.  \     `--..-'   O |     `.`-' .'
  _.'  .' |     `-.-'      /-.__   ' .-'
.' `-.` '.|='=.='=.='=.='=|._/_ `-'.'
`-._  `.  |________/\_____|    `-.'
   .'   ).| '=' '='\/ '=' |
   `._.`  '---------------'
           //___\   //___\
             ||       ||
             ||_.-.   ||_.-.
            (_.--__) (_.--__)""".format('EBAY-001') + "\n")


        input()
        sys.exit()
