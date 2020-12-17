import msvcrt
import random
#from bs4 import BeautifulSoup
import re
import smtplib
import time
import timeit
from collections import defaultdict
from smtplib import SMTPException

import requests
import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import itertools
import sys,os
#from scraper_api import ScraperAPIClient
import datetime, unidecode
from googletrans import Translator

# init the Google API translator
translator = Translator()

from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
req_proxy = RequestProxy() #you may get different number of proxy when  you run this at each time
proxies = req_proxy.get_proxy_list()

# define global init 'surebet' condition value (note by default any bet will not be a surebet given its > 1.0)
surebet_factor = 0.0
#cibstant initialised to False - for determining if they customer's expected odds are retrieved for alert system...
odd_are_found = False

#client = ScraperAPIClient('781fa06f6c29968fe2971fa6a90760dc')
#respondsr = client.get(url = "https://france-pari.fr/")
#print(result)


def check_is_surebet(*args): #odds_A, odds_B):

    total_iverse_odds_sum = 0.0
    for odds in args:
        if odds == 0:
            pass
        else:
            total_iverse_odds_sum += 1/(odds)

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
            pass
        else:
            surebet_factor += 1/(odds)

    print('in get surebet function -- surebet = ' + str(surebet_factor))

    return surebet_factor


def return_surebet_vals(*argv, stake):  #odds_A, odds_B,stake):

    surebetStakes = []

    for i,odds in enumerate(argv):

        if odds == 0.0 or surebet_factor == 0.0 :
            surebetStakes[i]  = stake
        else:    
            surebetStakes[i] = (1/surebet_factor)*(stake/odds)
                                                                                       
    return surebetStakes


## TODO : must generalize this and add file to code bundle
DRIVER_PATH = r'./chromedriver' #the path where you have "chromedriver" file.


#driver = webdriver.Chrome(executable_path=DRIVER_PATH)

options = Options()
options.headless = True
options.LogLevel = False
options.add_argument("--window-size=1920,1200")

driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

#remove?as done below for site's direct champ league url!

#ret = driver.get("https://france-pari.fr/")


## Class definitions :

# class ExtractorDataParser:
#     """Loads a CSV data file and provides functions for working with it"""

#     def __init__(self):
#         self.clear()

#     def clear(self):
#         # Records is a multidimensional dictionary of: records[frame_number][face_number][roi][signal] = value
#         self.records = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list))))
#         self.first_frame_number = sys.maxsize
#         self.last_frame_number = 0
#         self.number_frames = 0
#         self.meta_data = []
#         self.missing_records = []

#     def loadFile(self, filename):
#         self.clear()

#         if not (os.path.isfile(filename) and os.access(filename, os.R_OK)):
#             raise ValueError("Unable to read file '%s'" % filename )


    # def process_comment_record(self, record):
    #         # Ignore the pose information and the face rectangles
    #         if record[0].startswith( '#P:' ) or record[0].startswith( '#R:' ):
    #             return

    #         if record[0].startswith( '#M:'):
    #             record_number = int(record[0][3:])
    #             self.missing_records.append(record_number)
    #             return

    #         # Must be metadata, strip the leading #
    #         index = record[0].index(':')
    #         name = record[0][1:index]
    #         value = record[0][index+1:]
    #         metaString=name+" : "+value
    #         self.meta_data.append(metaString)

    #     def get_first_frame_number(self):
    #         """First frame number encountered when loading file"""
    #         return self.first_frame_number

    #     def get_last_frame_number(self):
    #         """Last frame number encountered when loading file"""
    #         return self.last_frame_number

    #     def get_number_frames(self):
    #         """Number of frames loaded from file."""
    #         return len(self.records)

    #     def get_missing_records(self):
    #         return self.missing_records

    #     def get_meta_data(self, key):
    #         try:
    #             return self.meta_data[key]
    #         except KeyError:
    #             return ""      


# Cbet general home page link :
# 
cbet_sports_link = "https://cbet.gg/en/sportsbook/prematch"   


###  *********************************** CHAMPION'S LEAGUE lINKS *****************************
#list of website links (most general for football mathces-1st few are for champions league)
france_pari_champions_league_link =  "https://www.france-pari.fr/competition/6674-parier-sur-ligue-des-champions"
# d lads dont want this site as it's shite.
#vbet_champions_league_link        = "https://www.vbet.fr/paris-sportifs?btag=147238_l56803&AFFAGG=#/Soccer/Europe/566/17145852"
unibet_champions_league_link       = "https://www.unibet.fr/sport/football/ligue-des-champions/ligue-des-champions-matchs"
zebet_champions_league_link        = "https://www.zebet.fr/fr/competition/6674-ligue_des_champions"
winimax_champions_league_link      = "https://www.winamax.fr/en/sports-betting/sports/1/800000006"

#passionsports__champions_ligue_link = "" 
sportsbwin_champs_ligue_link       = "https://sports.bwin.fr/fr/sports/football-4/paris-sportifs/europe-7/ligue-des-champions-0:3"

#betclic_champs_ligue_link         = ""
#pokerstarsSports_ligue1_link      = ""
#pasinoBet_ligue1_link             = ""

###  *********************************** LIGUE' 1  lINKS *****************************

betclic_ligue1_link       = "https://www.betclic.fr/football-s1/ligue-1-uber-eats-c4"
france_pari_ligue1_link   = "https://www.france-pari.fr/competition/96-parier-sur-ligue-1-uber-eats"
unibet_ligue1_link        = "https://www.unibet.fr/sport/football/france-foot/ligue-1-ubereats-france"
zebet_ligue1_link         = "https://www.zebet.fr/en/competition/96-ligue_1_uber_eats"
winimax_ligue1_link       = "https://www.winamax.fr/en/sports-betting/sports/1/7/4"
passionsports_ligue1_link = "https://www.enligne.parionssport.fdj.fr/paris-football/france/ligue-1-uber-eats?filtre=22892"
sportsbwin_ligue1_link    = "https://sports.bwin.fr/fr/sports/football-4/paris-sportifs/france-16/ligue-1-4131"
cbet_ligue1_link          = "https://cbet.gg/en/sportsbook/prematch"

#betclic_ligue1_link       = ""
#pokerstarsSports_ligue1_link = ""
#pasinoBet_ligue1_link        = ""

###  *********************************** EUROPA LEAGUE lINKS *****************************
#list of website links (most general for football mathces-1st few are for champions league)
france_pari_europa_league_link   =  "https://www.france-pari.fr/competition/6674-parier-sur-europa-ligue"   #(?? - check this !!)
# d lads dont want this site as it's shite.
#vbet_champions_league_link        = "https://www.vbet.fr/paris-sportifs?btag=147238_l56803&AFFAGG=#/Soccer/Europe/566/17145852"
unibet_europa_league_link           =  "https://www.unibet.fr/sport/football/europa-league/europa-league-matchs"
zebet_europa_league_link            =  "https://www.zebet.fr/en/competition/6675-europa_league"
winimax_europa_league_link          =  "https://www.winamax.fr/en/sports-betting/sports/1/800000007"
passionsports_europa_league_link    = "https://www.enligne.parionssport.fdj.fr/paris-football"
sportsbwin_europa_league_link       = "https://sports.bwin.fr/fr/sports/football-4/paris-sportifs/europe-7/europa-league-0:5"    
betclic_europa_league_link          = "https://www.betclic.fr/football-s1/ligue-europa-c3453"

#pokerstarsSports_europa_league_link = ""
#pasinoBet_europa_league_link        = ""

## name consistent Champ and Europa league team names:
#England
manchester_utd   = "manchester united"
manchester_city  = "manchester city"
chelsea          = "chelsea"
liverpool        = "liverpool"

#Espana
real            = "real madrid"
barcelona       = "barcelona"
sevilla         = "sevilla"
atletico_madrid = "atletico madrid"

#Italia
juventus    = "juventus"  
atalanta     = "atalanta"  
lazio        = "lazio"

#Germany
bayern_munich    = "bayern munich" 
dortmund         = "dortmund" 
munchen_flapjack = "bayern munchengladback"
leipzig          = "rb leipzig"

#France
paris_germain        = "paris st germain"

## russia/Ukraine
shaktar          = "shaktar donetsk"
dynamo_kiev      = "dynamo kiev"
krasnodar        = "fc krasnodar"

## Portugal / Greece / Turkey / Holland / Austria / Belgium/ Hungary  Denmark
porto                = "fc porto"
olympiakos           = "olympiakos"
ajax                 = "ajax"
salzburg             = "rb salzburg"
club_brugge          = "club brugge"



# english_to_french_mapper = {}
# english_to_french_mapper[club_brugge] = 'club bruges'
# english_to_french_mapper[lokomotiv] = 'lokomotiv_moscou'
# english_to_french_mapper[zenit_st_peters] = 'zenit saint petersbourg'
# english_to_french_mapper[barcelona] = 'barcelone'
# english_to_french_mapper[salzburg] = 'rb salzbourg'
# english_to_french_mapper[salzbourg] = 'rb salzbourg'


# english_to_french_mapper[] = 
# english_to_french_mapper[] = 
# english_to_french_mapper[] = 
# english_to_french_mapper[] = 
# english_to_french_mapper[] = 
# english_to_french_mapper[] = 
# english_to_french_mapper[] = 



#same order as data structures in their list
websites_champs_league_links = [france_pari_champions_league_link, unibet_champions_league_link, zebet_champions_league_link,winimax_champions_league_link, sportsbwin_champs_ligue_link]  # haS 5 LINKS NOW
websites_europa_league_links = [france_pari_europa_league_link, unibet_europa_league_link, zebet_europa_league_link,winimax_europa_league_link, sportsbwin_europa_league_link] # 7 links
websites_ligue1_links        = [france_pari_ligue1_link, unibet_ligue1_link, zebet_ligue1_link,winimax_ligue1_link, sportsbwin_ligue1_link, betclic_ligue1_link,cbet_ligue1_link] #,passionsports_ligue1_link] # 7 links m       # betclic_ligue1_link is empty for now

reference_champ_league_games_url = str(websites_champs_league_links[0])
driver.get(reference_champ_league_games_url)

# some vars for parsing the games data - strings.
#initialize data with todays date - better than empty string
date = '2 Decembre'
compettition = 'Ligue des Champions'    

# TODO :rename like actual sites 

# refernce_champ_league_gamesDict = defaultdict(list) # pari-france site
# #site_unibet_champ_league_gamse  = defaultdict(list)
# sites_zebetchamp_league_gamse   = defaultdict(list)
# unnibet_champ_league_gamse      = defaultdict(list)
# winimax_champ_league_gamse      = defaultdict(list)


# sportsbwin_champ_league_gamse   = {}
# site7s_champ_league_gamse       = {}
# site8s_champ_league_gamse       = {}    
# site9s_champ_league_gamse       = {}
# site10s_champ_league_gamse      = {}
# site11s_champ_league_gamse      = {}
# site12s_champ_league_gamse      = {}

full_all_bookies_allLeagues_match_data = defaultdict(list)
all_split_sites_data = []

#all_srpaed_sites_data = [refernce_champ_league_gamesDict, winimax_champ_league_gamse, sites_zebetchamp_league_gamse, unnibet_champ_league_gamse] #, site5s_champ_league_gamse]

#bookie 'nicknames'
zebet = 'zebet'
unibet = 'unibet'
winimax = 'winamax'
betclic = 'betclic'
france_pari = 'pari'
sports_bwin = 'sports.bwin'
pasinobet = 'pasinobet'
cbet      = 'cbet'


def odds_alert_system(oddType=1,expect_oddValue=1.0,teamA='Liverpool',teamB='barcelone',date='Mercredi 25 Novembre',competition='Ligue des Champions',Bookie1_used='winmax',Bookie2_used=''):

    #global refernce_champ_league_gamesDict, site_unibet_champ_league_gamse, sites_zebetchamp_league_gamse, site4s_champ_league_gamse, site5s_champ_league_gamse

    global full_all_bookies_allLeagues_match_data, all_split_sites_data # ,all_srpaed_sites_data
        
    #justParsed = False
    #remove bookies uused:
    #all_srpaed_sites_data.remove(Bookie1_used)
    #if(Bookie2_used):
    #    all_srpaed_sites_data.remove(Bookie2_used)
  
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
        for site_data in all_split_sites_data:

            for key in site_data.keys():
                if Bookie1_used in key:
                    break
                
                # store the bookie's name so as to send onto Paul et al to double check & place the bet...
                bookie_name = key.split('_')[1]  

                X = 0
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
                            print('issue with finding /checking the expected odd across all data and sites...')
                            return False
   
    return True

W_1 = 'Home team (1st team name on the betting card) to win'
W_2 = 'Away team (2nd team name on the betting card) to win'
D   = 'A dwraw between the team in the 90 minutes'
L_1 = 'Home team (1st team name on the betting card) to lose'
L_2 = 'Away team (2nd team name on the betting card) to lose'

def check_for_sure_bets():

    #global refernce_champ_league_gamesDict, site_unibet_champ_league_gamse, sites_zebetchamp_league_gamse, site4s_champ_league_gamse, site5s_champ_league_gamse

    global all_split_sites_data, DEBUG_OUTPUT



    #remove bookies uused:
    
    #all_srpaed_sites_data.remove(Bookie1_used)
    #if(Bookie2_used):
    #    all_srpaed_sites_data.remove(Bookie2_used)

    #sub_strs_in_key = [date.lower(),competition.lower(),teamA.lower(),teamB.lower()]

    # search for game (and competition and date to ensure uniqueness) on ref. site:

    # initialize proxy count and create list of proxies from the prox generator
    PROXY_COUNTER = 0
    k = 0
    proxies = req_proxy.get_proxy_list()
    while(True):

        if PROXY_COUNTER == len(proxies) - 1:
            proxies = req_proxy.get_proxy_list()

        PROXY = proxies[PROXY_COUNTER].get_address()
        print("Proxy address = ******************************** %s ************************************ %d",PROXY,k)
        
        driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

        webdriver.DesiredCapabilities.CHROME['proxy']={
            "httpProxy":PROXY,
            "ftpProxy":PROXY,
            "sslProxy":PROXY,
            "proxyType":"MANUAL",
        }
        PROXY_COUNTER += 1
        k += 1

        # intro randomness to not get caught ! - lol
        wait_time = random.randint(1,3)
        time.sleep(wait_time)
        
        #print('Click on the "esc" key @ any time to terminate this program and can then restart again any time you wish :) ......')

        # waitr a delay time to refresh sites parsings....
        if parseSites(driver): #all_srpaed_sites_data):
            pass
        else:
            print("Error i parsing function...retring... But needs diagnostics and/or a fix ! ...")
            continue
        
        ## !!! THIS PIECE OF CODE SEEMS TO BE BREAKING THE PROGRAM - CAUSING IT TO HAVE VERY UNDEFINED RUNTIME BEHAVIOUT ???     
        # if msvcrt.getch() == 'esc':
        #     print('Esc key pressed , stopping and exiting the constant Alert with odds function ....')
        #     break

        # for site_data in all_srpaed_sites_data:
        #     # fix one and find other combos of remaining 2...

        #     rmv_all_srpaed_sites_data = all_srpaed_sites_data.remove(site_data)
        #     #for key in site_data.keys():
            #for site_1,site_2 in all_srpaed_sites_data
                #bookie_name = key.split('_')[1]  

        ## removed - commented out old version fpr now ..        
        # for site_data in full_all_bookies_allLeagues_match_data:
        # # fix one and find other combos of remaining 2...
        #     rmvRef_all_srpaed_sites_data = full_all_bookies_allLeagues_match_data.pop(site_data)
 
        ## TODO  - a biggg TODO  -- convert this to just the combos of 3 and exclude this loop above ...09
  
    
        wait_time = random.randint(1,2)
        time.sleep(wait_time)
        
        if len(all_split_sites_data < 3):
            print('*************************** Error - less than three bookies scrapped for games here ..., try again -- if this error persists raise a bug ******************************')
            return False
  
        for subset in itertools.combinations(all_split_sites_data, 3):  
            #filter unique games across dicts/sites using the key from a fixed one ....   

            subsetList = list(subset)                          
            if (DEBUG_OUTPUT and len(subsetList) >= 3):
                print('subset[0] = ' + str(subset[0])) 
                print('subset[1] = ' + str(subset[1])) 
                print('subset[1] = ' + str(subset[1])) 

            second_bookie_keys = subsetList[1].keys() 
            third_bookie_keys  = subsetList[2].keys()         

            bookie_2 = ''
            for keys in second_bookie_keys:
                bookie_2 = keys.split('_')[0]
                break

            bookie_3 = ''        
            for keys in third_bookie_keys:
                bookie_3 = keys.split('_')[0]
                break

            if len(subsetList) >= 3:    

                for key in subsetList[0]:    

                    bookie_1 = key.split('_')[0]
                    date_1 = key.split('_')[1]
                    competition_1 = key.split('_')[2]
                    teamA_1 = key.split('_')[3].split(' - ')[0]
                    teamB_1 = key.split('_')[3].split(' - ')[1]

                    unique_math_identifiers = [competition_1,teamA_1,teamB_1]   # [date_1,competition_1,teamA_1,teamB_1]

                    if DEBUG_OUTPUT :
                        print('site_data key = ' + str(key)) 

                    # second_bookie_keys = subsetList[1].keys() 
                    # third_bookie_keys  = subsetList[2].keys() 
                    # 
                    
                    #truth_list_subStrKeysDict2 = [key for key,val in second_bookie_keys if (unique_math_identifiers[0] and unique_math_identifiers[1] and unique_math_identifiers[2])  in key]  

                    truth_list_subStrKeysDict2 = [key for key,val in subsetList[1].items() if (unique_math_identifiers[0] in key and unique_math_identifiers[1] in key and unique_math_identifiers[2] in key)]
                    if len(truth_list_subStrKeysDict2) > 0:
                        key_bookkie2 = truth_list_subStrKeysDict2[0]

                    #truth_list_subStrKeysDict2 = [key for key,val in second_bookie_keys if (unique_math_identifiers[0] and unique_math_identifiers[1] and unique_math_identifiers[2])  in key]  

                    truth_list_subStrKeysDict3 = [key for key,val in subsetList[2].items() if (unique_math_identifiers[0] in key and unique_math_identifiers[1] in key and unique_math_identifiers[2] in key)]
                    if len(truth_list_subStrKeysDict3) > 0:
                        key_bookkie3 = truth_list_subStrKeysDict3[0]                    

                ## check i stest for now here... !! re - undo former statement test after    
                    if len(second_bookie_keys) > 0 :  #(all(unique_math_identifiers) in second_bookie_keys and bookie_1 not in second_bookie_keys) and (all(unique_math_identifiers) in third_bookie_keys and bookie_1 not in third_bookie_keys ) :

                        # parse key for teams, date and competition:
                        ##  ??  parse code her ??\ ---  m ads MUST CHECk you are seaching the exact same UIQUE match.
                        # bookie_2 = second_bookie_keys[0].split('_')[0]
                        # bookie_3 = third_bookie_keys[0].split('_')[0]

                        #if bookie_1 == bookie_2 or bookie_1 == bookie_1 or bookie_1 == bookie_1:

                        if check_is_surebet(subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2]):  # encode bookie outcomes as 'W','D','L' wrt to the 1st team in the match descrpt. , i.e The 'hometeam'    
                            send_mail_alert_gen_socer_surebet(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1)

                        if check_is_surebet(subsetList[0][key][0],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][1]):
                            send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,W_1,W_2,teamA_1, teamB_1, date,competition_1)

                        if check_is_surebet(subsetList[0][key][1],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][2]):
                            send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,D,W_1,teamA_1, teamB_1, date,competition_1) 

                        if check_is_surebet(subsetList[0][key][1],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][0]):
                            send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,D,W_2,teamA_1, teamB_1, date,competition_1) 

                        if check_is_surebet(subsetList[0][key][2],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][1]):
                            send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,W_2,W_1,teamA_1, teamB_1, date,competition_1)                            

                        if check_is_surebet(subsetList[0][key][2],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][0]):
                            send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,W_2,D,teamA_1, teamB_1, date,competition_1)                            

            else:
                print("Not enough bookies scraped correctly to look for 3 - way surebets...")


    ## can't recall purpose of this shite... ??
    #print(subset)  
    #site_data[key][oddType]

    return True

## TODO :
# def try_catch_function():
#     exceptionBool = False

#     return exceptionBool

#if only soing 2 - way sure bet , then oddDraw can be set to -1 and used as such when read in here
def send_mail_alert_odds_thresh(win_lose_or_draw,init_oddA,expect_oddB,teamA,teamB,date,competition,bookiesNameEventB):

    global DEBUG_OUTPUT
    successFlag = False
    sender = 'godlikester@gmail.com'
    receivers = ['crowledj@tcd.ie']#'pauldarmas@gmail.com']

    home_or_away = 'AWAY'
    if win_lose_or_draw != 1:

        if win_lose_or_draw == 0:
            # swap team names as default here is away teams -B to win

            tmp = teamA
            teamA = teamB
            teamA = tmp
            home_or_away = 'HOME'

        else: # case is oddType (win_losr draw) == 2 and leave team names (home away order as they are @ input)
            pass
        message = """From: From Person <from@fromdomain.com>
        To: To Person <to@todomain.com>
        Subject: SMTP e-mail test

        The is an Alert to tell you that the bookmaker - 
        """  + str(bookiesNameEventB) + """ had its odd's on the """ + home_or_away + """ team --   """  + str(teamB) + """ to WIN the event against   """ + str(teamA) + """ \
           in the competition """  + str(competition) + """ reach a value of """ + str(expect_oddB) +  """ or greater at approx.
         5 - 10 seconds before this receipt of the email Alert """ 

    else: # draw case
        
        message = """From: From Person <from@fromdomain.com>
        To: To Person <to@todomain.com>
        Subject: SMTP e-mail test

        The is an Alert to tell you that the bookmaker - 
        """  + str(bookiesNameEventB) + """ had its odd's ON A DRAW between the away team --  """ + str(teamB) + """ and the home team --  """ + str(teamA) + """ \
          in the competition  """  + str(competition) + """ reach a value of """ + str(expect_oddB) +  """ or greater at approx. 
         5 - 10 seconds before this receipt of the email Alert """ 

    try:
        smtpObj = smtplib.SMTP_SSL("smtp.gmail.com",465)
        smtpObj.login("godlikester@gmail.com", "Pollgorm1")
        smtpObj.sendmail(sender, receivers, message)     

        if DEBUG_OUTPUT :
            print("Successfully sent email")

        successFlag = True
    except SMTPException:
        print("Error: unable to send email")
        pass

    return successFlag


def send_mail_alert_gen_socer_surebet(bookie_1,bookie_2,bookie_3,bookie_one_outcome, bookie_2_outcome,teamA,teamB,date,competition):

    global DEBUG_OUTPUT
    successFlag = False
    sender = 'godlikester@gmail.com'
    receivers = ['crowledj@tcd.ie']#'pauldarmas@gmail.com']

    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    The is an Alert to tell you that a three-way soccer sure bet exists between --""" + str(teamA) + """ and  """ + str(teamB) + """  in the event """ + str(competition) + """  \
    on the date  """ + str(date) + """  the bet will involve placing a bet on """ + str(bookie_one_outcome) + """  in the bookies - """ + str(bookie_1) + """ and on the outcome """ \
    + str(bookie_2_outcome) + """ in the """ + str(bookie_2) +  """ bookie and final 3rd bet left in  """ + str(bookie_3)

    try:
        smtpObj = smtplib.SMTP_SSL("smtp.gmail.com",465)
        smtpObj.login("godlikester@gmail.com", "Elnino_9")
        smtpObj.sendmail(sender, receivers, message)         
        print("Successfully sent email")
        successFlag = True
    except SMTPException:
        print("Error: unable to send email")
        pass

    return successFlag


def parseSites(driver): 

    global websites_champs_league_links, compettition, date, refernce_champ_league_gamesDict, full_all_bookies_allLeagues_match_data, DEBUG_OUTPUT, all_split_sites_data

    # reset full league dict so as not to keep appending to it below
    full_all_bookies_allLeagues_match_data.clear()

    any_errors = True
    ret = driver.get(france_pari_champions_league_link)

    # if not ret:
    #     print("Error  -> caught in your driver.get() call to france-pari website... :( ")
    #     any_errors = False
    #     return any_errors

    # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
    try:
        driver.find_elements_by_xpath("/html/body/div[@id='main']/section[@id='colonne_centre']/div[@class='nb-middle-content']/div/div[@class='bloc-inside-small']/div[@id='nb-sport-switcher']/div[@class='item-content uk-active']") #/div[@class='odd-event uk-flex']")
    
    except: # err as NoSuchElementException:

        print("Error  -> caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
        any_errors = False
        pass
        #continue
    # pick up date and competetion 1st beofre list of games:

    date_element = driver.find_element_by_xpath('//p[@class="date soccer"]')

    if date_element:
        print('game DATE names element block exists ! :) ...')
        
        try:
            Date = date_element.text
            # update global date hetre as this site has it reliably - (for others)
            date = Date

        except: # err as NoSuchElementException:
            any_errors = False
            print("Error  -> caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
            pass
    else:
        print('NAAH --  game href DATE element block DOESN"t exist :( ... ')    

    #.text
    competition = driver.find_element_by_xpath('//h2[@class="competition soccer"]').text
    #driver.back()
    champ_league_games_pariFrance_list = driver.find_elements_by_xpath("//div[@class='odd-event uk-flex']")


    #now loop thru all champ league games on france-pari site
    for j,games in enumerate(champ_league_games_pariFrance_list):

        team_names_element = False
        try:
            team_names_element = games.find_element_by_tag_name('a')  #//span[@class="bet-libEvent]') #/a') #.get_attribute("href")
            #div[@class="odd-event-block snc-odds-date-lib uk-flex"]/span/
        except: # err as NoSuchElementException:
            any_errors = False
            print("Error  -> caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
            pass

        if team_names_element:

            if DEBUG_OUTPUT:
                print('game href names element block exists ! :) ...')
            
            try:
                team_names_string = team_names_element.get_attribute("href")
            
            except: # err as NoSuchElementException:
                any_errors = False
                print("Error  -> caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
                pass
        else:
            print('NAAH --  game href names element block DOESN"t exist ! :( ... ')    


        split_game_data_str = games.text.split('\n') 

        odds_string_teamA = float(split_game_data_str[3].replace(',','.'))
        odds_string_teamB = float(split_game_data_str[7].replace(',','.'))
        odds_string_draw =  float(split_game_data_str[5].replace(',','.'))

        #test: leave orig. version here for now , but replace with the default dict loist way a few lines ahead...
        #refernce_champ_league_gamesDict[date + '_' + competition + '_' + team_names_string] = odds_string_teamA + '_' + odds_string_draw + '_' + odds_string_teamB
        full_all_bookies_allLeagues_match_data[ france_pari + '_' + date.lower() + '_' + competition.lower() + '_' + team_names_string.split('parier-sur-')[1].lower()].append(odds_string_teamA) 
        full_all_bookies_allLeagues_match_data[ france_pari + '_' + date.lower() + '_' +  competition.lower() + '_' + team_names_string.split('parier-sur-')[1].lower()].append(odds_string_draw)
        full_all_bookies_allLeagues_match_data[ france_pari + '_' + date.lower() + '_' +  competition.lower() + '_' + team_names_string.split('parier-sur-')[1].lower()].append(odds_string_teamB)

    if DEBUG_OUTPUT:
        print('all good the find_elements_by_xpath Call worked GRAND !! :) --- full champ league games data struct = ')
        print(refernce_champ_league_gamesDict)



    # !!!  NOTE : 'imn-play' live games have different structure of element style and content position in html tree ...
    #//*[@id="liveshome"]/div[1]
    # eg live sports panel for france-pari are in :      //*[@id="liveshome"]/div[1]/
    # this cpntains list of sub divs with all live sports event, some , usually first div has its @class string contin the word 'soccer' ->  then into a div (1st) -> a tag (with title string containing treams names and event 
    # , here Ligue de champions .)  Then lives odds are in :    //*[@id="liveshome"]/div[1]/div[1]/div/div/div/div[2]/div[1]/div/a/span[2]
    # this is basically just   

    #  -> two divs within this location contain team 1 , then next inner div - teAM 2'S NAME 


    #login_form =  driver.find_element_by_id("PARIS SPORTIFS")

    #############################     TEST ALERT - send to Paul darmas    #############################

    #send Alert to paul's mail:
    #send_mail_alert(2.5,3.25,'Liverpool','Barcelona','01/04/2021','Champions League','Unibet')

    #############################     TEST ALERT - send to Paul darmas    #############################

    # #Next loop thru all other SITE's champ league games besides  france-pari site as its the reference to compare to...



################# ***********************################# ***********************################# ***********************################# ***********************################# ***********************
################# *************************** START of Euro cups sites beyong pari *******************************########################################
################# ***********************################# ***********************################# ***********************################# ***********************################# ***********************

    

    # for i,sites in enumerate(websites_champs_league_links[1:]):

    #     #begin = timeit.timeit()  
    #     driver.get(sites)
    #     #finish = timeit.timeit()

    #     if  unibet in sites :

    #     ## NOTE unibet live champ league games live in :  
    #     #  all games are nested in li's of //*[@id="sportsoverviewlist"]/li/div/div/li/div[1]/ul/ul/ :   li[0] , li[1],.. 
    #     # (team names in 2 on;ly sub divs of)  //*[@id="sportsoverviewlist"]/li/div/div/li/div[1]/ul/ul/li/div[1]/div[3]/div[2]
    #     #  live-Odds then r @ //*[@id="ac63b56b-fd68-4bab-9e56-19c2887dc870"]/div -> where inside this is a list of spans (length 3 for hometeamwin, draw, teamB)... then this path from each ofthose 3 divs -> //span[1]/span[4] 

    #     # for more gamaes to show up - need to click a butto with 'Afficher'    

    #         wait_time = random.randint(1,2)*random.random()
    #         time.sleep(wait_time)  

    #         # have a check for the date and time of a champ league game or even a try each time:
    #         try:
    #             live_game_elements = driver.find_elements_by_xpath('//*[@id="sportsoverviewlist"]/li/div/div/li/div[1]/ul/ul/li')
    #             print(live_game_elements)
            
    #         except:
    #             print("failed to find live champ leagues games ...")
    #             pass    

    #         # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
    #         try:
    #             #start = timeit.timeit()

    #           # intro randomness to not get caught -=- unibet seems to not allowfast scraping... - lol
    #             wait_time = random.randint(1,3)
    #             time.sleep(wait_time)  

    #             champ_league_games_nested_gamesinfo_unibet = driver.find_elements_by_xpath('/html/body/div[@id="container"]/div[@id="wrapper"]/div[@id="content-container"]/div[@id="content"]/section/div[@id="main"] \
    #             /section[@id="view-main-container"]/div[@id="view-main"]/section[@id="page__competitionview"]/div[@class="view view-eventpath"]/div[@class="page-wrap"] \
    #             /div[@class="scroller"]/div[@class="ui-splitview"]/div[@class="ui-splitview-item ui-splitview-left"]/div[@class="i-splitview-item-inner"]/div[@class="c-eventpathlist bettingbox"] \
    #             /div[@class="ui-mainview-block eventpath-wrapper"]/div[@class="bettingbox-item box"]/div[@class="bettingbox-content oddsbox-hide-marketname bettingbox-wide"]/div[@class="ui-touchlink had-market inline-market calendar-event cell"]') 
    #             #end = timeit.timeit()
    #             #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 

    #             wait_time = random.randint(1,2)*random.random()
    #             time.sleep(wait_time) 

    #             for matches in  champ_league_games_nested_gamesinfo_unibet:
    #                 #print(matches.text)

    #                 wait_time = random.randint(0,1)*random.random()
    #                 time.sleep(wait_time) 

    #                 split_match_data_str = matches.text.split('\n') 
    #                 teams = split_match_data_str[0]

    #                 teams = unidecode.unidecode(teams)    

    #                 wait_time = random.randint(0,1)*random.random()
    #                 time.sleep(wait_time) 

    #                 competition =  split_match_data_str[1]
    #                 teamAWinOdds = split_match_data_str[2]
    #                 wait_time = random.randint(0,2)*random.random()
    #                 time.sleep(wait_time) 
    #                 teamBWinOdds = split_match_data_str[6]
    #                 wait_time = random.randint(0,2)*random.random()
    #                 time.sleep(wait_time) 
    #                 draw_odds    = split_match_data_str[4]

    #                 full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(float(teamAWinOdds.split(' ')[1].replace(',','.')) #=   teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
    #                 full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(float(draw_odds.split(' ')[1].replace(',','.'))
    #                 full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(float(teamBWinOdds.split(' ')[1].replace(',','.'))    
    #                 #check = 1


    #         except: #  NoSuchElementException:
    #             any_errors = False
    #             print("Error  ->  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
    #             continue
    #         #check = 1

        
    #     if  zebet in sites :
   
    #     ## NOTE live chgamp lieague hgames  on diff link when live - just normal football  page at top ! :
    #       #  this link :   
    #         ## This should be working, mas o menos, code for zebet live champions league           
    #         #driver.quit() 
    #         #driver.get('https://www.zebet.fr/fr/sport/13-football')

    #         #live_champ_gamesDiv = driver.find_elements_by_xpath('//*[@id="sport-top"]/div[1]/div[@class="page-sport-lives"]')

    #       #   //*[@id="sport-top"]/div[1]: sub divs in here called :  div[@class="page-sport-lives"]

    #         try:
    #             #start = timeit.timeit()
    #             champ_league_games_nested_gamesinfo_zebet = driver.find_elements_by_xpath('/html/body/div[@id="global"]/div[@id="content"]/main[@class="uk-flex-item-1 uk-width-7-12"]/section/ \
    #             div[@class="uk-block-20-20 uk-block-small-10-10"]/div[@id="event"]/article[@class="item"]/div[@class="uk-accordion uk-accordion-block item"]/ \
    #             div[@class="uk-accordion-wrapper item-bloc item"]/div/div[@class="uk-accordion-content uk-padding-remove uk-active"]/div/div[@class="item-content catcomp item-bloc-type-1"]')
    #                 #     # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
    #             #end = timeit.time
    #             #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 

    #             for matches in  champ_league_games_nested_gamesinfo_zebet:
    #                 #print(matches.text)
    #                 split_match_data_str = matches.text.split('\n') 
    #                 date = split_match_data_str[0]

    #                 # if  '-' in date:
    #                 #         d = datetime.datetime.strptime(date, '%d-%m-%d %H:%M')
    #                 #         date = d.strftime('%b %d')

    #                 # if  '/' in date:  
    #                 #         d = datetime.datetime.strptime(date, '%d/%m /%d %H:%M')
    #                 #         date = d.strftime('%b %d')    


    #                 teams = split_match_data_str[2] + '_' + split_match_data_str[6]
    #                 #teams = unidecode.unidecode(teams)
    #                 competition =  compettition #split_match_data_str[1]    
    #                 teamAWinOdds = float(split_match_data_str[1].replace(',','.'))
    #                 teamBWinOdds = float(split_match_data_str[3].replace(',','.'))
    #                 draw_odds    = float(split_match_data_str[5].replace(',','.'))

    #                 full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
    #                 full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
    #                 full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

    #         except NoSuchElementException:    
    #             any_errors = False
    #             print("Error  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
    #             continue


    #     if winimax in sites :
    #     # uNOTE : 'imn-play' live games have different structure of element style and content position in html tree ...
    #     # eg team names for champ leage are in :  //*[@id="app-inner"]/span/div/div[2]/div/section/div/div[1]/div/div/div[2]/div/a/div[2]/div[1]/div/div[2]/div[1] :
    #     #  -> two divs within this location contain team 1 , then next inner div - teAM 2'S NAME 

    #         try:
    #             #start = timeit.timeit()
    #             ## WRONG path !

                 #//*[@id="app-inner"]/span/div/div[2]/div/section/div/div[1]/div/div
    #             #champ_league_games_nested_gamesinfo_winimax = driver.find_elements_by_xpath('/html/body/div[@id="global"]/div[@id="content"]/main[@class="uk-flex-item-1 uk-width-7-12"]/section/ \
    #             #div[@class="uk-block-20-20 uk-block-small-10-10"]/div[@id="event"]/article[@class="item"]/div[@class="uk-accordion uk-accordion-block item"]/ \
    #             #div[@class="uk-accordion-wrapper item-bloc item"]/div/div[@class="uk-accordion-content uk-padding-remove uk-active"]/div/div[@class="item-content catcomp item-bloc-type-1"]')
    #                 #     # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
    #             champ_league_games_nested_gamesinfo_winimax = driver.find_elements_by_xpath('//*[@id="app-inner"]/span/div/div[2]/div/section/div/div[1]/div/div/div')
    #             #end = timeit.time
    #             #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 
    #             for matches in  champ_league_games_nested_gamesinfo_winimax:
    #                 # TODO - should come up with a more closely related check to get the right tabs                
    #                 if matches.rect['height'] < 50.0:
    #                     date = matches.text
    #                     #if '/' in date or '-' in date:
    #                     #    d = datetime.datetime.strptime(date, '%Y-%m-%d')
    #                     #    date = d.strftime('%b %d,%Y')
                            
    #                     continue

    #                 split_match_data_str = matches.text.split('\n') 

    #                 if len(split_match_data_str) >= 8:
    #                     teams = split_match_data_str[0]
    #                     #teams = split_match_data_str[2] #+ '_' + split_match_data_str[6]
    #                     competition =  compettition #split_match_data_str[1]    
    #                     teamAWinOdds = float(split_match_data_str[2].replace(',','.'))
    #                     teamBWinOdds = float(split_match_data_str[5].replace(',','.'))
    #                     draw_odds    = float(split_match_data_str[8].replace(',','.'))

    #                     full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
    #                     full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
        #                 full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

        #             else:
        #                 print('odds amd or teams dont exist -- exit with error ')    
        #                 any_errors = False
        #                 print("Error  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
        #                 continue

        #     except NoSuchElementException:
        #         any_errors = False
        #         print("Error  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
        #         continue

        # if sports_bwin in sites :

        #     try:
        #         #start = timeit.timeit()
                
        #         ## NOTE - this is just a placeholder -- must find proper Xpth to do this on sport.bwin site
        #         champ_league_games_nested_gamesinfo_sportsbwin = driver.find_elements_by_xpath('/html/body/div[@id="global"]/div[@id="content"]/main[@class="uk-flex-item-1 uk-width-7-12"]/section/ \
        #         div[@class="uk-block-20-20 uk-block-small-10-10"]/div[@id="event"]/article[@class="item"]/div[@class="uk-accordion uk-accordion-block item"]/ \
        #         div[@class="uk-accordion-wrapper item-bloc item"]/div/div[@class="uk-accordion-content uk-padding-remove uk-active"]/div/div[@class="item-content catcomp item-bloc-type-1"]')
        #             #     # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
        #         #end = timeit.time
        #         #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 
        #         # !! TODO - exception here on oTRY above !

        #         for matches in  champ_league_games_nested_gamesinfo_sportsbwin:
        #             #print(matches.text)

        #             if matches.rect['height'] < 50.0:
        #                 date = matches.text    
        #                 continue

        #             team_names = matches.find_element_by_xpath('//div/a/div/div').text.split('vs')
        #             team_nameA = team_names[0]
        #             team_nameB = team_names[1].split('\n')[0]
        #             teams = team_nameA + team_nameB
        #             competition =  compettition #split_match_data_str[1] 
        #             #team_odds = matches.find_element_by_xpath('//div/div/div/div/button/span').text
        #             odds_elememnts_list = driver.find_elements_by_xpath('//*[@id="app-inner"]/span/div/div[2]/div/section/div/div[1]/div/div/div[2]/div/a/div/div[2]/div/div') 

        #             split_match_data_str = odds_elememnts_list.text.split('\n') 
        #             date = split_match_data_str[0]
        #             teams = split_match_data_str[2] + '_' + split_match_data_str[6]
        #             competition =  compettition #split_match_data_str[1]    
        #             teamAWinOdds = float(split_match_data_str[1].replace(',','.'))
        #             teamBWinOdds = float(split_match_data_str[3].replace(',','.'))
        #             draw_odds    = float(split_match_data_str[5].replace(',','.'))

        #             full_all_bookies_allLeagues_match_data[ sports_bwin + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
        #             full_all_bookies_allLeagues_match_data[ sports_bwin + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
        #             full_all_bookies_allLeagues_match_data[ sports_bwin + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

        #     except NoSuchElementException:
        #         any_errors = False
        #         print("Error  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
        #         continue

#         #DEBUG = 0            

#     for i,sites in enumerate(websites_europa_league_links):

#     #         #begin = timeit.timeit()  
#     #         driver.get(sites)
#     #         #finish = timeit.timeit()

#         if  france_pari in sites  :
# #         # unibet tree struct to games elements:

# #             # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
#             try:
#                 #start = timeit.timeit()
#                 europa_league_games_nested_gamesinfo_unibet = driver.find_elements_by_xpath('/html/body/div[@id="container"]/div[@id="wrapper"]/div[@id="content-container"]/div[@id="content"]/section/div[@id="main"] \
#                 /section[@id="view-main-container"]/div[@id="view-main"]/section[@id="page__competitionview"]/div[@class="view view-eventpath"]/div[@class="page-wrap"] \
#                 /div[@class="scroller"]/div[@class="ui-splitview"]/div[@class="ui-splitview-item ui-splitview-left"]/div[@class="i-splitview-item-inner"]/div[@class="c-eventpathlist bettingbox"] \
#                 /div[@class="ui-mainview-block eventpath-wrapper"]/div[@class="bettingbox-item box"]/div[@class="bettingbox-content oddsbox-hide-marketname bettingbox-wide"]/div[@class="ui-touchlink had-market inline-market calendar-event cell"]') 
#                 #end = timeit.timeit()
#                 #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 

#                 for matches in  europa_league_games_nested_gamesinfo_unibet:
#                     #print(matches.text)
#                     split_match_data_str = matches.text.split('\n') 
#                     teams = split_match_data_str[0]
#                     competition =  split_match_data_str[1]
#                     teamAWinOdds = float(split_match_data_str[2])
#                     teamBWinOdds = float(split_match_data_str[6])
#                     draw_odds    = float(split_match_data_str[4])

#                     all_crapedSites_data[france_pari + date.lower() + '_' + competition.lower() + '_' + teams].append(teamAWinOdds.split(' ')[1].replace(',','.').lower())  #=   teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
#                     all_crapedSites_data[france_pari + date.lower() + '_' + competition.lower() + '_' + teams].append(draw_odds.split(' ')[1].replace(',','.').lower())
#                     all_crapedSites_data[france_pari + date.lower() + '_' + competition.lower() + '_' + teams].append(teamBWinOdds.split(' ')[1].replace(',','.').lower())    
# #                     #check = 1


#             except: #  NoSuchElementException:
#                 any_errors = False
#                 print("Error  ->  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
#                 continue


#             if unibet in sites:
#             # unibet tree struct to games elements:

#                 # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
#                 try:
#                     #start = timeit.timeit()
#                     europa_league_games_nested_gamesinfo_unibet = driver.find_elements_by_xpath('/html/body/div[@id="container"]/div[@id="wrapper"]/div[@id="content-container"]/div[@id="content"]/section/div[@id="main"] \
#                     /section[@id="view-main-container"]/div[@id="view-main"]/section[@id="page__competitionview"]/div[@class="view view-eventpath"]/div[@class="page-wrap"] \
#                     /div[@class="scroller"]/div[@class="ui-splitview"]/div[@class="ui-splitview-item ui-splitview-left"]/div[@class="i-splitview-item-inner"]/div[@class="c-eventpathlist bettingbox"] \
#                     /div[@class="ui-mainview-block eventpath-wrapper"]/div[@class="bettingbox-item box"]/div[@class="bettingbox-content oddsbox-hide-marketname bettingbox-wide"]/div[@class="ui-touchlink had-market inline-market calendar-event cell"]') 
#                     #end = timeit.timeit()
#                     #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 

#                     for matches in  europa_league_games_nested_gamesinfo_unibet:
#                         #print(matches.text)
#                         split_match_data_str = matches.text.split('\n') 
#                         teams = split_match_data_str[0]
#                         competition =  split_match_data_str[1]
#                         teamAWinOdds = float(split_match_data_str[2])
#                         teamBWinOdds = float(split_match_data_str[6])
#                         draw_odds    = float(split_match_data_str[4])

#                         all_crapedSites_data[unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(teamAWinOdds.split(' ')[1].replace(',','.').lower())  #=   teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
#                         all_crapedSites_data[unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(draw_odds.split(' ')[1].replace(',','.').lower())
#                         all_crapedSites_data[unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(teamBWinOdds.split(' ')[1].replace(',','.').lower())    
#                         #check = 1


#                 except: #  NoSuchElementException:
#                     any_errors = False
#                     print("Error  ->  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
#                     continue

#     #             #check = 1

            
#             if zebet in sites: 
#             # unibet tree struct to games elements:

#                 try:
#                     #start = timeit.timeit()
#                     europa_league_games_nested_gamesinfo_zebet = driver.find_elements_by_xpath('/html/body/div[@id="global"]/div[@id="content"]/main[@class="uk-flex-item-1 uk-width-7-12"]/section/ \
#                     div[@class="uk-block-20-20 uk-block-small-10-10"]/div[@id="event"]/article[@class="item"]/div[@class="uk-accordion uk-accordion-block item"]/ \
#                     div[@class="uk-accordion-wrapper item-bloc item"]/div/div[@class="uk-accordion-content uk-padding-remove uk-active"]/div/div[@class="item-content catcomp item-bloc-type-1"]')
#                         #     # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
#                     #end = timeit.time
#                     #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 

#                     for matches in  europa_league_games_nested_gamesinfo_zebet:
#                         print(matches.text)
#                         split_match_data_str = matches.text.split('\n') 
#                         date = split_match_data_str[0]
#                         teams = split_match_data_str[2] + '_' + split_match_data_str[6]
#                         competition =  compettition #split_match_data_str[1]    
#                         teamAWinOdds = float(split_match_data_str[1].replace(',','.'))
#                         teamBWinOdds = float(split_match_data_str[3].replace(',','.'))
#                         draw_odds    = float(split_match_data_str[5].replace(',','.'))

#                         all_crapedSites_data[zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
#                         all_crapedSites_data[zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
#                         all_crapedSites_data[zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

#                 except NoSuchElementException:
#                     any_errors = False
#                     print("Error  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
#                     continue




################# ***********************################# ***********************################# ***********************################# ***********************################# ***********************
################# *************************** END  of European cups sites beyong pari *******************************########################################
################# ***********************################# ***********************################# ***********************################# ***********************################# ***********************



    #         if winimax in sites :
    #         # unibet tree struct to games elements:

    #             try:
    #                 #start = timeit.timeit()
    #                 europa_league_gamesinfo_winimax = driver.find_elements_by_xpath('//*[@id="app-inner"]/span/div/div[2]/div/section/div/div[1]/div/div/div') #'/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div/div[2]')
                                                 
    #                 for matches in  europa_league_gamesinfo_winimax:

    #                     team_names = matches.find_element_by_xpath('//div/a/div/div').text.split('vs')
    #                     team_nameA = team_names[0]
    #                     team_nameB = team_names[1].split('\n')[0]
    #                     teams = team_nameA + team_nameB

    #                     competition =  compettition #split_match_data_str[1] 

    #                     team_odds = matches.find_element_by_xpath('//div/div/div/div/button/span')

    #                     #for odds in team_odds:
    #                     teamAWinOdds = team_odds[0]
    #                     draw_odds    = team_odds[1]
    #                     teamBWinOdds = team_odds[2]

    #                     teamAWinOdds = float(split_match_data_str[1].replace(',','.'))
    #                     teamBWinOdds = float(split_match_data_str[3].replace(',','.'))
    #                     draw_odds    = float(split_match_data_str[5].replace(',','.'))

    #                     all_crapedSites_data[winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
    #                     all_crapedSites_data[winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
    #                     all_crapedSites_data[winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

    #             except NoSuchElementException:
    #                 any_errors = False
    #                 print("Error  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
    #                 continue

    #         if sports_bwin in sites :
    #         # unibet tree struct to games elements:

    #             try:
    #                 #start = timeit.timeit()
    #                 europa_league_games_nested_gamesinfo_zebet = driver.find_elements_by_xpath('/html/body/div[@id="global"]/div[@id="content"]/main[@class="uk-flex-item-1 uk-width-7-12"]/section/ \
    #                 div[@class="uk-block-20-20 uk-block-small-10-10"]/div[@id="event"]/article[@class="item"]/div[@class="uk-accordion uk-accordion-block item"]/ \
    #                 div[@class="uk-accordion-wrapper item-bloc item"]/div/div[@class="uk-accordion-content uk-padding-remove uk-active"]/div/div[@class="item-content catcomp item-bloc-type-1"]')
    #                     #     # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
    #                 #end = timeit.time
    #                 #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 

    #                 for matches in  europa_league_games_nested_gamesinfo_zebet:
    #                     print(matches.text)
    #                     split_match_data_str = matches.text.split('\n') 
    #                     date = split_match_data_str[0]
    #                     teams = split_match_data_str[2] + '_' + split_match_data_str[6]
    #                     competition =  compettition #split_match_data_str[1]    
    #                     teamAWinOdds = float(split_match_data_str[1].replace(',','.'))
    #                     teamBWinOdds = float(split_match_data_str[3].replace(',','.'))
    #                     draw_odds    = float(split_match_data_str[5].replace(',','.'))

    #                     all_crapedSites_data[sports_bwin + '_' +  date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
    #                     all_crapedSites_data[sports_bwin + '_' +  date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
    #                     all_crapedSites_data[sports_bwin + '_' +  date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

    #             except NoSuchElementException:
    #                 any_errors = False
    #                 print("Error  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
    #                 continue            



################# ***********************################# ***********************################# ***********************################# ***********************################# ***********************
################# ***************************                            LIGUE 1 GAMES                      *******************************########################################
################# ***********************################# ***********************################# ***********************################# ***********************################# ***********************

   
    for i,sites in enumerate(websites_ligue1_links):
        
        wait_time = random.randint(1,2)*random.random()
        time.sleep(wait_time)  

        #begin = timeit.timeit()  
        driver.get(sites)
        #finish = timeit.timeit()
        compettition_ = 'ligue1'

        if  france_pari in sites :
        # # zebet tree struct to games elements:                                                     
            try:

                ligue1_games_info_france_pari_try_1 = driver.find_elements_by_xpath('//*[@id="nb-sport-switcher"]/div[1]/div') 
        #         # TODO : need to actually make call into zebet champ league page to get champ_league_games_nested_gamesinfo_zebet:
                ligue1_games_info_france_pari_try_2 = driver.find_elements_by_xpath('//*[@id="colonne_centre"]/div/div/div[2]/div')         
                #for matches in  ligue1_games_infozebet:

                #//div/div/
                #//div[2]/div
                #print(matches.text)
                competition = compettition_

                ligue1_games_info_france_pari = ligue1_games_info_france_pari_try_1
                if not ligue1_games_info_france_pari_try_1:
                    ligue1_games_info_france_pari = ligue1_games_info_france_pari_try_2

                #pargame_elements = ligue1_games_info_france_pari[0].text.split('+')
                for matches in  ligue1_games_info_france_pari:

                    #p_exist = driver.find_element_by_xpath('//p/')

                    # if p :
                    #     #get_date 
                    #     date = p_exist.text

                    game_info = matches.text.split('\n')
                    if len(game_info) >= 8 :

                        teams = game_info[1].split('/')

                        teamA = teams[0]
                        teamB = teams[1]

                        teamAWinOdds = game_info[3]
                        draw_odds    = game_info[5]
                        teamBWinOdds = game_info[7]

        #       split_match_data_str = matches.text.split('\n') 
        #       date = split_match_data_str[0]
        #       teams = split_match_data_str[2] + '_' + split_match_data_str[6]
        #       competition =  compettition #split_match_data_str[1]    
        #       teamAWinOdds = split_match_data_str[1].replace(',','.')
        #       teamBWinOdds = split_match_data_str[3].replace(',','.')
        #       draw_odds    = split_match_data_str[5].replace(',','.')
                    
                    date = '13 Bunny Cats'
                    full_all_bookies_allLeagues_match_data[ france_pari + '_' + date.lower() + '_' + competition.lower() + '_' + teamA.lower() + teamB.lower()].append(float(teamAWinOdds.replace(',','.'))) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                    full_all_bookies_allLeagues_match_data[ france_pari + '_' + date.lower() + '_' + competition.lower() + '_' + teamA.lower() + teamB.lower()].append(float(draw_odds.replace(',','.')))
                    full_all_bookies_allLeagues_match_data[ france_pari + '_' + date.lower() + '_' + competition.lower() + '_' + teamA.lower() + teamB.lower()].append(float(teamBWinOdds.replace(',','.')))

            except NoSuchElementException:
                any_errors = False
                print("Error  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
                continue


        # if  betclic in sites :

        #     try:
        #         # /html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details  
        #         ligue1_games_info_betclic = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details/div') 
                                                                                       
        # #         # TODO : need to actually make call into zebet champ league page to get champ_league_games_nested_gamesinfo_zebet:

        #         #for matches in  ligue1_games_infozebet:

        #             #//div/div/
        #             #//div[2]/div
        #         #print(matches.text)

        #         #parts1 = ligue1_games_info_betclic[0].text.split('+')
        #         for dates in  ligue1_games_info_betclic:

        #             game_info = dates.text.split('Ligue 1 Uber Eats')
        #             date = game_info[0].split('\n')[0]
        #             for matchs in game_info[1:]:

        #                 info_per_match = matchs.split('\n')
        #                 if len(info_per_match) >= 13 :

        #                     teamA = info_per_match_info[1]
        #                     teamB = info_per_match[2]
        #                     teamAWinOdds = info_per_match[6]
        #                     draw_odds    = info_per_match[9]
        #                     teamBWinOdds = info_per_match[12]

        # #             split_match_data_str = matches.text.split('\n') 
        # #             date = split_match_data_str[0]
        # #             teams = split_match_data_str[2] + '_' + split_match_data_str[6]
        # #             competition =  compettition #split_match_data_str[1]    
        # #             teamAWinOdds = float(split_match_data_str[1].replace(',','.'))
        # #             teamBWinOdds = float(split_match_data_str[3].replace(',','.'))
        # #             draw_odds    = float(split_match_data_str[5].replace(',','.'))

        #             full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA.lower() + teamB.lower()].append(teamAWinOdds.replace(',','.')) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
        #             full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA.lower() + teamB.lower()].append(draw_odds.replace(',','.'))
        #             full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA.lower() + teamB.lower()].append(teamBWinOdds.replace(',','.'))

        #     except NoSuchElementException:
        #         any_errors = False
        #         print("Error  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
        #         continue


        if  unibet in sites :

        # unibet tree struct to games elements:
            # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
            try:
                
                wait_time = random.randint(1,3)*random.random()
                time.sleep(wait_time)  

                ligue1_games_nested_gamesinfo_unibet =  driver.find_elements_by_xpath('//*[@id="page__competitionview"]/div/div[1]/div[2]/div/div/div/div[3]/div[2]/div')                                                                             #//*[@id="page__competitionview"]/div/div[1]/div[2]/div/div/div/div[3]/div[2] 

                print('in unibet and collected all ligue one games web element ! ... ')

                wait_time = random.randint(1,2)*random.random()
                time.sleep(wait_time)  
                #end = timeit.timeit()
                #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 

                #k = 0
                for game_info in  ligue1_games_nested_gamesinfo_unibet:
                
                    wait_time = random.randint(1,3)*random.random()
                    time.sleep(wait_time)  
                    # date =  driver.find_element_by_xpath('//h2').text
                    # date1_games = driver.find_elements_by_xpath('//div')
                    # for game in date1_games:

                    #print('in unibet -- in games for loop on the ' + str(k) + ' -th game ...;) ....')
                    #k += 1

                    split_match_data_str = game_info.text.split('\n') 
                    if len(split_match_data_str) >= 8:
                        date  = split_match_data_str[0]
                        wait_time = random.randint(1,2)*random.random()
                        time.sleep(wait_time) 
                        teams = split_match_data_str[1]

                        wait_time = random.randint(1,3)*random.random()
                        time.sleep(wait_time) 

                        #teams = split_match_data_str[2] #+ '_' + split_match_data_str[6]
                        competition =  compettition_ #split_match_data_str[1]    
                        teamAWinOdds = split_match_data_str[3].split(' ')[1]#.replace(',','.')
                        wait_time = random.randint(1,2)*random.random()
                        time.sleep(wait_time) 
                        teamBWinOdds = split_match_data_str[5].split(' ')[1]#.replace(',','.')
                        wait_time = random.randint(1,3)*random.random()
                        time.sleep(wait_time) 
                        draw_odds    = split_match_data_str[7].split(' ')[1] #.replace(',','.')
        


                    # if matches.rect['height'] < 50.0 :
                    #     #check if you get a non match day like - alternative betting type header
                    #     if not (any(char.isdigit() for char in matches.text)):
                    #         comtinue
                    #     date = matches.text    
                    #     continue

                    # split_match_data_str = matches.text.split('\n') 
                    # if len(split_match_data_str) >= 8:
                    #     date  = split_match_data_str[0]
                    #     wait_time = random.randint(0,1)*random.random()
                    #     time.sleep(wait_time) 
                    #     teams = split_match_data_str[1]

                    #     wait_time = random.randint(1,2)*random.random()
                    #     time.sleep(wait_time) 

                    #     #teams = split_match_data_str[2] #+ '_' + split_match_data_str[6]
                    #     competition =  compettition_ #split_match_data_str[1]    
                    #     teamAWinOdds = split_match_data_str[3].split(' ')[1]#.replace(',','.')
                    #     wait_time = random.randint(1,2)*random.random()
                    #     time.sleep(wait_time) 
                    #     teamBWinOdds = split_match_data_str[5].split(' ')[1]#.replace(',','.')
                    #     wait_time = random.randint(0,1)*random.random()
                    #     time.sleep(wait_time) 
                    #     draw_odds    = split_match_data_str[7].split(' ')[1] #.replace(',','.')


                    # team_names = matches.find_element_by_xpath('//div/a/div/div').text.split('vs')
                    # team_nameA = team_names[0]
                    # team_nameB = team_names[1].split('\n')[0]
                    # teams = team_nameA + team_nameB
                    # competition =  compettition_ #split_match_data_str[1] 
                    # #team_odds = matches.find_element_by_xpath('//div/div/div/div/button/span').text
                    # odds_elememnts_list = driver.find_elements_by_xpath('//*[@id="app-inner"]/span/div/div[2]/div/section/div/div[1]/div/div/div[2]/div/a/div/div[2]/div/div') 

                    # split_match_data_str = odds_elememnts_list.text.split('\n') 
                    # date = split_match_data_str[0]
                    # teams = split_match_data_str[2] + '_' + split_match_data_str[6]
                    # competition =  compettition #split_match_data_str[1]    
                    # teamAWinOdds = split_match_data_str[1].replace(',','.')
                    # teamBWinOdds = split_match_data_str[3].replace(',','.')
                    # draw_odds    = split_match_data_str[5].replace(',','.')


##################################################################################################################
##                                            START REOVE olD CODED TEST
##################################################################################################################        


                    # date = driver.find_element_by_xpath('//div[2]/h2/span').text
                    # competition =  compettition_
                    # teams = driver.find_element_by_xpath('//div[2]/div[1]/div/div/div/div/div/div[1]/div').text.split('\n')[0]
                    # teamAWinOdds = driver.find_element_by_xpath('//div[1]/div/div/div[2]/div/section/div/div/span/span/span[@class="ui-touchlink-needsclick price odd-price"]').text
                                
                    # wait_time = random.randint(1,3)*random.random()
                    # time.sleep(wait_time)  
                    
                    # #//*[@id="71b4da2a-b84f-4d3d-8fc3-76e13b09355f"]/div/span[1]/span[1]/span[4]
                    # draw_odds = driver.find_element_by_xpath('//div[1]/div/div/div[2]/div/section/div/div/span[2]/span/span[@class="ui-touchlink-needsclick price odd-price"]').text
                    # teamBWinOdds = driver.find_element_by_xpath('//div[1]/div/div/div[2]/div/section/div/div/span[3]/span/span[@class="ui-touchlink-needsclick price odd-price"]').text

##################################################################################################################
##                                            END TEST
##################################################################################################################

                    # !! TODO - exception here on first soring attempt! 
                    wait_time = random.randint(1,2)*random.random()
                    time.sleep(wait_time)  

                    full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower() ].append(float(teamAWinOdds))#.split(' ')[1].replace(',','.')) #=   teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                    #wait_time = random.randint(1,2)*random.random()float((
                    full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower() ].append(float(draw_odds)) #.split(' ')[1].replace(',','.'))
                    full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower() ].append(float(teamBWinOdds)) #.split(' ')[1].replace(',','.'))    
                                            
                    #check = 1

            except: #  NoSuchElementException:
                any_errors = False
                print("Error  ->  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
                continue
            #check = 1
        
        # if  zebet in sites :
        # # # zebet tree struct to games elements:                                                     

        #     try:

        #         ligue1_games_infozebet = driver.find_elements_by_xpath('//*[@id="event"]/article/div/div/div/div/div') 
        # #         # TODO : need to actually make call into zebet champ league page to get champ_league_games_nested_gamesinfo_zebet:

        #         #for matches in  ligue1_games_infozebet:

        #             #//div/div/
        #             #//div[2]/div
        #         #print(matches.text)

        #         parts1 = ligue1_games_infozebet[0].text.split('+')[0]
        #         for matches in  parts1:

        #             game_info = matches.split('\n')
        #             if len(game_info) >= 8 :

        #                 date = game_info[1]

        #                 teamA = str(game_info[3])
        #                 teamB = str(game_info[7])
        #                 teamAWinOdds = game_info[2]
        #                 draw_odds  = game_info[4]
        #                 teamBWinOdds     = game_info[6]

        #                 teams = teamA + '_vs_' + teamB


        # #             split_match_data_str = matches.text.split('\n') 
        # #             date = split_match_data_str[0]
        # #             teams = split_match_data_str[2] + '_' + split_match_data_str[6]
        # #             competition =  compettition #split_match_data_str[1]    
        # #             teamAWinOdds = float(split_match_data_str[1].replace(',','.'))
        # #             teamBWinOdds = float(split_match_data_str[3].replace(',','.'))
        # #             draw_odds    = float(split_match_data_str[5].replace(',','.'))

        #             full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
        #             full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
        #             full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

        #     except NoSuchElementException:
        #         any_errors = False
        #         print("Error  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
        #         continue

        #full path copied from sourcecode tool       
        #/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div/div[2]

        if winimax in sites :           
            try:
                ligue1_games_nested_gamesinfo_winimax = driver.find_elements_by_xpath('//*[@id="app-inner"]/span/div/div[2]/div/section/div/div[1]/div/div/div') #'/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div/div[2]')                                    
                for matches in  ligue1_games_nested_gamesinfo_winimax:                 #//*[@id="app-inner"]/span/div/div[2]/div/section/div/div[1]/div/div

                    if matches.rect['height'] < 50.0:
                        #check if you get a non match day like - alternative betting type header
                        # (occues at the end of the ligue one games list on winimax pro ejemplo0)
                        if not (any(char.isdigit() for char in matches.text)):
                            continue
                        date = matches.text    
                        continue
                    
                    split_match_data_str = matches.text.split('\n') 
                    if len(split_match_data_str) >= 8:
                        teams = split_match_data_str[0]
                        #teams = split_match_data_str[2] #+ '_' + split_match_data_str[6]
                        competition =  compettition_ #split_match_data_str[1]    
                        teamAWinOdds = float(split_match_data_str[2].replace(',','.'))
                        teamBWinOdds = float(split_match_data_str[5].replace(',','.'))
                        draw_odds    = float(split_match_data_str[8].replace(',','.'))

                    # teamAWinOdds = split_match_data_str[1].replace(',','.')
                    # teamBWinOdds = split_match_data_str[3].replace(',','.')
                    # draw_odds    = split_match_data_str[5].replace(',','.')

                    full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                    full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
                    full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

            except NoSuchElementException:
                any_errors = False
                print("Error  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
                continue


        ## somethin wrong with assumed html in link - think i must navigate all the way from base url with button click and hfers links etc.

        # if cbet in sites :           
        #     try:   
        #         resultElements = driver.find_elements_by_xpath('/html/body/div[1]/div/div[1]/div[1]/div[1]/ul/li')    #/html/body/div[1]/div/div[2]/div[1]/div/section/section/ul') #'/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div/div[2]')                                    
                
        #         resultElements = ligue1_games_nested_gamesinfo_cbet.click()
                
        #         for matches in  ligue1_games_nested_gamesinfo_cbet:                #/html/body/div[1]/div/div[2]/div[1]/div/section/section/ul                


        #             #/html/body/div[1]/div/div[1]/div[1]/div[1]/ul/li[7]

        #             #/html/body/div[1]/div/div[2]/div[1]/div/section/section/ul    

        #             #//*[@id="prematch-events"]/div[1]/div/section/section/ul/li[1]

                    
        #             split_match_data_str = matches.text.split('\n') 
        #             if len(split_match_data_str) >= 8:
        #                 teams = split_match_data_str[0]
        #                 #teams = split_match_data_str[2] #+ '_' + split_match_data_str[6]
        #                 competition =  compettition_ #split_match_data_str[1]    
        #                 teamAWinOdds = split_match_data_str[2].replace(',','.')
        #                 teamBWinOdds = split_match_data_str[5].replace(',','.')
        #                 draw_odds    = split_match_data_str[8].replace(',','.')

        #             # teamAWinOdds = float(split_match_data_str[1].replace(',','.'))
        #             # teamBWinOdds = float(split_match_data_str[3].replace(',','.'))
        #             # draw_odds    = float(split_match_data_str[5].replace(',','.'))

        #             full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
        #             full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
        #             full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

        #     except NoSuchElementException:
        #         any_errors = False
        #         print("Error  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
        #         continue


## Hiddemn Div here needs fixing:
            
        # if sports_bwin in sites :          #.startswith('sports.bwin',8) or sites.startswith('sports.bwin'9) :

        #     try:

        #         #     # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
        #         #end = timeit.time
        #         #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 

        #         for matches in  champ_league_games_nested_gamesinfo_zebet:
        #             print(matches.text)
        #             split_match_data_str = matches.text.split('\n') 
        #             date = split_match_data_str[0]
        #             teams = split_match_data_str[2] + '_' + split_match_data_str[6]
        #             competition =  compettition #split_match_data_str[1]    
        #             teamAWinOdds = float(split_match_data_str[1].replace(',','.'))
        #             teamBWinOdds = float(split_match_data_str[3].replace(',','.'))
        #             draw_odds    = float(split_match_data_str[5].replace(',','.'))

        #             all_crapedSites_data[i][date.lower() + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
        #             all_crapedSites_data[i][date.lower() + competition.lower() + '_' + teams.lower()].append(draw_odds)
        #             all_crapedSites_data[i][date.lower() + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

        #     except NoSuchElementException:
        #         any_errors = False
        #         print("Error  caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
        #         continue            


    ## create sepaarate dicts for each bookies :
    unibet_dict      = defaultdict(list)
    betclic_dict     = defaultdict(list)
    winimax_dict     = defaultdict(list)
    zebet_dict       = defaultdict(list)
    sports_bwin_dict = defaultdict(list)
    france_pari_dict = defaultdict(list)
    pasinobet_dict   = defaultdict(list)
    pasinobet_dict   = defaultdict(list)

    all_split_sites_data = []
    if len(full_all_bookies_allLeagues_match_data) == 0:
        print("Empty full_data dict encountered -- fix !")
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

        if pasinobet in keys:
            pasinobet_dict[keys] = values
            #all_split_sites_data.append(pasinobet_dict)

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

    if len(pasinobet_dict) > 0:
        all_split_sites_data.append(pasinobet_dict)

    driver.quit()
    return any_errors

if __name__ == '__main__':

    argv = sys.argv
    DEBUG_OUTPUT  = False

    # if len(argv) < 1 :
    #     print("usage:  please indicate with  0 or a 1 in the first cmd line argument to the program wherether you wish to include debugging output prints in it's run or not; 0/1 corresponding to no/yes....")
    # else:    
    #     DEBUG_OUTPUT = bool(int(argv[1]))


    #print('Running unit tests on sportsbetting applicationb version 1....')
    #unittest.main()


    retVal = odds_alert_system(oddType=2,expect_oddValue=1.35,teamA='metz',teamB='lens',date='Mercredi 25 Novembre',competition='ligue1',Bookie1_used='Winamax',Bookie2_used='')

    x = -1

    retval2 = check_for_sure_bets() #'unibet','zebet','winimaxc','W', 'D','marseilles','nantes','28/11/2020','ligue 1 UberEats')

    debug = -10

