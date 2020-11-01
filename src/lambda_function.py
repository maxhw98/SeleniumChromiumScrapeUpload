
import os
import time
import datetime
import pygsheets
import xlrd
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# login info
perf_url = "https://app.usealan.com/report/performance"
sched_url = "https://app.usealan.com/report/scheduling_rate"
username = "maximumfloats"
password = "4z?qGDYysmQ*6Ev"

#google sheets verification and getting the master sheet we'll edit the tabs in
auth_file = '/opt/bin/alanSheetsUpdater-ccbfcfd03f27.json'
gc = pygsheets.authorize(service_file=auth_file)
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1rLDIoaVNMVaVfYZj8id0hsVRcXqLzLa-dk1tbkBpcAw/edit#gid=1100991330')

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
    # initialize dates
    dates = get_dates()
    # make directory in tmp (my only writiable dir) for the files
    os.chdir("/tmp")
    if "data_downloads" not in os.listdir():
        os.mkdir("data_downloads")
    os.chdir("data_downloads")
    # get excel sheets
    for date in dates:
        scrape_page(date, get_default_chrome_options(), perf_url)
    # sort em
    files = os.listdir()
    correct_order = files.sort(key=os.path.getmtime)
    # initalize table for data
    tables = []
    # fill the table
    for i in range(len(files)):
        tables.append(make_tab(files[i]))
    
    for i in range(len(tables)):
        curr_sheet = sh.worksheet_by_title(sheet_names[i])
        curr_sheet.update_values('A1', tables[i])
        print(sheet_names[i],"updated - ", dates[i])
    # return(tables)


def scrape_page(date, options_in, url):
    
    driver = webdriver.Chrome(chrome_options=options_in)
    
    driver.get(url)
    driver.find_element_by_name('login_name').send_keys(username)
    driver.find_element_by_name('password').send_keys(password)
    driver.find_element_by_name('submit').click()

    hidden_element = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[2]/div[1]/form/div/div[1]/div/input')

    driver.execute_script(date, hidden_element)
    driver.find_element_by_name('filter').click()
    time.sleep(1)

    driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div[1]/form/div/div[5]/a').click()
    time.sleep(6)
    driver.find_element_by_xpath('//*[@id="downloadLink"]/a').click()
    
    driver.close()



def make_tab(workbook):
    # get workbook
    wb = xlrd.open_workbook(workbook)
    sheet1 = wb.sheet_by_index(0)
    
    out_tab = []
    # iterate through rows of workbook and update sheet value as you go
    for i in range(len(sheet1.col_values(0))):
        row = sheet1.row_values(i)
        row.pop(15) # remove problematic column with NaNs
        row.pop(0) # remove redundant column at beginning
        out_tab.append(row)
    
    return(out_tab)
  

def get_dates():
    # today (data so far for the current date)
    today = (datetime.datetime.now()-datetime.timedelta(hours=4)).isoformat()[0:10]+","+(datetime.datetime.now()-datetime.timedelta(hours=4)).isoformat()[0:10]
    today = "arguments[0].value = '"+today+"'"

    # past 3 days (excluding today, i.e. from four days ago to one day ago)
    past3 = (datetime.datetime.now()-datetime.timedelta(hours=4, days=3)).isoformat()[0:10]+","+(datetime.datetime.now()-datetime.timedelta(hours=4, days=1)).isoformat()[0:10]
    past3 = "arguments[0].value = '"+past3+"'"

    # past 5 days
    past5 = (datetime.datetime.now()-datetime.timedelta(hours=4, days=5)).isoformat()[0:10]+","+(datetime.datetime.now()-datetime.timedelta(hours=4, days=1)).isoformat()[0:10]
    past5 = "arguments[0].value = '"+past5+"'"

    # past 7 days
    past7 = (datetime.datetime.now()-datetime.timedelta(hours=4, days=7)).isoformat()[0:10]+","+(datetime.datetime.now()-datetime.timedelta(hours=4, days=1)).isoformat()[0:10]
    past7 = "arguments[0].value = '"+past7+"'"

    # past 14 days
    past14 = (datetime.datetime.now()-datetime.timedelta(hours=4, days=14)).isoformat()[0:10]+","+(datetime.datetime.now()-datetime.timedelta(hours=4, days=1)).isoformat()[0:10]
    past14 = "arguments[0].value = '"+past14+"'"

    # past 21 days
    past21 = (datetime.datetime.now()-datetime.timedelta(hours=4, days=21)).isoformat()[0:10]+","+(datetime.datetime.now()-datetime.timedelta(hours=4, days=1)).isoformat()[0:10]
    past21 = "arguments[0].value = '"+past21+"'"

    # past 42
    past42 = (datetime.datetime.now()-datetime.timedelta(hours=4, days=42)).isoformat()[0:10]+","+(datetime.datetime.now()-datetime.timedelta(hours=4, days=1)).isoformat()[0:10]
    past42 = "arguments[0].value = '"+past42+"'"

    # lifetime (start Jul 1 2018)
    lifetime = "2018-07-01"+","+(datetime.datetime.now()-datetime.timedelta(hours=4)).isoformat()[0:10]
    lifetime = "arguments[0].value = '"+lifetime+"'"

    # dates are :
    dates = [today, past3, past5, past7, past14, past21, past42, lifetime]
    return dates


def get_default_chrome_options():
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



