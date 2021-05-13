import random
from bs4 import BeautifulSoup
import re
import smtplib
import time
#strtime_file = time.time()
import timeit
from collections import defaultdict
from smtplib import SMTPException
import re,pprint

import requests
import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, InvalidSessionIdException

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import itertools
import sys,os
#from scraper_api import ScraperAPIClient
import datetime, unidecode
import subprocess
from datetime import date
#from googletrans import Translator

# init the Google API translator
#translator = Translator()

## turn down level of v verbose by dwfauklt selenium webdriver logging , lol
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import copy

sys.path.append('./')
from metaLeague_data import *

# define global init 'surebet' condition value (note by default any bet will not be a surebet given its > 1.0)
surebet_factor = 1.0
#cibstant initialised to False - for determining if they customer's expected odds are retrieved for alert system...
odd_are_found = False

TEST_MODE = True # False  


# set aws CLI creds using boto here:
import boto3
import botocore

botoErrList = [e for e in dir(botocore.exceptions) if e.endswith('Error')]
#botoErrList = tuple(botoErrList)

client = boto3.client('sns','ca-central-1')
#store Paul Darmas's number:
my_phone_number          = '0014372468105'
main_client_phone_number = '0033609590209'
courrouxbro1_client_phone_number = '0033647228992'
courrouxbro2client_phone_number  = '0033620858827'
## TODO : IMSERT HUGO'S PROPER NO. !!!!!

client_hugo = '003366784209'
# define global init 'surebet' condition value (note by default any bet will not be a surebet given its > 1.0)



#client = ScraperAPIClient('781fa06f6c29968fe2971fa6a90760dc')
#respondsr = client.get(url = "https://france-pari.fr/")
#print(result)
#text file with records of surebets already alerted for:

if not TEST_MODE:
    surebets_Done_list_textfile = './sure_bets_placed.txt'
    fp1 = open(surebets_Done_list_textfile, "r")

list_mailed_surebets = []


from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
req_proxy = RequestProxy(log_level=logging.ERROR) #you may get different number of proxy when  you run this at each time

if not TEST_MODE:
    proxies = req_proxy.get_proxy_list()

def check_is_surebet(*args): #odds_A, odds_B):

    total_iverse_odds_sum = 0.0
    for odds in args:
        #print('in check_is_surebet() func. --  odds_i = ' + str(odds) + ' ')
        if odds == 0:
            pass
        else:
            total_iverse_odds_sum += 1/(odds)

    #
    print(' Surebet value = ' + str(total_iverse_odds_sum))

    if total_iverse_odds_sum < 1.0 and total_iverse_odds_sum > 0.0:
        return True

    return False    

def get_surebet_factor(*argv): #  odds_A, odds_B):

    global surebet_factor

    if len(argv) >= 1:
    # reset this global value -- but must think on should I create class 'gambler' to correctly initialise these kinds of vars and update per instance etc..(?)
        surebet_factor = 0.0

        #total_iverse_odds_sum = 0.0
        for odds in argv:
            if odds == 0.0:
                pass
            else:
                surebet_factor += 1/(odds)

    #print('in get surebet function -- surebet = ' + str(surebet_factor))

    return surebet_factor


# def return_surebet_vals(*argv, stake):

#     surebetStakes = []

#     # !! NoTE : ive added a '100.0' factor into the calculations below to display to the lads in their emails

#     for i,odds in enumerate(argv):

#         if odds == 0.0 or surebet_factor == 0.0 :
#             surebetStakes.append(1)
#         else:    
#             surebetStakes.append((1/surebet_factor)*(1/odds))
#             #print('surebetStakes[' + str(i) + '] =  ' + str(surebetStakes[i]))

#     return surebetStakes


## TODO : must generalize this and add file to code bundle
DRIVER_PATH = r'/usr/bin/chromedriver' #the path where you have "chromedriver" file.


options = Options()
options.add_argument("start-maximized")
options.headless = True
#options.LogLevel = False
#options.add_argument("start-maximized")

options.add_argument("--window-size=1920,1200")

#options.add_argument("--LogLevel=0")
#options.add_argument("user-agent= 'Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41' ")
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_6) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.698.0 Safari/534.24'")
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH, service_args=["--verbose", "--log-path=D:\\qc1.log"])
    

W_1 = 'Home team (1st team name on the betting card) to win'
W_2 = 'Away team (2nd team name on the betting card) to win'
D   = 'A draw between the team in the 90 minutes'
#L_1 = 'Home team (1st team name on the betting card) to lose'
#L_2 = 'Away team (2nd team name on the betting card) to lose'

## TEST wait time for after a non dict - data change
wait_time_idirNoChanges = random.randint(0,1)

def check_for_tennis_value_bets(*args):

    global all_split_sites_data, DEBUG_OUTPUT, globCounter

    # init. copy data dict.
    all_split_sites_data_copy = {}
    dont_recimpute_surebets = False  

    # initialize proxy count and create list of proxies from the prox generator
    PROXY_COUNTER = 0
    k = 33
    proxies = req_proxy.get_proxy_list()

    #initialize counters
    sure_bet_counter = 0
    total_time_parsing = 0.0
    globCounter=0
    dataDictChangdCounter = 0
    RAND_PROXY_JUMP = 13

    while(True):

        if PROXY_COUNTER >= len(proxies) - (2*RAND_PROXY_JUMP + 1):
            proxies = req_proxy.get_proxy_list()
            PROXY_COUNTER = 0
        PROXY = proxies[PROXY_COUNTER].get_address()
        #print("Proxy address = ******************************** %s ************************************ %d",PROXY,k)
        
        driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

        webdriver.DesiredCapabilities.CHROME['proxy']={
            "httpProxy":PROXY,
            "ftpProxy":PROXY,
            "sslProxy":PROXY,
            "proxyType":"MANUAL",
        }
        
        PROXY_COUNTER += random.randint(1,RAND_PROXY_JUMP)
        k += 1
        
        start_parse = time.time() 
        start_full_parsingTimer = time.time()
        if parseTenisSites(driver): #all_srpaed_sites_data):
            end_parse = time.time() 
            print('Time to do parsing was = ' + str(end_parse - start_parse))
            total_time_parsing += (end_parse - start_parse) 
            pass
            
        else:
            end_parse = time.time() 
            print('Time to do parsing was = ' + str(end_parse - start_parse))
            total_time_parsing += (end_parse - start_parse)
            print("Error i parsing function...retring... But needs diagnostics and/or a fix ! ...")
            pass
        
        globCounter += 1
        if all_split_sites_data == all_split_sites_data_copy:
            dont_recimpute_surebets = True
            dataDictChangdCounter += 1
            print(' #############################################################new data dict. has NOT been updated ...:( -- so no need to re-check surebets        ################################################################### .... ;)')
            time.sleep(wait_time_idirNoChanges)
        else:
            dont_recimpute_surebets = False
            # print('lenght of NEWd dict = ' + str(len(all_split_sites_data)))
            print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&  new data dict. has been updated ...:( -- so can check surebets .. %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% .... ;)')
            
        print('total num attempts/loops  = ' + str(globCounter) + '-- no. of times data changes & was updated in parsing = ' + str(globCounter - dataDictChangdCounter))    

        print('AVerage time to do parsings was = ' + str(total_time_parsing/globCounter)) 
        print('number of surebets found so far is = ' + str(sure_bet_counter))    

        if not dont_recimpute_surebets :
            start_surebet_timer = time.time()
            index = 0   
            
        if not dont_recimpute_surebets:
            end_surebet_timer = time.time()
            print("Time taken to just check for surebets besides parsing = " + str(end_surebet_timer - start_surebet_timer))

    return True


def send_mail_alert_gen_socer_surebet_prportions(bookie_1,bookie_2,bookie_3,bookie_one_outcome, bookie_2_outcome,teamA,teamB,date,competition,proportions_list, Profit,odd1,odd2,odd3):

    global DEBUG_OUTPUT, surebet_factor
    successFlag = False
    sender =  'godlikester@gmail.com'

## TEST - ONLY HARDCODING HERE FOR FIRST KNCK OUT RUN OF CHAMPIONS LEAGUE GAMES
    #competition = 'Ligue des Champions'
## !!!!!!!!!!!!!!!!!!!!!!!!!!!!! END TEST !!!!!!!!!!!!!

    if TEST_MODE:
        receivers = ['crowledj@tcd.ie'] 
    else:
        receivers = ['godlikester@gmail.com', 'crowledj@tcd.ie', 'pauldarmas@gmail.com','raphael.courroux@hotmail.fr','theoletheo@hotmail.fr','alexandrecourroux@hotmail.com','scourroux@hotmail.com']    

    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test"""

    bookieTeamA = ""
    bookieTeamB = ""
    bookieDraw  = ""

    if   "Home team " in bookie_one_outcome:
        bookieTeamA           = bookie_1
        proportions_list_win  = proportions_list[0]
        winOdd                = odd1
    elif "Away team " in bookie_one_outcome:
        bookieTeamB           = bookie_1  
        proportions_list_lose = proportions_list[0]
        loseOdd               = odd1
    else:
        bookieDraw            = bookie_1
        proportions_list_draw = proportions_list[0]
        drawOdd               = odd1      
   

    if "Home team " in bookie_2_outcome:
        bookieTeamA           = bookie_2
        proportions_list_win  = proportions_list[1]
        winOdd                = odd2
    elif  "Away team " in bookie_2_outcome:
        bookieTeamB           = bookie_2  
        proportions_list_lose = proportions_list[1]
        loseOdd               = odd2        
    else:
        bookieDraw = bookie_2
        proportions_list_draw = proportions_list[1]
        drawOdd               = odd2        


    if  not bookieTeamA :
        bookieTeamA           = bookie_3
        proportions_list_win  = proportions_list[2]
        winOdd                = odd3
    elif  not bookieTeamB:
        bookieTeamB           = bookie_3  
        proportions_list_lose = proportions_list[2]
        loseOdd               = odd3        
    else:
        bookieDraw             = bookie_3
        proportions_list_draw = proportions_list[2]
        drawOdd               = odd3       

    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    Surebet Alert  :

    Profit = """ + str(round( Profit ,3)) + """
      
    Event: """ + str(competition) + """
    Date: """  + str(date) + """
    teamA: """ + str(teamA) + """
    teamB: """ + str(teamB) + """

    bookieTeamA: """ + str(bookieTeamA) + """   """  +  str(round(proportions_list_win  *100.0,2)) + """ % -- odd_1 is = """  +  str(winOdd)  + """     
    bookieDraw: """  + str(bookieDraw)  + """   """  +  str(round(proportions_list_draw *100.0,2)) + """ % -- odd_2 is = """  +  str(drawOdd) + """     
    bookieTeamB: """ + str(bookieTeamB) + """   """  +  str(round(proportions_list_lose *100.0,2)) + """ % -- odd_3 is = """  +  str(loseOdd)     

    #for line in fp1:
    global list_mailed_surebets 
    list_mailed_surebets.append("""bookieTeamA: """ + str(bookieTeamA) + """   """  + str(proportions_list[0]) + """ % -- odd_1 is = """    +  str(odd1) +  """ bookieDraw: """  + str(bookieDraw)  +  """   """  + str(proportions_list[1]) + """ % -- odd_2 is = """    + str(odd2) + """ \
        bookieTeamB: """ + str(bookieTeamB) + """   """  + str(proportions_list[2]) +  """ % -- odd_3 is = """   +  str(odd3) )
    #fp1.close()

    print(' ********************   message = ' + message)
    print(' ******************** ')
    #if message in list_mailed_surebets:
    #    print('sureBet already found -- dontt re-mail ')
    #    return successFlag

    if Profit > 100.0:

        try:
            smtpObj = smtplib.SMTP_SSL("smtp.gmail.com",465)
            smtpObj.login("godlikester@gmail.com", "Pollgorm1")
            #smtpObj.login("keano16@dcrowleycodesols.com", "Pollgorm9")
            smtpObj.sendmail(sender, receivers, message)         
            print("Successfully sent email")
            

            #FP1 = open(surebets_Done_list_textfile,'a')
            #FP1.write(message + '\n')
            #FP1.close()

            successFlag = True
        except SMTPException:
            print("Error: unable to send email")
            pass


    return successFlag, [bookieTeamA,bookieDraw, bookieTeamB], [proportions_list_win, proportions_list_draw, proportions_list_lose], [winOdd, drawOdd, loseOdd]  


def send_sms_alert_forfinal_round_ligue1():

    message = "the final round - round 38th of Ligue one's odds are on betclic's site ! :)"

    try:
        client.publish(PhoneNumber=main_client_phone_number,Message=message)
        client.publish(PhoneNumber=my_phone_number,Message=message)
        client.publish(PhoneNumber=courrouxbro1_client_phone_number,Message=message)
        client.publish(PhoneNumber=courrouxbro2client_phone_number,Message=message)


        client.publish(PhoneNumber=client_maxime,Message=message)
        client.publish(PhoneNumber=client_groco,Message=message)
        client.publish(PhoneNumber=client_hugo,Message=message)
        client.publish(PhoneNumber=client_theo,Message=message)


    except botocore.exceptions.ParamValidationError as e:
        print("Parameter validation error: %s" % e)
        return False
    except botocore.exceptions.ClientError as e:
        print("Unexpected error: %s" % e)
        return False
    except botoErrList as e:
        print("Unexpected error: %s" % e)
        return True
    finally:
        print('Error in the text SNS messaging not picked up :( ...')
        return False


    return True


def send_sms_alert_tennis(stuff='betclic', players_names= 'RAFA NADAL rOGERfEDERER', tourny_name = 'ATP Rome'):

    message = "Tournament : " +  tourny_name  + " \n Players : \t" + players_names   + " odds are now on betclic's site ! :)"

    try:
        client.publish(PhoneNumber=main_client_phone_number,Message=message)
        client.publish(PhoneNumber=my_phone_number,Message=message)
        client.publish(PhoneNumber=courrouxbro1_client_phone_number,Message=message)
        client.publish(PhoneNumber=courrouxbro2client_phone_number,Message=message)
        client.publish(PhoneNumber=client_hugo,Message=message)

    except botocore.exceptions.ParamValidationError as e:
        print("Parameter validation error: %s" % e)
        return False
    except botocore.exceptions.ClientError as e:
        print("Unexpected error: %s" % e)
        return False
    finally:
        print('Error in the text SNS messaging not picked up :( ...')
        return False


    return True


tot_parionbet   = 0.0
tot_france_pari = 0.0
tot_winimax     = 0.0
tot_cbet        = 0.0
tot_pmu         = 0.0
tot_unibet      = 0.0
tot_betclic     = 0.0



# teenis site links :
betclic_tenis_link = 'https://www.betclic.fr/tennis-s2'
def parseTenisSites(driver):
    
    betclic_new = True
    unique_match_dict = {}
    while True:
    
        driver.get(betclic_tenis_link)
        driver.maximize_window()
        driver.refresh()
        #igue1_games_info_betclic   = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/sports-left-menu/div/sports-list-menu/sports-list/div/div[2]/sports-tile[27]'  /html/body/app-desktop/div[1]/div/sports-left-menu/div/sports-list-menu/sports-list/div/div[2]/sports-tile[27]'              
        #SPORTS LIST LINK :  /html/body/app-desktop/div[1]/div/sports-left-menu/div/sports-list-menu/sports-list/div/div[2]         
        
        # sports list element :
        #/html/body/app-desktop/div[1]/div/sports-left-menu/div/sports-list-menu/sports-list/div/div[2]           
        
        #tennis_element = driver.find_element_by_class_name('sportList_list')                                   
        
        # sportList_element = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/sports-left-menu/div/sports-list-menu/sports-list/div/div[2]/sports-tile')
        # for panels in sportList_element:
        #     try:
        #        sport_name_per_panel = panels.find_element_by_class_name('sportlist_name').text
        #     except StaleElementReferenceException:
        #        print(" StaleElementReferenceException Error in Betclic site -- when trying to grab  ..... ")
        #        continue  

        #     if 'Tennis' in sport_name_per_panel:
        #         sport_name_per_panel = panels.find_element_by_xpath('.//sports-details/div/sports-competition-list/div').text
        #         if 'ATP' in sport_name_per_panel:
        #             atp_events_list = panels.find_elements_by_xpath('.//sports-details/div/sports-competition-list/div/sports-tile')
        #     else:
        #         continue        

        #     for event in atp_events_list:
        #         print('Found ATP event number i ...')

        #         if 'ATP' in event.text:
    
        #             checkbox_parent = event.find_element_by_xpath(".//a/sports-multi-competitions-checkbox/div/label/input")
        #             tick_return_val = checkbox_parent.click()
        #             event.click() #find_element_by_xpath('.//a').       

        #             #block-link-302 > sports-multi-competitions-checkbox > div
        

        #center_scroller_element = driver.find_element_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div')
    
       

        # for tennis_game in tennis_games_per_panel:

        #     event_element = tennis_game.find_element_by_xpath('../a')
        #     event_element_name_str = event_element.get_attribute('href').text
        #     if 'atp' in event_element_name_str.lower():

        #         try:
        #             event_element.click()
        #         except:
        #             print(" StaleElementReferenceException Error in Betclic site -- when trying to grab  ..... ")
        #             #exit(1)
        #             return False

        #         ## !!! LIVE games change to be done as swmn here...
        #         ## Live string needs another branch to handle - diff indices for teams and odds as per 'match' string then being :
        #         # ®\n37' - 1ère  mt\bordeaux\n1 - 1\nlorient\nrésultat du match\nbord\neaux\n2,15\nn\nul\n2,35\nlor\nient\n3,15\nquelle équipe marquera le but 3 ?\nbord\neaux\n1,75\npas de\n but\n4,10\nlor\nient\n2,25\n67\nparis\n"
        #         try:
        #             teamA = team_names_maping[unidecode.unidecode(info_per_match[1] + info_per_match[2]).lower().strip() ]
        #             teamB = team_names_maping[unidecode.unidecode(info_per_match[9] + info_per_match[10]).lower().strip()]
        #         except KeyError:
        #             any_errors = False
        #             print("Error  caught in your BETCLIC parse func.  -- keyError in team mapper  :( .....")
        #             continue

        if len(unique_match_dict) >= 6 :
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            scrolled_already = False
            time.sleep(3)  

        try:
            center_scroller_element = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-all-offer/div/bcdk-vertical-scroller/div/div[2]/div/div/sports-events-event')
            center_scroller_element_tag = driver.find_elements_by_tag_name('sports-events-event')

        except (KeyError, NoSuchElementException, StaleElementReferenceException, InvalidSessionIdException):
            any_errors = False
            print(" StaleElementReferenceException Error in Betclic site -- when trying to grab  first web ele,ment..... ")
            continue

        if not center_scroller_element:
            center_scroller_element = center_scroller_element_tag

        options.add_argument("start-maximized")
        options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_6) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.698.0 Safari/534.24'")
        driver_inner = webdriver.Chrome(options=options, executable_path=DRIVER_PATH) #, service_args=["--verbose", "--log-path=D:\\qc1.log"])
        scrolled_already = True
        for tennis_game in center_scroller_element:

            if len(unique_match_dict) == 6 and scrolled_already:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                scrolled_already = False
                time.sleep(3)  

            event_element = tennis_game
            try:
                event_element_name_str = event_element.text
            except (KeyError, NoSuchElementException, StaleElementReferenceException, InvalidSessionIdException):
                any_errors = False
                print(" StaleElementReferenceException Error in Betclic site -- when trying to grab games elements ..... ")
                continue

            if 'atp' in event_element_name_str.lower():

                try:
                    #event_element.find_element_by_xpath('.//a').click()
                    #time.sleep(1)
                    ## need to get this click to work really
                    #event_element.find_element_by_xpath('.//a').click()
                    link = event_element.find_element_by_xpath('.//a').get_attribute('href')

                    game_info = event_element.find_element_by_xpath('.//a/div').text
                    tourny_n_players  = game_info.split('\n')

                    if len(tourny_n_players) >= 3: 
                        tourny_name       = tourny_n_players[0]
                        players_names     = str(tourny_n_players[-3]) + ' ' + str(tourny_n_players[-1])

                    if (tourny_name + players_names) not in unique_match_dict.keys():
                        unique_match_dict[ tourny_name + players_names ] = True  
                    
                    #start_timer = time.time()
                    driver_inner.get(link)
                    #end_timer = time.time()
                    #time.sleep(1)
                    #print('time taken in getting new link in driver is = ' + str(end_timer - start_timer))        
                    #time.sleep(8)
                    match_beting_fields = driver_inner.find_elements_by_xpath('//*[@id="matchHeader"]/bcdk-chips-scroller/div/div/div/div')

                except (KeyError, NoSuchElementException, StaleElementReferenceException, InvalidSessionIdException):
                    any_errors = False
                    print(" StaleElementReferenceException Error in Betclic site -- when trying to grab  ..... ")
                    continue

                try:
                    for bet_types in match_beting_fields:
                        bet_type_name = bet_types.text
                        #print(bet_type_name)

                        if 'aces' in bet_type_name.lower() and unique_match_dict[ tourny_name + players_names ] :
                            unique_match_dict[ tourny_name + players_names ]  = False
                            send_sms_alert_tennis('betclic', players_names, tourny_name) 

                except (KeyError, NoSuchElementException, StaleElementReferenceException, InvalidSessionIdException):
                    any_errors = False
                    print("Error  caught in your BETCLIC parse func.  -- keyError in team mapper  :( .....")
                    continue


    return True

site_betclci_soccer_link ='https://www.betclic.fr/football-s1/ligue-1-uber-eats-c4'

TEST_MODE = False #True
sender =  'godlikester@gmail.com'
message = "  Le 38eme games sont en Betcliiiiiic !!!! make monaaaay  "
if TEST_MODE:
    receivers = ['crowledj@tcd.ie'] 
else:
    receivers = ['godlikester@gmail.com', 'crowledj@tcd.ie', 'pauldarmas@gmail.com','raphael.courroux@hotmail.fr','theoletheo@hotmail.fr','alexandrecourroux@hotmail.com','scourroux@hotmail.com']    

date_time = str(datetime.datetime.today())
def check_for_final_ligue_1_rounds_odds():


    print('in betclic final round checker thingy.... \n \n')  

    betclic_new = True
    #unique_match_dict = {}
    loop_coumter = 0
    while True:
        
        loop_coumter += 1

        global date_time 
        print('\n next iteration -- @ time = ' + date_time + ' -- in ' + str(loop_coumter) + ' iteration -- boop ... \n \n' )
        try:    
            driver.get(site_betclci_soccer_link)
            driver.maximize_window()
        except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
            any_errors = False
            print("Error  caught in your BETCLIC final rpound detect. func.  -- initial list games frabber  :( .....")
            continue

        # grab the day/month/.year from today's date and store it
        todays_date = str(datetime.datetime.today()).split()[0] 
        
        date_time = str(datetime.datetime.today())

        driver.refresh()

        # todays_date.replace('-','/')
        # todays_date =  todays_date.split('-')

        # if len(date_str_spliton_dashes) >= 3:
        #     new_date_str = date_str_spliton_dashes[-1] + '-' + date_str_spliton_dashes[-2] + '-' + date_str_spliton_dashes[0]
        # else:
        #     print("Error in parsing todays date ! fix quick fpor d lads for final ligue one round thingy !! :(")
        #     continue
                                                  
    
        #ligue_1_finalrounds_list = driver.find_elements_by_xpath('//html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-competition/bcdk-vertical-scroller/div/div[2]/div/div/div')

        #ligue1_games_info_betclic   = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details/div')
        
        
        ## use this when generalizing leagues ...                   '/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-competition/bcdk-vertical-scroller/div/div[2]/div/div/div'
        #ligue1_games_info_betclic_2  = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/app-left-menu/div/app-sports-nav-bar/div/div[1]/app-block/div/div[2]')           # ligue1_games_info_betclic_1 = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details/div[1]/div')
        

        # # champs league link n web elements location
        # ligue1_games_info_betclic_champsL = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-competition/bcdk-vertical-scroller/div/div[2]/div/div')

        # #competition = compettition_
        # second_route = False

        # if not ligue1_games_info_betclic and not ligue1_games_info_betclic_1:
        #     second_route = True

        # ## A whole new branch of code - relating to a change I  noticed in Betclic page-parsing since 01/02/2021
        # if second_route:

        # ## !! Change this     
        #     gen_games_info_betclic = ligue1_games_info_betclic_1
            
        #     if LEAGUE_FLAG == 'Champions':

        #         gen_games_info_betclic = ligue1_games_info_betclic_champsL

        #     for panels in gen_games_info_betclic:

        #         try:
        #             games_per_panel = panels.find_elements_by_xpath('.//app-event/div/a/div/div')
        #         except StaleElementReferenceException:
        #             print(" StaleElementReferenceException Error in Betclic site -- when trying to grab  ..... ")
        #             continue  
        

        #center_scroller_element = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-all-offer/div/bcdk-vertical-scroller/div/div[2]/div/div/sports-events-event')
        try:               
            ligue_1_finalrounds_list = driver.find_elements_by_xpath('//html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-competition/bcdk-vertical-scroller/div/div[2]/div/div/div/sports-events-event')
            ligue_1_finalrounds_list2 = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-competition/div/sports-events-list/bcdk-vertical-scroller/div/div[2]/div/div/div')                          

            ligue_1_finalrounds_list2 = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-competition/div/sports-events-list/bcdk-vertical-scroller/div/div[2]/div/div/div')
                                                                  #'/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-competition/div/sports-events-list/bcdk-vertical-scroller/div/div[2]/div/div'
                                                                        
            ligue1_games_info_betclic   = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details/div')
            ## use this when generalizing leagues ...
            #ligue1_games_info_betclic_2  = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/app-left-menu/div/app-sports-nav-bar/div/div[1]/app-block/div/div[2]')    
            ligue1_games_info_betclic_1 = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details/div[1]/div')
        except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
            any_errors = False
            print("Error  caught in your BETCLIC final rpound detect. func.  -- initial list games frabber  :( .....")
            continue
        

        center_scroller_element_tag = driver.find_elements_by_tag_name('sports-events-event')
        # champs league link n web elements location
        #ligue1_games_info_betclic_champsL = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-competition/bcdk-vertical-scroller/div/div[2]/div/div')

        tag_web_element_one_too_deep_flag = False
        if not ligue_1_finalrounds_list:
            ligue_1_finalrounds_list = ligue_1_finalrounds_list2
            if not ligue_1_finalrounds_list2:
                ligue_1_finalrounds_list = center_scroller_element_tag
                tag_web_element_one_too_deep_flag = True
                if not center_scroller_element_tag:
                    ligue_1_finalrounds_list = ligue1_games_info_betclic
                    tag_web_element_one_too_deep_flag = False
                    if not  ligue1_games_info_betclic :
                        ligue_1_finalrounds_list =  ligue1_games_info_betclic_1
                        tag_web_element_one_too_deep_flag = False
        
        for games in ligue_1_finalrounds_list:

            if tag_web_element_one_too_deep_flag:
                game_event_info = games.find_element_by_xpath('.//a/div/sports-events-event-info')
            #game_event_info = games.find_element_by_xpath('a/div/sports-events-event-info')
            else:
                game_event_info = games.find_element_by_xpath('.//sports-events-event/a/div/sports-events-event-info')
            try:

                # if len(center_scroller_element) > num_pre_final_round_games:
                #     unique_match_dict[ tourny_name + players_names ]  = False
                #     #send_sms_alert(betclic, players_names, tourny_name) 
                
                date_str = game_event_info.text
                print('date of game is ' + date_str)

                if '23/05/2021' in date_str  and ( '2021-05-11' in todays_date or '2021-05-12' in todays_date or '2021-05-13' in todays_date or '2021-05-14' in todays_date or '2021-05-15' in todays_date  or '2021-05-16' in todays_date or '2021-05-17' in todays_date) :  
                    print('FOUND odds coming up !, sending sms to alert lads')
                    ret_val_of_ligue1round38_alert =  send_sms_alert_forfinal_round_ligue1() 
                    print('just sent sms , return value =  ' + str(ret_val_of_ligue1round38_alert) + ' now exitingf thw infinite loop and program ..')
                    fej = 0
                    return True

            except (KeyError,NoSuchElementException, StaleElementReferenceException, InvalidSessionIdException) as err:
                any_errors = False
                print("Error  caught in your BETCLIC final rpound detect. func.  -- keyError in team mapper  :( .....")
                continue

##  TODO: BETTER VERSION OF SCRAPING 

        # try:
        #     WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME,'sports-events-list')))
        #     tennis_games_per_panel = center_scroller_element.find_element_by_tag_name('sports-events-list')
        #     time.sleep(1)
        #     all_ligue1_games = tennis_games_per_panel.find_elements_by_tag_name('sports-events-levent')
        # except StaleElementReferenceException:
        #     print(" StaleElementReferenceException Error in Betclic site -- when trying to grab  ..... ")
        #     #exit(1)
        #     return False

        # for game in all_ligue1_games:

        #     game_event_info = game.find_element_by_xpath('.//a/div/sports-events-event-info')
        #     try:

        #         # if len(center_scroller_element) > num_pre_final_round_games:
        #         #     unique_match_dict[ tourny_name + players_names ]  = False
        #         #     #send_sms_alert(betclic, players_names, tourny_name) 
                
        #         date_str = game_event_info.text

        #         print('date of game is ' + date_str)

        #         if '23/05/2021' in date_str  and ( '2021-05-11' in todays_date or '2021-05-12' in todays_date ) :  

        #             try:
        #                 smtpObj = smtplib.SMTP_SSL("smtp.gmail.com",465)
        #                 smtpObj.login("godlikester@gmail.com", "Pollgorm1")
        #                 #smtpObj.login("keano16@dcrowleycodesols.com", "Pollgorm9")
        #                 smtpObj.sendmail(sender, receivers, message)         
        #                 print("Successfully sent email")
                        
        #                 #FP1 = open(surebets_Done_list_textfile,'a')
        #                 #FP1.write(message + '\n')
        #                 #FP1.close()

        #                 successFlag = True
        #             except SMTPException:
        #                 print("Error: unable to send email")
        #                 pass
        #             print('FOUND odds coming up !, sending sms to alert lads')
        #             #ret_val_of_ligue1round38_alert = send_sms_alert_forfinal_round_ligue1() 
        #             #print('just sent sms , return value =  ' + str(ret_val_of_ligue1round38_alert) + ' now exitingf thw infinite loop and program ..')
        #             #exit(1)

        #     except KeyError:
        #         any_errors = False
        #         print("Error  caught in your BETCLIC final rpound detect. func.  -- keyError in team mapper  :( .....")
        #         continue


    return True



if __name__ == '__main__':

    argv = sys.argv
    DEBUG_OUTPUT  = False
    
    #print(' len(argv)  = ' + str(len(argv) ))

    if 'football_ligue1_round38' in str(argv[-1]): 
        retval2 = check_for_final_ligue_1_rounds_odds() 

    elif 'tennis' in str(argv[-1]):    
        retval2 = check_for_tennis_value_bets() 

    else:
        print('issue with cmd line entry -- usage : "python ./sports_bettor_tennis.py tennis" or "python ./sports_bettor_tennis.py football_ligue1_round38"  please ...')
        exit(1)


    #schtake = 1000
    #retval2 = check_for_sure_bets(float(schtake)) #argv[1]))

## TEST OOIF SEND MAIL for gen sure

    #W_1 = 'Home team (1st team name on the betting card) to win'
    #W_2 = 'Away team (2nd team name on the betting card) to win'
    #D   = 'A draw between the team in the 90 minutes'
    #bookie_1 = unibet
    #bookie_2 = winimax
    #bookie_3 = betclic
    #bookie_one_outcome = W_1
    #bookie_2_outcome   = D
    #teamA = 'paris sg'
    #teamB = 'lille'
    #date  = 'janvier, 16  2020'
    #competition = 'ligue1' 

    #send_mail_alert_gen_socer_surebet(bookie_1,bookie_2,bookie_3,bookie_one_outcome, bookie_2_outcome,teamA,teamB,date,competition)

    # if len(argv) >= 2 :

    #     if len(argv) == 8 :

    #         retVal = odds_alert_system(oddType= int(argv[1]), expect_oddValue= float(argv[2]), teamA= argv[3], teamB= argv[4], date= argv[5], competition= argv[6], Bookie1_used= argv[7])

    #     elif  len(argv) == 2 and argv[-1] == 'tennis':

    #         retval2 = check_for_tennis_value_bets()

    #     elif  len(argv) == 2 and argv[-1] == 'ligue1_bets_appear':

    #         retval2 = check_for_final_ligue_1_rounds_odds() 

    #     else:

    #         #print("usage:  please indicate with  0 or a 1 in the first cmd line argument to the program wherether you wish to include debugging output prints in it's run or not; 0/1 corresponding to no/yes....")
    #         print("Usage : sportsbetAlertor_v1.py oddType (0 -home team win, 1 - a dra. 2 - away team win ) expect_oddValue teamA teamB competition Bookie1_used.    i.e 7 parameters on thye cmd line after the filename")
    #         print("Heres an Example --- sportsbetAlertor_v1.py  0 1.75  lyon  marseille  ligue1 Winamax")
    #         exit(1)
   
    # else:    
    #     #DEBUG_OUTPUT = bool(int(argv[1]))
    #     retval2 = check_for_tennis_value_bets() #'unibet','zebet','winimaxc','W', 'D','marseilles','nantes','28/11/2020','ligue 1 UberEats')





