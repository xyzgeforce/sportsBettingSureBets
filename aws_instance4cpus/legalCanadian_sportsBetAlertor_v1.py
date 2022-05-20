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
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException

from selenium.webdriver.support.ui import Select

from selenium.webdriver.chrome.options import Options
import itertools
import sys,os
#from scraper_api import ScraperAPIClient
import datetime, unidecode
import subprocess
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


# set aws CLI creds using boto here:
import boto3	
client = boto3.client('sns','ca-central-1')
#store Paul Darmas's number:
my_phone_number          = '0014372468105'
main_client_phone_number = '0033609590209'
courrouxbro1_client_phone_number = '0033647228992'
courrouxbro2client_phone_number  = '0033620858827'
# define global init 'surebet' condition value (note by default any bet will not be a surebet given its > 1.0)

sys.path.append('./')
from metaLeague_data import *

# define global init 'surebet' condition value (note by default any bet will not be a surebet given its > 1.0)
surebet_factor = 1.0
#cibstant initialised to False - for determining if they customer's expected odds are retrieved for alert system...
odd_are_found = False
TEST_MODE = False

#client = ScraperAPIClient('781fa06f6c29968fe2971fa6a90760dc')
#respondsr = client.get(url = "https://france-pari.fr/")
#print(result)
#text file with records of surebets already alerted for:

# if not TEST_MODE:
#     surebets_Done_list_textfile = './sure_bets_placed.txt'
#     fp1 = open(surebets_Done_list_textfile, "r")

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
    #print(' Surebet value = ' + str(total_iverse_odds_sum))

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


def return_surebet_vals(*argv, stake):  #odds_A, odds_B,stake):

    surebetStakes = []

    # !! NoTE : ive added a '100.0' factor into the calculations below to display to the lads in their emails

    for i,odds in enumerate(argv):

        if odds == 0.0 or surebet_factor == 0.0 :
            surebetStakes.append(1)
        else:    
            surebetStakes.append((1/surebet_factor)*(1/odds))
            #print('surebetStakes[' + str(i) + '] =  ' + str(surebetStakes[i]))

    return surebetStakes


## TODO : must generalize this and add file to code bundle
DRIVER_PATH = 'chromedriver' #the path where you have "chromedriver" file.

options = Options()
options.headless =  False #True
#options.LogLevel = False
options.add_argument("--window-size=1920,1200")
#options.add_argument("--LogLevel=0")
#options.add_argument("user-agent= 'Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41' ")
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_6) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.698.0 Safari/534.24'")
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH, service_args=["--verbose", "--log-path=D:\\qc1.log"])
    
def odds_alert_system(oddType=1,expect_oddValue=2.5,teamA='Liverpool',teamB='barcelone',date='Mercredi 25 Novembre',competition='Ligue des Champions',Bookie1_used='winmax', input_sports = ['soccer'], input_competitions = ['MLS']):

    global full_all_bookies_allLeagues_match_data, all_split_sites_data # ,all_srpaed_sites_data

    # init. copy data dict.
    all_split_sites_data_copy = {}
        
    Bookie1_used = Bookie1_used.lower()
    sub_strs_in_key = [competition.lower(),teamA.lower(),teamB.lower()] #,date.lower()]
    # search for game (and competition and date to ensure uniqueness) on ref. site:

    # initialize proxy count and create list of proxies from the prox generator
    PROXY_COUNTER = 0
    proxies = req_proxy.get_proxy_list()
    while(True):

        if PROXY_COUNTER == len(proxies) - 1:
            proxies = req_proxy.get_proxy_list()

        PROXY = proxies[PROXY_COUNTER].get_address()
        driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

        webdriver.DesiredCapabilities.CHROME['proxy']={
            "httpProxy":PROXY,
            "ftpProxy":PROXY,
            "sslProxy":PROXY,
            "proxyType":"MANUAL",
        }

        PROXY_COUNTER += 1
        # waitr a delay time to refresh sites parsings....
        #if  (not justParsed) :
        
        if parseSites(driver, input_sports, input_competitions): #all_srpaed_sites_data):
            pass

        ## !!! THIS PIECE OF CODE SEEMS TO BE BREAKING THE PROGRAM - CAUSING IT TO HAVE VERY UNDEFINED RUNTIME BEHAVIOUT ???     
        # if msvcrt.getch() == 'esc':
        #     print('Esc key pressed , stopping and exiting the constant Alert with odds function ....')
        #     break TODO

        #check if its changed or not - then dont need to redo sure bets checks if not
        if all_split_sites_data_copy == all_split_sites_data:
            #print('detected redundant dict odss info for games -- so parsing again and skipping the odd threshold check... also all_split_sites_data = ' + str(all_split_sites_data))
            continue

        for site_data in all_split_sites_data:

            for key in site_data.keys():
                if Bookie1_used in key:
                    #print('breaking as bookie used already..')
                    break
                
                # store the bookie's name so as to send onto Paul et al to double check & place the bet...
                bookie_name = key.split('_')[0]  
                truth_list_match_check_keys = [True for test_key in sub_strs_in_key if (test_key in key)]
                if len(truth_list_match_check_keys) == 3:
                    if truth_list_match_check_keys[0] and truth_list_match_check_keys[1] and truth_list_match_check_keys[2]:
                        
                # # check exact match for event -> i.e date,competition and two teams - in home/away order also for the necessary unique 'hit'
                # if all(x in key for x in sub_strs_in_key) :
                        if oddType == 0 and float(site_data[key][oddType]) > expect_oddValue:
                            send_mail_alert_odds_thresh(oddType,expect_oddValue, site_data[key][0], teamA, teamB, date, competition, bookie_name)
                        elif oddType and float(site_data[key][oddType]) > expect_oddValue:
                            send_mail_alert_odds_thresh(oddType,expect_oddValue, site_data[key][oddType], teamA, teamB, date, competition, bookie_name)  
                        else:
                            #print('issue with finding /checking the expected odd across all data and sites...')
                            return False


        #local copy in infinite loop to check if its changed or not - then dont need to redo sure bets checks if not
        all_split_sites_data_copy = all_split_sites_data

    return True

W_1 = 'Home team (1st team name on the betting card) to win'
W_2 = 'Away team (2nd team name on the betting card) to win'
D   = 'A draw between the team in the 90 minutes'
#L_1 = 'Home team (1st team name on the betting card) to lose'
#L_2 = 'Away team (2nd team name on the betting card) to lose'

## TEST wait time for after a non dict - data change
wait_time_idirNoChanges = random.randint(0,1)

def check_for_sure_bets(*args, input_sports, input_competitions):

    global all_split_sites_data, DEBUG_OUTPUT, globCounter

    # init. copy data dict.
    all_split_sites_data_copy = {}
    dont_recimpute_surebets = False  

    returnBetSizes = False
    stake_val      = 1.0  #(euro)  
    if len(args) > 0 :
        stake_val      = args[0]    
        returnBetSizes = True

    # initialize proxy count and create list of proxies from the prox generator
    PROXY_COUNTER = 0
    k = 33
    proxies = req_proxy.get_proxy_list()

    ## TEST
    proxies = proxies[:100]
    ##end test

    #initialize counters
    sure_bet_counter = 0
    total_time_parsing = 0.0
    globCounter=0
    dataDictChangdCounter = 0
    RAND_PROXY_JUMP = 3

    compettitions =  [ north_murica_links, all_premier_league_sites] #websites_ligue1_links]
    #else:
    sports =  ['soccer']
    if  input_sports:
        sports = input_sports    

    if  input_competitions: 
        compettitions =  input_competitions  

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
        
        #endtime_file = time.time()
        #print('time to get to parsing was = ' + str(endtime_file - strtime_file))
        #print('Click on the "esc" key @ any time to terminate this program and can then restart again any time you wish :) ......')
        # waitr a delay time to refresh sites parsings....
        start_parse = time.time() 

        start_full_parsingTimer = time.time()
        if parseSites(driver, input_sports, input_competitions): #all_srpaed_sites_data):
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

        # print('********************************************************************************print  ******************************************************************************** ')   
        # print(' ******************************************************************************** OLD Dict : ********************************************************************************')
       
        # print(str(all_split_sites_data_copy))
        # print(' ############################################################################### OLD Dict : FOINISHED   ###############################################################################')
        # print('lenght of old dict = ' + str(len(all_split_sites_data_copy)))
        
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
            #print('###############################################################################  Current Dict : ')
        
            # print(str(all_split_sites_data))
            # print(' ############################################################################### Current Dict FINISHED  ###############################################################################')
            # #print('new data dict. has been updated ...! :)')

    ## print average timers  parsings of each sites:
        #print('AVerage time to do cbet parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_cbet/globCounter))
        print('AVerage time to do unibet parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_unibet/globCounter))
        print('AVerage time to do france_pari parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_france_pari/globCounter))
        print('AVerage time to do winimax parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_winimax/globCounter))
        print('AVerage time to do betclic parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_betclic/globCounter))
        print('AVerage time to do parion parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_parionbet/globCounter))
        print('AVerage time to do pmu parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_pmu/globCounter))


        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)

        #local copy in infinite loop to check if its changed or not - then dont need to redo sure bets checks if not
        all_split_sites_data_copy = copy.deepcopy(all_split_sites_data)

        wait_time = random.randint(1,2)
        time.sleep(wait_time)   
        if len(all_split_sites_data) < 3 :
            print('*************************** Error - less than three bookies scrapped for games here ..., try again -- if this error persists raise a bug ******************************')
            #return False            
            continue

    #    /\ if (globCounter % 5) == 0:
        print('AVerage time to do parsings was = ' + str(total_time_parsing/globCounter)) 
        print('number of surebets found so far is = ' + str(sure_bet_counter))    

        if not dont_recimpute_surebets :
            start_surebet_timer = time.time()
            index = 0    
            ## TODO  - a biggg TODO  -- the following is just the combos of 3 but will also need to cater for when only 2 bookies are involved in a footy surebet :
            # i.e 1 bookie has the needed home win and draw odd and the other the awat=y win and also vice versa.
            #redundancy_bet_checklist = {}

            checxking_surebet_counts = 0
            for subset in itertools.combinations(all_split_sites_data, 3):  
                #filter unique games across dicts/sites using the key from a fixed one ....  
                #                
                subsetList = list(subset)         
                #print('combination ' + str(index) + '  -- has ordered bookies as  -- ' + str(subsetList)) 
                index += 1 

                if ( len(subsetList) >= 3):
                    second_bookie_keys = subsetList[1].keys() 
                    third_bookie_keys  = subsetList[2].keys()         

                #local_bookies_list = []
                bookie_2 = ''
                for keys in second_bookie_keys:
                    bookie_2 = keys.split('_')[0]
                    #local_bookies_list.append(bookie_2)
                    break

                bookie_3 = ''        
                for keys in third_bookie_keys:
                    bookie_3 = keys.split('_')[0]
                    #local_bookies_list.append(bookie_3)
                    break

                if len(subsetList) >= 3:    
                    for key in subsetList[0]:    

                        key_str_split_by_underscore = key.split('_')    
                        if len(key_str_split_by_underscore) >= 4:

                            bookie_1 = key_str_split_by_underscore[0]
                            #local_bookies_list.append(bookie_1)
                            date_1 =   key_str_split_by_underscore[1]
                            competition_1 = key_str_split_by_underscore[2]
                            sub_key_str_split_by_underscore = key_str_split_by_underscore[-1].split(' - ')
                            sub_key_str_split_by_space = key_str_split_by_underscore[-1].split(' ')
                            sub_key_str_split_by_vs = key_str_split_by_underscore[-1].split(' vs ')

                            if len(sub_key_str_split_by_underscore) != 2:
                                if len(sub_key_str_split_by_space) != 2:
                                    sub_key_str_split_by_works = sub_key_str_split_by_vs
                                else:
                                    sub_key_str_split_by_works = sub_key_str_split_by_space    
                            else:
                                sub_key_str_split_by_works = sub_key_str_split_by_underscore        

                            if len(sub_key_str_split_by_works) >= 2:
                                teamA_1 =  sub_key_str_split_by_works[0]
                                teamB_1 =  sub_key_str_split_by_works[1]

                        #if bookie_1 == betclic and bookie_2 == winimax and bookie_3 == 'paris-sportifs.pmu':
                        #    print('team A and team B are: ->' + str(teamA_1) + '<-  ->' + str(teamB_1) + '<-')        

                        unique_math_identifiers = [competition_1,teamA_1,teamB_1]   # [date_1,competition_1,teamA_1,teamB_1]

                        ## leave this redundancy check shit till next version !!
                        # create unique keys to prevent surebets beiung redyndant acros the bookies triplets 
                        #local_bookies_list.sort()
                        #bookie_surebetsCombo_uniq_strs_list = [x + unique_math_identifiers[i] for i,x in enumerate(local_bookies_list)]
                        #unique_key_string = ''.join(y for y in bookie_surebetsCombo_uniq_strs_list)

                        #redundancy_bet_checklist[unique_key_string] = redundancy_bet_checklist.get(unique_key_string,0) + 1
                        #if redundancy_bet_checklist[unique_key_string] > 1:
                        #    continue

                        if DEBUG_OUTPUT :
                            print('site_data key = ' + str(key) )

                        matching_keys2_list = []
                        matching_keys3_list = []
                        key_bookkie2 = 'void2'
                        key_bookkie3 = 'void3'
                        truth_list_subStrKeysDict2 = [matching_keys2_list.append(key2) for key2,val in subsetList[1].items() if (unique_math_identifiers[0] in key2 and unique_math_identifiers[1] in key2 and unique_math_identifiers[2] in key2)]
                        
                        #if truth_list_subStrKeysDict2:
                        #    print(truth_list_subStrKeysDict2[0])
                        if len(truth_list_subStrKeysDict2) > 0:
                            key_bookkie2 = matching_keys2_list[0] #truth_list_subStrKeysDict2[0]
                        #else:
                        #    GAN = 'nah' 

                        truth_list_subStrKeysDict3 = [matching_keys3_list.append(key3) for key3,val in subsetList[2].items() if (unique_math_identifiers[0] in key3 and unique_math_identifiers[1] in key3 and unique_math_identifiers[2] in key3)]
                        if len(truth_list_subStrKeysDict3) > 0 :
                            key_bookkie3 = matching_keys3_list[0] # truth_list_subStrKeysDict3[0]   
                        #else:
                        #    GAN = 'nah'    

                        #print(' Bookies 1 is ' + str(bookie_1) + ' Bookies 2 is ' + str(bookie_2) + ' -- and bookie_3 is ' + str(bookie_3)) 
                        #print(' teams  are : ->' + str(teamA_1) +  '<-  and  ->' + str(teamB_1) + '<-')
                        #print('keys, in order, are : ->' + str(key) + '<-,  ->' + str(key_bookkie2) + '<-,  ->' + str(key_bookkie3) + '<-')        
                        ## check i stest for now here... !! re - undo former statement test after    
                        if (truth_list_subStrKeysDict2 and not (find_substring(bookie_1,bookie_2) )) and (truth_list_subStrKeysDict3 and not ( find_substring(bookie_1,bookie_3))):
                            
                            checxking_surebet_counts += 6
                            #print('Checking for surebets -- idir teams : ' + str(teamA_1) +  '  and  ' + str(teamB_1)   + '.... checking_surebet_counts =  ' + str(checxking_surebet_counts)) 
                            #print('Bookies in order of odds are : ' + bookie_1  + bookie_2 + bookie_3 + '\n')
                            
                            #test for mail with %s -- this ensures a surebet is found !;)
                            #subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2] = 1.1,7.5,25     #8.0, 2.0, 4.0
                            #subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2] = 15.1, 1.75, 2.5 

                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][0], subsetList[1][key_bookkie2][1], subsetList[2][key_bookkie3][2]


                            #print('\n \n')

                            #print(' Bookies 1 is ' + str(bookie_1) + ' Bookies 2 is ' + str(bookie_2) + ' -- and bookie_3 is ' + str(bookie_3)) 
                            #print(' teams  are : ->' + str(teamA_1) +  '<-  and  ->' + str(teamB_1) + '<-')
                            #print('keys, in order, are : ->' + str(key) + '<-,  ->' + str(key_bookkie2) + '<-,  ->' + str(key_bookkie3) + '<-')  

                            #print('home_win_odds = ' + str(home_win_odds) + ', draw_odds = ' +  str(draw_odds) + ' and away_win_odds = ' + str(away_win_odds))

                            #print('\n \n')

                            if  check_is_surebet(home_win_odds, draw_odds, away_win_odds):  # encode bookie outcomes as 'W','D','L' wrt to the 1st team in the match descrpt. , i.e The 'hometeam' 
                                
                                # if  returnBetSizes:
                                sure_bet_counter += 1
                                print('***********************************************************************************************************************************************************************************')   
                                print('*****************************************************************************  SURE BET FOUND !  :)   *****************************************************************************')   
                                print('***********************************************************************************************************************************************************************************')   
                                #     #surebet_odds_list = [subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2]]                                 
                                #     #get_surebet_factor(surebet_odds_list) #  odds_A, odds_B):
                                #     #sure_betsto_place = return_surebet_vals(surebet_odds_list, stake_val)
                                #     send_mail_alert_gen_socer_surebet(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1,sure_betsto_place)
                                # else:      
                                #     send_mail_alert_gen_socer_surebet(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1)
                                print('Odds comboo is')
                                print(W_1)
                                print(D)
                                ## as odds are 0,1 from 1st two bookies

                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                if surebet_factor != 0.0 and surebet_factor != 0:
                                    actual_profit = (stake)/surebet_factor
                                else:
                                    actual_profit = 100.0                                   
                                ## calc. % profit for the lads:
                                #profit = 1.0 - (1/subsetList[0][key][0] + 1/subsetList[1][key_bookkie2][1] + 1/subsetList[2][key_bookkie3][2]) 
                                #184 45238262
                                #get_surebet_factor(subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2])
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)

                                #avg_profit = round(stake*(-subsetList[0][key][0]*proportionsABC_list[0]  + subsetList[1][key_bookkie2][1]*proportionsABC_list[1] + subsetList[2][key_bookkie3][2]*proportionsABC_list[2]),3)
                                #profit_2 = round(stake*( subsetList[0][key][0]*proportionsABC_list[0]  - subsetList[1][key_bookkie2][1]*proportionsABC_list[1] + subsetList[2][key_bookkie3][2]*proportionsABC_list[2]),3)
                                #profit_3 = round(stake*( subsetList[0][key][0]*proportionsABC_list[0]  + subsetList[1][key_bookkie2][1]*proportionsABC_list[1] - subsetList[2][key_bookkie3][2]*proportionsABC_list[2]),3)
                                #avg_profit = round((1/3)*(profit_1 + profit_2 + profit_3),3)

                                proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, actual_profit, home_win_odds, draw_odds, away_win_odds)
                                #print('Bet (sure)  kombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 'in the bookie ->' + bookie_1 + ' the draw at odds = '  + str(subsetList[1][key_bookkie2][1]) + ' in bookie ' + str(bookie_2) + ' and finally the other teams win odds @ ' + str(subsetList[2][key_bookkie3][2]) + str(bookie_3) + '  \n')
                                # these continues will avoid the sitch of 'same' surebet (swapoed one) being mailed out
                                #return_surebet_vals([subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2]],1000)
                                continue

                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][0],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][1]
                            if  check_is_surebet(home_win_odds, draw_odds, away_win_odds):

                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE BET FOUND !  :)   *****************************************************************************') 
                                # given the last indices are 2,1,0
                                # W_1,W_2
                                ## calc. % profit for the lads:
                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                if surebet_factor != 0.0 and surebet_factor != 0:
                                    actual_profit = (stake)/surebet_factor
                                else:
                                    actual_profit = 100.0 
                                
                                #get_surebet_factor(subsetList[0][key][0],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][1])
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)

                                #vg_profit = round((1/3)*(profit_1 + profit_2 + profit_3),3)                                

                                proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3,W_1,W_2,teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, actual_profit, home_win_odds, draw_odds, away_win_odds)
                                #print('Bet (sure)  sombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 'in the bookie ->' + bookie_1 + ' the away win at odds = '  + str(subsetList[1][key_bookkie2][2]) + ' in bookie ' + str(bookie_2) + ' and finally the draw odds @ ' + str(subsetList[2][key_bookkie3][1]) + str(bookie_3) + '  \n')
                                #return_surebet_vals([subsetList[0][key][0],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][1]],1000)
                                continue

                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][1],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][2]
                            if  check_is_surebet(home_win_odds, draw_odds, away_win_odds):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE-BET FOUND !  :)   *****************************************************************************') 
                                # D,W_1
                                # as final odds indices in first 2 bookies here are : 1,0 respectively
                                stake = 100.0
                             
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                if surebet_factor != 0.0 and surebet_factor != 0:
                                    actual_profit = (stake)/surebet_factor
                                else:
                                    actual_profit = 100.0
                                ## calc. % profit for the lads:
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)

                                proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3, D, W_1, teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, actual_profit, home_win_odds, draw_odds, away_win_odds) 

                                continue
                            home_win_odds, draw_odds, away_win_odds =  subsetList[0][key][1], subsetList[1][key_bookkie2][2] ,subsetList[2][key_bookkie3][0]
                            if  check_is_surebet(home_win_odds, draw_odds, away_win_odds):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE-BET FOUND !  :)   *****************************************************************************') 
                                
                                stake = 100.0
    
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                if surebet_factor != 0.0 and surebet_factor != 0:
                                    actual_profit = (stake)/surebet_factor
                                else:
                                    actual_profit = 100.0
                                #profit = 1.0 - (1/subsetList[0][key][1] + 1/subsetList[1][key_bookkie2][2] + 1/subsetList[2][key_bookkie3][0])
                                #given the last indices are 2,1,0
                                # D,W_2
                                #1, 2    
                                #get_surebet_factor(subsetList[0][key][1],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][0])
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds, stake = stake)
                                
                                proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3,D , W_2 ,teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, actual_profit, home_win_odds, draw_odds, away_win_odds)
                                #return_surebet_vals([subsetList[0][key][1],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][0]],1000)
                                continue

                            #print('Odds youre checking are  =  ' + str(W_2) + ' = ' + str(subsetList[0][key][2]))
                            #print('   -- and  --  ' + str(W_1) + ' = ' + str(subsetList[1][key_bookkie2][0]))
                            #print('   -- and  --  ' + str(D) + ' = '   + str(subsetList[2][key_bookkie3][1]))
                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][2],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][1]
                            if  check_is_surebet(home_win_odds, draw_odds, away_win_odds):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SUREBET FOUND !  :)   *****************************************************************************') 
                                # given the last indices are 2,1,0
                                # W_2,W_1
                                # 2,0
                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                if surebet_factor != 0.0 and surebet_factor != 0:
                                    actual_profit = (stake)/surebet_factor
                                else:
                                    actual_profit = 100.0
                                #get_surebet_factor(subsetList[0][key][2],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][1])
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)

                                proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3, W_2, W_1, teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, actual_profit, home_win_odds, draw_odds, away_win_odds)  
                                #print('Bet (sure)  combo just found has the away team ' +  teamB_1  + ' win odds at ' + str(subsetList[0][key][2]) + 'in the bookie ->' + bookie_1 + ' the home team -> ' + teamA_1  +  '<- win at odds = '  + str(subsetList[1][key_bookkie2][0]) + ' in bookie ' + str(bookie_2) + ' and finally the draw odds @ ' +  str(subsetList[2][key_bookkie3][1]) + ' in the bookies ->' + str(bookie_3) + '  \n') 
                                #return_surebet_vals([subsetList[0][key][2],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][1]],1000)
                                continue                         

                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][2],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][0]
                            if  check_is_surebet(home_win_odds, draw_odds, away_win_odds):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SUREBET FOUND !  :)   *************************0****************************************************')                                 
                                
                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                if surebet_factor != 0.0 and surebet_factor != 0:
                                    actual_profit = (stake)/surebet_factor
                                else:
                                    actual_profit = 100.0

                                # W_2,D

                                #get_surebet_factor(subsetList[0][key][2],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][0])
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)

                                #avg_profit = round(stake*(-subsetList[0][key][2]*proportionsABC_list[0]  + subsetList[1][key_bookkie2][1]*proportionsABC_list[1] + subsetList[2][key_bookkie3][0]*proportionsABC_list[2]),3)

                                proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 , bookie_3, W_2, D, teamA_1, teamB_1, date, competition_1,proportionsABC_listRnd, actual_profit, home_win_odds, draw_odds, away_win_odds)    
                                #return_surebet_vals([subsetList[0][key][2],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][0]],1000)
                                continue  
                else:
                    print("Not enough bookies scraped correctly to look for 3 - way surebets...")
            print('NO. surebets possibilities checked = ' + str(checxking_surebet_counts))        
        if not dont_recimpute_surebets:
            end_surebet_timer = time.time()
            print("Time taken to just check for surebets besides parsing = " + str(end_surebet_timer - start_surebet_timer))

    return True

## TODO :
# def try_catch_function():
#     exceptionBool = False

#     return exceptionBool

#if only soing 2 - way sure bet , then oddDraw can be set to -1 and used as such when read in here
def send_mail_alert_odds_thresh(win_lose_or_draw,expect_oddB,actualOdd,teamA,teamB,date,competition,bookiesNameEventB):

    global DEBUG_OUTPUT
    successFlag = False
    sender = 'godlikester@gmail.com'
    receivers = ['crowledj@tcd.ie','pauldarmas@gmail.com','raphael.courroux@hotmail.fr','theoletheo@hotmail.fr','alexandrecourroux@hotmail.com']

    # message = """From: From Person <from@fromdomain.com>
    # To: To Person <to@todomain.com>
    # Subject: SMTP e-mail test

    # The is an Alert to tell you that a three-way soccer sure bet exists between --""" + str(teamA) + """ and  """ + str(teamB) + """  in the event """ + str(competition) + """  \
    # on the date  """ + str(date) + """  the bet will involve placing a bet on """ + str(bookie_one_outcome) + """  in the bookies - """ + str(bookie_1) + """ and on the outcome """ \
    # + str(bookie_2_outcome) + """ in the """ + str(bookie_2) +  """ bookie and final 3rd bet left in  """ + str(bookie_3)

    bookieTeamA = ""
    bookieTeamB = ""
    bookieDraw  = ""

    if "Home team " in bookie_one_outcome:
        bookieTeamA = bookie_1
    elif  "Away team " in bookie_one_outcome:
        bookieTeamB = bookie_1  
    else:
        bookieDraw = bookie_1      
   
    if "Home team " in bookie_2_outcome:
        bookieTeamA = bookie_2
    elif  "Away team " in bookie_2_outcome:
        bookieTeamB = bookie_2  
    else:
        bookieDraw = bookie_2


    if  bookieTeamA == "":
        bookieTeamA = bookie_3

    elif bookieTeamB == "":
        bookieTeamB = bookie_3     

    else:
        bookieDraw = bookie_3 


    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    Surebet Alert 
      
    Event: """ + str(competition) + """
    Date: """ + str(date) + """
    teamA: """ + str(teamA) + """
    teamB: """ + str(teamB) + """

    bookieTeamA: """ + str(bookieTeamA) + """
    bookieDraw: """  + str(bookieDraw) + """
    bookieTeamB: """ + str(bookieTeamB) 

    print(' ********************   message = ' + message)
    print(' ******************** ')

    try:
        smtpObj = smtplib.SMTP_SSL("smtp.gmail.com",465)
        smtpObj.login("godlikester@gmail.com", "Pollgorm1")
        smtpObj.sendmail(sender, receivers, message)     
        
        # Fp1 = open(surebets_Done_list_textfile,'a')
        # Fp1.write(message + '  ' + date + '\n')
        # Fp1.close()

        if DEBUG_OUTPUT :
            print("Successfully sent email")

        successFlag = True
    except SMTPException:
        print("Error: unable to send email")
        pass

    return successFlag

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

    if Profit > 100.5:
        try:
            print('trying to send texts - first mine ')
            client.publish(PhoneNumber=main_client_phone_number,Message=message)
            print('tried already to send to  mine -- now the french lads... ')
            client.publish(PhoneNumber=my_phone_number,Message=message)
            client.publish(PhoneNumber=courrouxbro1_client_phone_number,Message=message)
            client.publish(PhoneNumber=courrouxbro2client_phone_number,Message=message)
        except err as e:#SMTPException:
            print("Error: unable to send textsi - error is ->" + str(e))
            pass
        try:
            smtpObj = smtplib.SMTP_SSL("smtp.gmail.com",465)
            smtpObj.login("godlikester@gmail.com", "Pollgorm1")
            #smtpObj.login("keano16@dcrowleycodesols.com", "Pollgorm9")
            smtpObj.sendmail(sender, receivers, message)         
            print("Successfully sent email")

            FP1 = open(surebets_Done_list_textfile,'a')
            FP1.write(message + '\n')
            FP1.close()

            successFlag = True
        except SMTPException:
            print("Error: unable to send email")
            pass


    return successFlag, [bookieTeamA,bookieDraw, bookieTeamB], [proportions_list_win, proportions_list_draw, proportions_list_lose], [winOdd, drawOdd, loseOdd]  


def send_mail_alert_gen_socer_surebet(bookie_1,bookie_2,bookie_3,bookie_one_outcome, bookie_2_outcome,teamA,teamB,date,competition):

    global DEBUG_OUTPUT
    successFlag = False
    sender = 'godlikester@gmail.com'
    receivers = ['crowledj@tcd.ie','pauldarmas@gmail.com','raphael.courroux@hotmail.fr','theoletheo@hotmail.fr','alexandrecourroux@hotmail.com','scourroux@hotmail.com']

    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test"""

    bookieTeamA = ""
    bookieTeamB = ""
    bookieDraw  = ""

    if "Home team " in bookie_one_outcome:
        bookieTeamA = bookie_1
    elif  "Away team " in bookie_one_outcome:
        bookieTeamB = bookie_1  
    else:
        bookieDraw = bookie_1      
   

    if "Home team " in bookie_2_outcome:
        bookieTeamA = bookie_2
    elif  "Away team " in bookie_2_outcome:
        bookieTeamB = bookie_2  
    else:
        bookieDraw = bookie_2


    if  not bookieTeamA :
        bookieTeamA = bookie_3

    elif not bookieTeamB :
        bookieTeamB = bookie_3     

    else:
        bookieDraw = bookie_3 


    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    Surebet Alert 
      
    Event: """ + str(competition) + """
    Date: """ + str(date) + """
    teamA: """ + str(teamA) + """
    teamB: """ + str(teamB) + """

    bookieTeamA: """ + str(bookieTeamA) + """
    bookieDraw: """  + str(bookieDraw) + """
    bookieTeamB: """ + str(bookieTeamB)

    print(' ********************   message = ' + message)
    print(' ******************** ')
    if message in list_mailed_surebets:
        print('sureBet already found -- dontt re-mail ')
        return successFlag

    try:
        smtpObj = smtplib.SMTP_SSL("smtp.gmail.com",465)
        smtpObj.login("godlikester@gmail.com", "Pollgorm1")
        smtpObj.sendmail(sender, receivers, message)         
        print("Successfully sent email")

        FP1 = open(surebets_Done_list_textfile,'a')
        FP1.write(message + '\n')
        FP1.close()

        successFlag = True
    except SMTPException:
        print("Error: unable to send email")
        pass

    return successFlag

tot_parionbet   = 0.0
tot_france_pari = 0.0
tot_winimax     = 0.0
tot_cbet        = 0.0
tot_pmu         = 0.0
tot_unibet      = 0.0
tot_betclic     = 0.0

league_or_cup_name = "MLs"
compettition = "reg_competition"
def parseSites(driver, input_sports, input_competitions ): 

    start_mainParserTimer = time.time()
    global websites_champs_league_links, compettition, date, refernce_champ_league_gamesDict, full_all_bookies_allLeagues_match_data, DEBUG_OUTPUT, all_split_sites_data, tot_parionbet , tot_france_pari, tot_winimax, tot_cbet, tot_pmu, tot_unibet, tot_betclic    

    # reset full league dict so as not to keep appending to it below
    full_all_bookies_allLeagues_match_data.clear()
    any_errors = True      

    global compettition
################# ***********************################# ***********************################# ***********************################# ***********************################# ***********************
################# ***************************                            LIGUE 1 GAMES                      *******************************########################################
################# ***********************################# ***********************################# ***********************################# ***********************################# ***********************

    LEAGUE_FLAG = 'france'

    wait_time12 = random.randint(1,2)
    #time.sleep(wait_time12)  
    #websites_ligue1_links.append('https://www.zebet.fr/fr/lives')g
    #websites_ligue1_links.append('https://www.france-pari.fr/lives')

    #compettitions =  [ websites_europa_league_links ]  # websites_champs_league_links ] #, bundesliga_links]

    # websites_champs_league_links
     # websites_europa_league_links,  #
    compettitions =  [ ] #north_murica_links, all_premier_league_sites] #websites_ligue1_links]
    #else:
    # sports =  ['soccer']
    # input_sports = [input_sports]
    if  input_sports:
        sports = input_sports    

    #if  input_competitions: 
    #    compettitions =  input_competitions     


    ## default for teams mapping dict. is Ligue 1 :
    # team_names_maping = comon_TeamNames_mapper
    # if websites_champs_league_links in compettitions or websites_europa_league_links in compettitions :

    global league_or_cup_name
    for sport in input_sports:
        index = 1
        for competetits in input_competitions:

            competetits = competetits.lower()
            if 'mls' in competetits:
                compettitions.append(north_murica_links)
                league_or_cup_name = "MLS"

            if 'epl' in competetits or 'premier league' in competetits or 'premiership' in competetits:
                compettitions.append(epl_links)
                league_or_cup_name = "English Premier league"

            if 'la liga' in competetits:
                compettitions.append(all_la_liga_sites)
                league_or_cup_name = "la Liga"
                
            if 'bundesliga' in competetits:
                compettitions.append(bundesliga_links)
                league_or_cup_name = "bundesliga"
                
            if 'serie a' in competetits:
                compettitions.append(serie_a_links)
                league_or_cup_name = "Serie A"
                
            if 'ligue-1' in competetits:
                compettitions.append(websites_ligue1_links)
                league_or_cup_name = "Ligue1"
                
            if not compettitions :
                compettitions=  [north_murica_links, all_premier_league_sites] #websites_ligue1_links]
                league_or_cup_name = "MLS"

            combined_leagues_maping = {}
            #comon_TeamNames_mapper = {'stade brestois': 'brest', 'brestois': 'brest', 'olympiue lyonnais':'lyon', 'olympiue lyon':'lyon','paris saint-germain':'psg','paris saint germain':'psg','paris st-germain':'psg','paris st germain':'psg'
            combined_leagues_maping.update( comon_TeamNames_mapper )
            combined_leagues_maping.update( EPL_commonName_mapping )
            combined_leagues_maping.update( xtra_champ_league_maping )
            combined_leagues_maping.update( la_Liga_commonName_mapping )
            combined_leagues_maping.update( comon_team_maping_europa )
            combined_leagues_maping.update( serie_a_commonName_mapping )
            combined_leagues_maping.update( bundesliga_commonName_mapping )

            team_names_maping = combined_leagues_maping

            print('team_names_maping = ' + str(team_names_maping))

            for indx, compettition in enumerate(compettitions):

                # if compettition:
                #     compettition_link1 = compettition[0].lower()

                # if compettition == websites_ligue1_links:
                #     # 'ligue1' in compettition_link1 or  'ligue-1' in compettition_link1 or  'ligue_1' in compettition_link1 or  'ligue 1' in compettition_link1 : # == websites_ligue1_links:
                #     LEAGUE_FLAG = 'french'
                #     print('parsing the ' + str(LEAGUE_FLAG ) + ' league SONS :)... ')
                #     compettition = 'Ligue 1'

                # elif compettition == all_premier_league_sites:
                #     # 'premier-league' in compettition_link1 or 'premier league' in compettition_link1 or 'premierleague' in compettition_link1 or 'premier_league' in compettition_link1:  # == websites_ligue1_links:
                #     LEAGUE_FLAG = 'english prem. league ... '
                #     print('parsing the ' + str(LEAGUE_FLAG ) + ' league SONS :)... ') 
                #     compettition = 'Premier League'


                # elif compettition == all_la_liga_sites:
                #     # 'la liga' in compettition_link1 or 'primera liga' in compettition_link1 or 'la-liga' in compettition_link1 or  'la_liga' in compettition_link1 or  'liga-primera' in compettition_link1  or  'primera-liga' in \
                #     # compettition_link1 or  'espagne' in compettition_link1 or  'laliga' in compettition_link1 : #== websites_ligue1_links:
                #     LEAGUE_FLAG = 'spanish league - La liga ... '    
                #     print('parsing the ' + str(LEAGUE_FLAG ) + ' league SONS :)... ')
                #     compettition = 'La Liga'

                # elif compettition == serie_a_links:
                #     # 'serie a' in compettition_link1 or 'seriea' in compettition_link1 or 'serie-a' in compettition_link1 or 'italie' in compettition_link1 or 'serie_a' in compettition_link1: # == websites_ligue1_links:
                #     LEAGUE_FLAG = 'Italian league -- Serie A ...'   
                #     print('parsing the ' + str(LEAGUE_FLAG ) + ' league SONS :)... ') 
                #     compettition = 'Serie A'

                # elif compettition == bundesliga_links:
                #     # 'bundesliga' in compettition_link1: # == websites_ligue1_links:
                #     LEAGUE_FLAG = 'German top league -- Bundeslagi BAUSh Bush ! ... ' 
                #     compettition = 'Bundesliga'
                #     print('parsing the ' + str(LEAGUE_FLAG ) + ' league SONS :)... ')   

                # elif compettition == websites_champs_league_links: #'champs_league' in compettition_link1 or 'champions' in compettition_link1:
                #     LEAGUE_FLAG = 'Champions' 
                #     print('parsing the ' + str(LEAGUE_FLAG ) + ' league SONS :)... ')  
                #     compettition = 'Ligue des Champions' 

                # elif compettition == websites_europa_league_links:
                #     # 'europa' in compettition_link1:
                #     LEAGUE_FLAG = 'Europa' 
                #     print('parsing the ' + str(LEAGUE_FLAG ) + ' league SONS :)... ')   
                #     compettition = 'Europa League'

                # elif compettition == north_murica_links :
                #     # 'europa' in compettition_link1:
                #     LEAGUE_FLAG = 'MLS' 
                #     print('parsing the ' + str(LEAGUE_FLAG ) + ' league SONS :)... ')   
                #     compettition = 'MLS East/west Conference.. '            

                # else:
                #     print('league not found in compettitions list...')
                #     compettition = 'Ligue 1'
                #     continue                

                for i,sites in enumerate(compettition):
                    
                    wait_time = random.randint(1,2)*random.random()
                    time.sleep(wait_time)  
                    #begin = timeit.timeit()  
                    #try:
                    print(sites)
                    # try:
                    #     driver.get(sites)
                    # except StaleElementReferenceException:
                    #     print(" StaleElementReferenceException Error in Betclic site -- when trying to grab  ..... ")
                    #     continue 

                    #if 

                            
                    #except NameError:
                    #    print(" generic Error  trying to pick up a site with the driver - line 979 ..... ")
                    #    continue

                    #finish = timeit.timeit()
                    #compettition_ = 'Europa League'


                    start_betclic = time.time()            
                    if  betclic in sites :
                        print('in betclic ' +  league_or_cup_name  + ' pre-match parsing .... \n \n')  

                        # /html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-compettition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details  
                                                                                
                        ligue1_games_info_betclic   = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-compettition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details/div')
                        ## use this when generalizing leagues ...
                        #ligue1_games_info_betclic_2  = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/app-left-menu/div/app-sports-nav-bar/div/div[1]/app-block/div/div[2]')    
                        ligue1_games_info_betclic_1 = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-compettition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details/div[1]/div')
                        
                        # champs league link n web elements location
                        ligue1_games_info_betclic_champsL = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-compettition/bcdk-vertical-scroller/div/div[2]/div/div')
                        ligue1_games_info_betclic_champsL2 = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-compettition/bcdk-vertical-scroller/div/div[2]/div/div/div')

                        ## TODO : need to actually make call into zebet champ league page to get champ_league_games_nested_gamesinfo_zebet:
                        #for matches in  ligue1_games_infozebet:
                        #parts1 = ligue1_games_info_betclic[0].text.split('+')

                        #compettition = compettition_
                        second_route = False

                        if not ligue1_games_info_betclic and not ligue1_games_info_betclic_1:
                            second_route = True

                        ## A whole new branch of code - relating to a change I  noticed in Betclic page-parsing since 01/02/2021
                        if second_route:

                        ## !! Change this     
                            gen_games_info_betclic = ligue1_games_info_betclic_1
                            
                            if LEAGUE_FLAG == 'Champions':

                                gen_games_info_betclic = ligue1_games_info_betclic_champsL

                                if not gen_games_info_betclic:

                                    gen_games_info_betclic = ligue1_games_info_betclic_champsL2

                                    
                                    if not gen_games_info_betclic:

                                        gen_games_info_betclic = ligue1_games_info_betclic_champsL2

                            elif LEAGUE_FLAG == 'Europa':
                                gen_games_info_betclic = ligue1_games_info_betclic_champsL2

                            else:
                                print('Have not encountered any known league in Betclic parsing')    


                            for panels in gen_games_info_betclic:
                                try:
                                    games_per_panel = panels.find_elements_by_xpath('.//app-event/div/a/div/div')
                                except StaleElementReferenceException:
                                    print(" StaleElementReferenceException Error in Betclic site -- when trying to grab  ..... ")
                                    continue  

                                ## commenting out this for now - but nee3d to retry as its proper way to do it..

                                # for matchs in  games_per_panel:
                                #     date = str(datetime.datetime.today()).split()[0] 


                                        ## Live string needs another branch to handle - diff indices for teams and odds as per 'match' string then being :
                                        # ®\n37' - 1ère  mt\bordeaux\n1 - 1\nlorient\nrésultat du match\nbord\neaux\n2,15\nn\nul\n2,35\nlor\nient\n3,15\nquelle équipe marquera le but 3 ?\nbord\neaux\n1,75\npas de\n but\n4,10\nlor\nient\n2,25\n67\nparis\n"
                                try:                       
                                    infos_per_matches = gen_games_info_betclic[0].text.split('Ligue des Champions')

                                    if not infos_per_matches:
                                        infos_per_matches = gen_games_info_betclic[0].text.split('Ligue Europa')

                                except StaleElementReferenceException:
                                    print(" StaleElementReferenceException Error in Betclic site -- when trying to grab  ..... ")
                                    continue

                                if len(infos_per_matches) >= 1 :

                                    ## !!! LIVE games change to be done as swmn here...

                                    ## Live string needs another branch to handle - diff indices for teams and odds as per 'match' string then being :
                                    # ®\n37' - 1ère  mt\bordeaux\n1 - 1\nlorient\nrésultat du match\nbord\neaux\n2,15\nn\nul\n2,35\nlor\nient\n3,15\nquelle équipe marquera le but 3 ?\nbord\neaux\n1,75\npas de\n but\n4,10\nlor\nient\n2,25\n67\nparis\n"

                                    matches = infos_per_matches[0].split('Ligue Europa')

                                    for indxs,stuffs in enumerate(matches): 

                                        time.sleep(wait_time12)
                                        if len(stuffs) < 2 or '\n' not in stuffs:
                                            continue

                                        info_per_match = stuffs.split('\n')
                                        try:
                                            teams = team_names_maping[unidecode.unidecode(info_per_match[1].lower().strip())] +  '-' +   team_names_maping[unidecode.unidecode(info_per_match[3].lower().strip())]
                                        except KeyError:
                                            any_errors = False
                                            print("Error  caught in your BETCLIC parse func.  -- keyError in team mapper  :( .....")
                                            pass

                                        try:
                                            teams = team_names_maping[unidecode.unidecode(info_per_match[2].lower().strip())] +  '-' +   team_names_maping[unidecode.unidecode(info_per_match[4].lower().strip())]
                                        except KeyError:
                                            any_errors = False
                                            print("Error  caught in your BETCLIC parse func.  -- keyError in team mapper  :( .....")
                                            pass

                                        try:
                                            teamAWinOdds = info_per_match[7]
                                            draw_odds    = info_per_match[11]
                                            teamBWinOdds = info_per_match[15]
                                        except IndexError:
                                            any_errors = False
                                            print("Error  caught in 6your BETCLIC parse fu6nc.  -- IndexError in team mapper  :( .....")
                                            pass


                                        try:
                                            teamAWinOdds = info_per_match[8]
                                            draw_odds    = info_per_match[12]
                                            teamBWinOdds = info_per_match[16]
                                        except IndexError:
                                            any_errors = False
                                            print("Error  caught in 6your BETCLIC parse fu6nc.  -- IndexError in team mapper  :( .....")
                                            pass

                                        try:
                                            full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams].append(float(teamAWinOdds.replace(',','.'))) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                                            full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams].append(float(draw_odds.replace(',','.')))
                                            full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams].append(float(teamBWinOdds.replace(',','.')))

                                        except ValueError:
                                            any_errors = False
                                            print("Error  caught in your BETCLIC parse func. block call --  :( .....")
                                            continue

                                    for key,val in full_all_bookies_allLeagues_match_data.items(): 
                                        if betclic in key:
                                            break

                                    # try:3
                                    #     teamA = team_names_maping[unidecode.unidecode(info_per_matches[1] + info_per_match[2]).lower().strip() ]
                                    #     teamB = team_names_maping[unidecode.unidecode(info_per_matches[9] + info_per_match[10]).lower().strip()]
                                    # except KeyError:
                                    #     any_errors = False
                                    #     print("Error  caught in your BETCLIC parse func.  -- keyError in team mapper  :( .....")
                                    #     continue
                                    
                                    # try:
                                    #     teamAWinOdds = info_per_matches[3]
                                    #     draw_odds    = info_per_matches[7]
                                    #     teamBWinOdds = info_per_matches[11]
                                    # except IndexError:
                                    #     any_errors = False
                                    #     print("Error  caught in 6your BETCLIC parse func.  -- IndexError in team mapper  :( .....")
                                    #     continue

                                    # try:
                                    #     full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teamA + ' - ' + teamB].append(float(teamAWinOdds.replace(',','.'))) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                                    #     full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teamA + ' - ' + teamB].append(float(draw_odds.replace(',','.')))
                                    #     full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teamA + ' - ' + teamB].append(float(teamBWinOdds.replace(',','.')))

                                    # except ValueError:
                                    #     any_errors = False
                                    #     print("Error  caught in your BETCLIC parse func. block call --  :( .....")
                                    #     continue

                        else:

                            for dates in  ligue1_games_info_betclic:

                                game_info_france1  = dates.text.lower().split('ligue 1 uber eats')
                                game_info_england1 = dates.text.lower().split('premier league')
                                game_info_spain1   = dates.text.lower().split('liga primera')
                                game_info_italy1   = dates.text.lower().split('serie a')
                                game_info_germany1 = dates.text.lower().split('bundesliga')

                                if len(game_info_france1) > 1:
                                    game_info = game_info_france1

                                elif len(game_info_england1) > 1:
                                    game_info = game_info_england1    

                                elif len(game_info_spain1) > 1:
                                    game_info = game_info_spain1

                                elif len(game_info_italy1) > 1:
                                    game_info = game_info_italy1 

                                elif len(game_info_germany1) > 1:
                                    game_info = game_info_germany1

                                else:
                                    print('issue in getting any proper matches data in betclic...')
                                    continue

                                date = unidecode.unidecode(game_info[0].split('\n')[0])
                                for matchs in game_info[1:]:

                                    ## Live string needs another branch to handle - diff indices for teams and odds as per 'match' string then being :
                                    # ®\n37' - 1ère  mt\bordeaux\n1 - 1\nlorient\nrésultat du match\nbord\neaux\n2,15\nn\nul\n2,35\nlor\nient\n3,15\nquelle équipe marquera le but 3 ?\nbord\neaux\n1,75\npas de\n but\n4,10\nlor\nient\n2,25\n67\nparis\n"

                                    info_per_match = matchs.split('\n')
                                    if len(info_per_match) >= 13 :

                                        ## !!! LIVE games change to be done as swmn here...

                                        ## Live string needs another branch to handle - diff indices for teams and odds as per 'match' string then being :
                                        # ®\n37' - 1ère  mt\bordeaux\n1 - 1\nlorient\nrésultat du match\nbord\neaux\n2,15\nn\nul\n2,35\nlor\nient\n3,15\nquelle équipe marquera le but 3 ?\nbord\neaux\n1,75\npas de\n but\n4,10\nlor\nient\n2,25\n67\nparis\n"
                                        try:
                                            teamA = team_names_maping[unidecode.unidecode(info_per_match[1]).lower().strip()]
                                            teamB = team_names_maping[unidecode.unidecode(info_per_match[2]).lower().strip()]
                                        except KeyError:
                                            any_errors = False
                                            print("Error  caught in your BETCLIC parse func.  -- keyError in team mapper  :( .....")
                                            continue
                                        
                                        try:
                                            teamAWinOdds = info_per_match[6]
                                            draw_odds    = info_per_match[9]
                                            teamBWinOdds = info_per_match[12]
                                        except IndexError:
                                            any_errors = False
                                            print("Error  caught in your BETCLIC parse func.  -- IndexError in team mapper  :( .....")
                                            continue

                                        try:
                                            full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teamA + ' - ' + teamB].append(float(teamAWinOdds.replace(',','.'))) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                                            full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teamA + ' - ' + teamB].append(float(draw_odds.replace(',','.')))
                                            full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teamA + ' - ' + teamB].append(float(teamBWinOdds.replace(',','.')))

                                        except ValueError:
                                            any_errors = False
                                            print("Error  caught in your BETCLIC parse func. block call --  :( .....")
                                            continue                                


                        end_betclic = time.time()  
                        tot_betclic += end_betclic - start_betclic
                        print('time taken to process betclic was = ' + str(end_betclic - start_betclic))                 

                    start_unibet = time.time()

                    # if 'draftkings' in sites:

                    #     try:

                    #         wait_time37 = random.randint(3,6)
                    #         #time.sleep(wait_time37)  

                    #         a_z_sportslist_dkings =  driver.find_elements_by_xpath('//*[@id="root"]/section/section[1]/nav/div[1]/div/div/div')

                    #         a_z_sportslist_dkings =  driver.find_element_by_class_name('sportsbook subnav__link')  # > nav > div.sportsbook-subnav__responsive-more-nav > div > div > div

                    #         # MLS div : 
                    #         mls_elmment = driver.find_element_by_xpth('//*[@id="root"]/section/section[2]/section/div[3]/div/div[3]/div/div/div[2]')

                    #         if mls_elmment:

                    #             for game_div in games:

                    #                 print(game_div.text)


                    #     except: #  NoSuchElementException:
                    #         any_errors = False
                    #         print("Error  ->  caught in your draftKings parse func. block call --  :( ..... ")
                    #         continue



                    if  unibet in sites :
                    # unibet tree struct to games elements:
                        print('in unibet ligue1 pre-match parsing .... \n \n')  
                        # Live ligue1 games...

                        # //*[@id="page__compettitionview"]/div/div[1]/div[2]/div/div/div 
                        # team names and competitio nshud be in here

                        #odds of game are then in :
                        # //*[@id="b03b18c2-763c-44ea-aa2b-53835d043b8c"]/div//*[@id="root"]/section/section[2]/section/div[3]/div/div[3]/div/div/div[2]
                        ## full psath gfor this (odds) probly better
                        #/html/body/div[1]/div[2]/div[5]/div/section/div/section/div/section/div/div[1]/div[2]/div/div/div/    section/div/ul/li/div/div/li/div/ul/ul/li/div[2]/div[2]/div/section/div/div
                        
                        # 3 'span' elements in here with odds
                        # now navigate using the driver and xpathFind to get to the matches section of Ref. site :

                        # if 'ligue 1' in sites:
                        #     compettition_ = 'Ligue 1'

                        # elif 'Liga 1' in sites:
                        #     compettition_ = 'La Liga'

                        # elif 'Premier' in sites:
                        #     compettition_ = 'Premier League'

                        # elif 'Champions' in sites:
                        #     compettition_ = 'Ligue des Champions'                    

                        # elif 'Europa' in sites:
                        #     compettition_ = 'Europa League'

                        # else:
                        #     compettition_ = 'Ligue 1'


                        try:

                            wait_time37 = random.randint(3,6)
                            #print('second rand wait time = ' + str(wait_time37))
                            time.sleep(wait_time37)  

                            ligue1_games_nested_gamesinfo_unibet_1 =  driver.find_elements_by_xpath('//*[@id="page__compettitionview"]/div/div[1]/div[2]/div/div/div/div[3]/div[2]/div')  
                            ligue1_games_nested_gamesinfo_unibet_2 =  driver.find_elements_by_xpath('/html/body/div[1]/div[2]/div[5]/div/section/div/section/div/section/div[1]/div/div[2]/div/div/div[2]/div[2]/div[1]/div/div')                                                                            #//*[@id="page__compettitionview"]/div/div[1]/div[2]/div/div/div/div[3]/div[2] 
                            time.sleep(wait_time12)                                                                         #//*[@id="page__compettitionview"]/div/div[1]/div[2]/div/div/div/div[3]/div[2]
                            ligue1_games_nested_gamesinfo_unibet_3 =  driver.find_elements_by_xpath('//*[@id="page__compettitionview"]/div[1]/div/div[2]/div/div/div[2]/div[2]/div[1]/div')
                            ligue1_games_nested_gamesinfo_unibet_4 =  driver.find_elements_by_xpath('//*[@id="page__compettitionview"]/div[1]/div/div[2]/div/div/div[2]/div[2]')
                            #print('in unibet and collected all ligue one games web element ! ... ')
                            #compettition =  compettition_

                            time.sleep(wait_time12)  

                            ligue1_games_nested_gamesinfo_unibet =  ligue1_games_nested_gamesinfo_unibet_1
                            if not ligue1_games_nested_gamesinfo_unibet_1:
                                ligue1_games_nested_gamesinfo_unibet = ligue1_games_nested_gamesinfo_unibet_2
                                if not ligue1_games_nested_gamesinfo_unibet_2:
                                    ligue1_games_nested_gamesinfo_unibet = ligue1_games_nested_gamesinfo_unibet_3
                                    if ligue1_games_nested_gamesinfo_unibet_3 and len(ligue1_games_nested_gamesinfo_unibet_3[0].text) > len(ligue1_games_nested_gamesinfo_unibet_4[0].text) :
                                        ligue1_games_nested_gamesinfo_unibet = ligue1_games_nested_gamesinfo_unibet_3
                
                                    elif  ligue1_games_nested_gamesinfo_unibet_4 and len(ligue1_games_nested_gamesinfo_unibet_3[0].text) < len(ligue1_games_nested_gamesinfo_unibet_4[0].text) :   
                                        ligue1_games_nested_gamesinfo_unibet = ligue1_games_nested_gamesinfo_unibet_4

                                    elif   ligue1_games_nested_gamesinfo_unibet_3 and  not ligue1_games_nested_gamesinfo_unibet_4:
                                        ligue1_games_nested_gamesinfo_unibet = ligue1_games_nested_gamesinfo_unibet_3

                                    elif  not ligue1_games_nested_gamesinfo_unibet_3 and  ligue1_games_nested_gamesinfo_unibet_4:
                                        ligue1_games_nested_gamesinfo_unibet = ligue1_games_nested_gamesinfo_unibet_4

                                    else:
                                        print('driver find element call return nothing ... try again or exit with no results for games in ligue 1 UNIBET...')
                                        ## TODO : implement another method - different path - maybe full Xpath to a known root easily or use Bueaty soup ...etc.
                                        continue
                                    
                                elif  ligue1_games_nested_gamesinfo_unibet_4 and len(ligue1_games_nested_gamesinfo_unibet_2[0].text) < len(ligue1_games_nested_gamesinfo_unibet_4[0].text) :   
                                    ligue1_games_nested_gamesinfo_unibet = ligue1_games_nested_gamesinfo_unibet_4

                                elif   ligue1_games_nested_gamesinfo_unibet_2 and  not ligue1_games_nested_gamesinfo_unibet_4:
                                    ligue1_games_nested_gamesinfo_unibet = ligue1_games_nested_gamesinfo_unibet_2

                                elif  not ligue1_games_nested_gamesinfo_unibet_2 and  ligue1_games_nested_gamesinfo_unibet_4:
                                    ligue1_games_nested_gamesinfo_unibet = ligue1_games_nested_gamesinfo_unibet_4

                                else:
                                    print('driver find element call return nothing ... try again or exit with no results for games in ligue 1 UNIBET...')
                                    ## TODO : implement another method - different path - maybe full Xpath to a known root easily or use Bueaty soup ...etc.
                                    continue
                            
                            for game_info in  ligue1_games_nested_gamesinfo_unibet:
                            
                                time.sleep(wait_time12)  

                                parts_france1  = game_info.text.lower().split('ligue 1 ubereats')
                                parts_england1 = game_info.text.lower().split('premier league')
                                parts_spain1   = game_info.text.lower().split('liga primera')
                                parts_italy1   = game_info.text.lower().split('serie a')
                                parts_germany1 = game_info.text.lower().split('bundesliga')
                                parts_champsLi = game_info.text.lower().split('ligue des champions')
                                parts_europa = game_info.text.lower().split('europa league')

                                if len(parts_france1) > 1:
                                    parts = parts_france1

                                elif len(parts_england1) > 1:
                                    parts = parts_england1    

                                elif len(parts_spain1) > 1:
                                    parts = parts_spain1

                                elif len(parts_italy1) > 1:
                                    parts = parts_italy1 

                                elif len(parts_germany1) > 1:
                                    parts = parts_germany1

                                elif len(parts_champsLi) > 1:
                                    parts = parts_champsLi    

                                elif len(parts_europa) > 1:
                                    parts = parts_europa                   

                                else:
                                    print('issue in getting any proper matches data in unibet...')
                                    continue

                                delimit_1 = parts[0].split('\n')
                                date = unidecode.unidecode(delimit_1[0])

                                if unidecode.unidecode(date.lower()) not in french_dates_list:
                                    date = date_ 

                                longer_info_match = True
                                for i in range(len(parts)-1):
                                                    
                                    if '%' not in parts[i+1]:
                                        longer_info_match = False

                                    delimit_2 = parts[i+1].split('\n')
                                    if len(delimit_1) >= 2 and len(delimit_2) >= 6 :

                                        sep_team_names = parts[i].split('\n')[-2].split(' - ')

                                        # handle the case of 'sain-etienne'
                                        #if len(sep_team_names) > 2 and 'tienne' in sep_team_names:

                                        teamA_raw = sep_team_names[0].strip()
                                        teamB_raw = sep_team_names[1].strip()       

                                        teams =  team_names_maping[unidecode.unidecode(teamA_raw).lower()] + ' - ' + team_names_maping[unidecode.unidecode(teamB_raw).lower()] 
                                        #unidecode.unidecode(parts[i].split('\n')[-2]).lower()
                                        time.sleep(wait_time12)
                                        if longer_info_match:
                                            
                                            teamAWinOdds = delimit_2[2]
                                            draw_odds = delimit_2[5]                          
                                            teamBWinOdds = delimit_2[8]
                                        else:

                                            teamAWinOdds = delimit_2[1].split(' ')[1]
                                            draw_odds = delimit_2[2].split(' ')[1]                            
                                            teamBWinOdds = delimit_2[3].split(' ')[1]                            

                                        full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams].append(float(teamAWinOdds))   
                                        full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams].append(float(draw_odds))    
                                        full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams].append(float(teamBWinOdds))  

                            end_unibet = time.time()  
                            tot_unibet += end_unibet - start_unibet
                            print('time taken to process unibet was = ' + str( end_unibet - start_unibe ))                                

                        except: #  NoSuchElementException:
                            any_errors = False
                            print("Error  ->  caught in your UNIBET parse func. block call --  :( ..... ")
                            continue
                        #check = 1

                    #full path copied from sourcecode tool       
                    #/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div/div[2]
                    start_winimax = time.time()
                    if winimax in sites :        
                        print('in winimax ' +   league_or_cup_name  + ' pre-match parsing .... \n \n')   
                        #ompetition   =  compettition_ #split_match_data_str[1]  
                        match_count_wini = 0
                                                                                            
                        ligue1_games_nested_gamesinfo_winimax = driver.find_elements_by_xpath('/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div/div')                                    
                        ligue1_games_nested_gamesinfo_winimax_2 = driver.find_elements_by_xpath('//*[@id="app-inner"]/span/div/div/div[2]/div/section/div/div[1]/div/div/div') 
                        ligue1_games_nested_gamesinfo_winimax_3 = driver.find_elements_by_xpath('//*[@id="app-inner"]/span/div/div/div[2]/div/section/div/div[1]/div/div/div/div')    
                        ligue1_games_nested_gamesinfo_winimax_4 = driver.find_elements_by_xpath('//*[@id="app-inner"]/span/div/div/div[2]/div/section/div[2]/div[1]/div/div')                                                                
                        if not  ligue1_games_nested_gamesinfo_winimax:
                            ligue1_games_nested_gamesinfo_winimax = ligue1_games_nested_gamesinfo_winimax_2   
                            if not   ligue1_games_nested_gamesinfo_winimax:
                                ligue1_games_nested_gamesinfo_winimax =  ligue1_games_nested_gamesinfo_winimax_3
                                if not ligue1_games_nested_gamesinfo_winimax_3:
                                    ligue1_games_nested_gamesinfo_winimax = ligue1_games_nested_gamesinfo_winimax_4
                                                                                                                                                                            # #//*[@id="app-inner"]/span/div/div[2]/div/section/div/div[1]/div/div
                        # TEST _ CHANGE Loop var to the live one here temporarily
                        for matches in ligue1_games_nested_gamesinfo_winimax: #ligue1_games_nested_gamesinfo_winimax_live_footy:  # ligue1_games_nested_gamesinfo_winimax:                 #//*[@id="app-inner"]/span/div/div[2]/div/section/div/div[1]/div/div
                            if matches.rect['height'] < 50.0:
                                #check if you get a non match day like - alternative betting type header
                                # (occues at the end of the ligue one games list on winimax pro ejemplo0)
                                # if not (any(char.isdigit() for char in matches.text)):
                                #    continue
                                if find_substring("BETS ON THE ", matches.text):
                                    break
                                date = unidecode.unidecode(matches.text)   
                                continue
                            
                            longer_info_match = True
                            if '%' not in matches.text:
                                longer_info_match = False

                            time.sleep(wait_time12)
                            split_match_data_str = matches.text.split('\n')
                            if len(split_match_data_str) >= 4:
                                # check_teams_in_str = [True for y in All_ligue1_team_list if find_substring(y,unidecode.unidecode(matches.text).lower())]

                        ## !! will have to change this later as its not general enough to not miss NB games - here as winimax can have too many games in its pages and take too long parse just ewhats neeeded
                                match_count_wini += 1

                                if match_count_wini > 10:
                                    break

                                # if not check_teams_in_str:
                                #     continue
                                #time.sleep(wait_time12) 
                                separate_team_names = split_match_data_str[0].split(' vs ')
                                try:
                                    teamA = team_names_maping[unidecode.unidecode(separate_team_names[0]).lower().strip()]
                                    teamB = team_names_maping[unidecode.unidecode(separate_team_names[1]).lower().strip()]
                                except ValueError:
                                    any_errors = False
                                    print(" Value  Error  caught in mapper your winamax parse func. block call --  :( ..... ")
                                    continue
                                except KeyError:
                                    any_errors = False
                                    print(" Key  Error  caught in mapper your winamax parse func. block call --  :( ..... ")
                                    continue            
        
                                try :
                                    time.sleep(wait_time12)
                                    if longer_info_match:
                                        teamAWinOdds  = float(split_match_data_str[2].replace(',','.'))
                                        draw_odds     = float(split_match_data_str[5].replace(',','.'))
                                        teamBWinOdds  = float(split_match_data_str[8].replace(',','.'))

                                    else:
                                        teamAWinOdds  = float(split_match_data_str[2].replace(',','.'))
                                        draw_odds     = float(split_match_data_str[4].replace(',','.'))
                                        teamBWinOdds  = float(split_match_data_str[6].replace(',','.'))             

                                except ValueError:
                                    any_errors = False
                                    print(" Value  Error  caught in your winamax parse func. block call --  :( ..... ")
                                    continue

                                full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teamA +  ' - ' + teamB].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                                full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teamA +  ' - ' + teamB].append(draw_odds)
                                full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teamA +  ' - ' + teamB].append(teamBWinOdds)

                        end_winimax = time.time()  
                        tot_winimax +=  end_winimax - start_winimax
                        print('time taken to process winimax was = ' + str(end_winimax - start_winimax))

            ## TODO - games element not getting picked up by find_elements driver call - try somtin else or beuaty soup!    
                    
                    ## somethin wrong with assumed html in link - think i must navigate all the way from base url with button click and hfers links etc

                    start_cbet = time.time()  
                    cbet_win_odds_indx  = 4
                    cbet_draw_odds_indx = 5
                    cbet_lose_odds_indx = 6
                    #print('time taken to process unibet was = ' + str(start_unibet - end_unibet))
                    if cbet in sites :        
                        time.sleep(wait_time12)
                        #time.sleep(wait_time12)     
                        #time.sleep(wait_time12) 
                        #driver.implicitly_wait(13)
                        print('in cbet ' +   league_or_cup_name  + ' pre-match parsing .... \n \n')   
                        #compettition  =  compettition_ #split_match_data_str[1]    
                        
                        try:
                            #WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/section/section/ul/li')))
                            ligue1_games_nested_gamesinfo_cbet = driver.find_elements_by_xpath('//*[@id="prematch-events"]/div[1]/div/section/section/ul/li')    
                            ligue1_games_nested_gamesinfo_cbet_2 = driver.find_elements_by_xpath('/html/body/main') #body/div[1]/div/div[2]/div[1]/div/section/section/ul') #'/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div/div[2]')                                    
                        except:
                            print('error in Cbet trying to read webelement - first list of games..., wait a sec and retry...')
                            time.sleep(wait_time12)
                            ligue1_games_nested_gamesinfo_cbet = driver.find_elements_by_xpath('//*[@id="prematch-events"]/div[1]/div/section/section/ul/li')    
                            ligue1_games_nested_gamesinfo_cbet_2 = driver.find_elements_by_xpath('/html/body/main') #body/div[1]/div 
                            pass

                        #ligue1_games_gamesinfo_cbet  = ligue1_games_nested_gamesinfo_cbet
                        time.sleep(wait_time12) 
                        if not  ligue1_games_nested_gamesinfo_cbet_2:
                            ligue1_games_gamesinfo_cbet = ligue1_games_nested_gamesinfo_cbet

                            try:
                                iframe_     = ligue1_games_nested_gamesinfo_cbet_2[0].find_element_by_xpath('.//iframe')
                            except IndexError:
                                print('Key error caught in cbet parsing, continuing ...')
                                continue 
                        else:    

                            ligue1_games_gamesinfo_cbet = ligue1_games_nested_gamesinfo_cbet
                    
                            try:
                                iframe_     = ligue1_games_nested_gamesinfo_cbet_2[0].find_element_by_xpath('.//iframe')
                            except IndexError:
                                print('Key error caught in cbet parsing, continuing ...')
                                continue  

                        iframe_link = iframe_.get_attribute('src')
                        driver.get(iframe_link)
                        ## Now in the internal links html and can crawl and scrAPE  as per usual

                    #TODO !!!!        frech_ligue_gamesinfo_list = driver.find_elements_by_xpath('???? ')

                        date = '20 decembre' #unidecode.unidecode('?? ') 
                        #time.sleep(wait_time12)
                        #time.sleep(wait_time12)

                        wait_time37 = random.randint(3,6)
                        #print('second rand wait time = ' + str(wait_time37))
                        time.sleep(wait_time37)  
                                                                        
                        league_selector =  driver.find_elements_by_xpath('//*[@id="prematch-top-leagues"]/ul/li')                    
                        for leagues in league_selector:

                            if 'Ligue 1' in leagues.text and 'Ligue1' in compettition[0]:
                                leagues.click()
                                print(' league found in Cbet is : Ligue 1 - France' + ' ...') 
                                break

                            elif 'champions' in leagues.text.lower() and 'champions' in compettition[0]:
                                leagues.click()
                                print(' league found in Cbet is : ' + str('Champions league ') + ' ...') 
                                break

                            elif 'premier league' in leagues.text.lower() and 'premier-league' in compettition[0]:
                                leagues.click()
                                print(' league found in Cbet is : ' + str('Premier league -- England') + ' ...') 
                                break

                            elif 'bundesliga' in leagues.text.lower() and 'bundesliga' in compettition[0].lower():
                                leagues.click()
                                print(' league found in Cbet is : ' + str('Bundesliga - Germany') + ' ...') 
                                break

                            elif 'la liga' in leagues.text.lower() and ( 'laliga' in compettition[0].lower() or 'liga-primera' in compettition[0].lower() or 'la-liga' in compettition[0]):
                                leagues.click()
                                print(' league found in Cbet is : ' + str('La Liga - Espana !! `') + ' ...') 
                                break

                            elif 'serie a' in leagues.text.lower() and 'serie-a' in compettition[0]:
                                leagues.click()
                                print(' league found in Cbet is : ' + str('Serie A italia') + ' ...') 
                                break    

                            elif 'europa' in leagues.text.lower() and 'europa' in compettition[0]:
                                leagues.click()
                                print(' league found in Cbet is : ' + str('Europa shite league') + ' ...') 
                                break    

                            else:
                                print('No league found in Cbet so ... GAN ! ...')                

                        time.sleep(wait_time12)
                        time.sleep(wait_time37) 
                        #matches_soccer_info_2 = driver.find_elements_by_xpath('//*[@id="prematch-events"]/div[1]/div/section/section/ul/li')
                        matches_soccer_info_2 =  driver.find_elements_by_xpath( '//*[@id="prematch-events"]/div[1]/div/section/section/ul/li')
                        for matches in matches_soccer_info_2:

                            split_match_data_str = matches.text.split('\n') 

                            if len(split_match_data_str) >= 4:
                                time.sleep(wait_time12)
                                teams = unidecode.unidecode(split_match_data_str[3]).lower().strip() # + unidecode.unidecode(split_match_data_str[5]).lower().strip(0)
                                #teams = split_match_data_str[2] #+ '_' + split_match_data_str[6]
                                try:
                                    teams_split = teams.split('-')

                                    if len(teams_split) == 2:
                                        teamA = team_names_maping[unidecode.unidecode(teams_split[0]).lower().strip()]
                                        teamB = team_names_maping[unidecode.unidecode(teams_split[1]).lower().strip()]
                                        teams = teamA + ' - ' + teamB

                                except KeyError:
                                    print('Key error caught in cbet parsing, continuing ...')
                                    continue 

                                try:
                                    teamAWinOdds = split_match_data_str[4].replace(',','.')
                                    draw_odds    = split_match_data_str[5].replace(',','.')
                                    teamBWinOdds = split_match_data_str[6].replace(',','.')
                                except IndexError:
                                    print('Index error caught in cbet parsing, continuing ...')
                                    continue    
                                    
                                try:    
                                
                                    full_all_bookies_allLeagues_match_data[ cbet + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams.lower()].append(float(teamAWinOdds)) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                                    full_all_bookies_allLeagues_match_data[ cbet + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams.lower()].append(float(draw_odds))
                                    full_all_bookies_allLeagues_match_data[ cbet + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams.lower()].append(float(teamBWinOdds))
                                
                                except  ValueError:
                                    print("error  in CBET site parsing... ") 
                                    continue


                        end_cbet = time.time()  
                        tot_cbet +=  end_cbet - start_cbet
                        print('time taken to process cbet was = ' + str(start_cbet - end_cbet))
                        # url = sites
                        # headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
                        # res = requests.get(url=url, headers=headers).json()
                        # print(res)
                        # for i in res['data']: #['list']:
                        #     print(i)                

            # Hiddemn Div here needs fixing:
            # TODO - games element not getting picked up by find_elements driver call - try somtin else or beuaty soup!

                    if sports_bwin in sites :          #.startswith('sports.bwin',8) or sites.startswith('sports.bwin'9) :
                        print('in sports_bwin ' +   league_or_cup_name  + ' pre-match parsing .... \n \n')   
                        #compettition   =  compettition_ 

                        time.sleep(wait_time12) 
                        #try:
                        time.sleep(wait_time12) 
                        # relative path to all upcoming ligue 1 games    
                        #resultElements_all_dates = driver.find_elements_by_xpath("/html/body/vn-app/vn-dynamic-layout-single-slot[3]/vn-main/main/div/ms-main/div/div/ms-fixture-list/div/div/div/ms-grid/ms-event-group")
                        #resultElements_all_dates = driver.find_elements_by_xpath("/html/body/vn-app/vn-dynamic-layout-single-slot[3]/vn-main/main/div/ms-main/div/div/ms-fixture-list/div/div/div/ms-grid/ms-event-group/ms-event")                
                                                                                    #"/html/body/vn-app/vn-dynamic-layout-single-slot[3]/vn-main/main/div/ms-main/div/div/ms-fixture-list/div/div/div/ms-grid/ms-event-group"    
                                                                                    #/html/body/vn-app/vn-dynamic-layout-single-slot[3]/vn-main/main/div/ms-main/div/div/ms-fixture-list/div/div/div/ms-grid/ms-event-group/ms-event[1]   
                        resultElements_all_dates = driver.find_elements_by_xpath('//*[@id="main-view"]/ms-fixture-list/div/div/div/ms-grid/ms-event-group/ms-event')

                        #     # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
                        #end = timeit.time
                        time.sleep(wait_time12) 
                        #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 
                        #time.sleep(wait_time12)
                        for index,groups in enumerate(resultElements_all_dates):
                            #all_games =  games.find_elements_by_xpath('//ms-event')
                            time.sleep(wait_time12)

                            #print(groups.text + '\n\n')
                            if '/' in groups.text:
                                bwin_parts = groups.text.split('/')
                                delimit_1 = bwin_parts[0].split('\n')
                                time.sleep(wait_time12)
                                if index == 0:
                                    if len(bwin_parts) == 2:
                                        date = unidecode.unidecode(bwin_parts[0])

                                    if len(bwin_parts) == 3:    
                                        date = unidecode.unidecode(delimit_1[-1] + bwin_parts[1] + bwin_parts[-1].split('\n')[0])
                            else:
                                bwin_parts = groups.text
                                delimit_1 = groups.text.split('\n')

                            #if unidecode.unidecode(date.lower()) not in french_dates_list:
                            #    date = date_ 

                                #for i in range(len(parts)-1):
                            delimit_2 = bwin_parts[-1].split('\n')

                            if len(delimit_1) >= 2 and len(delimit_2) >= 6 :
                                
                                time.sleep(wait_time12)

                                ##   !!!!  NB !!!! DEF IMPLENT THE TRY - except as can easily hit non existat keyError and just continue on ... !!!!
                                #try
                                #teams =  ligue1_teamNamesMap[unidecode.unidecode(parts[0].split('\n')[-3])] + ' - ' +  ligue1_teamNamesMap[unidecode.unidecode(parts[0].split('\n')[-2])]            
                                teams =  team_names_maping[unidecode.unidecode(bwin_parts[0].split('\n')[-3]).lower().strip()] + ' - ' +  team_names_maping[unidecode.unidecode(bwin_parts[0].split('\n')[-2]).lower().strip()]   

                                teamAWinOdds = delimit_2[1]
                                time.sleep(wait_time12)
                                draw_odds = delimit_2[2]                           
                                teamBWinOdds = delimit_2[3]

                                time.sleep(wait_time12)
                                try:

                                    full_all_bookies_allLeagues_match_data[sports_bwin + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams.lower() ].append(float(teamAWinOdds))                
                                    full_all_bookies_allLeagues_match_data[sports_bwin + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams.lower() ].append(float(draw_odds))    
                                    full_all_bookies_allLeagues_match_data[sports_bwin + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams.lower() ].append(float(teamBWinOdds))  
                                    #time.sleep(wait_time13)      
                                except  ValueError:
                                    print("error  in sports.bwin site parsing... ")



                    start_parion = time.time()                                          
            # TODO - games element not getting picked up by find_elements driver call - try somtin else or beuaty soup!
                    parion_win_odds_indx  = 3
                    parion_draw_odds_indx = 4
                    parion_lose_odds_indx = 5
     
                    if 'draftkings' in sites :

                    #     joon = driver.find_elements_by_xpath('/html/body/div[1]/div/div[3]/div[3]/div/div/div/div[1]/div/div/div[2]/div/div[1]/div/div[2]/div[2]/div/div')
                    #     for games in joon :

                    ## Choose upcoming (not live) games

                    #root > section > section.sportsbook-wrapper__body > div.sportsbook-featured-page.dkbetslip > section.sportsbook-featured-page__wrapper > section.sportsbook-featured-page__offers > div > div.sportsbook-responsive-card-container__header.sportsbook-custom-scrollbar-darkest

        #                 pg_root_0 = driver.find_element_by_id('root')
        #                 try:
        #                     pg_root = pg_root_0.find_element_by_class_name("sportsbook-responsive-card-container") #__header.sportsbook-custom-scrollbar-darkest")

        #                     #root > section > section.sportsbook-wrapper__body > div.sportsbook-featured-page.dkbetslip > section.sportsbook-featured-page__wrapper > section.sportsbook-featured-page__offers > div > div.sportsbook-responsive-card-container__header.sportsbook-custom-scrollbar-darkest

        #                 except NoSuchElementException:
        #                     any_errors = False
        #                     print("Error  caught in your draftkings sports parse func. block ..... :( ")
        #                     #continue
        #                 except StaleElementReferenceException:
        #                     print('StaleElementReferenceException exception  error in parion in float casting odds...')    
        #                     continue         
                        
        #                 ## get to clicking soccer
        #                 try:

        #                     event_types = pg_root.find_element_by_id("game_category_Game Lines") 
        #                     # event_types_full_txt = pg_root.text
        #                     # event_types = event_types_full_txt.split('\n')

        #                     #in_game_btn = event_types.find_element_by_xpath("./../")

        #                     # for event_type in event_types:
        
        #                     #     # event = event_type.get_id()

        #                     #     if 'game lines' in event_type.lower():
        #                     #         time.sleep(wait_time12)
                            
        #                     event_types.click()

        #                     #pg_root = pg_roots.find_element_by_class_name('sportsbook-featured-page dkbetslip')

        #                 except NoSuchElementException:
        #                     any_errors = False
        #                     print("Error  caught in your pmu sports parse func. block ..... :( ")
        #                     #continue 

        #                 except StaleElementReferenceException:
        #                     print('StaleElementReferenceException exception  error in parion in float casting odds...')    
        #                     continue 

        #                 try:    
        #                     time.sleep(wait_time12)
        #                     #event_types_parent = event_types.parent # find_element_by_class_name('//../')
        #                     sports_list_parent = pg_root_0.find_elements_by_class_name("sportsbook-tabbed-subheader")
        #                     #sports_list_parent = pg_root.find_element_by_class_name("sportsbook-featured__featured-offers")
        #                     time.sleep(wait_time12)
        #                     #sports_list = sports_list_parent.find_element_by_class_name("sportsbook-responsive-card-container__header sportsbook-custom-scrollbar-darkest")

        #                 except NoSuchElementException:
        #                     any_errors = False
        #                     print("Error  caught in your pmu sports parse func. block ..... :( ")
        #                     #continue 

        #                 except StaleElementReferenceException:
        #                     print('StaleElementReferenceException exception  error in parion in float casting odds...')    
        #                     continue 

        #                 time.sleep(wait_time12)
        #                 # games = sports_list.find_elements_by_css_selector('a')
        #                 if sports_list_parent:
        #                     games = sports_list_parent[-1].find_elements_by_css_selector('a')
                        
        #                     time.sleep(wait_time12)
        #                     for sports in games:

        #                         sport = sports.text.lower()
        #                         if 'soccer' in sport:
        #                             time.sleep(wait_time12)
        #                             sports.click()
        #                 else:
        #                     print('missed sports_list+parent- list doesn exist...Error ...')            

        # # "//*[contains(@class,'ms-active-highlight')]

        #                 wait_time12 = random.randint(1,2)
        #                 time.sleep(wait_time12)
        #                 try:
        #                     #bunny = pg_root.find_elements_by_xpath("//*[@contains(@class, 'ReactVirtualized__Grid__innerScrollContainer')]")
        #                     socer_leagues_global = driver.find_elements_by_xpath("//*[contains(@class, 'ReactVirtualized__Grid__innerScrollContainer')]")

        #                 except NoSuchElementException:
        #                     any_errors = False
        #                     print("Error  caught in your pmu sports parse func. block ..... :( ")
        #                     #continue 

        #                 except StaleElementReferenceException:
        #                     print('StaleElementReferenceException exception  error in parion in float casting odds...')    
        #                     continue 

        #                 time.sleep(wait_time12)
        #                 if socer_leagues_global:
        #                     for league_names in socer_leagues_global:
        #                         league = league_names.text.lower()
        #                         #if 'MLS' in league:
        #                         # testing wuth bundesliga for now as no MLS games le fail @ time of testing :
        #                         if 'mls' in league:
        #                             time.sleep(wait_time12)
        #                             time.sleep(wait_time12)
        #                             league_names.click()

        #                 time.sleep(wait_time12)
        #                 # Now lets looop thru the games and pick up the various requested odds, finally :

        #                 #<div class="sportsbook-event-accordion__wrapper expanded"><div role="button" tabindex="0" aria-expanded="true" aria-label="Event Accordion for Bayern Munchen vs Augsburg" class="sportsbook-event-accordion__accordion" data-tracking="{&quot;target&quot;:&quot;ExpandEvent&quot;,&quot;action&quot;:&quot;click&quot;,&quot;section&quot;:&quot;GamesComponent&quot;,&quot;sport&quot;:5312,&quot;league&quot;:88670568,&quot;value&quot;:&quot;Bayern Munchen vs Augsburg&quot;}"><a class="sportsbook-event-accordion__title" href="/event/180267546">Bayern Munchen vs Augsburg</a><span class="sportsbook-event-accordion__date"><span>SAT 9th APR 9:30AM</span></span><svg role="img" aria-label="Arrow pointing up icon" class="sportsbook__icon--arrow-up" fill="#ababab" width="12" height="12" viewBox="0 0 32 32"><path d="M16.032 6.144h-0.032l-14.624 14.656c-0.384 0.384-0.384 0.992 0 1.344l1.504 1.504c0.384 0.384 0.992 0.384 1.344 0l11.776-11.776h0.032l11.776 11.776c0.384 0.384 0.992 0.384 1.344 0l1.504-1.504c0.384-0.384 0.384-0.992 0-1.344l-14.624-14.656z"></path></svg></div><div class="sportsbook-event-accordion__children-wrapper"><ul class="game-props-card17"><li class="game-props-card17__cell"><div class="sportsbook-outcome-cell"><div role="button" tabindex="0" aria-pressed="false" class="sportsbook-outcome-cell__body" aria-label="Bayern Munchen " data-tracking="{&quot;section&quot;:&quot;GamesComponent&quot;,&quot;action&quot;:&quot;click&quot;,&quot;target&quot;:&quot;RemoveBet&quot;,&quot;sportName&quot;:&quot;5312&quot;,&quot;leagueName&quot;:&quot;88670568&quot;,&quot;subcategoryId&quot;:4514,&quot;eventId&quot;:180267546}"><div class="sportsbook-outcome-body-wrapper"><div class="sportsbook-outcome-cell__label-line-container"><span class="sportsbook-outcome-cell__label">Bayern Munchen</span></div><div class="sportsbook-outcome-cell__elements"><div class="sportsbook-outcome-cell__element"></div><div class="sportsbook-outcome-cell__element"><span class="sportsbook-odds american default-color">-1000</span></div></div></div></div></div></li><li class="game-props-card17__cell"><div class="sportsbook-outcome-cell"><div role="button" tabindex="0" aria-pressed="false" class="sportsbook-outcome-cell__body" aria-label="Draw " data-tracking="{&quot;section&quot;:&quot;GamesComponent&quot;,&quot;action&quot;:&quot;click&quot;,&quot;target&quot;:&quot;RemoveBet&quot;,&quot;sportName&quot;:&quot;5312&quot;,&quot;leagueName&quot;:&quot;88670568&quot;,&quot;subcategoryId&quot;:4514,&quot;eventId&quot;:180267546}"><div class="sportsbook-outcome-body-wrapper"><div class="sportsbook-outcome-cell__label-line-container"><span class="sportsbook-outcome-cell__label">Draw</span></div><div class="sportsbook-outcome-cell__elements"><div class="sportsbook-outcome-cell__element"></div><div class="sportsbook-outcome-cell__element"><span class="sportsbook-odds american default-color">+900</span></div></div></div></div></div></li><li class="game-props-card17__cell"><div class="sportsbook-outcome-cell"><div role="button" tabindex="0" aria-pressed="false" class="sportsbook-outcome-cell__body" aria-label="Augsburg " data-tracking="{&quot;section&quot;:&quot;GamesComponent&quot;,&quot;action&quot;:&quot;click&quot;,&quot;target&quot;:&quot;RemoveBet&quot;,&quot;sportName&quot;:&quot;5312&quot;,&quot;leagueName&quot;:&quot;88670568&quot;,&quot;subcategoryId&quot;:4514,&quot;eventId&quot;:180267546}"><div class="sportsbook-outcome-body-wrapper"><div class="sportsbook-outcome-cell__label-line-container"><span class="sportsbook-outcome-cell__label">Augsburg</span></div><div class="sportsbook-outcome-cell__elements"><div class="sportsbook-outcome-cell__element"></div><div class="sportsbook-outcome-cell__element"><span class="sportsbook-odds american default-color">+2200</span></div></div></div></div></div></li></ul></div></div>

        #                 socer_matches_forMLS = league_names.find_element_by_xpath('//*[@class="sportsbook-event-accordion__wrapper expanded"]')

        #                 #root > section > section.sportsbook-wrapper__body > div.sportsbook-featured-page.dkbetslip > section.sportsbook-featured-page__wrapper > section.sportsbook-featured-page__offers > div > div.sportsbook-responsive-card-container__body > div.sportsbook-responsive-card-container__card.selected > div > div.cards > div:nth-child(1) > div > div
        #                 # 'ReactVirtualized__'
        #                 check = 0


                        #try:
                        # sports_list = driver.find_element_by_class_name("col-3 widget-slot ng-star-inserted")
                        # sports_list = driver.find_element_by_xpath('//*[@class="col-3 widget-slot ng-star-inserted"]')   #"slot slot-single slot-header_bottom_items")
                        # #'leaf-item list-item ng-star-inserted'
                        # sports_list = driver.find_element_by_class_name("col-3 widget-slot ng-star-inserted")
                        # driver.get('https://sportsbook.draftkings.com/leagues/soccer/88670597')
                        time.sleep(wait_time12)
                        time.sleep(wait_time12)

                        # keep taking the earloest sprt a user entered (box ticked on the website)
                        # and go thru them until the list os sports is exhausted, then break out of the current loop
                        sports_btn_val = input_sports[-index]
                        index += 1

                        if index == len(input_sports):
                            break

                        if sports_btn_val == 'soccer':
                            driver.get('https://sportsbook.draftkings.com/sports/soccer')
                        elif sports_btn_val == 'hockey':   
                            driver.get('https://sportsbook.draftkings.com/sports/hockey')
                        elif sports_btn_val == 'basketball':   

                            driver.get('https://sportsbook.draftkings.com/sports/basketball')
                        elif sports_btn_val == 'nfl':   
                            driver.get('https://sportsbook.draftkings.com/sports/nfl')
                        else:
                            driver.get('https://sportsbook.draftkings.com/sports/tennis')

                        time.sleep(wait_time12)
                        wait_time35 = random.randint(3,5)
                        time.sleep(wait_time35)
                        time.sleep(wait_time12)
                        try:
                            #test_wrongPg_mls_btn = WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Game Lines')))
                            # mls_btn = WebDriverWait(driver, 7).until(EC.element_to_be_visible((By.LINK_TEXT, 'USA - MLS')))
                            mls_btn = driver.find_element_by_link_text('USA - MLS')
                        except TimeoutException as e:
                                print("[{}] Element not clickable".format(str(datetime.now())))                    
                        #time.sleep(wait_time12)
                        wait_time35 = random.randint(3,5)
                        time.sleep(wait_time35)

                        matches_pg_url = mls_btn.get_attribute('href')
                        driver.get(matches_pg_url)

                        #mls_btn.click()
                        #time.sleep(wait_time12)
                        # #sports_list = driver.find_elements_by_xpath('//*[@id="main-view"]/ms-widget-layout/ms-widget-slot[2]/ms-top-items-widget/ms-promo-item')
                                                
                        #//*[@id="main-view"]/ms-widget-layout/ms-widget-slot[2]/ms-top-items-widget/ms-promo-item[3]
                        # time.sleep(wait_time37)

                        #time.sleep(wait_time12)

                        # except:
                            
                        #     any_errors = False
                        #     print("Error  caught in your pmu sports parse func. block ..... :( ")

                        sports_list = driver.find_elements_by_xpath('//*[@id="root"]/section/section[2]/section/div[3]/div/div[3]/div/div/div[2]/div/div[2]/div')
                                    
                        games_list = sports_list
                        if games_list:

                            for match in games_list:
                                
                                # default is pre game - i.e an eptyy livetag to prepend the dictionry key
                                live_tag = ''

                                time.sleep(wait_time12)
                                game_info = match.text.split('\n')
                                if len(game_info) >= 2:
                                    date = unidecode.unidecode(game_info[1]) #.split('\n')[0])
                                #for games in game_info:

                                if '2nd half' in game_info[1].lower() or '1st half' in game_info[1].lower():
                                    print('LIVE GAME ENCOUNTERED !')
                                    live_tag = 'Live_'
                                    # skip to next game fow , but in future sort apart live and pre game matches.
                                    continue
                                
                                #matches = games.split('//')            
                                if len(game_info) >= 5 :
                                    time.sleep(wait_time12)
                                    #for match in matches :
                                    # game_info  = matches[0].split('\n')
                                    # single_game_right = matches[1].split('\n')

                                    # if len(game_info) < 1 or len(single_game_right) < 4:
                                    #     breaks
                                    
                                    #time.sleep(wait_time12)
                                    try:
                                        teamA = unidecode.unidecode(game_info[2]).lower().strip()
                                        teamB = unidecode.unidecode(game_info[-2]).lower().strip()
                                    except KeyError:
                                        print('key error in draft kings in float casting odds...')    
                                        continue                        
                                        #time.sleep(wait_time12)
                                    try:
                                        # attempt assuming euro dds format
                                        #teamAWinOdds = float(game_info[-5].replace(',','.'))
                                        #draw_odds    = float(game_info[-3].replace(',','.'))
                                        #teamBWinOdds = float(game_info[-1].replace(',','.'))

                                        teamAOdds_str = game_info[-5]
                                        drawOdds_str = game_info[-3]
                                        teamBOdds_str = game_info[-1]                
                                        if teamAOdds_str[0] == '+':
                                            print(' teamAOdds_str[1:] = ' + str(teamAOdds_str[1:]))
                                            teamAOdds = round((float(teamAOdds_str[1:])/ 100.0),4) + 1.0
                                        else:
                                            teamAOdds = round((100.0/(float(teamAOdds_str[1:]))),4) + 1.0   
                                        if drawOdds_str[0] == '+':    
                                            draw_odds = round((float(drawOdds_str[1:]) / 100.0),4) + 1.0
                                        else:   
                                            draw_odds = round(( 100.0/(float(drawOdds_str[1:]))),4) + 1.0             
                                        if teamBOdds_str[0] == '+':
                                            teamBOdds = round((float(teamBOdds_str[1:])/ 100.0),4) + 1.0
                                        else:

                                            teamBOdds = round(( 100.0/(float(teamBOdds_str[1:]))),4) + 1.0                   

                                    except ValueError:
                                        print('value error in draft kings in float casting odds...')    
                                        continue

                                    print('teamA Win Odds = ' + str(teamAOdds))
                                    print('teamB Win Odds = ' + str(draw_odds))
                                    print('Draw Odds = ' + str(teamBOdds))

                                    #time.sleep(wait_time12)
                                    teams = teamA + ' - ' + teamB                                            
                                    full_all_bookies_allLeagues_match_data[ 'draftkings' + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams].append(teamAOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                                    full_all_bookies_allLeagues_match_data[ 'draftkings' + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams].append(draw_odds)
                                    full_all_bookies_allLeagues_match_data[ 'draftkings' + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams].append(teamBOdds)

                    web_pg_soccer = ""
                    if 'betmgm' in sites:
                        time.sleep(wait_time12)
                        driver.get(sites)

                        # <ms-widget-slot msautomation="widget-slot-left" class="cg32t435ol-3 widget-slot ng-star-inserted"><ms-favourites-widget class="hidden favourites-widget list list-card ng-star-inserted"><!----><!----></ms-favourites-widget><ms-top-items-widget class="list list-card top-items-widget ng-star-inserted"><ms-item class="list-title list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted"><div class="icon ng-star-inserted"><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Top Sports</span><!----></div><!----><!----><!----></a><!----><!----><!----></ms-item><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/football-11"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-11"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Football</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/mma-45"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-45"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">MMA</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/boxing-24"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-24"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Boxing</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/formula-1-6?fallback=true"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-6"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Formula 1</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/table-tennis-56"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-56"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Table Tennis</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/nascar-39?fallback=true"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-39"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">NASCAR</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/basketball-7"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-7"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Basketball</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/baseball-23"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-23"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Baseball</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/hockey-12"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-12"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Hockey</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/golf-13?fallback=true"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-13"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Golf</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><div class="separator-item ng-star-inserted">A-Z SPORTS</div><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/aussie-rules-36?fallback=true"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-36"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Aussie Rules</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/baseball-23"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-23"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Baseball</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/basketball-7"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-7"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Basketball</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/boxing-24"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-24"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Boxing</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/cricket-22"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-22"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Cricket</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/curling-68"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-68"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Curling</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/cycling-10?fallback=true"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-10"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Cycling</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/darts-34"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-34"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Darts</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/football-11"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-11"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Football</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/formula-1-6?fallback=true"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-6"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Formula 1</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/gaelic-sports-48?fallback=true"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-48"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Gaelic Sports</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/golf-13?fallback=true"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-13"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Golf</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/handball-16"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-16"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Handball</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/hockey-12"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-12"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Hockey</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/lacrosse-88"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-88"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Lacrosse</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/mma-45"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-45"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">MMA</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/motorsport-41?fallback=true"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-41"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Motorsport</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/nascar-39?fallback=true"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-39"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">NASCAR</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/rugby-league-31"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-31"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Rugby League</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/rugby-union-32"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-32"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Rugby Union</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/snooker-33"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-33"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Snooker</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/soccer-4"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-4"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Soccer</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/table-tennis-56"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-56"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Table Tennis</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/tennis-5"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-5"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Tennis</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><ms-promo-item class="leaf-item list-item ng-star-inserted"><a class="ms-active-highlight ng-star-inserted" href="/en/sports/volleyball-18"><div class="icon ng-star-inserted"><span class="base-icon ng-star-inserted"><span class="sports-18"></span></span><!----><!----></div><div class="title ng-star-inserted"><span class="ng-star-inserted">Volleyball</span><!----><!----><!----></div><!----><!----><!----></a><!----><!----><!----></ms-promo-item><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----></ms-top-items-widget><!----></ms-widget-slot>
                        # <vn=-098765ynamic-layout-multi-slot slot="header_bottom_items" class="slot slot-single slot-header_bottom_items"><ms-breadcrumbs class="breadcrumb hidden"><div class="breadcrumb-back"><span class="breadcrumb-theme-left"><i class="theme-left"></i></span></div><!----><!----><!----></ms-breadcrumbs><!----><!----><ms-navigation><div class="navigation-wrapper"><nav id="sports-nav" class="compact"><ms-main-items><ms-scroll-adapter class="scroll-adapter" style="touch-action: pan-y; user-select: none; -webkit-user-drag: none; -webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><div class="scroll-adapter__container scroll-adapter__container--scrollable-right" style="overflow-x: hidden;"><div class="scroll-adapter__content"><div class="main-items"><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/live/betting"><i class="ui-icon ui-icon-size-lg sports-icon theme-live"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">Live</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="https://casino.on.betmgm.ca/en/games"><i class="ui-icon ui-icon-size-lg sports-icon theme-livecasinoblackjack"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">Casino</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/basketball-7/betting/usa-9/nba-6004"><i class="ui-icon ui-icon-size-lg sports-icon theme-custom-nba"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">NBA</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/hockey-12/betting/usa-9/nhl-34"><i class="ui-icon ui-icon-size-lg sports-icon theme-custom-nhl"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">NHL</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/baseball-23/betting/usa-9/mlb-75"><i class="ui-icon ui-icon-size-lg sports-icon theme-custom-mlb"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">MLB</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/golf-13/betting/world-6/us-masters-11144?tab=matches"><i class="ui-icon ui-icon-size-lg sports-icon sports-13"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">The Masters</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/soccer-4"><i class="ui-icon ui-icon-size-lg sports-icon sports-4"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">Soccer</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/mma-45/betting/usa-9/ufc-273-75854"><i class="ui-icon ui-icon-size-lg sports-icon sports-45"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">UFC 273</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/tennis-5"><i class="ui-icon ui-icon-size-lg sports-icon sports-5"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">Tennis</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/multi-builder"><i class="ui-icon ui-icon-size-lg sports-icon theme-multi-builder"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">Easy Parlay</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="before-separator menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/football-11"><i class="ui-icon ui-icon-size-lg sports-icon sports-11"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">Football</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/mma-45"><i class="ui-icon ui-icon-size-lg sports-icon sports-45"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">MMA</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/boxing-24"><i class="ui-icon ui-icon-size-lg sports-icon sports-24"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">Boxing</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/formula-1-6?fallback=true"><i class="ui-icon ui-icon-size-lg sports-icon sports-6"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">Formula 1</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/table-tennis-56"><i class="ui-icon ui-icon-size-lg sports-icon sports-56"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">Table Tennis</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/nascar-39?fallback=true"><i class="ui-icon ui-icon-size-lg sports-icon sports-39"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">NASCAR</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/basketball-7"><i class="ui-icon ui-icon-size-lg sports-icon sports-7"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">Basketball</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="/en/sports/favourites"><i class="ui-icon ui-icon-size-lg sports-icon sports-favourites"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">Favorites</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href="https://promo.on.betmgm.ca/en/promo/offers"><i class="ui-icon ui-icon-size-lg sports-icon theme-offers"><span vnmenuitembadge="" hidden="" class="badge badge-circle badge-danger badge-offset badge-size-sm badge-t-r"></span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">Promotions</span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><vn-menu-item displaymode="icon" badgeclass="badge-size-sm badge-offset" badgeposition="icon" linkclass="top-nav-link" textclass="text-truncate ui-icon-text" class="before-separator menu-item"><a poppertrigger="none" class="menu-item-link top-nav-link" href=""><i class="ui-icon ui-icon-size-lg sports-icon theme-search before-separator"><span vnmenuitembadge="" class="badge badge-circle badge-offset badge-size-sm badge-t-r topnav-new-badge">New</span><!----><!----><!----></i><!----><!----><!----><!----><!----><!----><span class="menu-item-txt text-truncate ui-icon-text">Search </span><!----><!----><!----><!----><!----><!----><!----><!----><!----></a><!----><!----><vn-popper-content showcloselink="false" closetype="button"><popper-content class="ngxp__tooltip tooltip-info"><div class="ngxp__container ngxp__animation" aria-hidden="true" role="popper" style="display: none; opacity: 0;"><!----><div class="ngxp__inner"><span class="ui-icon ui-close theme-ex"></span><!----><div><div></div><!----></div><div class="popper-buttons"><!----></div></div><!----><div class="ngxp__arrow"></div></div></popper-content><!----></vn-popper-content><!----><!----><!----><!----></vn-menu-item><!----></div><!----></div></div><span class="scroll-adapter__arrow scroll-adapter__arrow--left scroll-adapter__arrow--hidden scroll-adapter__arrow--disabled"><span class="theme-left"></span></span><span class="scroll-adapter__arrow scroll-adapter__arrow--right"><span class="theme-right"></span></span></ms-scroll-adapter><!----><!----><!----></ms-main-items></nav></div><!----><div class="az-menu-container"></div></ms-navigation><!----><!----><ms-sub-navigation><!----><!----></ms-sub-navigation><!----><!----><!----></vn-dynamic-layout-multi-slot>

                        wait_time35 = random.randint(3,5)
                        time.sleep(wait_time35)                        

                        try:
                            #test_wrongPg_mls_btn = WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Game Lines')))
                            # mls_btn = WebDriverWait(driver, 7).until(EC.element_to_be_visible((By.LINK_TEXT, 'USA - MLS')))
                            mls_btn = driver.find_element_by_link_text('Soccer')
                        except TimeoutException as e:
                                print("[{}] Element not clickable".format(str(datetime.now())))   

                        time.sleep(wait_time35)
                        time.sleep(wait_time35)

                        matches_pg_url = mls_btn.get_attribute('href')

                    ############################
                        driver.quit()
                        proxies = req_proxy.get_proxy_list()
                        PROXY_COUNTER = random.randint(1, len(proxies))

                        PROXY = proxies[PROXY_COUNTER].get_address()
                        webdriver.DesiredCapabilities.CHROME['proxy']={
                            "httpProxy":PROXY,
                            "ftpProxy":PROXY,
                            "sslProxy":PROXY,
                            "proxyType":"MANUAL",
                        }
                        driver_1 = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
                        driver_1.maximize_window()
                            
                        time.sleep(wait_time12)
                        time.sleep(wait_time12)

                        driver_1.get(matches_pg_url) 
                        randFloatNUm5_7 = random.SystemRandom().uniform(5, 7)
                        time.sleep(randFloatNUm5_7)

                        # if len(driver.window_handles) > 0 :
                        #     window_after = driver.window_handles[-1]
                        #     driver.switch_to.window(window_after)

#driver.refresh()
                        time.sleep(wait_time12)
                        try:
                            usa_btn = driver_1.find_element_by_partial_link_text('USA')
                        except TimeoutException as e:
                                print("[{}] Element not clickable".format(str(datetime.now())))   

                        #usa_btn = WebDriverWait(driver_1, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, 'USA')))
                        time.sleep(wait_time12)
                        matches_pg_url_usa = usa_btn.get_attribute('href')

                        driver_1.quit()
                        PROXY = proxies[PROXY_COUNTER].get_address()
                        webdriver.DesiredCapabilities.CHROME['proxy']={
                        "httpProxy":PROXY,
                        "ftpProxy":PROXY,
                        "sslProxy":PROXY,
                        "proxyType":"MANUAL",
                        }
                        driver_2 = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
                        driver_2.maximize_window()
                        time.sleep(wait_time35)
                        time.sleep(wait_time12)
                        time.sleep(wait_time35)
                        driver_2.get(matches_pg_url_usa)

                        try:
                            # sports_list = driver.find_element_by_class_name("col-3 widget-slot ng-star-inserted")
                            # sports_list = driver.find_element_by_xpath('//*[@class="col-3 widget-slot ng-star-inserted"]')   #"slot slot-single slot-header_bottom_items")
                            # #'leaf-item list-item ng-star-inserted'
                            # sports_list = driver.find_element_by_class_name("col-3 widget-slot ng-star-inserted")

                            sports_list = driver.find_elements_by_xpath('//*[@id="main-view"]/ms-widget-layout/ms-widget-slot[2]/ms-top-items-widget/ms-promo-item')
                            #//*[@id="main-view"]/ms-widget-layout/ms-widget-slot[2]/ms-top-items-widget/ms-promo-item[3]

                        except:
                            
                            any_errors = False
                            print("Error  caught in your BetMGM parse func. block ..... :( ")
                            #continue 

                        # if sports_list:    

                        #     for index, sports in enumerate(sports_list):

                        #         if 'soccer' in sports.text.lower():
                        #             #time.sleep(wait_time12)
                        #             element_str = '//*[@id="main-view"]/ms-widget-layout/ms-widget-slot[2]/ms-top-items-widget/ms-promo-item[' + str(index + 1) + ']/a'
                        #             #print('formed string = ->' + element_str + '<-')
                        #             #enter_next_page = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, element_str)))
                        #             web_pg_soccer
                        #             web_pg_soccer = enter_next_page.get_attribute('href')
                        #             time.sleep(wait_time12)
                        #             driver.get(web_pg_soccer)
                        #             time.sleep(3)
                        #             #click_element =  g
                        #             #enter_next_page.click()
                        #             break

                        #     time.sleep(wait_time12)
                        # time.sleep(wait_time12)

                        # driver.implicitly_wait(7)

                        # try:
                        #     outer_sports_picker_elemt_1 = driver.find_element_by_xpath("//*[contains(@class, 'row sport-lobby widget-layout ng-star-inserted')]")
                        # except:
                        #     any_errors = False
                        #     print("Error  caught in your BetMGM parse func. block ..... :( ")
                        #     #continue 

                        # check_alls_well  = 1    
                        # proxies = req_proxy.get_proxy_list()
                        # ## TEST
                        # proxies = proxies[:51]
                        # PROXY_COUNTER = random.randint(1, len(proxies))
                        # proxies = req_proxy.get_proxy_list()

                        # if PROXY_COUNTER == len(proxies) - 1:
                        #     proxies = req_proxy.get_proxy_list()

                        # PROXY = proxies[PROXY_COUNTER].get_address()
                        # webdriver.DesiredCapabilities.CHROME['proxy']={
                        #     "httpProxy":PROXY,
                        #     "ftpProxy":PROXY,
                        #     "sslProxy":PROXY,
                        #     "proxyType":"MANUAL",
                        # }
                        # driver_1 = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

                        # PROXY_COUNTER += 1
                        # driver_1.get(web_pg_soccer)

                        #WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, '/html/body/vn-app/vn-dynamic-layout-single-slot[4]/vn-main/main/div/ms-main/ng-scrollbar/div/div/div/div/ms-main-column/div/ms-widget-layout/ms-widget-slot[2]/ms-top-items-widget/ms-promo-item[5]/a')))

                        #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main-view"]/ms-widget-layout/ms-widget-slot[2]/ms-top-items-widget/ms-promo-item[4]')))

                        try:
                            countries_soccer_list = driver_1.find_elements_by_xpath('//*[@id="main-view"]/ms-widget-layout/ms-widget-slot[2]/ms-top-items-widget/ms-promo-item[4]')
                            time.sleep(wait_time12)
                            if countries_soccer_list:    

                                for index, leagues in enumerate(countries_soccer_list):

                                    if 'usa' in leagues.text.lower():
                                        #time.sleep(wait_time12)
                                        element_str = '//*[@id="main-view"]/ms-widget-layout/ms-widget-slot[2]/ms-top-items-widget/ms-promo-item[' + str(index + 1) + ']/a'
                                        #print('formed string = ->' + element_str + '<-')
                                        
                                        #enter_next_page = WebDriverWait(driver_1, 3).until(EC.element_to_be_clickable((By.XPATH, element_str)))
                                        enter_next_page = driver.find_elemnt_by_xpath(element_str)
                                        time.sleep(wait_time12)
                                        web_pg_mls = enter_next_page.get_attribute('href')
                                        # wait_time23 = random.randint(2,3)
                                        #time.sleep(wait_time23)
                                        driver.get(web_pg_mls)
                                        
                                        btn = driver.find_element_by_xpath('//*[@id="main-view"]/ms-widget-layout/ms-widget-slot[2]/ms-top-items-widget/ms-promo-item[' + str(index + 1) + ']')
                                        btn.click()

                                        #click_element = 
                                        #enter_next_page.click()
                                        break

                                time.sleep(wait_time12)

                        except:
                            any_errors = False
                            print("Error  caught in your v sports parse func. block ..... :( ")
                            #continue 

                        # get_afrts_href0

                        #then grab games - go thru 'em and get odds'

                        try:
                            league_games_list = driver.find_elements_by_xpath('//*[@id="main-view"]/ms-widget-layout/ms-widget-slot[2]/ms-top-items-widget/ms-promo-item')
                            time.sleep(wait_time12)
                        except KeyError:
                            print('value error in parion in float casting odds...')    
                            continue                      

                            if league_games_list:    
                                ligue1_games_info_pmu = resultPmuElements_1
                            if not resultPmuElements_1:
                                ligue1_games_info_pmu = resultPmuElements

                            if not  ligue1_games_info_pmu:
                                continue   
                            
                            #//*[@id="tabs-second_center-block-0"]/div/div/div/div/div/div/div/div
                            #//*[@id="table-content-20201220_0_2"]/div/div[2]
                            #     # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
                            #end = timeit.time
                            #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 
                            game_info = ligue1_games_info_pmu[0].text.split('+')
                            date = unidecode.unidecode(game_info[0].split('\n')[0])
                            for games in game_info:
                                #all_games =  games.find_elements_by_xpath('//ms-event')
                                #time.sleep(wait_time12)
                                    #[0].split('\n')
                                #for game in game_info:

                                pmu_loop_counter += 1
                                if pmu_loop_counter > 20 :
                                    print('breaking out of crazy pmu loop.. ! as it goes on ad infinitum, lool')
                                    break
                            
                                matches = games.split('//')    
                                if len(matches) >= 2 :
                                    time.sleep(wait_time12)
                                    #for match in matches :
                                    single_game_left  = matches[0].split('\n')
                                    single_game_right = matches[1].split('\n')

                                    if len(single_game_left) < 1 or len(single_game_right) < 4:
                                        break
                                    
                                    #time.sleep(wait_time12)
                                    try:
                                        teamA = team_names_maping[unidecode.unidecode(single_game_left[-1]).lower().strip()]
                                        teamB = team_names_maping[unidecode.unidecode(single_game_right[0]).lower().strip()]
                                    except KeyError:
                                        print('value error in BetMGM in float casting odds...')    
                                        continue                        
                                        #time.sleep(wait_time12)
                                    try:
                                        teamAWinOdds = float(single_game_right[1].replace(',','.'))
                                        draw_odds    = float(single_game_right[2].replace(',','.'))
                                        teamBWinOdds = float(single_game_right[3].replace(',','.'))

                                    except ValueError:
                                        print('value error in BetMGM in float casting odds...')    
                                        continue

                                    #time.sleep(wait_time12)
                                    teams = teamA + ' - ' + teamB
                                    init_index_pmu_name = 8
                                    end_index_pmu_name = 26                                               
                                    full_all_bookies_allLeagues_match_data[ 'BetMGM'.lower() + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                                    full_all_bookies_allLeagues_match_data[ 'BetMGM'.lower() + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams].append(draw_odds)
                                    full_all_bookies_allLeagues_match_data[ 'BetMGM'.lower() + '_' + date.lower() + '_' + league_or_cup_name.lower() + '_' + teams].append(teamBWinOdds)


    stop_mainParserTimer = time.time()

    print('Time to do main files full sites (8) parsing was = ' + str( stop_mainParserTimer - start_mainParserTimer ))
                        
    ## create sepaarate dicts for each bookies :

    unibet_dict      = defaultdict(list)
    betclic_dict     = defaultdict(list)
    winimax_dict     = defaultdict(list)
    zebet_dict       = defaultdict(list) 
    sports_bwin_dict = defaultdict(list)
    france_pari_dict = defaultdict(list)
    parionbet_dict   = defaultdict(list)
    cbet_dict        = defaultdict(list)
    pmu_dict         = defaultdict(list)

    print(' **************************************************************************************************************************************************************************************************************** ')
    print(' **************************** no. of sites in data struct post parsing  ********************************* -> ' + str(len(full_all_bookies_allLeagues_match_data)))

    print('its keys are :')

    for keys in full_all_bookies_allLeagues_match_data.keys():
        print(keys)
    print(' ************************************************************************************************************** ************************************************************************************************** ')   

    all_split_sites_data = []
    if len(full_all_bookies_allLeagues_match_data) == 0:
        #print("Empty full_data dict encountered -- fix !")
        return False 
        
    items = full_all_bookies_allLeagues_match_data.items() 
    for item in items: 

        try:
            keys = item[0]
            values = item[1]

        except KeyError:        
            print("Error -- key value does not exist in the full_data dict. ! -- return False as a failure from the parsing function...")
            return False    
        
        if unibet in keys:
            unibet_dict[keys] = values
            #all_split_sites_data.append(unibet_dict)

        if betclic in keys:
            betclic_dict[keys] = values
            #all_split_sites_data.append(betclic_dict)

        if winimax in keys:
            winimax_dict[keys] = values
            #all_split_sites_data.append(winimax_dict)

        if zebet in keys:
            zebet_dict[keys] = values
            #all_split_sites_data.append(zebet_dict)

        if sports_bwin in keys:
            sports_bwin_dict[keys] = values
            #all_split_sites_data.append(sports_bwin_dict)

        if france_pari in keys:
            france_pari_dict[keys] = values
            #all_split_sites_data.append(france_pari_dict)

        if parionbet in keys:
            parionbet_dict[keys] = values
            #all_split_sites_data.append(pasinobet_dict)

        if cbet in keys:
            if  not values:
                continue
            cbet_dict[keys] = values
            #all_split_sites_data.append(pasinobet_dict)
            # 
        if paris_sportifs_pmu[8:26] in keys:
            pmu_dict[keys] = values
            #all_split_sites_data.append(pasinobet_dict)\
            #                 

    if len(unibet_dict) > 0:
        all_split_sites_data.append(unibet_dict)

    if len(betclic_dict) > 0:
        all_split_sites_data.append(betclic_dict)

    if len(winimax_dict) > 0:
        all_split_sites_data.append(winimax_dict)

    if len(zebet_dict) > 0:
        all_split_sites_data.append(zebet_dict)

    if len(sports_bwin_dict) > 0: 
        all_split_sites_data.append(sports_bwin_dict)

    if len(france_pari_dict) > 0:
        all_split_sites_data.append(france_pari_dict)

    if len(parionbet_dict) > 0:
        all_split_sites_data.append(parionbet_dict)
 
    if cbet_dict and len(cbet_dict) > 0:
        all_split_sites_data.append(cbet_dict)

    if len(pmu_dict) > 0:
        all_split_sites_data.append(pmu_dict)               

    driver.quit()
    return any_errors

if __name__ == '__main__':

    argv = sys.argv
    DEBUG_OUTPUT  = False
    print(' len(argv)  = ' + str(len(argv) ))

    print('Enter list of sports and compettitions you want alerts for ... \n')
    print('Use format :   soccer, mls, serie A; basketball, MBA; tennis, wimbledon, US Open. ')
  
    input_stream = input()
    sports_n_competetitons_list = input_stream.split(';')

    if not sports_n_competetitons_list : # or other issues like no recognized or supprted sports then choose default (soccer and MLS only)
        sports_n_competetitons_list = ['soccer, MLS']
        #         sports_n_competetitons['soccer'] = ['MLS']
    else:
        if sports_n_competetitons_list[-1] == '':
            sports_n_competetitons_list = sports_n_competetitons_list[:-1]
        for item in sports_n_competetitons_list:
            if len(item) >= 2:
                competetes_per_sport_list = item.split(',')#[1:]
                for index, competetition in enumerate(competetes_per_sport_list[1:]):
                    #if (index+1) <= len(competetes_per_sport_list[1:]):
                        sports_n_competetitons[competetes_per_sport_list[0]].append(competetition.strip())   # competetes_per_sport_list[index+1])
            else:
                sports_n_competetitons['soccer'] = ['MLS']

## temporarily use these instead of dict aboove until it is worling and reliable
    
    sports_btn_val = 'soccer' # 'hockey' 'basketball' 'nfl'  'curling'
    compettition_btn_val    =  'MLS'
    
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

    if len(argv) >= 2 :

        if len(argv) == 8 :

            retVal = odds_alert_system(oddType= int(argv[1]), expect_oddValue= float(argv[2]), teamA= argv[3], teamB= argv[4], date= argv[5], competition= argv[6], Bookie1_used= argv[7], input_sports= [sports_btn_val], input_competitions = [compettition_btn_val])

        elif  len(argv) == 2 :

            retval2 = check_for_sure_bets(float(argv[1]), sports_n_competetitons) 

        else:

            #print("usage:  please indicate with  0 or a 1 in the first cmd line argument to the program wherether you wish to include debugging output prints in it's run or not; 0/1 corresponding to no/yes....")
            print("Usage : sportsbetAlertor_v1.py oddType (0 -home team win, 1 - a dra. 2 - away team win ) expect_soddValue teamA teamB competition Bookie1_used.    i.e 7 parameters on thye cmd line after the filename")
            print("Heres an Example --- sportsbetAlertor_v1.py  0 1.75  lyon  marseille  ligue1 Winamax")
            exit(1)
   
    else:
        #DEBUG_OUTPUT = bool(int(argv[1]))
        retval2 = check_for_sure_bets(input_sports= [sports_btn_val], input_competitions = [compettition_btn_val])   #sports_n_competetitons) #'unibet','zebet','winimaxc','W', 'D','marseilles','nantes','28/11/2020','ligue 1 UberEats')





