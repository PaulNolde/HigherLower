import time
import json
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import NoSuchElementException
url = 'http://www.higherlowergame.com/'
delay = 4
DATABASE_FILENAME = 'db.json'

def load_database():
    if not os.path.exists(DATABASE_FILENAME):
        db = {}
        db['MYHIGHSCORE'] = 0
        return db
    with open(DATABASE_FILENAME, 'r') as f:
        return json.loads(f.read())

def save_database(db):
    with open(DATABASE_FILENAME, 'w') as f:
        json.dump(db, f)

def take_screenshot(score):
    screenshots_dir = 'hl-screenshots'
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
    pic_name = "Highscore-"+ str(score) + '.png'
    print ("New Highscore: " + str(score))
    driver.save_screenshot(os.path.join(screenshots_dir, pic_name))

def higher():
    but = driver.find_element(By.XPATH, '//*[@id="root"]/div/span/span/div/div[2]/div[2]/button[1]')
    but.click()

def lower():
    but = driver.find_element(By.XPATH, '//*[@id="root"]/div/span/span/div/div[2]/div[2]/button[2]')
    but.click()

def start_game():
    driver.get(url)
    time.sleep(2)
    start_game_btn = driver.find_element(By.XPATH, '//*[@id="root"]/div/span/section/div[2]/div/button[1]')
    time.sleep(delay)
    start_game_btn.click()
    
def play(rounds, hs):
    start_game()
    gameLost = False
    roundsReached = False
    currRound = 0
    while not roundsReached:
        time.sleep(delay)
        try:
            oldTitle = driver.find_element(By.XPATH, '//*[@id="root"]/div/span/span/div/div[2]/div[1]/div[1]/div/div[1]/p[1]').text[1:-1]
            oldNumber = int(driver.find_element(By.XPATH, '//*[@id="root"]/div/span/span/div/div[2]/div[1]/div[1]/div/div[2]/p[1]').text.replace(',', ''))
        except NoSuchElementException as e:
            gameLost = True
        
        if gameLost:
            score = int(driver.find_element(By.XPATH, '//*[@id="root"]/div/span/span/div/div/div[1]/p/span').text)
            if score > hs:
                take_screenshot(score)
                hs = score
                db["MYHIGHSCORE"] = score
            
            
            but = driver.find_element(By.ID, 'game-over-btn')
            time.sleep(delay/2)
            but.click()
            gameLost = False
            save_database(db)
            if(currRound > rounds):
                roundsReached = True
            continue
        
        currRound += 1
        db[oldTitle] = oldNumber
        newTitle = driver.find_element(By.XPATH, '//*[@id="root"]/div/span/span/div/div[2]/div[1]/div[2]/div/div[1]/p[1]').text[1:-1]

        if newTitle in db.keys():
            if db[oldTitle] >= db[newTitle]:
                lower()
            else:
                higher()
        else:
            if db[oldTitle] > 2000000:
                lower()
            elif db[oldTitle] < 100000:
                higher()
            else:
                if random.choice([True, False]):
                    higher()
                else:
                    lower()
    return currRound, hs

if __name__ == '__main__':
    chrome_options = ChromeOptions()

    #Hier Namen des crx files der Adguard-Extention eintragen
    chrome_options.add_extension('adguard.crx')


    driver = webdriver.Chrome(options=chrome_options)

    db = load_database()
    dbChange = 0
    highscore = db["MYHIGHSCORE"]
    print("DB size: " + str(len(db)-1) + " --- Highscore " + str(highscore))
    for i in range(100):
        db = load_database()
        oldDbLength = len(db)-1

        try:
            rr, highscore = play(50, highscore)
        except Exception as e:
            print (e)
            break

        dbChange = (len(db)-1) - oldDbLength
        print("Found overall: " + str(len(db)-1) + " | +" + str(dbChange) +  " in " +str(rr) + " rounds ( " + str(float(dbChange) / rr * 100) + "% )")
        save_database(db)
        

    driver.close()