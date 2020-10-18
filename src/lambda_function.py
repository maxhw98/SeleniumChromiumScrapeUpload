import time
import datetime
import pygsheets
from html_table_parser import HTMLTableParser


from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# login info
perf_url = "https://app.usealan.com/report/performance"
# sched_url = "https://app.usealan.com/report/scheduling_rate" other url I scraped
username = "USERNAME"
password = "PASSWORD"

# google sheets verification and getting the master sheet we'll edit the tabs in
auth_file = '/opt/bin/alanSheetsUpdater-ccbfcfd03f27.json'
gc = pygsheets.authorize(service_file=auth_file)
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/***************************/edit#gid=************')

# these are the tabs we will be updating, and we'll fetch them by name
sheet_names = ['Today Performance Report Raw Data',
               'Past 3 Days Performance Report Raw Data',
               'Past 5 Days Performance Report Raw Data',
               'Past 7 Days Performance Report Raw Data',
               'Past 14 Days Performance Report Raw Data',
               'Past 21 Days Performance Report Raw Data',
               'Past 42 Days Performance Report Raw Data',
               'Lifetime Performance Report Raw Data']

# main function in AWS lambda enviroment
def lambda_handler(event, context):
    dates = get_dates()  # get the date ranges to pull based on the current date and time, the AWS enviroment operates in UTC, so i actually skip back a few hours
    master_table_list = []
    # get the data
    for date in dates:
        perf_parser = scrape_page(date, get_default_chrome_options(), perf_url)
        master_table_list.append(comb_tab(perf_parser))
    # upload it to sheets
    for i in range(len(sheet_names)):
        update_sheets(sheet_names[i], master_table_list[i])
    # no real need for a return but having the dates pulled is good for debugging, checking accuracy, etc
    return(dates)


def scrape_page(date, options_in, url):
    # get fresh parser and driver
    myParser = HTMLTableParser()
    driver = webdriver.Chrome(chrome_options=options_in)
    
    # login to page
    driver.get(url)
    driver.find_element_by_name('login_name').send_keys(username)
    driver.find_element_by_name('password').send_keys(password)
    driver.find_element_by_name('submit').click()
    
    # get the JS date object
    hidden_element = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[2]/div[1]/form/div/div[1]/div/input')
    
    # tell it the date range to pull
    driver.execute_script(date, hidden_element)
    driver.find_element_by_name('filter').click()
    time.sleep(1)
    
    # grab the HTML table and give it to the parser
    table = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div[2]/table')
    outerHTML = table.get_attribute('outerHTML')
    myParser.feed(outerHTML)
    
    # get the next page
    curr_url = driver.current_url
    page_num = 2
    curr_url = curr_url + "&page="+str(page_num)

    # keep going for all the pages
    while(nested_scrape(date, options_in, curr_url, myParser, driver)):
        if page_num <= 10:
            page_num+= 1
            curr_url = curr_url[0:-1]+str(page_num)
        elif page_num <= 100:
            page_num+= 1
            curr_url = curr_url[0:-1]+str(page_num)
        else:
            print("wow you have 100 pages of clients, maybe time to update this")
    
    driver.close()
    return(myParser)

def nested_scrape(date, options_in, url, parser, driver): # a limited version of the scrape function to scrape next pages of table
    driver.get(url)
    table = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div[2]/table')
    innerHTML = table.get_attribute('innerHTML')
    outerHTML = table.get_attribute('outerHTML')
    if "No data found!" in outerHTML:
        return False
    else:
        parser.feed(outerHTML)
        return True
    
def update_sheets(sheet_title, table): # pygsheets helper function
    curr_sheet = sh.worksheet_by_title(sheet_title)
    curr_sheet.clear()
    for i, row in enumerate(table, start=1):
        curr_sheet.update_row(i, row, col_offset=0)

def comb_tab(parser): # this function combines the multiple pages of tables into one and throws away duplicate header rows
    master_list = []
    for row in parser.tables[0]:
        master_list.append(row)
    for i in range(1, len(parser.tables)):
        parser.tables[i].pop(0)
        for row in parser.tables[i]:
            master_list.append(row)
    return master_list

def get_dates(): # creates desired date ranges for JS script execution
    # today (data so far for the current date)
    today = (datetime.datetime.now()-datetime.timedelta(hours=4)).isoformat()[0:10]+","+(datetime.datetime.now()-datetime.timedelta(hours=4)).isoformat()[0:10]
    today = "arguments[0].value = '"+today+"'"

    # past 3 days (excluding today, i.e. from four days ago to one day ago)
    past3 = (datetime.datetime.now()-datetime.timedelta(hours=4, days=4)).isoformat()[0:10]+","+(datetime.datetime.now()-datetime.timedelta(hours=4, days=1)).isoformat()[0:10]
    past3 = "arguments[0].value = '"+past3+"'"

    # past 5 days
    past5 = (datetime.datetime.now()-datetime.timedelta(hours=4, days=6)).isoformat()[0:10]+","+(datetime.datetime.now()-datetime.timedelta(hours=4, days=1)).isoformat()[0:10]
    past5 = "arguments[0].value = '"+past5+"'"

    # past 7 days
    past7 = (datetime.datetime.now()-datetime.timedelta(hours=4, days=8)).isoformat()[0:10]+","+(datetime.datetime.now()-datetime.timedelta(hours=4, days=1)).isoformat()[0:10]
    past7 = "arguments[0].value = '"+past7+"'"

    # past 14 days
    past14 = (datetime.datetime.now()-datetime.timedelta(hours=4, days=15)).isoformat()[0:10]+","+(datetime.datetime.now()-datetime.timedelta(hours=4, days=1)).isoformat()[0:10]
    past14 = "arguments[0].value = '"+past14+"'"

    # past 21 days
    past21 = (datetime.datetime.now()-datetime.timedelta(hours=4, days=22)).isoformat()[0:10]+","+(datetime.datetime.now()-datetime.timedelta(hours=4, days=1)).isoformat()[0:10]
    past21 = "arguments[0].value = '"+past21+"'"

    # past 42
    past42 = (datetime.datetime.now()-datetime.timedelta(hours=4, days=43)).isoformat()[0:10]+","+(datetime.datetime.now()-datetime.timedelta(hours=4, days=1)).isoformat()[0:10]
    past42 = "arguments[0].value = '"+past42+"'"

    # lifetime (start Jul 1 2018)
    lifetime = "2018-07-01"+","+(datetime.datetime.now()-datetime.timedelta(hours=4)).isoformat()[0:10]
    lifetime = "arguments[0].value = '"+lifetime+"'"

    # dates are :
    dates = [today, past3, past5, past7, past14, past21, past42, lifetime]
    return dates


def get_default_chrome_options(): # options we use, moslty from vittario nardone's project
    chrome_options = webdriver.ChromeOptions()
    lambda_options = [
        '--autoplay-policy=user-gesture-required',
        '--disable-background-networking',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-breakpad',
        '--disable-client-side-phishing-detection',
        '--disable-component-update',
        '--disable-default-apps',
        '--disable-dev-shm-usage',
        '--disable-domain-reliability',
        '--disable-extensions',
        '--disable-features=AudioServiceOutOfProcess',
        '--disable-hang-monitor',
        '--disable-ipc-flooding-protection',
        '--disable-notifications',
        '--disable-offer-store-unmasked-wallet-cards',
        '--disable-popup-blocking',
        '--disable-print-preview',
        '--disable-prompt-on-repost',
        '--disable-renderer-backgrounding',
        '--disable-setuid-sandbox',
        '--disable-speech-api',
        '--disable-sync',
        '--disk-cache-size=33554432',
        '--hide-scrollbars',
        '--ignore-gpu-blacklist',
        '--ignore-certificate-errors',
        '--metrics-recording-only',
        '--mute-audio',
        '--no-default-browser-check',
        '--no-first-run',
        '--no-pings',
        '--no-sandbox',
        '--no-zygote',
        '--password-store=basic',
        '--use-gl=swiftshader',
        '--use-mock-keychain',
        '--single-process',
        '--window-size=1165,685',
        '--headless']
        

    for argument in lambda_options:
        chrome_options.add_argument(argument)
            
    return chrome_options


