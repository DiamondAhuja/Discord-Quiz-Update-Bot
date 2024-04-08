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
    # Setup webdriver
    webdriver_service = Service(ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-web-security")  
    chrome_options.add_argument("--allow-running-insecure-content")  
    chrome_options.add_argument("--enable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")

    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    
    # Open login page
    driver.get('https://avenue.mcmaster.ca/login.php?target=%2Fd2l%2Fhome%2F6605')

    # Wait for user to manually login
    input("Press Enter to continue after you have logged in...")  

    # Get cookies from the session and quit the driver
    cookies = driver.get_cookies()  
    driver.quit()  

    # Create a requests session and add the cookies to it
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])  

    return session

previous_row_count = 2  

def check_for_updates(session):
    global previous_row_count  
    try:
        # Get the page and parse it with BeautifulSoup
        response = session.get('https://avenue.cllmcmaster.ca/d2l/lms/quizzing/user/quizzes_list.d2l?ou=600882')
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')

        # If there are more rows than before, send a message to the discord channel
        if len(rows) > previous_row_count:  
            asyncio.run_coroutine_threadsafe(client.get_channel(CHANNEL_ID).send("A new quiz has been posted!"), client.loop)

        # Update the row count
        previous_row_count = len(rows)  
    except Exception as e:
        print(f'Error in check_for_updates: {e}')
        
@client.event
async def on_ready():
    try:
        # Log the bot in
        driver = login()
        # Continuously check for updates every 60 seconds
        while True:  
            check_for_updates(driver)
            await asyncio.sleep(60)  
    except Exception as e:
        print(f'Error in on_ready: {e}')

# Run the bot
client.run(TOKEN)