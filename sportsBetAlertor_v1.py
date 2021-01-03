import random
from bs4 import BeautifulSoup
import re
import smtplib
import time
import timeit
from collections import defaultdict
from smtplib import SMTPException
import re,pprint

import requests
import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import itertools
import sys,os
#from scraper_api import ScraperAPIClient
import datetime, unidecode
#from googletrans import Translator

# init the Google API translator
#translator = Translator()

## turn down level of v verbose by dwfauklt selenium webdriver logging , lol
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)

from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
req_proxy = RequestProxy(log_level=logging.ERROR) #you may get different number of proxy when  you run this at each time
proxies = req_proxy.get_proxy_list()

# define global init 'surebet' condition value (note by default any bet will not be a surebet given its > 1.0)
surebet_factor = 0.0
#cibstant initialised to False - for determining if they customer's expected odds are retrieved for alert system...
odd_are_found = False

#client = ScraperAPIClient('781fa06f6c29968fe2971fa6a90760dc')
#respondsr = client.get(url = "https://france-pari.fr/")
#print(result)

#text file woith records of surebets already alerted for:

surebets_Done_list_textfile = './sure_bets_placed.txt'
fp1 = open(surebets_Done_list_textfile, "r")

list_mailed_surebets = []

for line in fp1:
    list_mailed_surebets.append(line)

fp1.close()

def check_is_surebet(*args): #odds_A, odds_B):

    

    total_iverse_odds_sum = 0.0
    for odds in args:
        #print('in check_is_surebet() func. --  odds_i = ' + str(odds) + ' ')
        if odds == 0:
            pass
        else:
            total_iverse_odds_sum += 1/(odds)

    #
    # print(' Surebet value = ' + str(total_iverse_odds_sum))

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

    #print('in get surebet function -- surebet = ' + str(surebet_factor))

    return surebet_factor


def return_surebet_vals(*argv, stake):  #odds_A, odds_B,stake):

    surebetStakes = []

    for i,odds in enumerate(argv):

        if odds == 0.0 or surebet_factor == 0.0 :
            surebetStakes[i]  = stake
        else:    
            surebetStakes[i] = (1/surebet_factor)*(stake/odds)
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
    
#remove?as done below for site's direct champ league url!
headers = {"Connection" : "close"}
ret = driver.get("https://france-pari.fr/") #,headers = headers)
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

###  *********************************** premier league  lINKS *****************************







###  *********************************** La Liga  lINKS *****************************








###  *********************************** Serie A'   lINKS *****************************








###  *********************************** Bundesliga  lINKS *****************************





###  *********************************** LIGUE 1  lINKS *****************************
betclic_ligue1_link       = "https://www.betclic.fr/football-s1/ligue-1-uber-eats-c4"
france_pari_ligue1_link   = "https://www.france-pari.fr/competition/96-parier-sur-ligue-1-uber-eats"
unibet_ligue1_link        = "https://www.unibet.fr/sport/football/france-foot/ligue-1-ubereats-france"
zebet_ligue1_link         = "https://www.zebet.fr/en/competition/96-ligue_1_uber_eats"
winimax_ligue1_link       = "https://www.winamax.fr/en/sports-betting/sports/1/7/4"
passionsports_ligue1_link = "https://www.enligne.parionssport.fdj.fr/paris-football/france/ligue-1-uber-eats?filtre=22892"
sportsbwin_ligue1_link    = "https://sports.bwin.fr/fr/sports/football-4/paris-sportifs/france-16/ligue-1-4131"
cbet_ligue1_link          = "https://cbet.gg/en/sportsbook/prematch#/prematch"
paris_sportifs_pmu        = "https://paris-sportifs.pmu.fr/pari/competition/169/football/ligue-1-uber-eats%C2%AE"



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



##  LIGUE ! TEAMS 2020/2021

PSG           =  'paris saint germain'
Montpeiller   =  'montpeiller'
Marseille     =  'marseille'
Monaco        =  'monaco'
Lyon          =  'lyon'
Metz          =  'metz'
lens          =  'lens'
lille         =  'lille'
dijon         =  'dijon'
Nice          =  'nice'
Nimes         =  'mimes'
Rennes        =  'Rennes'
Strasbourg    =  'strasbourg'
Nantes        =  'nantes'
Bordeaux       =  'bordeax'
Angers        =  'angers'
Brest         =  'bordeaux'
Reims         =  'reims'
Lorient       =  'lorient'

All_ligue1_team_list = [PSG, ",paris sg" ,"paris saint germaine", "paris st germain","saint etienne","st-etienne", Montpeiller, Marseille, Monaco, Lyon, Metz, lens, lille, dijon, Nice, Nimes, Rennes, Strasbourg, Nantes, Bordeaux, Angers, Brest, Reims, Lorient]

french_dates_list = ['janvier','fevrier','mars','avril','mai','juin','juillet','aout','septembre','octobre','novembre','decembre']

# english_to_french_mapper = {}
# english_to_french_mapper[club_brugge] = 'club bruges'
# english_to_french_mapper[lokomotiv] = 'lokomotiv_moscou'
# english_to_french_mapper[zenit_st_peters] = 'zenit saint petersbourg'
# english_to_french_mapper[barcelona] = 'barcelone'
# english_to_french_mapper[salzburg] = 'rb salzbourg'
# english_to_french_mapper[salzbourg] = 'rb salzbourg'


#same order as data structures in their list
websites_champs_league_links = [france_pari_champions_league_link, unibet_champions_league_link, zebet_champions_league_link,winimax_champions_league_link, sportsbwin_champs_ligue_link]  # haS 5 LINKS NOW
websites_europa_league_links = [france_pari_europa_league_link, unibet_europa_league_link, zebet_europa_league_link,winimax_europa_league_link, sportsbwin_europa_league_link] # 7 links
websites_ligue1_links        = [france_pari_ligue1_link, unibet_ligue1_link, zebet_ligue1_link,winimax_ligue1_link, sportsbwin_ligue1_link, betclic_ligue1_link,cbet_ligue1_link,passionsports_ligue1_link,paris_sportifs_pmu] # 7 links m       # betclic_ligue1_link is empty for now

reference_champ_league_games_url = str(websites_champs_league_links[0])
driver.get(reference_champ_league_games_url)

# some vars for parsing the games data - strings.
#initialize data with todays date - better than empty string
date_ = '31 mai'
compettition = 'Ligue des Champions'    

# TODO :rename like actual sites 

# refernce_champ_league_gamesDict = defaultdict(list) # pari-france site
# #site_unibet_champ_league_gamse = defaultdict(list)
# sites_zebetchamp_league_gamse   = defaultdict(list)
# unnibet_champ_league_gamse      = defaultdict(list)
# winimax_champ_league_gamse      = defaultdict(list)
# sportsbwin_champ_league_gamse   = {}
# site7s_champ_league_gamse       = {}


full_all_bookies_allLeagues_match_data = defaultdict(list)
all_split_sites_data = []

#all_srpaed_sites_data = [refernce_champ_league_gamesDict, winimax_champ_league_gamse, sites_zebetchamp_league_gamse, unnibet_champ_league_gamse] #, site5s_champ_league_gamse]

#bookie 'nicknames'
zebet = 'zebet'
unibet = 'unibet'
winimax = 'winamax'
betclic = 'betclic'
france_pari = 'france-pari'
sports_bwin = 'sports.bwin'
parionbet = 'parion'
cbet      = 'cbet'
pmu       = ''


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
        
        #print('Click on the "esc" key @ any time to terminate this program and can then restart again any time you wish :) ......')
        # waitr a delay time to refresh sites parsings....
        start_parse = time.time() 
        if parseSites(driver): #all_srpaed_sites_data):
            end_parse = time.time() 
            print('Time to do parsing was = ' + str(end_parse - start_parse))
            total_time_parsing += (end_parse - start_parse) 
            pass
        else:
            print("Error i parsing function...retring... But needs diagnostics and/or a fix ! ...")
            continue

        # print('********************************************************************************print  ******************************************************************************** ')   
        # print(' ******************************************************************************** OLD Dict : ********************************************************************************')
       
        # print(str(all_split_sites_data_copy))
        # print(' ############################################################################### OLD Dict : FOINISHED   ###############################################################################')
        # print('lenght of old dict = ' + str(len(all_split_sites_data_copy)))

        globCounter += 1
        if all_split_sites_data == all_split_sites_data_copy:
            dont_recimpute_surebets = True
            dataDictChangdCounter += 1
            print(' #############################################################new data dict. has NOT been updated ...:( -- so need to parse again         ################################################################### .... ;)')
            time.sleep(wait_time_idirNoChanges)
        else:
            dont_recimpute_surebets = False
            # print('lenght of NEWd dict = ' + str(len(all_split_sites_data)))
            print('  &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&  new data dict. has been updated ...:( -- so need to parse again     %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% .... ;)')
            
        print('total num attempts/loops  = ' + str(globCounter) + '-- no. of times data changes & was updated in parsing = ' + str(dataDictChangdCounter))    
            #print('###############################################################################  Current Dict : ')
        
            # print(str(all_split_sites_data))
            # print(' ############################################################################### Current Dict FINISHED  ###############################################################################')
            # #print('new data dict. has been updated ...! :)')

        #local copy in infinite loop to check if its changed or not - then dont need to redo sure bets checks if not
        all_split_sites_data_copy = all_split_sites_data

        wait_time = random.randint(1,2)
        time.sleep(wait_time)   
        if len(all_split_sites_data) < 3 :
            print('*************************** Error - less than three bookies scrapped for games here ..., try again -- if this error persists raise a bug ******************************')
            return False

        if (globCounter % 10) == 0:
            print('AVerage time to do parsings was = ' + str(total_time_parsing/globCounter)) 
            print('number of surebets found so far is = ' + str(sure_bet_counter))    

        if not dont_recimpute_surebets :
            start_surebet_timer = time.time()
            index = 0    
            ## TODO  - a biggg TODO  -- the following is just the combos of 3 but will also need to cater for when only 2 bookies are involved in a footy surebet :
            # i.e 1 bookie has the needed home win and draw odd and the other the awat=y win and also vice versa.
            #redundancy_bet_checklist = {}
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
                            print('site_data key = ' + str(key)) 

                        matching_keys2_list = []
                        matching_keys3_list = []
                        truth_list_subStrKeysDict2 = [matching_keys2_list.append(key2) for key2,val in subsetList[1].items() if (unique_math_identifiers[0] in key2 and unique_math_identifiers[1] in key2 and unique_math_identifiers[2] in key2)]
                        if len(truth_list_subStrKeysDict2) > 0:
                            key_bookkie2 = matching_keys2_list[0] #truth_list_subStrKeysDict2[0]
                        truth_list_subStrKeysDict3 = [matching_keys3_list.append(key3) for key3,val in subsetList[2].items() if (unique_math_identifiers[0] in key3 and unique_math_identifiers[1] in key3 and unique_math_identifiers[2] in key3)]
                        if len(truth_list_subStrKeysDict3) > 0:
                            key_bookkie3 = matching_keys3_list[0] # truth_list_subStrKeysDict3[0]                


                        ## check i stest for now here... !! re - undo former statement test after    
                        if (truth_list_subStrKeysDict2 and not (find_substring(bookie_1,bookie_2) )) and (truth_list_subStrKeysDict3 and not ( find_substring(bookie_1,bookie_3))):
                            print('Checking for surebets .... ') 
                            if check_is_surebet(subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2]):  # encode bookie outcomes as 'W','D','L' wrt to the 1st team in the match descrpt. , i.e The 'hometeam' 
                                
                                # if  returnBetSizes:
                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE BET FOUND !  :)   *****************************************************************************')   
                                #     #surebet_odds_list = [subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2]]                                 
                                #     #get_surebet_factor(surebet_odds_list) #  odds_A, odds_B):
                                #     #sure_betsto_place = return_surebet_vals(surebet_odds_list, stake_val)
                                #     send_mail_alert_gen_socer_surebet(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1,sure_betsto_place)

                                # else:      
                                #     send_mail_alert_gen_socer_surebet(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1)

                                send_mail_alert_gen_socer_surebet(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1)
                                #print('Bet (sure)  kombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 'in the bookie ->' + bookie_1 + ' the draw at odds = '  + str(subsetList[1][key_bookkie2][1]) + ' in bookie ' + str(bookie_2) + ' and finally the other teams win odds @ ' + str(subsetList[2][key_bookkie3][2]) + str(bookie_3) + '  \n')
                                # these continues will avoid the sitch of 'same' surebet (swapoed one) being mailed out
                                #return_surebet_vals([subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2]],1000)
                                continue

                            if check_is_surebet(subsetList[0][key][0],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][1]):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE BET FOUND !  :)   *****************************************************************************') 
                                send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,W_1,W_2,teamA_1, teamB_1, date,competition_1)
                                #print('Bet (sure)  sombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 'in the bookie ->' + bookie_1 + ' the away win at odds = '  + str(subsetList[1][key_bookkie2][2]) + ' in bookie ' + str(bookie_2) + ' and finally the draw odds @ ' + str(subsetList[2][key_bookkie3][1]) + str(bookie_3) + '  \n')
                                #return_surebet_vals([subsetList[0][key][0],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][1]],1000)
                                continue

                            if check_is_surebet(subsetList[0][key][1],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][2]):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE-BET FOUND !  :)   *****************************************************************************') 
                                send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,D,W_1,teamA_1, teamB_1, date,competition_1) 
                                #print('Bet (sure)  combo just found has the draw odds at ' + str(subsetList[0][key][1]) + 'in the bookie ->' + bookie_1 + ' the home win at odds = '  + str(subsetList[1][key_bookkie2][0]) + ' in bookie ' + str(bookie_2) + ' and finally the away team win odds @ ' +  str(subsetList[2][key_bookkie3][2]) + ' in the bookies ->' + str(bookie_3) + '  \n') 
                                #return_surebet_vals([subsetList[0][key][1],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][2]],1000)
                                continue

                            if check_is_surebet(subsetList[0][key][1],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][0]):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE-BET FOUND !  :)   *****************************************************************************') 
                                send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,D,W_2,teamA_1, teamB_1, date,competition_1) 
                                #return_surebet_vals([subsetList[0][key][1],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][0]],1000)
                                continue

                            if check_is_surebet(subsetList[0][key][2],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][1]):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SUREBET FOUND !  :)   *****************************************************************************') 
                                send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,W_2,W_1,teamA_1, teamB_1, date,competition_1)  
                                #print('Bet (sure)  combo just found has the away team ' +  teamB_1  + ' win odds at ' + str(subsetList[0][key][2]) + 'in the bookie ->' + bookie_1 + ' the home team -> ' + teamA_1  +  '<- win at odds = '  + str(subsetList[1][key_bookkie2][0]) + ' in bookie ' + str(bookie_2) + ' and finally the draw odds @ ' +  str(subsetList[2][key_bookkie3][1]) + ' in the bookies ->' + str(bookie_3) + '  \n') 
                                #return_surebet_vals([subsetList[0][key][2],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][1]],1000)
                                continue                         

                            if check_is_surebet(subsetList[0][key][2],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][0]):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SUREBET FOUND !  :)   *****************************************************************************') 
                                send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,W_2,D,teamA_1, teamB_1, date,competition_1)    
                                #return_surebet_vals([subsetList[0][key][2],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][0]],1000)
                                continue                        

                else:
                    print("Not enough bookies scraped correctly to look for 3 - way surebets...")

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

        BOLD = '\033[1m'
        message = """From: From Person <from@fromdomain.com>
        To: To Person <to@todomain.com>
        Subject: SMTP e-mail test

        The is an Alert to tell you that the bookmaker - 
        """ + str(bookiesNameEventB) + """ had its odd's on the """ + home_or_away + """ team --   """  + str(teamB) + """ to """  + """ WIN """ + """ the event against   """ +  str(teamA) + """ \
           in the competition """  + str(competition) + """ reach a value of """ + str(expect_oddB) +  """ or greater at approx. 5 \
                - 10 seconds before this receipt of the email Alert --- its value has actually reached -> """ + str(actualOdd) +  "   "

        print('**************************************************************  message = ' + message)
        if message in list_mailed_surebets:
            print('sureBet already found -- dontt re-mail ')
            return successFlag


    else: # draw case
        
        message = """From: From Person <from@fromdomain.com>
        To: To Person <to@todomain.com>
        Subject: SMTP e-mail test

        The is an Alert to tell you that the bookmaker - 
        """  + str(bookiesNameEventB) + """ had its odd's ON A DRAW between the away team --  """ + str(teamB) + """ and the home team --  """ + str(teamA) + """ \
          in the competition  """  + str(competition) + """ reach a value of """ + str(expect_oddB) +  """ or greater at approx. \
         5 - 10 seconds before this receipt of the email Alert --- its value has actually reached -> """ + str(actualOdd) +  "   " 

        print('**************************************************************  A draw case -- message = ' + message)

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


# helper functions :
def find_substring(substring, string):
    """
    Returns list of indices where substring begins in string
    >>> find_substring(’me’, "The cat says meow, meow")
    [13, 19]
    """
    indices = []
    index = -1 # Begin at -1 so index + 1 is 0
    while True:
        # Find next index of substring, by starting search from index + 1
        index = string.find(substring, index + 1)
        if index == -1:
            break # All occurrences have been found
        indices.append(index)
 
    return indices 



def parseSites(driver): 

    global websites_champs_league_links, compettition, date, refernce_champ_league_gamesDict, full_all_bookies_allLeagues_match_data, DEBUG_OUTPUT, all_split_sites_data

    # reset full league dict so as not to keep appending to it below
    full_all_bookies_allLeagues_match_data.clear()

    any_errors = True
    #ret = driver.get(france_pari_champions_league_link)

    # if not ret:
    #     print("Error  -> caught in your driver.get() call to france-pari website... :( ")
    #     any_errors = False
    #     return any_errors

    # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
    # try:
    #     driver.find_elements_by_xpath("/html/body/div[@id='main']/section[@id='colonne_centre']/div[@class='nb-middle-content']/div/div[@class='bloc-inside-small']/div[@id='nb-sport-switcher']/div[@class='item-content uk-active']") #/div[@class='odd-event uk-flex']")
    
    # except: # err as NoSuchElementException:

    #     print("Error  -> caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
    #     any_errors = False
    #     pass
    #     #continue
    # # pick up date and competetion 1st beofre list of games:

    # date_element = driver.find_element_by_xpath('//p[@class="date soccer"]')

    # if date_element:
    #     print('game DATE names element block exists ! :) ...')
        
    #     try:
    #         Date = date_element.text
    #         # update global date hetre as this site has it reliably - (for others)
    #         date = unidecode.unidecode(Date)

    #     except: # err as NoSuchElementException:
    #         any_errors = False
    #         print("Error  -> caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
    #         pass
    # else:
    #     print('NAAH --  game href DATE element block DOESN"t exist :( ... ')    

    # #.text
    # competition = driver.find_element_by_xpath('//h2[@class="competition soccer"]').text
    # #driver.back()
    # champ_league_games_pariFrance_list = driver.find_elements_by_xpath("//div[@class='odd-event uk-flex']")


    # #now loop thru all champ league games on france-pari site
    # for j,games in enumerate(champ_league_games_pariFrance_list):

    #     team_names_element = False
    #     try:
    #         team_names_element = games.find_element_by_tag_name('a')  #//span[@class="bet-libEvent]') #/a') #.get_attribute("href")
    #         #div[@class="odd-event-block snc-odds-date-lib uk-flex"]/span/
    #     except: # err as NoSuchElementException:
    #         any_errors = False
    #         print("Error  -> caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
    #         pass

    #     if team_names_element:

    #         if DEBUG_OUTPUT:
    #             print('game href names element block exists ! :) ...')
            
    #         try:
    #             team_names_string = unidecode.unidecode(team_names_element.get_attribute("href"))
            
    #         except: # err as NoSuchElementException:
    #             any_errors = False
    #             print("Error  -> caught in your find_elements_by_xpath() call -- NoSuchElementException ! :( ")
    #             pass
    #     else:
    #         print('NAAH --  game href names element block DOESN"t exist ! :( ... ')    


    #     split_game_data_str = games.text.split('\n') 

    #     odds_string_teamA = float(split_game_data_str[3].replace(',','.'))
    #     odds_string_teamB = float(split_game_data_str[7].replace(',','.'))
    #     odds_string_draw =  float(split_game_data_str[5].replace(',','.'))

    #     #test: leave orig. version here for now , but replace with the default dict loist way a few lines ahead...
    #     #refernce_champ_league_gamesDict[date + '_' + competition + '_' + team_names_string] = odds_string_teamA + '_' + odds_string_draw + '_' + odds_string_teamB
    #     full_all_bookies_allLeagues_match_data[ france_pari + '_' + date.lower() + '_' + competition.lower() + '_' + team_names_string.split('parier-sur-')[1].lower()].append(odds_string_teamA) 
    #     full_all_bookies_allLeagues_match_data[ france_pari + '_' + date.lower() + '_' +  competition.lower() + '_' + team_names_string.split('parier-sur-')[1].lower()].append(odds_string_draw)
    #     full_all_bookies_allLeagues_match_data[ france_pari + '_' + date.lower() + '_' +  competition.lower() + '_' + team_names_string.split('parier-sur-')[1].lower()].append(odds_string_teamB)

    if DEBUG_OUTPUT:
        print('all good the find_elements_by_xpath Call worked GRAND !! :) --- full champ league games data struct = ')
        #print(refernce_champ_league_gamesDict)



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

        
    # if  zebet in sites :
   
    # #     ## NOTE live chgamp lieague hgames  on diff link when live - just normal football  page at top ! :
    # #       #  this link :   
    # #         ## This should be working, mas o menos, code for zebet live champions league           
    #         driver.quit() 
    #         driver.get('https://www.zebet.fr/fr/sport/13-football')

    #         live_champ_gamesDiv = driver.find_elements_by_xpath('//*[@id="sport-top"]/div[1]/div[@class="page-sport-lives"]')


    #         for stuff in live_champ_gamesDiv:

    #             y = -1

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
        #             date =  unidecode.unidecode(split_match_data_str[0])
        #             teams = unidecode.unidecode(split_match_data_str[2] + '_' + split_match_data_str[6])
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
#                     teams = unidecode.unidecode(split_match_data_str[0])
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
#                         teams = unidecode.unidecode(split_match_data_str[0])
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
#                         date =  unidecode.unidecode(split_match_data_str[0])
#                         teams = unidecode.unidecode(split_match_data_str[2] + '_' + split_match_data_str[6])
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
    #                     team_nameA = unidecode.unidecode(team_names[0])
    #                     team_nameB = unidecode.unidecode(team_names[1].split('\n')[0])
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
    #                     date =  unidecode.unidecode(split_match_data_str[0])
    #                     teams = unidecode.unidecode(split_match_data_str[2] + '_' + split_match_data_str[6])
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
   

    wait_time12 = random.randint(1,2)
    time.sleep(wait_time12)  

    #websites_ligue1_links.append('https://www.betclic.fr/football-s1/angl-premier-league-c3')
    #websites_ligue1_links.append('https://www.zebet.fr/fr/competition/94-premier_league')


    for i,sites in enumerate(websites_ligue1_links[0:]):
        
        wait_time = random.randint(1,2)*random.random()
        time.sleep(wait_time)  

        #begin = timeit.timeit()  
        driver.get(sites)
        #finish = timeit.timeit()
        compettition_ = 'ligue1'

        if  france_pari in sites :
        # # zebet tree struct to games elements:    
            print('in france_pari ligue1 pre-match parsing .... \n \n')                                                 
            try:

                ligue1_games_info_france_pari_try_1 = driver.find_elements_by_xpath('//*[@id="nb-sport-switcher"]/div[1]/div') 
        #       # TODO : need to actually make call into zebet champ league page t33o get champ_league_games_nested_gamesinfo_zebet:
                ligue1_games_info_france_pari_try_2 = driver.find_elements_by_xpath('//*[@id="colonne_centre"]/div/div/div[2]/div')         
                #for matches in  ligue1_games_infozebet:

                competition = compettition_
                ligue1_games_info_france_pari = ligue1_games_info_france_pari_try_1
                if not ligue1_games_info_france_pari_try_1:
                    ligue1_games_info_france_pari = ligue1_games_info_france_pari_try_2

                #pargame_elements = ligue1_games_info_france_pari[0].text.split('+')
                for matches in  ligue1_games_info_france_pari:

                    game_info = matches.text.split('\n')
                    indx = 0
                    for i in range(len(game_info)):
                        teamName_check = [x for x in All_ligue1_team_list if find_substring(x, unidecode.unidecode(game_info[i].lower()))]
                        if teamName_check :
                            indx = i
                            break

                    if len(game_info) >= 8 :
                        teams = game_info[indx].split('/')

                        if len(teams) < 2:
                            #print('No teams found -- either real issue or more likely - you are running the alert system with a match that is not in the betting card YET , please retry ...')
                            break

                        teamA = unidecode.unidecode(teams[0])
                        teamB = unidecode.unidecode(teams[1])

                        teamAWinOdds = game_info[i+2]
                        draw_odds    = game_info[i+4]
                        teamBWinOdds = game_info[i+6]
   
                    date = '23 decembre'
                    
                    full_all_bookies_allLeagues_match_data[ france_pari + '_' + unidecode.unidecode(date.lower()) + '_' + competition.lower() + '_' + teamA.lower() + teamB.lower()].append(float(teamAWinOdds.replace(',','.'))) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                    full_all_bookies_allLeagues_match_data[ france_pari + '_' + unidecode.unidecode(date.lower()) + '_' + competition.lower() + '_' + teamA.lower() + teamB.lower()].append(float(draw_odds.replace(',','.')))
                    full_all_bookies_allLeagues_match_data[ france_pari + '_' + unidecode.unidecode(date.lower()) + '_' + competition.lower() + '_' + teamA.lower() + teamB.lower()].append(float(teamBWinOdds.replace(',','.')))

            except NoSuchElementException:
                any_errors = False
                print("Error  caught in your FRANCE_PARI parse func. block call --  :( ..... ")
                continue


        if  betclic in sites :
            print('in betclic ligue1 pre-match parsing .... \n \n')  
            try:
                # /html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details  
                ligue1_games_info_betclic = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details/div') 
                                                                                   
                ## TODO : need to actually make call into zebet champ league page to get champ_league_games_nested_gamesinfo_zebet:
                #for matches in  ligue1_games_infozebet:
                #parts1 = ligue1_games_info_betclic[0].text.split('+')
                competition = compettition_
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

                        info_per_match = matchs.split('\n')
                        if len(info_per_match) >= 13 :

                            teamA = unidecode.unidecode(info_per_match[1])
                            teamB = unidecode.unidecode(info_per_match[2])
                            teamAWinOdds = info_per_match[6]
                            draw_odds    = info_per_match[9]
                            teamBWinOdds = info_per_match[12]


                            full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA.lower() + ' - ' + teamB.lower()].append(float(teamAWinOdds.replace(',','.'))) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                            full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA.lower() + ' - ' + teamB.lower()].append(float(draw_odds.replace(',','.')))
                            full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA.lower() + ' - ' + teamB.lower()].append(float(teamBWinOdds.replace(',','.')))

            except NoSuchElementException:
                any_errors = False
                print("Error  caught in your BETCLIC parse func. block call --  :( .....")
                continue

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
           
            #wait_time12 = random.randint(1,2)
            #time.sleep(wait_time12)  
            #print('second rand wait time = ' + str(wait_time12))
            try:

                wait_time37 = random.randint(3,6)
                #print('second rand wait time = ' + str(wait_time37))
                time.sleep(wait_time37)  

                ligue1_games_nested_gamesinfo_unibet_1 =  driver.find_elements_by_xpath('//*[@id="page__competitionview"]/div/div[1]/div[2]/div/div/div/div[3]/div[2]/div')  
                ligue1_games_nested_gamesinfo_unibet_2 =  driver.find_elements_by_xpath('/html/body/div[1]/div[2]/div[5]/div/section/div/section/div/section/div[1]/div/div[2]/div/div/div[2]/div[2]/div[1]/div/div')                                                                            #//*[@id="page__competitionview"]/div/div[1]/div[2]/div/div/div/div[3]/div[2] 
                                                                                       #//*[@id="page__competitionview"]/div/div[1]/div[2]/div/div/div/div[3]/div[2]
                #print('in unibet and collected all ligue one games web element ! ... ')
                competition =  compettition_
                #wait_time13 = random.randint(1,3)*random.random()
                time.sleep(wait_time12)  
                #end = timeit.timeit()
                #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 

                #k = 0
                ligue1_games_nested_gamesinfo_unibet =  ligue1_games_nested_gamesinfo_unibet_1
                if not ligue1_games_nested_gamesinfo_unibet_1:
                    ligue1_games_nested_gamesinfo_unibet = ligue1_games_nested_gamesinfo_unibet_2
                    if not ligue1_games_nested_gamesinfo_unibet_2:
                        print('driver find element call return nothing ... try again or exit with no results for games in ligue 1 UNIBET...')
                        ## TODO : implement another method - different path - maybe full Xpath to a known root easily or use Bueaty soup ...etc.
                        continue
                    else:
                        pass
                
                for game_info in  ligue1_games_nested_gamesinfo_unibet:
                
                    #wait_time13 = random.randint(1,3)*random.random()
                    time.sleep(wait_time12)  

                    #parts = game_info.text.split('Ligue 1 UberEATS')


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
                        print('issue in getting any proper matches data in betclic...')
                        continue

                    delimit_1 = parts[0].split('\n')

                    date = unidecode.unidecode(delimit_1[0])

                    if unidecode.unidecode(date.lower()) not in french_dates_list:
                        date = date_ 

                    for i in range(len(parts)-1):
                        delimit_2 = parts[i+1].split('\n')

                        if len(delimit_1) >= 2 and len(delimit_2) >= 6 :

                            teams = unidecode.unidecode(parts[i].split('\n')[-2])
                            #time.sleep(wait_time12)
                            teamAWinOdds = delimit_2[1].split(' ')[1]
                            #time.sleep(wait_time12)
                            draw_odds = delimit_2[3].split(' ')[1]                            
                            teamBWinOdds = delimit_2[5].split(' ')[1]

                            full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower() ].append(float(teamAWinOdds))   
                            #time.sleep(wait_time13)
                            full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower() ].append(float(draw_odds))    
                            full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower() ].append(float(teamBWinOdds))  
                            #time.sleep(wait_time13)                       

                    #for j,matchs in enumerate(parts[1:-1]):
                       
                        #j += 1
                    #     EACH_matchs_INFO_pieced =  parts[j+1].split('\n')
                    #     teams = unidecode.unidecode(EACH_matchs_INFO_pieced[-2])
                    #     next_EACH_matchs_INFO_pieced =  parts[j+2].split('\n')
                    #     if len(next_EACH_matchs_INFO_pieced) >= 6:

                    #         teamAWinOdds = next_EACH_matchs_INFO_pieced[1].split(' ')[1]
                    #         wait_time = random.randint(1,2)*random.random()
                    #         time.sleep(wait_time) 
                    #         draw_odds = next_EACH_matchs_INFO_pieced[3].split(' ')[1]
                    #         time.sleep(wait_time) 
                    #         teamAWinOdds = next_EACH_matchs_INFO_pieced[5].split(' ')[1]
                    #          # !! TODO - exception here on first soring attempt! 
                    #         time.sleep(wait_time)  
                    #         full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower() ].append(float(teamAWinOdds)) 
                    #         time.sleep(wait_time12)
                    #         full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower() ].append(float(draw_odds))    
                    #         time.sleep(wait_time12)
                    #         full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower() ].append(float(teamBWinOdds))                            
                    # #check = 1

            except: #  NoSuchElementException:
                any_errors = False
                print("Error  ->  caught in your UNIBET parse func. block call --  :( ..... ")
                continue
            #check = 1

######################################################################
##            LATEAST TESTING CODE  FOR LIVE LIGUE1  ON  ZEBET   
######################################################################            
        # if  zebet in sites :
    
        # #     ## NOTE live chgamp lieague hgames  on diff link when live - just normal football  page at top ! :
        # #       #  this link :   
        # #         ## This should be working, mas o menos, code for zebet live champions league           
        #         driver.quit() 
        #         driver.get('https://www.zebet.fr/fr/lives')

        #         # can see games here - check for frech team pairings -> click on sref link in //*[@id="lives"]/div (all live game group elements) -> then <a href = "link.....fr"  
        #         # # is directly in here and clickable

        #         live_foorball_gamesDiv = driver.find_elements_by_xpath('//*[@id="lives"]/div')
        #         for stuff in live_champ_gamesDiv:
        #            game_link =  stuff.find_element_by_xpath('//a href').text
        #            teams = game_link.split('-')[1].split('_') 
        #            if teams[0] in french_ligue1_teams and teams[0] in french_ligue1_teams:
        #                print('yes its a ligue 1 match -> follow link !')
        #                # follow link code goes here...


        #         live_champ_gamesDiv = driver.find_elements_by_xpath('//*[@id="sport-top"]/div[1]/div[@class="page-sport-lives"]')

        #         for stuff in live_champ_gamesDiv:

        #             y = -1


        if  zebet in sites :
        # # zebet tree struct to games elements:                                                     
            print('in zebet ligue1 pre-match parsing .... \n \n')  
            try:

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
                        teams = teamA + ' - ' + teamB

                        full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                        full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
                        full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

            except NoSuchElementException:
                any_errors = False
                print("Error  caught in your ZEBET parse func. block call --  :( ..... ")
                continue

        #full path copied from sourcecode tool       
        #/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div/div[2]

        if winimax in sites :        
            print('in winimax ligue1 pre-match parsing .... \n \n')   
            #try:
            ligue1_games_nested_gamesinfo_winimax = driver.find_elements_by_xpath('//*[@id="app-inner"]/span/div/div[2]/div/section/div/div[1]/div/div/div') #'/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div/div[2]')                                    
            
            
            #premiership_games_nested_gamesinfo_winimax = driver.find_elements_by_xpath('/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div')
            
            for matches in  ligue1_games_nested_gamesinfo_winimax:                 #//*[@id="app-inner"]/span/div/div[2]/div/section/div/div[1]/div/div

                if matches.rect['height'] < 50.0:
                    #check if you get a non match day like - alternative betting type header
                    # (occues at the end of the ligue one games list on winimax pro ejemplo0)
                    # if not (any(char.isdigit() for char in matches.text)):
                    #    continue
                    date = unidecode.unidecode(matches.text)    
                    #continue
                
                split_match_data_str = matches.text.split('\n')

                if len(split_match_data_str) >= 8:
                    check_teams_in_str = [True for y in All_ligue1_team_list if find_substring(y,unidecode.unidecode(matches.text).lower())]

                    if not check_teams_in_str:
                        continue
                    teams = unidecode.unidecode(split_match_data_str[0])
                    competition   =  compettition_ #split_match_data_str[1]    

                    try :

                        teamAWinOdds  = float(split_match_data_str[2].replace(',','.'))
                        draw_odds     = float(split_match_data_str[5].replace(',','.'))
                        teamBWinOdds  = float(split_match_data_str[8].replace(',','.'))

                    except ValueError:
                            
                        any_errors = False
                        print(" Value  Error  caught in your winamax parse func. block call --  :( ..... ")
                        continue
                    

                full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
                full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

            # except NoSuchElementException:
            #     any_errors = False
            #     print("Error  caught in your winamax parse func. block call --  :( ..... ")
            #     continue

   ## TODO - games element not getting picked up by find_elements driver call - try somtin else or beuaty soup!         

        ## somethin wrong with assumed html in link - think i must navigate all the way from base url with button click and hfers links etc
        # if cbet in sites :           
        #     try:   
        #             ligue1_games_nested_gamesinfo_cbet = driver.find_elements_by_xpath('//*[@id="prematch-events"]/div[1]/div/section/section/ul/li')    #/html/body/div[1]/div/div[2]/div[1]/div/section/section/ul') #'/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div/div[2]')                                    
                                                                                       
        #             #resultElements = ligue1_games_nested_gamesinfo_cbet.click()
        #             for matches in  ligue1_games_nested_gamesinfo_cbet :            

        #                 #/html/body/div[1]/div/div[1]/div[1]/div[1]/ul/li[7]
        #                 #/html/body/div[1]/div/div[2]/div[1]/div/section/section/ul    
        #                 #//*[@id="prematch-events"]/div[1]/div/section/section/ul/li[1]
        #                 date = '20 decembre' #unidecode.unidecode('?? ') 

        #                 split_match_data_str = matches.text.split('\n') 
        #                 if len(split_match_data_str) >= 8:
        #                     teams = unidecode.unidecode(split_match_data_str[0])
        #                     #teams = split_match_data_str[2] #+ '_' + split_match_data_str[6]
        #                     competition  =  compettition_ #split_match_data_str[1]    
        #                     teamAWinOdds = split_match_data_str[2].replace(',','.')
        #                     draw_odds    = split_match_data_str[5].replace(',','.')
        #                     teamBWinOdds = split_match_data_str[8].replace(',','.')
                            
        #                     full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(float(teamAWinOdds)) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
        #                     full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(float(draw_odds))
        #                     full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(float(teamBWinOdds))

        #     except NoSuchElementException:
        #         any_errors = False
        #         print("Error  caught in your CBET parse func. block call --  :( .....  ")
        #         continue


## Hiddemn Div here needs fixing:

## TODO - games element not getting picked up by find_elements driver call - try somtin else or beuaty soup!

        if sports_bwin in sites :          #.startswith('sports.bwin',8) or sites.startswith('sports.bwin'9) :
            #print('in sports_bwin ligue1 pre-match prsing .... \n \n')
            try:
                
                time.sleep(wait_time12)  
                # relative path to all upcoming ligue 1 games    

                resultElements_all_dates = driver.find_elements_by_xpath("/html/body/vn-app/vn-dynamic-layout-single-slot[3]/vn-main/main/div/ms-main/div/div/ms-fixture-list/div/div/div/ms-grid/ms-event-group")
                                                             
                #     # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
                #end = timeit.time
                #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 
                #time.sleep(wait_time12)
                for groups in resultElements_all_dates:
                    #all_games =  games.find_elements_by_xpath('//ms-event')
                    #time.sleep(wait_time12)

                    #teams_element = groups.find_element_by_xpath("//div/a")
                    #odds_element  = groups.find_element_by_xpath("//div/div")
                    parsed_games_data = groups.text.split('\n')
                    date = parsed_games_data[0]

                    teams_indx = 1
                    for indx,texts in enumerate(parsed_games_data):

                        formatted_texts = unidecode.unidecode(texts.lower())
                        if formatted_texts in All_ligue1_team_list:
                            teams_indx = indx
                            break

                    for info_block in range(len(parsed_games_data[teams_indx:]),9):

                        teamA = unidecode.unidecode( parsed_games_data[info_block].lower())
                        teamB = unidecode.unidecode( parsed_games_data[info_block + 1].lower())

                        teamAWinOdds   =  float(parsed_games_data[info_block + 3])
                        draw_odds      =  float(parsed_games_data[info_block + 4])
                        teamBWinOdds   =  float(parsed_games_data[info_block + 5])


                            
                        full_all_bookies_allLeagues_match_data[ sports_bwin + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                        full_all_bookies_allLeagues_match_data[ sports_bwin + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
                        full_all_bookies_allLeagues_match_data[ sports_bwin + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)


                    # for game in groups:

                    #     #print(game.text) 
                    #     split_match_data_str = game.text.split('\n') 
                    #     if len(split_match_data_str) >= 6:

                    #         date = unidecode.unidecode(split_match_data_str[2])
                    #         teams = unidecode.unidecode(split_match_data_str[0] + '_' + split_match_data_str[1])
                    #         competition    =  compettition #split_match_data_str[1]    
                    #         teamAWinOdds   = float(split_match_data_str[3].replace(',','.'))
                    #         draw_odds      = float(split_match_data_str[4].replace(',','.'))
                    #         #time.sleep(wait_time12)
                    #         teamBWinOdds   = float(split_match_data_str[5].replace(',','.'))
    
                    #     full_all_bookies_allLeagues_match_data[ sports_bwin + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                    #     full_all_bookies_allLeagues_match_data[ sports_bwin + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
                    #     full_all_bookies_allLeagues_match_data[ sports_bwin + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

            except NoSuchElementException:
                any_errors = False
                print("Error  caught in your sports_bwin parse func. block call -- NoSuchElementException ! :( ")
                continue 


## TODO - games element not getting picked up by find_elements driver call - try somtin else or beuaty soup!
        if parionbet in sites :          #.startswith('sports.bwin',8) or sites.startswith('sports.bwin'9) :
            print('in parionbet ligue1 pre-match prsing .... \n \n')
            try:
                time.sleep(wait_time12)
                # relative path to all upcoming ligue 1 games    
                resultParionElements = driver.find_elements_by_xpath('/html/body/div[2]/div[3]/wpsel-app/lib-sport-enligne/div[1]/wpsel-home/div')
                #     # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
                #end = timeit.time
                #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 
                for games in resultParionElements:
                    time.sleep(wait_time12)
                    all_games =  games.find_elements_by_xpath('//ms-event')
                    for game in all_games:

                        #print(game.text)  
                        split_match_data_str = game.text.split('\n') 
                        if len(split_match_data_str) >= 6:
                            date = unidecode.unidecode(split_match_data_str[2])
                            teams = unidecode.unidecode(split_match_data_str[0] + '_' + split_match_data_str[1])
                            competition =  compettition #split_match_data_str[1]   
                            time.sleep(wait_time12)
                            teamAWinOdds  = float(split_match_data_str[3].replace(',','.'))
                            draw_odds     = float(split_match_data_str[4].replace(',','.'))
                            teamBWinOdds  = float(split_match_data_str[5].replace(',','.'))
    
                            full_all_bookies_allLeagues_match_data[ parionbet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                            full_all_bookies_allLeagues_match_data[ parionbet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
                            full_all_bookies_allLeagues_match_data[ parionbet + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

            except NoSuchElementException:
                any_errors = False
                print("Error  caught in your parionBet  parse func. block :( ")
                continue 
                        
        #https://paris-sportifs.pmu.fr/pari/competition/169/football/ligue-1-uber-eats%C2%AE
        if paris_sportifs_pmu[8:26] in sites :          #.startswith('sports.bwin',8) or sites.startswith('sports.bwin'9) :
            print('in pmu ligue1 pre-match prsing .... \n \n')
            try:
                # relative path to all upcoming ligue 1 games    
                resultPmuElements = driver.find_elements_by_xpath("//*[contains(@class,'ms-active-highlight')]")
                
                resultPmuElements_1 = driver.find_elements_by_xpath("//*[@id='tabs-second_center-block-0']/div/div/div/div/div/div/div/div")
                
                ligue1_games_info_pmu = resultPmuElements_1
                if not resultPmuElements_1:
                    ligue1_games_info_pmu = resultPmuElements
                
                #//*[@id="tabs-second_center-block-0"]/div/div/div/div/div/div/div/div
                #//*[@id="table-content-20201220_0_2"]/div/div[2]
                #     # now navigate using the driver and xpathFind to get to the matches section of Ref. site :
                #end = timeit.time
                #print('Time taken to scrape unibets champ league shit was = ' + str(end - start)) 
                game_info = ligue1_games_info_pmu[0].text.split('+')
                for games in game_info:
                    #all_games =  games.find_elements_by_xpath('//ms-event')

                        #[0].split('\n')
                    #for game in game_info:
                    matches = games.split('//')            
                    if len(matches) >= 2 :

                        #for match in matches :

                        single_game_left  = matches[0].split('\n')
                        single_game_right = matches[1].split('\n')

                        if len(single_game_left) < 5 or len(single_game_right) < 5:
                            break

                        teamA = unidecode.unidecode(single_game_left[-1])
                        teamB = unidecode.unidecode(single_game_right[0])

                        teamAWinOdds = float(single_game_right[1].replace(',','.'))
                        draw_odds    = float(single_game_right[2].replace(',','.'))
                        teamBWinOdds = float(single_game_right[3].replace(',','.'))

                        teams = teamA + ' - ' + teamB

                        full_all_bookies_allLeagues_match_data[ paris_sportifs_pmu[8:26].lower() + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                        full_all_bookies_allLeagues_match_data[ paris_sportifs_pmu[8:26].lower() + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
                        full_all_bookies_allLeagues_match_data[ paris_sportifs_pmu[8:26].lower() + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

            except NoSuchElementException:
                any_errors = False
                print("Error  caught in your pmu sports parse func. block ..... :( ")
                continue 
                        
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
 
    if len(cbet_dict) > 0:
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

    if len(argv) >= 2 :

        if len(argv) == 8 :
            #print(' argv[0] = ' + str(argv[0]))
            #print(' argv[1] = ' + str(argv[1]))   
            #print(' argv[7] = ' + str(argv[7])) 
            retVal = odds_alert_system(oddType= int(argv[1]),expect_oddValue= float(argv[2]) ,teamA= argv[3],teamB= argv[4],date= argv[5],competition= argv[6],Bookie1_used= argv[7])

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


