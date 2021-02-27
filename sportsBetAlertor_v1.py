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
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

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

sys.path.append('./')
from metaLeague_data import *
1
# define global init 'surebet' condition value (note by default any bet will not be a surebet given its > 1.0)
surebet_factor = 1.0
#cibstant initialised to False - for determining if they customer's expected odds are retrieved for alert system...
odd_are_found = False

TEST_MODE =   True #False

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
    #print(' Surebet value = ' + str(total_iverse_odds_sum))

    if total_iverse_odds_sum < 1.0 and total_iverse_odds_sum > 0.0:
        return True

    return False    

def get_surebet_factor(*argv): #  odds_A, odds_B):

    global surebet_factor

    # reset this global value -- but must think on should I create class 'gambler' to correctly initialise these kinds of vars and update per instance etc..(?)
    surebet_factor = 0.0

    #total_iverse_odds_sum = 0.0
    for odds in argv:
        if odds == 0:
            continue
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
DRIVER_PATH = r'./chromedriver' #the path where you have "chromedriver" file.


options = Options()
options.headless = True
#options.LogLevel = False
options.add_argument("--window-size=1920,1200")
#options.add_argument("--LogLevel=0")
#options.add_argument("user-agent= 'Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41' ")
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_6) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.698.0 Safari/534.24'")
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH, service_args=["--verbose", "--log-path=D:\\qc1.log"])
    
def odds_alert_system(oddType=1,expect_oddValue=2.5,teamA='Liverpool',teamB='barcelone',date='Mercredi 25 Novembre',competition='Ligue des Champions',Bookie1_used='winmax'):

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
        
        if parseSites(driver): #all_srpaed_sites_data):
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

def check_for_sure_bets(*args):

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
        
        #endtime_file = time.time()
        #print('time to get to parsing was = ' + str(endtime_file - strtime_file))
        #print('Click on the "esc" key @ any time to terminate this program and can then restart again any time you wish :) ......')
        # waitr a delay time to refresh sites parsings....
        start_parse = time.time() 

        start_full_parsingTimer = time.time()
        if parseSites(driver): #all_srpaed_sites_data):
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
        print('AVerage time to do cbet parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_cbet/globCounter))
        print('AVerage time to do unibet parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_unibet/globCounter))
        print('AVerage time to do france_pari parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_france_pari/globCounter))
        print('AVerage time to do winimax parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_winimax/globCounter))
        print('AVerage time to do betclic parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_betclic/globCounter))
        print('AVerage time to do parion parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_parionbet/globCounter))
        print('AVerage time to do pmu parsings at the ' + str(globCounter) + ' iteration = ' + str(tot_pmu/globCounter))

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
                            
                            
                            #print('Checking for surebets -- idir teams : ' + str(teamA_1) +  '  and  ' + str(teamB_1)   + '.... checking_surebet_counts =  ' + str(checxking_surebet_counts)) 
                            #print('Bookies in order of odds are : ' + bookie_1  + bookie_2 + bookie_3 + '\n')
                            
                            #test for mail with %s -- this ensures a surebet is found !;)
                            #subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2] = 1.1,7.5,25     #8.0, 2.0, 4.0
                            #subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2] = 15.1, 1.75, 2.5 

                            #print('Odds youre checking are  =  ' + str(W_1) + ' = ' + str(subsetList[0][key][0]))
                            #print('   -- and  --  ' + str(D) + ' = ' + str(subsetList[1][key_bookkie2][1]))
                            #print('   -- and  --  ' + str(W_2) + ' = ' + str(subsetList[2][key_bookkie3][2]))
                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][0], subsetList[1][key_bookkie2][1], subsetList[2][key_bookkie3][2]
                            checxking_surebet_counts += 1
                            if  check_is_surebet(home_win_odds, draw_odds, away_win_odds):  # encode bookie outcomes as 'W','D','L' wrt to the 1st team in the match descrpt. , i.e The 'hometeam' 
                                
                                # if  returnBetSizes:
                                sure_bet_counter += 1
                                print('***********************************************************************************************************************************************************************************')   
                                print('*****************************************************************************  SURE BET FOUND !  :)   *****************************************************************************')   
                                print('***********************************************************************************************************************************************************************************')   
                                print('Odds comboo is')
                                print(W_1)
                                print(D)
                                ## as odds are 0,1 from 1st two bookies

                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                if surebet_factor != 0.0 and surebet_factor != 0:
                                    profit = (stake)/surebet_factor
                                else:
                                    profit = 100.0 
                                ## calc. % profit for the lads:
                                #profit = 1.0 - (1/subsetList[0][key][0] + 1/subsetList[1][key_bookkie2][1] + 1/subsetList[2][key_bookkie3][2]) 
                                #184 45238262
                                #get_surebet_factor(subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2])
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)

                                proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, profit,home_win_odds, draw_odds, away_win_odds)

                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][0],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][1]
                            #checxking_surebet_counts += 1
                            if  check_is_surebet(home_win_odds, draw_odds, away_win_odds):

                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE BET FOUND !  :)   *****************************************************************************') 
                                # given the last indices are 2,1,0
                                # W_1,W_2
                                ## calc. % profit for the lads:
                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                if surebet_factor != 0.0 and surebet_factor != 0:
                                    profit = (stake)/surebet_factor
                                else:
                                    profit = 100.0
                                
                                #get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)                          

                                proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3,W_1,W_2,teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, profit,home_win_odds, draw_odds, away_win_odds)

                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][1],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][2]
                            #checxking_surebet_counts += 1
                            if  check_is_surebet(home_win_odds, draw_odds, away_win_odds):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE-BET FOUND !  :)   *****************************************************************************') 
                                # D,W_1
                                # as final odds indices in first 2 bookies here are : 1,0 respectively
                                stake = 100.0
                                get_surebet_factor( home_win_odds, draw_odds, away_win_odds)
         
                                if surebet_factor != 0.0 and surebet_factor != 0:
                                    profit = (stake)/surebet_factor
                                else:
                                    profit = 100.0
                                ## calc. % profit for the lads:
                                #get_surebet_factor(subsetList[0][key][1],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][2])
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)
                                proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3, D, W_1, teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, profit, home_win_odds, draw_odds, away_win_odds) 

                            home_win_odds, draw_odds, away_win_odds =  subsetList[0][key][1], subsetList[1][key_bookkie2][2] ,subsetList[2][key_bookkie3][0]
                            #checxking_surebet_counts += 1
                            if  check_is_surebet(home_win_odds, draw_odds, away_win_odds):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE-BET FOUND !  :)   *****************************************************************************') 
                                
                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                if surebet_factor != 0.0 and surebet_factor != 0:
                                    profit = (stake)/surebet_factor
                                else:
                                    profit = 100.0
                                #profit = 1.0 - (1/subsetList[0][key][1] + 1/subsetList[1][key_bookkie2][2] + 1/subsetList[2][key_bookkie3][0])
                                #given the last indices are 2,1,0
                                # D,W_2
                                #1, 2    
                                #get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)
                                proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3,D , W_2 ,teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, profit, home_win_odds, draw_odds, away_win_odds)

                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][2],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][1]
                            #checxking_surebet_counts += 1
                            if  check_is_surebet(home_win_odds, draw_odds, away_win_odds):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SUREBET FOUND !  :)   *****************************************************************************') 
                                # given the last indices are 2,1,0
                                # W_2,W_1
                                # 2,0
                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                if surebet_factor != 0.0 and surebet_factor != 0:
                                    profit = (stake)/surebet_factor
                                else:
                                    profit = 100.0 
                                #get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)

                                proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3, W_2, W_1, teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, profit, home_win_odds, draw_odds, away_win_odds)                        

                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][2],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][0]
                            # checxking_surebet_counts += 1
                            if  check_is_surebet(home_win_odds, draw_odds, away_win_odds):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SUREBET FOUND !  :)   *************************0****************************************************')                                 
                                
                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                if surebet_factor != 0.0 and surebet_factor != 0:
                                    profit = (stake)/surebet_factor
                                else:
                                    profit = 100.0    

                                #get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)

                                proportionsABC_listRnd = [round(x,4) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 , bookie_3, W_2, D, teamA_1, teamB_1, date, competition_1,proportionsABC_listRnd, profit, home_win_odds, draw_odds, away_win_odds )    
                                #continue  
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
        
        Fp1 = open(surebets_Done_list_textfile,'a')
        Fp1.write(message + '  ' + date + '\n')
        Fp1.close()

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
    sender = 'godlikester@gmail.com'

    if TEST_MODE:
        receivers = ['crowledj@tcd.ie'] 
    else:
        receivers = ['crowledj@tcd.ie','pauldarmas@gmail.com','raphael.courroux@hotmail.fr','theoletheo@hotmail.fr','alexandrecourroux@hotmail.com','scourroux@hotmail.com']    

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
    if message in list_mailed_surebets:
        print('sureBet already found -- dontt re-mail ')
        return successFlag

    if Profit > 100.9:

        try:
            smtpObj = smtplib.SMTP_SSL("smtp.gmail.com",465)
            smtpObj.login("godlikester@gmail.com", "Pollgorm1")
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

def parseSites(driver): 

    start_mainParserTimer = time.time()
    global websites_champs_league_links, compettition, date, refernce_champ_league_gamesDict, full_all_bookies_allLeagues_match_data, DEBUG_OUTPUT, all_split_sites_data, tot_parionbet , tot_france_pari, tot_winimax, tot_cbet, tot_pmu, tot_unibet, tot_betclic    

    # reset full league dict so as not to keep appending to it below
    full_all_bookies_allLeagues_match_data.clear()
    any_errors = True      

################# ***********************################# ***********************################# ***********************################# ***********************################# ***********************
################# ***************************                            LIGUE 1 GAMES                      *******************************########################################
################# ***********************################# ***********************################# ***********************################# ***********************################# ***********************

    wait_time12 = random.randint(1,2)
    #time.sleep(wait_time12)  
    #websites_ligue1_links.append('https://www.zebet.fr/fr/lives')
    #websites_ligue1_links.append('https://www.france-pari.fr/lives')

    for i,sites in enumerate(websites_ligue1_links[0:]):
        
        wait_time = random.randint(1,2)*random.random()
        time.sleep(wait_time)  
        #begin = timeit.timeit()  
        driver.get(sites)
        #finish = timeit.timeit()

        compettition_ = 'ligue1'
        start_france_pari = time.time()  
        if  france_pari in sites :
        # # zebet tree struct to games elements:    
            # live games parsing tips ...:
            # in live link - go to element : //*[@id="currentlive"]/div/div -> list of sub element are divs
    ## !!! NBBB !!!!
            ## the sub elements per game in here's text = 'Ligue 1 Uber Eats®\n1\n0\nMi-temps\nRennes\nLyon\n1\n1,62\nN\n2,88\n2\n4,33'
            # also note - other league games r mixed up with them so must do a continue in the loop if not a game idir ligue one teams, NOT a break!7
            print('in france_pari ligue1 pre-match parsing .... \n \n')                                                 
            try:

                ## find sport 1st - > football ,
                sports_list_info_france_pari_try_1 = driver.find_elements_by_xpath('//*[@id="sports"]/ul/li')
                for sport in sports_list_info_france_pari_try_1:
                    time.sleep(wait_time)
                    sports = sport.find_elements_by_xpath('.//div/a')#.text
                   # sport_text = sports[1].text
                    if len(sports) >= 2:
                        sport_link = sports[0].get_attribute('href').lower()
                    else:
                        continue    

                    if 'football' in sport_link:
                        parent_ = sports[0].find_element_by_xpath('./..')
                        footy_leagues_cups = parent_.find_elements_by_xpath('.//div[2]/div/a')
                        #soccer_list_competits = sports[1:]
                        for leagues_cups in footy_leagues_cups:
                            tournys = leagues_cups.find_elements_by_xpath('.//a')    
                            for tourny in tournys:

                                league_link_text = tourny.get_attribute('href').lower()
                                if 'ligue-1-uber' in league_link_text:
                                    competettion = france_ligue1
                                    tourny.click()

                                elif 'premier league' in league_link_text:
                                    competettion = england_premier    
                                    tourny.click()

                                elif 'la liga' in league_link_text:
                                    competettion = spain_la_liga
                                    tourny.click()    

                                elif  'serie a'  in league_link_text:
                                    competettion = italy_serie_a
                                    tourny.click()

                                elif 'bundesliga' in league_link_text:
                                    competettion = germany_bundesliga
                                    tourny.click()

                                else:
                                    print('issue in getting any proper leagues or cup tputnies in competitions list...')
                                    continue                  


                # # then find -> competittions, here go to france - > ligue1

                ligue1_games_info_france_pari_try_1 = driver.find_elements_by_xpath('//*[@id="nb-sport-switcher"]/div[1]/div') 
        #       # TODO : need to actually make call into zebet champ league page t33o get champ_league_games_nested_gamesinfo_zebet:
                ligue1_games_info_france_pari_try_2 = driver.find_elements_by_xpath('//*[@id="colonne_centre"]/div/div/div[2]/div')         
                #for matches in  ligue1_games_infozebet:

                competition = compettition_
                ligue1_games_info_france_pari = ligue1_games_info_france_pari_try_1
                if not ligue1_games_info_france_pari_try_1:
                    ligue1_games_info_france_pari = ligue1_games_info_france_pari_try_2

                #pargame_elements = ligue1_games_info_france_pari[0].text.split('+')
                indx = 3
                for matches in  ligue1_games_info_france_pari:

                    game_info = matches.text.split('\n')
                    indx = 0
                    for i in range(len(game_info)):
                        teamName_check = [x for x in All_ligue1_team_list if find_substring(x, unidecode.unidecode(game_info[i].lower()))]
                        if teamName_check :
                            indx = i
                        else:
                            continue    

                        if len(game_info) >= 8 and '/' in game_info[indx]:
                            teams = game_info[indx].split('/')

                            if len(teams) < 2:
                                #print('No teams found -- either real issue or more likely - you are running the alert system with a match that is not in the betting card YET , please retry ...')
                                break
                            try:
                                teamA = comon_TeamNames_mapper[unidecode.unidecode(teams[0]).lower().strip()]
                                teamB = comon_TeamNames_mapper[unidecode.unidecode(teams[1]).lower().strip()]

                                teamAWinOdds = game_info[i+2]
                                draw_odds    = game_info[i+4]
                                teamBWinOdds = game_info[i+6]
                            except IndexError:
                                print("Error  non existant Index Error in france-pari site ..... ")
                                continue    
    
                        date = '23 decembre'
                        
                        full_all_bookies_allLeagues_match_data[ france_pari + '_' + unidecode.unidecode(date.lower()) + '_' + competition.lower() + '_' + teamA + ' - ' + teamB].append(float(teamAWinOdds.replace(',','.'))) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                        full_all_bookies_allLeagues_match_data[ france_pari + '_' + unidecode.unidecode(date.lower()) + '_' + competition.lower() + '_' + teamA + ' - ' + teamB].append(float(draw_odds.replace(',','.')))
                        full_all_bookies_allLeagues_match_data[ france_pari + '_' + unidecode.unidecode(date.lower()) + '_' + competition.lower() + '_' + teamA + ' - ' + teamB].append(float(teamBWinOdds.replace(',','.')))

                end_france_pari = time.time()     
                tot_france_pari +=  end_france_pari - start_france_pari
                print('time taken to process france_pari was = ' + str(end_france_pari - start_france_pari))    
            except NoSuchElementException:
                any_errors = False
                print("Error  caught in your FRANCE_PARI parse func. block call --  :( ..... ")
                continue

        start_betclic = time.time()            
        if  betclic in sites :
            print('in betclic ligue1 pre-match parsing .... \n \n')  

            # /html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details  
                                                                        
            ligue1_games_info_betclic   = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details/div')
            ## use this when generalizing leagues ...
            #ligue1_games_info_betclic_2  = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/app-left-menu/div/app-sports-nav-bar/div/div[1]/app-block/div/div[2]')    
            ligue1_games_info_betclic_1 = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details/div[1]/div')


            ## TODO : need to actually make call into zebet champ league page to get champ_league_games_nested_gamesinfo_zebet:
            #for matches in  ligue1_games_infozebet:
            #parts1 = ligue1_games_info_betclic[0].text.split('+')
            competition = compettition_
            second_route = False
            if not ligue1_games_info_betclic:
                second_route = True

            ## A whole new branch of code - relating to a change I  noticed in Betclic page-parsing since 01/02/2021
            if second_route:

                for panels in ligue1_games_info_betclic_1:

                    games_per_panel = panels.find_elements_by_xpath('.//app-event/div/a/div/div')
                    for matchs in  games_per_panel:

                        date = str(datetime.datetime.today()).split()[0] 
                        
                            ## Live string needs another branch to handle - diff indices for teams and odds as per 'match' string then being :
                            # ®\n37' - 1ère  mt\bordeaux\n1 - 1\nlorient\nrésultat du match\nbord\neaux\n2,15\nn\nul\n2,35\nlor\nient\n3,15\nquelle équipe marquera le but 3 ?\nbord\neaux\n1,75\npas de\n but\n4,10\nlor\nient\n2,25\n67\nparis\n"
                        info_per_match = matchs.text.split('\n')
                        if len(info_per_match) >= 13 :

                            ## !!! LIVE games change to be done as swmn here...

                            ## Live string needs another branch to handle - diff indices for teams and odds as per 'match' string then being :
                            # ®\n37' - 1ère  mt\bordeaux\n1 - 1\nlorient\nrésultat du match\nbord\neaux\n2,15\nn\nul\n2,35\nlor\nient\n3,15\nquelle équipe marquera le but 3 ?\nbord\neaux\n1,75\npas de\n but\n4,10\nlor\nient\n2,25\n67\nparis\n"
                            try:
                                teamA = comon_TeamNames_mapper[unidecode.unidecode(info_per_match[1] + info_per_match[2]).lower().strip()]
                                teamB = comon_TeamNames_mapper[unidecode.unidecode(info_per_match[9] + info_per_match[10]).lower().strip()]
                            except KeyError:
                                any_errors = False
                                print("Error  caught in your BETCLIC parse func.  -- keyError in team mapper  :( .....")
                                continue
                            
                            try:
                                teamAWinOdds = info_per_match[3]
                                draw_odds    = info_per_match[7]
                                teamBWinOdds = info_per_match[11]
                            except IndexError:
                                any_errors = False
                                print("Error  caught in 6your BETCLIC parse func.  -- IndexError in team mapper  :( .....")
                                continue

                            try:
                                full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA + ' - ' + teamB].append(float(teamAWinOdds.replace(',','.'))) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                                full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA + ' - ' + teamB].append(float(draw_odds.replace(',','.')))
                                full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA + ' - ' + teamB].append(float(teamBWinOdds.replace(',','.')))

                            except ValueError:
                                any_errors = False
                                print("Error  caught in your BETCLIC parse func. block call --  :( .....")
                                continue

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
                                teamA = comon_TeamNames_mapper[unidecode.unidecode(info_per_match[1]).lower().strip()]
                                teamB = comon_TeamNames_mapper[unidecode.unidecode(info_per_match[2]).lower().strip()]
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
                                full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA + ' - ' + teamB].append(float(teamAWinOdds.replace(',','.'))) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                                full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA + ' - ' + teamB].append(float(draw_odds.replace(',','.')))
                                full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA + ' - ' + teamB].append(float(teamBWinOdds.replace(',','.')))

                            except ValueError:
                                any_errors = False
                                print("Error  caught in your BETCLIC parse func. block call --  :( .....")
                                continue                                


            end_betclic = time.time()  
            tot_betclic += end_betclic - start_betclic
            print('time taken to process betclic was = ' + str(end_betclic - start_betclic))                 

        start_unibet = time.time()
        if  unibet in sites :
        # unibet tree struct to games elements:
            print('in unibet ligue1 pre-match parsing .... \n \n')  
            # Live ligue1 games...

            # //*[@id="page__competitionview"]/div/div[1]/div[2]/div/div/div 
            # team names and competitio nshud be in here

            #odds of game are then in :
            # //*[@id="b03b18c2-763c-44ea-aa2b-53835d043b8c"]/div
            ## full psath gfor this (odds) probly better
            #/html/body/div[1]/div[2]/div[5]/div/section/div/section/div/section/div/div[1]/div[2]/div/div/div/    section/div/ul/li/div/div/li/div/ul/ul/li/div[2]/div[2]/div/section/div/div
            
            # 3 'span' elements in here with odds
            # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
           
            try:

                wait_time37 = random.randint(3,6)
                #print('second rand wait time = ' + str(wait_time37))
                time.sleep(wait_time37)  

                ligue1_games_nested_gamesinfo_unibet_1 =  driver.find_elements_by_xpath('//*[@id="page__competitionview"]/div/div[1]/div[2]/div/div/div/div[3]/div[2]/div')  
                ligue1_games_nested_gamesinfo_unibet_2 =  driver.find_elements_by_xpath('/html/body/div[1]/div[2]/div[5]/div/section/div/section/div/section/div[1]/div/div[2]/div/div/div[2]/div[2]/div[1]/div/div')                                                                            #//*[@id="page__competitionview"]/div/div[1]/div[2]/div/div/div/div[3]/div[2] 
                time.sleep(wait_time12)                                                                         #//*[@id="page__competitionview"]/div/div[1]/div[2]/div/div/div/div[3]/div[2]
                ligue1_games_nested_gamesinfo_unibet_3 =  driver.find_elements_by_xpath('//*[@id="page__competitionview"]/div[1]/div/div[2]/div/div/div[2]/div[2]/div[1]/div')
                ligue1_games_nested_gamesinfo_unibet_4 =  driver.find_elements_by_xpath('//*[@id="page__competitionview"]/div[1]/div/div[2]/div/div/div[2]/div[2]')
                #print('in unibet and collected all ligue one games web element ! ... ')
                competition =  compettition_

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

                            teams =  comon_TeamNames_mapper[unidecode.unidecode(teamA_raw).lower()] + ' - ' + comon_TeamNames_mapper[unidecode.unidecode(teamB_raw).lower()]
                            #unidecode.unidecode(parts[i].split('\n')[-2]).lower()

                            if longer_info_match:
                                
                                teamAWinOdds = delimit_2[2]
                                draw_odds = delimit_2[5]                          
                                teamBWinOdds = delimit_2[8]
                            else:

                                teamAWinOdds = delimit_2[1].split(' ')[1]
                                draw_odds = delimit_2[2].split(' ')[1]                            
                                teamBWinOdds = delimit_2[3].split(' ')[1]                            

                            full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(float(teamAWinOdds))   
                            full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(float(draw_odds))    
                            full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(float(teamBWinOdds))  

                end_unibet = time.time()  
                tot_unibet += end_unibet - start_unibet
                print('time taken to process unibet was = ' + str( end_unibet - start_unibe ))                                

            except: #  NoSuchElementException:
                any_errors = False
                print("Error  ->  caught in your UNIBET parse func. block call --  :( ..... ")
                continue
            #check = 1

######################################################################
##            LATEAST TESTING CODE FOR LIVE LIGUE1  ON  ZEBET   
######################################################################            
        if  zebet in sites and 'live' in sites :
            competition =  compettition_
            date = 'LIVE'
    
        # #     ## NOTE live chgamp lieague hgames  on diff link when live - just normal football  page at top ! :
        # #       #  this link :   
        # #         ## This should be working, mas o menos, code for zebet live champions league           
        #         driver.quit() 
        #         driver.get('https://www.zebet.fr/fr/lives')

        #         # can see games here - check for frech team pairings -> click on sref link in //*[@id="lives"]/div (all live game group elements) -> then <a href = "link.....fr"  
        #         # # is directly in here and clickable

        #all live sports games as on 9/01 in :
        #//*[@id="lives"/artcle]

            live_football_gamesDiv = driver.find_elements_by_xpath('//*[@id="lives"]/article')
            for stuff in live_football_gamesDiv:
                #game_link =  stuff.find_element_by_xpath('//a href').text
                teamA = unidecode.unidecode(stuff.text.split('\n')[2]).lower()
                teamB = unidecode.unidecode(stuff.text.split('\n')[4]).lower() 
                teams = comon_TeamNames_mapper[teamA] + ' - ' + comon_TeamNames_mapper[teamB]  
                #live_odds_path =  stuff.find_element_by_xpath('//div/div[2]/a')

                ## check syntax !?....?
                #live_odds_match_link = odds_path.get('href')

                #then odds are given for home teAm to win or draw only ...??

                # can ue fact that sum of the 3 odds inverses should equal 1 to get :
                # odd away team to win :  1/odd_awat_team_to_win   = 1 - [1/(home_team_win) + 1/draw]
                # then do surebet calc as usual

                ## must click on and navigate on the lives odds link here :

                #then inspect @ //*[@id="live"]/article[1] - for win/draw odds  
                live_odds_game_info = stuff.text.split('\n')

                if teamA in All_ligue1_team_list and teamB in All_ligue1_team_list and len(live_odds_game_info) >= 11:
                    print('yes its a ligue 1 match -> follow link !')
                    # follow link code goes here...

                    teamAWinOdds = float(live_odds_game_info[7].replace(',','.'))
                    draw_odds    = float(live_odds_game_info[9].replace(',','.'))
                    teamBWinOdds = float(live_odds_game_info[11].replace(',','.'))
                    

                    full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                    full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(draw_odds)
                    full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(teamBWinOdds)


        #sites = "https://www.zebet.fr/en/competition/94-premier_league"
        if  zebet in sites and 'live' not in sites:
        # # zebet tree struct to games elements:                                                     
            print('in zebet ligue1 pre-match parsing .... \n \n')  
            try:
                                                                        #//*[@id="event"]/article[1]/div/div/div/div
                ligue1_games_infozebet = driver.find_elements_by_xpath('//*[@id="event"]/article/div/div/div/div/div') 
                ## TODO : need to actually make call into zebet champ league page to get champ_league_games_nested_gamesinfo_zebet:

                #will have to take out and pprocess leagues separately for zebet.
                #prem_leagueGames_info =  driver.find_elements_by_xpath('//*[@id="event"]/article/div/div/div/div/div/div[1]/div')                

                #parts1 = ligue1_games_infozebet[0].text.split('+')[0]
                for matches in  ligue1_games_infozebet:

                    game_info = matches.text.split('+')[0].split('\n')
                    if len(game_info) >= 8 :

                        date = unidecode.unidecode(game_info[0])
                        #handle case where the parser begins to mis-identify the ligue 1 winners betting...
                        if 'Winner' in date or "goalscorer" in date:
                            continue
                        
                        teamA = unidecode.unidecode(str(game_info[2]))
                        teamB = unidecode.unidecode(str(game_info[6]))
                        teamAWinOdds = float(game_info[1].replace(',','.'))
                        draw_odds    = float(game_info[3].replace(',','.'))
                        teamBWinOdds = float(game_info[5].replace(',','.'))
                        teams = comon_TeamNames_mapper[teamA.lower()] + ' - ' + comon_TeamNames_mapper[teamB.lower()]

                        full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                        full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(draw_odds)
                        full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(teamBWinOdds)

            except NoSuchElementException:
                any_errors = False
                print("Error  caught in your ZEBET parse func. block call --  :( ..... ")
                continue

        #full path copied from sourcecode tool       
        #/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div/div[2]
        start_winimax = time.time()
        if winimax in sites :        
            print('in winimax ligue1 pre-match parsing .... \n \n')   
                                                                                       
            ligue1_games_nested_gamesinfo_winimax = driver.find_elements_by_xpath('/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div/div')                                    
                                                                                  # /html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div  
            ligue1_games_nested_gamesinfo_winimax_2 = driver.find_elements_by_xpath('//*[@id="app-inner"]/span/div/div/div[2]/div/section/div/div[1]/div/div/div')                                                                    

            if not  ligue1_games_nested_gamesinfo_winimax:
                ligue1_games_nested_gamesinfo_winimax = ligue1_games_nested_gamesinfo_winimax_2                                                                    
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
                
                split_match_data_str = matches.text.split('\n')

                if len(split_match_data_str) >= 4:
                    # check_teams_in_str = [True for y in All_ligue1_team_list if find_substring(y,unidecode.unidecode(matches.text).lower())]

                    # if not check_teams_in_str:
                    #     continue
                    
                    separate_team_names = split_match_data_str[0].split(' vs ')
                    try:
                        teamA = comon_TeamNames_mapper[unidecode.unidecode(separate_team_names[0]).lower()]
                        teamB = comon_TeamNames_mapper[unidecode.unidecode(separate_team_names[1]).lower()]
                    except ValueError:
                        any_errors = False
                        print(" Value  Error  caught in mapper your winamax parse func. block call --  :( ..... ")
                        continue
                    except KeyError:
                        any_errors = False
                        print(" Key  Error  caught in mapper your winamax parse func. block call --  :( ..... ")
                        continue            

                    competition   =  compettition_ #split_match_data_str[1]    
                    try :

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

                    #if teams in locals() or teams in globals():    

                    full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teamA +  ' - ' + teamB].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                    full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teamA +  ' - ' + teamB].append(draw_odds)
                    full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teamA +  ' - ' + teamB].append(teamBWinOdds)

            end_winimax = time.time()  
            tot_winimax +=  end_winimax - start_winimax
            print('time taken to process winimax was = ' + str(end_winimax - start_winimax))

   ## TODO - games element not getting picked up by find_elements driver call - try somtin else or beuaty soup!    
        
        
        time.sleep(wait_time12) 
        ## somethin wrong with assumed html in link - think i must navigate all the way from base url with button click and hfers links etc

        start_cbet = time.time()  
        #print('time taken to process unibet was = ' + str(start_unibet - end_unibet))
        if cbet in sites :        
            time.sleep(wait_time12)
            #time.sleep(wait_time12)     
            #time.sleep(wait_time12) 
            #driver.implicitly_wait(13)
            
            #WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/section/section/ul/li')))

            ligue1_games_nested_gamesinfo_cbet = driver.find_elements_by_xpath('//*[@id="prematch-events"]/div[1]/div/section/section/ul/li')  
            time.sleep(wait_time12)   
            ligue1_games_nested_gamesinfo_cbet_2 = driver.find_elements_by_xpath('/html/body/main') #body/div[1]/div/div[2]/div[1]/div/section/section/ul') #'/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div/div[2]')                                    
            time.sleep(wait_time12) 

            ligue1_games_gamesinfo_cbet  = ligue1_games_nested_gamesinfo_cbet
            if not  ligue1_games_nested_gamesinfo_cbet:
                ligue1_games_gamesinfo_cbet = ligue1_games_nested_gamesinfo_cbet_2

            time.sleep(wait_time12) 
        
            #/html/body/div[1]/div/div[1]/div[1]/div[1]/ul/li[7]
            #/html/body/div[1]/div/div[2]/div[1]/div/section/section/ul    
            #//*[@id="prematch-events"]/div[1]/div/section/section/ul/li[1]
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
            time.sleep(wait_time12)
            #time.sleep(wait_time12)

            wait_time37 = random.randint(3,6)
            #print('second rand wait time = ' + str(wait_time37))
            time.sleep(wait_time37)  
                                                               
            league_selector =  driver.find_elements_by_xpath('//*[@id="prematch-top-leagues"]/ul/li')                    
            for leagues in league_selector:

                if 'Ligue 1' in leagues.text:
                    leagues.click()
                    break
                
            time.sleep(wait_time12)
            time.sleep(wait_time37) 
            #matches_soccer_info_2 = driver.find_elements_by_xpath('//*[@id="prematch-events"]/div[1]/div/section/section/ul/li')
            matches_soccer_info_2 =  driver.find_elements_by_xpath( '//*[@id="prematch-events"]/div[1]/div/section/section/ul/li')
            for matches in matches_soccer_info_2:

                split_match_data_str = matches.text.split('\n') 

                if len(split_match_data_str) >= 4:
                    teams = unidecode.unidecode(split_match_data_str[3]).lower().strip() # + unidecode.unidecode(split_match_data_str[5]).lower().strip(0)
                    #teams = split_match_data_str[2] #+ '_' + split_match_data_str[6]
                    try:
                        teams_split = teams.split('-')

                        if len(teams_split) == 2:
                            teamA = comon_TeamNames_mapper[unidecode.unidecode(teams_split[0]).strip()]
                            teamB = comon_TeamNames_mapper[unidecode.unidecode(teams_split[1]).strip()]
                            teams = teamA + ' - ' + teamB

                    except KeyError:
                        print('Key error caught in cbet parsing, continuing ...')
                        continue 

                    competition  =  compettition_ #split_match_data_str[1]    
                    print(split_match_data_str)
                    print('\n \n')

                    try:
                        teamAWinOdds = split_match_data_str[4].replace(',','.')
                        draw_odds    = split_match_data_str[5].replace(',','.')
                        teamBWinOdds = split_match_data_str[6].replace(',','.')
                    except IndexError:
                        print('Index error caught in cbet parsing, continuing ...')
                        continue    

                    #=
                        
                    try:    
                    
                        full_all_bookies_allLeagues_match_data[ cbet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(float(teamAWinOdds)) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                        full_all_bookies_allLeagues_match_data[ cbet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(float(draw_odds))
                        full_all_bookies_allLeagues_match_data[ cbet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(float(teamBWinOdds))
                    
                    except  ValueError:
                        print("error  in CBET site parsing... ") 

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
            print('in sports_bwin ligue1 pre-match prsing .... \n \n')
            competition_ = 'ligue 1'
            competition = competition_
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

                print(groups.text + '\n\n')

                #teams_element = groups.find_element_by_xpath("//div/a")
                #odds_element  = groups.find_element_by_xpath("//div/div")

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
                    teams =  comon_TeamNames_mapper[unidecode.unidecode(bwin_parts[0].split('\n')[-3]).lower()] + ' - ' +  comon_TeamNames_mapper[unidecode.unidecode(bwin_parts[0].split('\n')[-2]).lower()]   

                    teamAWinOdds = delimit_2[1]
                    time.sleep(wait_time12)
                    draw_odds = delimit_2[2]                           
                    teamBWinOdds = delimit_2[3]

                    time.sleep(wait_time12)
                    try:

                        full_all_bookies_allLeagues_match_data[sports_bwin + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower() ].append(float(teamAWinOdds))                
                        full_all_bookies_allLeagues_match_data[sports_bwin + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower() ].append(float(draw_odds))    
                        full_all_bookies_allLeagues_match_data[sports_bwin + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower() ].append(float(teamBWinOdds))  
                        #time.sleep(wait_time13)      
                    except  ValueError:
                        print("error  in sports.bwin site parsing... ")



        start_parion = time.time()                                          
# TODO - games element not getting picked up by find_elements driver call - try somtin else or beuaty soup!
        if parionbet in sites :          #.startswith('sports.bwin',8) or sites.startswith('sports.bwin'9) :
            print('in parionbet ligue1 pre-match prsing .... \n \n')
            compettition_ = "ligue1"
            #try:
            time.sleep(wait_time12)
            # relative path to all upcoming ligue 1 games    
            #resultParionElements = driver.find_elements_by_xpath('/html/body/div[2]/div[3]/wpsel-app/lib-sport-enligne/div[1]/wpsel-home/div')
            resultParionElements = driver.find_elements_by_xpath('/html/body/div[2]/div[3]/wpsel-app/lib-sport-enligne/div[1]/wpsel-sport/wpsel-sport-game/div/div/div[1]/section/div')   

            resultParionElements_2 = driver.find_elements_by_xpath(' /html/body/div[2]/div[3]/wpsel-app/lib-sport-enligne/div[1]/wpsel-sport/wpsel-sport-game/div/div/div')

            for block in resultParionElements_2:
                if '+' in block.text:
                    sections_dated = block.text.split('+')
                #     # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
                #end = timeit.time
                #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 

                    date = unidecode.unidecode(sections_dated[0].split('\n')[0])

                else:
                    sections_dated = block.text
                    if '\n' in sections_dated:
                        date = unidecode.unidecode(sections_dated.split('\n')[0])
                    else:
                        date = '01/Fevrier/2021'    

                for section in sections_dated:
                    if '\n' not in section:
                        continue
                    split_match_data_str = section.split('\n')    
                    #date = unidecode.unidecode(split_match_data_str[0])                    time.sleep(wait_time12)
                    #all_games =  games.find_elements_by_xpath('//ms-event')
                    #for game in all_games:
                    
                        #print(game.text)  
                    #split_match_data_str = games.text.split('\n') 

                    if len(split_match_data_str) >= 6:

                        if ' - ' in  split_match_data_str[1]:
                            separate_team_names = split_match_data_str[1].split(' - ')
                            try:
                                teamA = comon_TeamNames_mapper[unidecode.unidecode(separate_team_names[0]).lower()]
                                teamB = comon_TeamNames_mapper[unidecode.unidecode(separate_team_names[1]).lower()]
                            except KeyError:
                                print('KeyError in parionBet parsing, continuing on ...')
                                continue

                            if teamA in comon_TeamNames_mapper and teamB in comon_TeamNames_mapper:

                                date = unidecode.unidecode(split_match_data_str[2])
                                teams = teamA + ' - ' + teamB                          
                                competition =  compettition_ 

                                try:

                                    teamAWinOdds  = float(split_match_data_str[3].replace(',','.'))
                                    draw_odds     = float(split_match_data_str[4].replace(',','.'))
                                    teamBWinOdds  = float(split_match_data_str[5].replace(',','.'))

                                    full_all_bookies_allLeagues_match_data[ parionbet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                                    full_all_bookies_allLeagues_match_data[ parionbet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(draw_odds)
                                    full_all_bookies_allLeagues_match_data[ parionbet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(teamBWinOdds)

                                except ValueError:
                                    print('value error in parion in float casting odds...')    
                                    continue        

                        else:

                            if  ' - ' in  split_match_data_str[2]:
                                separate_team_names = split_match_data_str[2].split(' - ')

                                try:
                                    teamA = comon_TeamNames_mapper[unidecode.unidecode(separate_team_names[0]).lower()]
                                    teamB = comon_TeamNames_mapper[unidecode.unidecode(separate_team_names[1]).lower()]

                                except KeyError:
                                    print('KeyError in parionBet parsing, continuing on ...')
                                    continue

                                if teamA in comon_TeamNames_mapper and teamB in comon_TeamNames_mapper:

                                    date = unidecode.unidecode(split_match_data_str[0])
                                    teams = teamA + ' - ' + teamB                          
                                    competition =  compettition_                                    

                                    try:

                                        teamAWinOdds  = float(split_match_data_str[4].replace(',','.'))
                                        draw_odds     = float(split_match_data_str[5].replace(',','.'))
                                        teamBWinOdds  = float(split_match_data_str[6].replace(',','.'))
                                        
                                        full_all_bookies_allLeagues_match_data[ parionbet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                                        full_all_bookies_allLeagues_match_data[ parionbet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(draw_odds)
                                        full_all_bookies_allLeagues_match_data[ parionbet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(teamBWinOdds)

                                    except ValueError:
                                        print('value error in parion in float casting odds...')    
            
                                        continue      

            end_parion = time.time()  
            tot_parionbet +=  end_parion - start_parion
            print('time taken to process pmu was = ' + str(end_parion - start_parion )) 

        start_pmu = time.time() 
         ## canr SEEM TO RUN AT AL WHEN LIVE LIGUE ONE GAMES ARE ON !??                
        #https://paris-sportifs.pmu.fr/pari/competition/169/football/ligue-1-uber-eats%C2%AE
        if paris_sportifs_pmu[8:26] in sites :          #.startswith('sports.bwin',8) or sites.startswith('sports.bwin'9) :
            print('in pmu ligue1 pre-match prsing .... \n \n')
            competition = "ligue1"


            # relative path to all upcoming ligue 1 games    
            try:
                resultPmuElements = driver.find_elements_by_xpath("//*[contains(@class,'ms-active-highlight')]")
                time.sleep(wait_time12)
                resultPmuElements_1 = driver.find_elements_by_xpath("//*[@id='tabs-second_center-block-0']/div/div/div/div/div/div/div/div")
            except StaleElementReferenceException:
                print('value error in parion in float casting odds...')    
                continue 
            
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
                matches = games.split('//')            
                if len(matches) >= 2 :

                    #for match in matches :
                    single_game_left  = matches[0].split('\n')
                    single_game_right = matches[1].split('\n')

                    if len(single_game_left) < 1 or len(single_game_right) < 4:
                        break
                    
                    #time.sleep(wait_time12)
                    teamA = comon_TeamNames_mapper[unidecode.unidecode(single_game_left[-1]).lower().strip()]
                    teamB = comon_TeamNames_mapper[unidecode.unidecode(single_game_right[0]).lower().strip()]
                    #time.sleep(wait_time12)
                    try:
                        teamAWinOdds = float(single_game_right[1].replace(',','.'))
                        draw_odds    = float(single_game_right[2].replace(',','.'))
                        teamBWinOdds = float(single_game_right[3].replace(',','.'))

                    except ValueError:
                        print('value error in parion in float casting odds...')    
                        continue

                    #time.sleep(wait_time12)
                    teams = teamA + ' - ' + teamB

                    full_all_bookies_allLeagues_match_data[ paris_sportifs_pmu[8:26].lower() + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                    full_all_bookies_allLeagues_match_data[ paris_sportifs_pmu[8:26].lower() + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(draw_odds)
                    full_all_bookies_allLeagues_match_data[ paris_sportifs_pmu[8:26].lower() + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(teamBWinOdds)

            end_pmu = time.time()  
            tot_pmu +=  end_pmu - start_pmu
            print('time taken to process pmu was = ' + str(end_pmu - start_pmu))
        #     except NoSuchElementException:
                # any_errors = False
                # print("Error  caught in your pmu sports parse func. block ..... :( ")
                # continue 

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

            retVal = odds_alert_system(oddType= int(argv[1]), expect_oddValue= float(argv[2]), teamA= argv[3], teamB= argv[4], date= argv[5], competition= argv[6], Bookie1_used= argv[7])

        elif  len(argv) == 2 :

            retval2 = check_for_sure_bets(float(argv[1])) 

        else:

            #print("usage:  please indicate with  0 or a 1 in the first cmd line argument to the program wherether you wish to include debugging output prints in it's run or not; 0/1 corresponding to no/yes....")
            print("Usage : sportsbetAlertor_v1.py oddType (0 -home team win, 1 - a dra. 2 - away team win ) expect_oddValue teamA teamB competition Bookie1_used.    i.e 7 parameters on thye cmd line after the filename")
            print("Heres an Example --- sportsbetAlertor_v1.py  0 1.75  lyon  marseille  ligue1 Winamax")
            exit(1)
   
    else:    
        #DEBUG_OUTPUT = bool(int(argv[1]))
        retval2 = check_for_sure_bets() #'unibet','zebet','winimaxc','W', 'D','marseilles','nantes','28/11/2020','ligue 1 UberEats')


