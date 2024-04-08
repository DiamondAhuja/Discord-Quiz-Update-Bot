from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import discord
import asyncio
import requests
import config

TOKEN = config.TOKEN
CHANNEL_ID = config.CHANNEL_ID

intents = discord.Intents.default()  # Use default intents
client = discord.Client(intents=intents)

def login():
    print('Starting login function')
    webdriver_service = Service(ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-web-security")  
    chrome_options.add_argument("--allow-running-insecure-content")  
    chrome_options.add_argument("--enable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")

    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    
    driver.get('https://avenue.mcmaster.ca/login.php?target=%2Fd2l%2Fhome%2F6605')

    print('Please login manually.')
    input("Press Enter to continue after you have logged in...")  

    cookies = driver.get_cookies()  
    driver.quit()  

    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])  

    print('Finished login function')
    return session

previous_row_count = 2  

def check_for_updates(session):
    global previous_row_count  
    try:
        print('Starting check_for_updates function')
        response = session.get('https://avenue.cllmcmaster.ca/d2l/lms/quizzing/user/quizzes_list.d2l?ou=600882')

        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        print(f'Number of rows: {len(rows)}')
        print(f'Previous number of rows: {previous_row_count}')
        if len(rows) > previous_row_count:  
            asyncio.run_coroutine_threadsafe(client.get_channel(CHANNEL_ID).send("A new quiz has been posted!"), client.loop)

        previous_row_count = len(rows)  
        print('Finished check_for_updates function')
    except Exception as e:
        print(f'Error in check_for_updates: {e}')
        
@client.event
async def on_ready():
    try:
        print(f'Logged in as {client.user}')
        driver = login()
        while True:  
            check_for_updates(driver)
            await asyncio.sleep(60)  
    except Exception as e:
        print(f'Error in on_ready: {e}')

client.run(TOKEN)