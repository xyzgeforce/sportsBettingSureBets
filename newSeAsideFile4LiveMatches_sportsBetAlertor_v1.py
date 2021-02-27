import random
from bs4 import BeautifulSoup
import re
import smtplib
import time
import timeit
from collections import defaultdict
from smtplib import SMTPException
import re,pprint
import urllib3
import copy
import requests
import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from urllib3.exceptions import MaxRetryError
from selenium.webdriver.chrome.options import Options
import itertools
import sys,os
#from scraper_api import ScraperAPIClient
import datetime, unidecode
#from googletrans import Translator

## 416 86453333 - MS nurse

# init the Google API translator
#translator = Translator()

## turn down level of v verbose by dwfauklt selenium webdriver logging , lol
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)

from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
req_proxy = RequestProxy(log_level=logging.ERROR, sustain=True) #you may get different number of proxy when  you run this at each time
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
        print('in check_is_surebet() func. --  odds_i = ' + str(odds) + ' ')
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
            surebetStakes.append(1)
        else:    
            surebetStakes.append((1/surebet_factor)*(stake/odds))
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

## prematch :

betclic_ligue1_link       = "https://www.betclic.fr/football-s1/ligue-1-uber-eats-c4"
france_pari_ligue1_link   = "https://www.france-pari.fr/competition/96-parier-sur-ligue-1-uber-eats"
unibet_ligue1_link        = "https://www.unibet.fr/sport/football/france-foot/ligue-1-ubereats-france"
zebet_ligue1_link         = "https://www.zebet.fr/en/competition/96-ligue_1_uber_eats"
winimax_ligue1_link       = "https://www.winamax.fr/en/sports-betting/sports/1/7/4"
passionsports_ligue1_link = "https://www.enligne.parionssport.fdj.fr/paris-football/france/ligue-1-uber-eats?filtre=22892"
sportsbwin_ligue1_link    = "https://sports.bwin.fr/fr/sports/football-4/paris-sportifs/france-16/ligue-1-4131"
cbet_ligue1_link          = "https://cbet.gg/en/sportsbook/prematch#/prematch"
paris_sportifs_pmu        = "https://paris-sportifs.pmu.fr/pari/competition/169/football/ligue-1-uber-eats"

# live :
## most these needf the actual live links inserted !
betclic_ligue1_live         = "https://www.betclic.fr/live"
france_pari_ligue1_live     = "https://www.france-pari.fr/lives"
unibet_ligue1_live          = "https://www.unibet.fr/live"
zebet_ligue1_live           = "https://www.zebet.fr/en/lives"
winimax_ligue1_live         = "https://www.winamax.fr/en/sports-betting/live"
passionsports_ligue1_live   = "https://www.enligne.parionssport.fdj.fr/paris-en-direct"
sportsbwin_ligue1_live      = "https://sports.bwin.fr/fr/sports/en-direct/football-4"
cbet_ligue1_live            = "https://cbet.gg/en/sportsbook/live"
#sparis_sportifs_pmu_live     = #"https://sports.bwin.fr/fr/sports/en-direct/football-4"


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
Montpellier   =  'montpellier'
Marseille     =  'marseille'
Monaco        =  'monaco'
Lyon          =  'lyon'
Metz          =  'metz'
lens          =  'lens'
lille         =  'lille'
dijon         =  'dijon'
Nice          =  'nice'
Nimes         =  'nimes'
Rennes        =  'rennes'
Strasbourg    =  'strasbourg'
Nantes        =  'nantes'
Bordeaux      =  'bordeax'
Angers        =  'angers'
Brest         =  'brest'
Reims         =  'reims'
Lorient       =  'lorient'

## dict for weird french team naming -> standard:

ligue1_teamNamesMap = {'Stade Brestois': 'brest', 'Olympiue Lyonnais':'lyon','Paris Saint-Germain':'psg','Girondins de Bordeaux':'bordeaux','OGC Nice':'nice','Stade Rennais':'rennes','AS Saint-Etienne':'st etienne','Angers SCO':'angers','FC Metz':'metz','RC Strasbourg':'strasbourg'
                      ,'RC Lens':'lens','AS Monaco':'monaco','Dijon FCO':'dijon','Olympique de Marseille':'marseille','LOSC Lille':'lille','FC Nantes':'nantes','Stade de Reims':'reims'
                      ,'Nimes Olympique':'nimes','Montpellier HSC':'montpellier','FC Lorient':'lorient'}

All_ligue1_team_list = [PSG, "paris sg" ,"paris saint germaine", "paris st germain","saint etienne", "saint-etienne","st-etienne", Montpellier, Marseille, Monaco, Lyon, Metz, lens, lille, dijon, Nice, Nimes, Rennes, Strasbourg, Nantes, Bordeaux, Angers, Brest, Reims, Lorient]
french_dates_list = ['janvier','fevrier','mars','avril','mai','juin','juillet','aout','septembre','octobre','novembre','decembre']


comon_TeamNames_mapper ={'stade brestois': 'brest', 'brestois': 'brest','brest':'brest', 'olympiue lyonnais':'lyon', 'olympiue lyon':'lyon','paris saint-germain':'psg','paris saint germain':'psg','paris st-germain':'psg','paris st germain':'psg'
                      ,'paris sg':'psg','paris s g':'psg','girondins de bordeaux':'bordeaux','girondins bordeaux':'bordeaux','ogc nice':'nice','stade rennais':'rennes', 'rennais':'rennes', 'as saint-etienne':'st etienne', 
                      'saint etienne':'st etienne','saint-etienne':'st etienne', 'st-etienne':'st etienne','as st-etienne':'st etienne','angers sco':'angers','fc metz':'metz','rc strasbourg':'strasbourg'
                      ,'rc lens':'lens','racing club de lens':'lens','as monaco':'monaco','dijon fco':'dijon','olympique de marseille':'marseille', 'olympique marseille':'marseille','st etienne':'st etienne',
                       'losc lille':'lille','fc nantes':'nantes','stade de reims':'reims','nimes olympique':'nimes','montpellier hsc':'montpellier','montpellier':'montpellier','Montpellier':'montpellier','fc lorient':'lorient'
                       , PSG :  'psg', Montpellier:'montpellier', Marseille: 'marseille', Monaco:'monaco', Lyon: 'lyon', Metz: 'metz', lens: 'lens', lille:'lille', dijon:'dijon',Nice: 'nice',
                        Nimes:'nimes', Rennes: 'rennes', Strasbourg:'strasbourg', Nantes:  'nantes', Bordeaux:'bordeaux', Angers:  'angers', Brest:   'brest', Reims:   'reims', Lorient: 'lorient','racing strasbourg':'strasbourg'}

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
#websites_ligue1_links        = [france_pari_ligue1_link, zebet_ligue1_link, unibet_ligue1_link, winimax_ligue1_link, betclic_ligue1_link,cbet_ligue1_link,passionsports_ligue1_link,paris_sportifs_pmu] # 7 links m       # betclic_ligue1_link is empty for now
#sportsbwin_ligue1_link
#websites_ligue1_links        = [passionsports_ligue1_link] # 7 links m       # betclic_ligue1_link is empty for now
websites_ligue1_live_links   = [ cbet_ligue1_live, betclic_ligue1_live, france_pari_ligue1_live, unibet_ligue1_live, zebet_ligue1_live, winimax_ligue1_live, passionsports_ligue1_live] #, paris_sportifs_pmu_live] #,sportsbwin_ligue1_live
#websites_ligue1_live_links = [winimax_ligue1_live]


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
zebet       = 'zebet'
unibet      = 'unibet'
winimax     = 'winamax'
betclic     = 'betclic'
france_pari = 'france-pari'
sports_bwin = 'sports.bwin'
parionbet   = 'parion'
cbet        = 'cbet'
pmu         = ''



W_1 = 'Home team (1st team name on the betting card) to win'
W_2 = 'Away team (2nd team name on the betting card) to win'
D   = 'A draw between the team in the 90 minutes'
#L_1 = 'Home team (1st team name on the betting card) to lose'
#L_2 = 'Away team (2nd team name on the betting card) to lose'

## TEST wait time for after a non dict - data change
wait_time_idirNoChanges = random.randint(0,1)

# def check_for_sure_bets(*args):

#     global all_split_sites_data, DEBUG_OUTPUT, globCounter

#     # init. copy data dict.
#     all_split_sites_data_copy = {}
#     dont_recimpute_surebets = False  

#     returnBetSizes = False
#     stake_val      = 1.0  #(euro)  
#     if len(args) > 0 :
#         stake_val      = args[0]    
#         returnBetSizes = True

#     # initialize proxy count and create list of proxies from the prox generator
#     PROXY_COUNTER = 0
#     k = 33
#     proxies = req_proxy.get_proxy_list()

#     ## TEST
#     # proxies = proxies[:100]
#     # ##end test

#     #initialize counters
#     sure_bet_counter = 0
#     total_time_parsing = 0.0
#     globCounter=0
#     dataDictChangdCounter = 0
#     RAND_PROXY_JUMP = 13
#     while(True):

#         if PROXY_COUNTER >= len(proxies) - (2*RAND_PROXY_JUMP + 1):
#             proxies = req_proxy.get_proxy_list()
#             PROXY_COUNTER = 0
#         PROXY = proxies[PROXY_COUNTER].get_address()
#         #print("Proxy address = ******************************** %s ************************************ %d",PROXY,k)
        
#         driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

#         webdriver.DesiredCapabilities.CHROME['proxy']={
#             "httpProxy":PROXY,
#             "ftpProxy":PROXY,
#             "sslProxy":PROXY,
#             "proxyType":"MANUAL",
#         }
#         PROXY_COUNTER += random.randint(1,RAND_PROXY_JUMP)
#         k += 1
        
#         #print('Click on the "esc" key @ any time to terminate this program and can then restart again any time you wish :) ......')
#         # waitr a delay time to refresh sites parsings....
#         start_parse = time.time() 
#         if parseSites(driver): #all_srpaed_sites_data):
#             end_parse = time.time() 
#             print('Time to do parsing was = ' + str(end_parse - start_parse))
#             total_time_parsing += (end_parse - start_parse) 
#             pass
#         else:
#             print("Error i parsing function...retring... But needs diagnostics and/or a fix ! ...")
#             continue

#         # print('********************************************************************************print  ******************************************************************************** ')   
#         # print(' ******************************************************************************** OLD Dict : ********************************************************************************')
       
#         # print(str(all_split_sites_data_copy))
#         # print(' ############################################################################### OLD Dict : FOINISHED   ###############################################################################')
#         # print('lenght of old dict = ' + str(len(all_split_sites_data_copy)))

#         globCounter += 1
#         if all_split_sites_data == all_split_sites_data_copy:
#             dont_recimpute_surebets = True
#             dataDictChangdCounter += 1
#             print(' #############################################################new data dict. has NOT been updated ...:( -- so no need to re-check surebets        ################################################################### .... ;)')
#             time.sleep(wait_time_idirNoChanges)
#         else:
#             dont_recimpute_surebets = False
#             # print('lenght of NEWd dict = ' + str(len(all_split_sites_data)))
#             print('  &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&  new data dict. has been updated ...:( -- so can check surebets ..     %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% .... ;)')
            
#         print('total num attempts/loops  = ' + str(globCounter) + '-- no. of times data changes & was updated in parsing = ' + str(dataDictChangdCounter))    
#             #print('###############################################################################  Current Dict : ')
        
#             # print(str(all_split_sites_data))
#             # print(' ############################################################################### Current Dict FINISHED  ###############################################################################')
#             # #print('new data dict. has been updated ...! :)')

#         #local copy in infinite loop to check if its changed or not - then dont need to redo sure bets checks if not
#         all_split_sites_data_copy = all_split_sites_data

#         wait_time = random.randint(1,2)
#         time.sleep(wait_time)   
#         if len(all_split_sites_data) < 3 :
#             print('*************************** Error - less than three bookies scrapped for games here ..., try again -- if this error persists raise a bug ******************************')
#             return False

#         if (globCounter % 10) == 0:
#             print('AVerage time to do parsings was = ' + str(total_time_parsing/globCounter)) 
#             print('number of surebets found so far is = ' + str(sure_bet_counter))    

#         if not dont_recimpute_surebets :
#             start_surebet_timer = time.time()
#             index = 0    
#             ## TODO  - a biggg TODO  -- the following is just the combos of 3 but will also need to cater for when only 2 bookies are involved in a footy surebet :
#             # i.e 1 bookie has the needed home win and draw odd and the other the awat=y win and also vice versa.
#             #redundancy_bet_checklist = {}

#             checxking_surebet_counts = 0
#             for subset in itertools.combinations(all_split_sites_data, 3):  
#                 #filter unique games across dicts/sites using the key from a fixed one ....  
#                 #                
#                 subsetList = list(subset)         
#                 #print('combination ' + str(index) + '  -- has ordered bookies as  -- ' + str(subsetList)) 
#                 index += 1 

#                 if ( len(subsetList) >= 3):
#                     second_bookie_keys = subsetList[1].keys() 
#                     third_bookie_keys  = subsetList[2].keys()         

#                 #local_bookies_list = []
#                 bookie_2 = ''
#                 for keys in second_bookie_keys:
#                     bookie_2 = keys.split('_')[0]
#                     #local_bookies_list.append(bookie_2)
#                     break

#                 bookie_3 = ''        
#                 for keys in third_bookie_keys:
#                     bookie_3 = keys.split('_')[0]
#                     #local_bookies_list.append(bookie_3)
#                     break

#                 if len(subsetList) >= 3:    
#                     for key in subsetList[0]:    

#                         key_str_split_by_underscore = key.split('_')    
#                         if len(key_str_split_by_underscore) >= 4:

#                             bookie_1 = key_str_split_by_underscore[0]
#                             #local_bookies_list.append(bookie_1)
#                             date_1 =   key_str_split_by_underscore[1]
#                             competition_1 = key_str_split_by_underscore[2]
#                             sub_key_str_split_by_underscore = key_str_split_by_underscore[-1].split(' - ')
#                             sub_key_str_split_by_space = key_str_split_by_underscore[-1].split(' ')
#                             sub_key_str_split_by_vs = key_str_split_by_underscore[-1].split(' vs ')

#                             if len(sub_key_str_split_by_underscore) != 2:
#                                 if len(sub_key_str_split_by_space) != 2:
#                                     sub_key_str_split_by_works = sub_key_str_split_by_vs
#                                 else:
#                                     sub_key_str_split_by_works = sub_key_str_split_by_space    
#                             else:
#                                 sub_key_str_split_by_works = sub_key_str_split_by_underscore        

#                             if len(sub_key_str_split_by_works) >= 2:
#                                 teamA_1 =  sub_key_str_split_by_works[0]
#                                 teamB_1 =  sub_key_str_split_by_works[1]

#                         unique_math_identifiers = [competition_1,teamA_1,teamB_1]   # [date_1,competition_1,teamA_1,teamB_1]

#                         ## leave this redundancy check shit till next version !!
#                         # create unique keys to prevent surebets beiung redyndant acros the bookies triplets 
#                         #local_bookies_list.sort()
#                         #bookie_surebetsCombo_uniq_strs_list = [x + unique_math_identifiers[i] for i,x in enumerate(local_bookies_list)]
#                         #unique_key_string = ''.join(y for y in bookie_surebetsCombo_uniq_strs_list)

#                         #redundancy_bet_checklist[unique_key_string] = redundancy_bet_checklist.get(unique_key_string,0) + 1
#                         #if redundancy_bet_checklist[unique_key_string] > 1:
#                         #    continue

#                         if DEBUG_OUTPUT :
#                             print('site_data key = ' + str(key)) 

#                         matching_keys2_list = []
#                         matching_keys3_list = []
#                         truth_list_subStrKeysDict2 = [matching_keys2_list.append(key2) for key2,val in subsetList[1].items() if (unique_math_identifiers[0] in key2 and unique_math_identifiers[1] in key2 and unique_math_identifiers[2] in key2)]
#                         if len(truth_list_subStrKeysDict2) > 0:
#                             key_bookkie2 = matching_keys2_list[0] #truth_list_subStrKeysDict2[0]
#                         truth_list_subStrKeysDict3 = [matching_keys3_list.append(key3) for key3,val in subsetList[2].items() if (unique_math_identifiers[0] in key3 and unique_math_identifiers[1] in key3 and unique_math_identifiers[2] in key3)]
#                         if len(truth_list_subStrKeysDict3) > 0:
#                             key_bookkie3 = matching_keys3_list[0] # truth_list_subStrKeysDict3[0]                

 
#                         ## check i stest for now here... !! re - undo former statement test after    
#                         if (truth_list_subStrKeysDict2 and not (find_substring(bookie_1,bookie_2) )) and (truth_list_subStrKeysDict3 and not ( find_substring(bookie_1,bookie_3))):
                            
#                             checxking_surebet_counts += 1
#                             print('Checking for surebets .... checxking_surebet_counts =  ' + str(checxking_surebet_counts)) 
#                             print('Bookies in order of odds are : ' + bookie_1  + bookie_2 + bookie_3 )
#                             if check_is_surebet(subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2]):  # encode bookie outcomes as 'W','D','L' wrt to the 1st team in the match descrpt. , i.e The 'hometeam' 
                                
#                                 # if  returnBetSizes:
#                                 sure_bet_counter += 1
#                                 print('*****************************************************************************  SURE BET FOUND !  :)   *****************************************************************************')   
#                                 #     #surebet_odds_list = [subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2]]                                 
#                                 #     #get_surebet_factor(surebet_odds_list) #  odds_A, odds_B):
#                                 #     #sure_betsto_place = return_surebet_vals(surebet_odds_list, stake_val)
#                                 send_mail_alert_gen_socer_surebet(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1,sure_betsto_place)

#                                 # else:      
#                                 #     send_mail_alert_gen_socer_surebet(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1)
#                                 print('Odds comboo is')
#                                 print(W_1)
#                                 print(D)
#                                 send_mail_alert_gen_socer_surebet(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1)
#                                 #print('Bet (sure)  kombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 'in the bookie ->' + bookie_1 + ' the draw at odds = '  + str(subsetList[1][key_bookkie2][1]) + ' in bookie ' + str(bookie_2) + ' and finally the other teams win odds @ ' + str(subsetList[2][key_bookkie3][2]) + str(bookie_3) + '  \n')
#                                 # these continues will avoid the sitch of 'same' surebet (swapoed one) being mailed out
#                                 #return_surebet_vals([subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2]],1000)
#                                 continue

#                             if check_is_surebet(subsetList[0][key][0],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][1]):
#                                 sure_bet_counter += 1
#                                 print('*****************************************************************************  SURE BET FOUND !  :)   *****************************************************************************') 
#                                 send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,W_1,W_2,teamA_1, teamB_1, date,competition_1)
#                                 #print('Bet (sure)  sombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 'in the bookie ->' + bookie_1 + ' the away win at odds = '  + str(subsetList[1][key_bookkie2][2]) + ' in bookie ' + str(bookie_2) + ' and finally the draw odds @ ' + str(subsetList[2][key_bookkie3][1]) + str(bookie_3) + '  \n')
#                                 #return_surebet_vals([subsetList[0][key][0],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][1]],1000)
#                                 continue

#                             if check_is_surebet(subsetList[0][key][1],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][2]):
#                                 sure_bet_counter += 1
#                                 print('*****************************************************************************  SURE-BET FOUND !  :)   *****************************************************************************') 
#                                 send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,D,W_1,teamA_1, teamB_1, date,competition_1) 
#                                 #print('Bet (sure)  combo just found has the draw odds at ' + str(subsetList[0][key][1]) + 'in the bookie ->' + bookie_1 + ' the home win at odds = '  + str(subsetList[1][key_bookkie2][0]) + ' in bookie ' + str(bookie_2) + ' and finally the away team win odds @ ' +  str(subsetList[2][key_bookkie3][2]) + ' in the bookies ->' + str(bookie_3) + '  \n') 
#                                 #return_surebet_vals([subsetList[0][key][1],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][2]],1000)
#                                 continue

#                             if check_is_surebet(subsetList[0][key][1],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][0]):
#                                 sure_bet_counter += 1
#                                 print('*****************************************************************************  SURE-BET FOUND !  :)   *****************************************************************************') 
#                                 send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,D,W_2,teamA_1, teamB_1, date,competition_1) 
#                                 #return_surebet_vals([subsetList[0][key][1],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][0]],1000)
#                                 continue

#                             if check_is_surebet(subsetList[0][key][2],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][1]):
#                                 sure_bet_counter += 1
#                                 print('*****************************************************************************  SUREBET FOUND !  :)   *****************************************************************************') 
#                                 send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,W_2,W_1,teamA_1, teamB_1, date,competition_1)  
#                                 #print('Bet (sure)  combo just found has the away team ' +  teamB_1  + ' win odds at ' + str(subsetList[0][key][2]) + 'in the bookie ->' + bookie_1 + ' the home team -> ' + teamA_1  +  '<- win at odds = '  + str(subsetList[1][key_bookkie2][0]) + ' in bookie ' + str(bookie_2) + ' and finally the draw odds @ ' +  str(subsetList[2][key_bookkie3][1]) + ' in the bookies ->' + str(bookie_3) + '  \n') 
#                                 #return_surebet_vals([subsetList[0][key][2],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][1]],1000)
#                                 continue                         

#                             if check_is_surebet(subsetList[0][key][2],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][0]):
#                                 sure_bet_counter += 1
#                                 print('*****************************************************************************  SUREBET FOUND !  :)   *****************************************************************************') 
#                                 send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,W_2,D,teamA_1, teamB_1, date,competition_1)    
#                                 #return_surebet_vals([subsetList[0][key][2],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][0]],1000)
#                                 continue                        

#                 else:
#                     print("Not enough bookies scraped correctly to look for 3 - way surebets...")

#         if not dont_recimpute_surebets:

#             end_surebet_timer = time.time()
#             print("Time taken to just check for surebets besides parsing = " + str(end_surebet_timer - start_surebet_timer))

#     return True

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



def send_mail_alert_gen_socer_surebet_prportions(bookie_1,bookie_2,bookie_3,bookie_one_outcome, bookie_2_outcome,teamA,teamB,date,competition,proportions_list, Profit,odd1,odd2,odd3):

    global DEBUG_OUTPUT, surebet_factor
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


   #round(1/(proportions_list[0]*surebet_factor),2)) + """
   #round(1/(proportions_list[1]*surebet_factor),2)) + """
   #round(1/(proportions_list[2]*surebet_factor),2))      


    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    Surebet Alert  :

    Profit = """ + str(round(100.0 +( Profit*100),3)) + """
      
    Event: """ + str(competition) + """
    Date: """ + str(date) + """
    teamA: """ + str(teamA) + """
    teamB: """ + str(teamB) + """

    bookieTeamA: """ + str(bookieTeamA) + """   """  + str(proportions_list[0]) + """ % -- odd_1 is = """    +  str(odd1) + """     
    bookieDraw: """  + str(bookieDraw)  +  """   """  + str(proportions_list[1]) + """ % -- odd_2 is = """    + str(odd2) + """     
    bookieTeamB: """ + str(bookieTeamB) + """   """  + str(proportions_list[2]) +  """ % -- odd_3 is = """   +  str(odd3)          


    if  not find_substring(unibet,bookieTeamA) and  not find_substring(zebet,bookieTeamA) and  not find_substring(betclic,bookieTeamA) and  not find_substring(winimax ,bookieTeamA) and  not find_substring(paris_sportifs_pmu ,bookieTeamA) \
        and  not find_substring(parionbet,bookieTeamA) and  not find_substring(france_pari,bookieTeamA):
        print('bookieTeamA = ->' + str(bookieTeamA) + '<-')
        c = 3

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

            # FP1 = open(surebets_Done_list_textfile,'a')
            # FP1.write(message + '\n')
            # FP1.close()

            successFlag = True
        except SMTPException:
            print("Error: unable to send email")
            pass


    return successFlag    


def send_mail_alert_gen_socer_surebet(bookie_1,bookie_2,bookie_3,bookie_one_outcome, bookie_2_outcome,teamA,teamB,date,competition):

    global DEBUG_OUTPUT
    successFlag = False
    sender = 'godlikester@gmail.com'
    receivers = ['crowledj@tcd.ie','pauldarmas@gmail.com','raphael.courroux@hotmail.fr','theoletheo@hotmail.fr','alexandrecourroux@hotmail.com','scourroux@hotmail.com']

    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: LIVE Surebet found ! """

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

################# ***********************################# ***********************################# ***********************################# ***********************################# ***********************
################# ***************************                            LIGUE 1 GAMES                      *******************************########################################
################# ***********************################# ***********************################# ***********************################# ***********************################# ***********************
   
    wait_time12 = random.randint(1,2)
    time.sleep(wait_time12)  

    #websites_ligue1_links.append('https://www.betclic.fr/football-s1/angl-premier-league-c3')
    #websites_ligue1_links.append('https://www.zebet.fr/fr/competition/94-premier_league')
    
    #websites_ligue1_links.append('https://www.zebet.fr/fr/lives')
    #websites_ligue1_links.append('https://www.france-pari.fr/lives')
    websites_ligue1_live_links.append('file:///C:/Users/MaaD/Desktop/pythonCode/sportsBettingProjects/ActualLIve_ligue1GamesPages_downloads/Live%20betting_%20schedule%20and%20odds%20of%20matches%20on%20Betclic.html')



#websites_ligue1_live_links   =  [betclic_ligue1_live, france_pari_ligue1_live, unibet_ligue1_live, zebet_ligue1_live, winimax_ligue1_live, passionsports_ligue1_live, sportsbwin_ligue1_live, paris_sportifs_pmu_live]    
full_all_bookies_allLeaguesLIVE_match_data = defaultdict(list)


websites_ligue1_live_links   =  [cbet_ligue1_live, france_pari_ligue1_live, betclic_ligue1_live, winimax_ligue1_live, unibet_ligue1_live, zebet_ligue1_live ]  #, passionsports_ligue1_live] #, paris_sportifs_pmu_live] #winimax_ligue1_live   
#websites_ligue1_live_links =  [unibet_ligue1_live]  # [zebet_ligue1_live]   #[winimax_ligue1_live]

def parseSites_live(Driver):

    global full_all_bookies_allLeaguesLIVE_match_data, DEBUG_OUTPUT#, all_split_sites_data

    # reset full league dict so as not to keep appending to it below
    full_all_bookies_allLeaguesLIVE_match_data.clear()

    any_errors = True
    all_split_sites_data = []    

    wait_time12 = random.randint(1,2)
    time.sleep(wait_time12)  

    #websites_ligue1_links.append('https://www.betclic.fr/football-s1/angl-premier-league-c3')
    #websites_ligue1_links.append('https://www.zebet.fr/fr/competition/94-premier_league')
    
    #websites_ligue1_links.append('https://www.zebet.fr/fr/lives')
    #websites_ligue1_links.append('https://www.france-pari.fr/lives')

    for i,sites in enumerate(websites_ligue1_live_links[0:]):
        
        #wait_time = random.randint(1,2)*random.random()
        time.sleep(wait_time12)  

        #begin = timeit.timeit()  
        try:
            driver.get(sites)
        except MaxRetryError:
            wait_time = random.randint(1,2)
            time.sleep(wait_time)
            continue
        # except BadStatusLine:
        #     wait_time = random.randint(1,2)
        #     time.sleep(wait_time)
        #     continue

        #finish = timeit.timeit()
        compettition_ = 'ligue1'
        date = 'Live'

        if cbet in sites :        
            time.sleep(wait_time12)
            #time.sleep(wait_time12)     
            #time.sleep(wait_time12) 
            #driver.implicitly_wait(13)
            
            #WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/section/section/ul/li')))

            #ligue1_games_nested_gamesinfo_cbet = driver.find_elements_by_xpath('//*[@id="prematch-events"]/div[1]/div/section/section/ul/li')  
            #time.sleep(wait_time12)   
            ligue1_games_nested_gamesinfo_cbet_2 = driver.find_elements_by_xpath('/html/body/main') #body/div[1]/div/div[2]/div[1]/div/section/section/ul') #'/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div/div[2]')                                    
            time.sleep(wait_time12) 

            # if not  ligue1_games_nested_gamesinfo_cbet:
            #     ligue1_games_gamesinfo_cbet = ligue1_games_nested_gamesinfo_cbet_2

            #time.sleep(wait_time12) 
        
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
                                                            
            # league_selector =  driver.find_elements_by_xpath('//*[@id="live-top-leagues"]/ul/li')                    
            # for leagues in league_selector:

            #     if 'Ligue 1' in leagues.text:
            #         leagues.click()
            #         break

            ligue1_live_games_nested_gamesinfo_cbet_1 = driver.find_elements_by_xpath('//*[@id="live-tree"]/div[3]/ul/li')

            ligue1_games_gamesinfo_cbet  = ligue1_live_games_nested_gamesinfo_cbet_1    

            time.sleep(wait_time12)
            #time.sleep(wait_time37) 
            #matches_soccer_info_2 = driver.find_elements_by_xpath('//*[@id="prematch-events"]/div[1]/div/section/section/ul/li')
            #matches_soccer_info_2 =  driver.find_elements_by_xpath( '//*[@id="prematch-events"]/div[1]/div/section/section/ul/li')
            for matches in ligue1_games_gamesinfo_cbet:
                try :
                    split_match_data_str = matches.text.split('\n') 
                except selenium.common.exceptions.StaleElementReferenceException:
                    print('error in cbet with splitting a web element text') 

                    continue   

                if 'Ligue 1' not in split_match_data_str:
                    continue

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



        if  france_pari in sites :

            competition = "ligue 1"
            accept_btn = driver.find_elements_by_xpath('//*[@id="lives"]/div[1]/div/a[1]')
            # relative path to all upcoming ligue 1 games    
            multiSportResults_1 = driver.find_elements_by_xpath("/html/body/div[2]/section/div/div/article[1]/div/div/div")
            multiSportResults_2 = driver.find_elements_by_xpath('//*[@id="currentlive"]/div/div/div')

            multiSportResults = multiSportResults_1
            if not multiSportResults_1:
                multiSportResults = multiSportResults_2

            time.sleep(wait_time12)

            print('in france_pari parsing ...')

            # if not multiSportResults:
            #     liveSportblocks_results = multiSportResults_1_short_link
                
            # if not  multiSportResults_1_short_link:
            #     continue   
            i=0        

            # FIX COOKIES ISSUE FOR THIS SITE !!

            for blocks in multiSportResults:

                # inner_sport_info = driver.find_element_by_xpath("//div/div")
                # sports_type_str = inner_sport_info.text
                # if 'soccer' not in sports_type_str or 'football' not in sports_type_str:
                #     continue

                if '1 Uber Eats' not in blocks.text:
                    #pass
                    continue

                siomtin = blocks.text
                matches = siomtin.split('\n')
                if len(matches) > 5 :

                #for match in matches :

            ##!!!!     ## Must check in future why I had this parsing structure with 'sing;e game' and 'left game' -- maybe it has changed for lives games, or wk ends, or when more than one game on 
                    # #(as i made this change on a single wed game)

                    # single_game_left  = matches[0].split('\n')
                    # single_game_right = matches[1].split('\n')

                    # if len(single_game_left) < 1 or len(single_game_right) < 4:
                    #     break
                    
                    # #time.sleep(wait_time12)
                    # teamA = unidecode.unidecode(single_game_left[-1])
                    # teamB = unidecode.unidecode(single_game_right[0])

            ##!!!!!!!!!!!!NBB   can scrape team names from ligue 1games here BUT SOMETIMES  Must follow the "acces the live - Acceder au live " button and scrape odds from there 

            ## in the accesss live can have suspended betting - i.e no odds  -- eg au francais this page haD  " Paris en cours de mise à jour" written where odds would have been 
            # -- and in a loading type page ... so hopefiully I can detect this?! and skip the site

                    new_element = blocks.find_element_by_xpath('.//div/div/a')  
                    if 'acceder au live' not in unidecode.unidecode(blocks.text.lower()): #not new_element:
                        pass

                    else:
                        new_element_text = new_element.get_attribute('href')
                        if 'acceder au live' in unidecode.unidecode(new_element_text.lower()):
                            #new_element = driver.find_element_by_xpath('.//div/div/a')
                            new_element.click()
                            check = -1

                    if matches[1] == "--:--":
                        begin_info_index = 2
                    else:
                        begin_info_index = 4           

                    try:
                        teamA = comon_TeamNames_mapper[ unidecode.unidecode(matches[begin_info_index]).lower().strip()]
                        teamB = comon_TeamNames_mapper[ unidecode.unidecode(matches[begin_info_index+1]).lower().strip()]
                    except IndexError:
                        print('index error in france_pari live in grabbing team names...')    
                        continue

                    if len(matches) > 10: # when odds are le fail o the first screen
                        #time.sleep(wait_time12)
            #s!!!! must change this code - see NB notrte above         
                        try:
                            #teamAWinOdds = float(single_game_right[2].replace(',','.'))
                            #draw_odds    = float(single_game_right[4].replace(',','.'))
                            #teamBWinOdds = float(single_game_right[6].replace(',','.'))

                            teamAWinOdds = float(matches[begin_info_index+3].replace(',','.'))
                            draw_odds    = float(matches[begin_info_index+5].replace(',','.'))
                            teamBWinOdds = float(matches[begin_info_index+7].replace(',','.'))     

                        except IndexError:
                            print('index error in france_pari live in float casting odds...')    
                            continue
                        except ValueError:
                            print('value error in france_pari live in float casting odds...')    
                            continue

                    else: # when odds are le fail o the first screen
                        #time.sleep(wait_time12)
            #s!!!! must change this code - see NB notrte above         

            ## DO CODE TO FOLLOW TO OTHER SCREEN ..!? ...

                        try:
                            #teamAWinOdds = float(single_game_right[2].replace(',','.'))
                            #draw_odds    = float(single_game_right[4].replace(',','.'))
                            #teamBWinOdds = float(single_game_right[6].replace(',','.'))

                            if len(matches) <= 7:
                                
                                teamAWinOdds = float(matches[begin_info_index+3].replace(',','.'))
                                #draw_odds    = float(matches[begin_info_index+5].replace(',','.'))
                                teamBWinOdds = float(matches[begin_info_index+5].replace(',','.'))  
                                draw_odds    = -1.0
                            else:
                                teamAWinOdds = float(matches[begin_info_index+3].replace(',','.'))
                                draw_odds    = float(matches[begin_info_index+5].replace(',','.'))
                                teamBWinOdds = float(matches[begin_info_index+7].replace(',','.'))     

                        except IndexError:
                            print('index error in france_pari live in float casting odds...')    
                            continue
                        except ValueError:
                            print('value error in france_pari live in float casting odds...')    
                            continue        

                    #time.sleep(wait_time12)
                    teams = teamA + ' - ' + teamB

                    full_all_bookies_allLeagues_match_data[ france_pari + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                    full_all_bookies_allLeagues_match_data[ france_pari + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
                    full_all_bookies_allLeagues_match_data[ france_pari + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)

            print('block number ' + str(i+1))


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

                txt_content = stuff.text

                check_teams_in_str = [y for y in All_ligue1_team_list if find_substring(y,unidecode.unidecode(txt_content).lower())]

                if len(check_teams_in_str) < 1 and 'HALF' not in txt_content: # and 'win the match' in txt_content:
                    pass
                    #continue

                try:
                    teamA = comon_TeamNames_mapper[unidecode.unidecode(txt_content.split('\n')[2]).lower().strip()]
                    teamB = comon_TeamNames_mapper[unidecode.unidecode(txt_content.split('\n')[4]).lower().strip()] 
                    teams = teamA + ' - ' + teamB
                except IndexError:
                    print('index error in zebet live in float casting odds...')    
                    
                except KeyError:
                    print('value error in zebet live in float casting odds...')    
                    continue  


                #live_odds_path =  stuff.find_element_by_xpath('//div/div[2]/a')

                ## check syntax !?....?
                #live_odds_match_link = odds_path.get('href')

                #then odds are given for home teAm to win or draw only ...??

                # can ue fact that sum of the 3 odds inverses shou
                # ld equal 1 to get :
                # odd away team to win :  1/odd_awat_team_to_win   = 1 - [1/(home_team_win) + 1/draw]
                # then do surebet calc as usual

                ## must click on and navigate on the lives odds link here :

        ##(this is the xpath on the navigated to page via the button clivk())
        ### !!!!!//*[@id="event"]   -- NOW NOTTEEE BIG ONE --> the number of odds here can vary, eg rn writing this lyon were 3- 0 to Strasbourg at 85 mins or so and they only had a draw and strasbourg win 
        ### to bet on , ie no odds le fail for lyon win ! ?? -- this affects A LOT OF CODE

                #then inspect @ //*[@id="live"]/article[1] - for win/draw odds  
                live_odds_game_info = txt_content.split('\n')

                if len(live_odds_game_info) <= 7:
                    continue

                if len(live_odds_game_info) >= 2:
                    if live_odds_game_info[1] == 'ENDED':
                        continue   
                #if teamA in All_ligue1_team_list and teamB in All_ligue1_team_list and len(live_odds_game_info) >= 11:
                print('yes its a ligue 1 match -> follow link !')
                # follow link code goes here...

                try:
                    teamAWinOdds = float(live_odds_game_info[7].replace(',','.'))
                    draw_odds    = float(live_odds_game_info[9].replace(',','.'))
                    teamBWinOdds = float(live_odds_game_info[11].replace(',','.'))
                except IndexError:
                    print('index error in zebet live in float casting odds...')    
                    continue
                except ValueError:
                    print('value error in zebet live in float casting odds...')    
                    continue                
            
                try:
                    full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                    full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(draw_odds)
                    full_all_bookies_allLeagues_match_data[ zebet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(teamBWinOdds)
                except IndexError:
                    print('index error in zebet live in filling the dict...')    
                    continue
                except ValueError:
                    print('value error in zebet live in float casting odds...')    
                    continue  

 
        if winimax in sites :        
            print('in winimax ligue1 pre-match parsing .... \n \n')   
            time.sleep(wait_time12)
            time.sleep(wait_time12)
            ligue1_games_nested_gamesinfo_winimax = driver.find_elements_by_xpath('//*[@id="app-inner"]/span/div/div[2]/div/section/div/div[1]/div/div/div')    
            ligue1_games_nested_gamesinfo_winimax_3 = driver.find_elements_by_xpath('//*[@id="app-inner"]/span/div/div/div[2]/section/div/div[1]/div/div/div')
            ligue1_games_nested_gamesinfo_winimax_1 = driver.find_elements_by_xpath('/html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/section/div/div[1]/div/div/div')                    
            ligue1_games_nested_gamesinfo_winimax_2 = driver.find_elements_by_xpath('//*[@id="app-inner"]/span/div/div[2]/section/div/div[1]/div/div/div')                                
                                                                                # /html/body/div[3]/div/div/section/div/div[1]/div/span/div/div[2]/div/section/div/div[1]/div/div    
            if not  ligue1_games_nested_gamesinfo_winimax:
                ligue1_games_nested_gamesinfo_winimax = ligue1_games_nested_gamesinfo_winimax_1
                if not ligue1_games_nested_gamesinfo_winimax_1:
                    ligue1_games_nested_gamesinfo_winimax = ligue1_games_nested_gamesinfo_winimax_2                                                                    
                    if not ligue1_games_nested_gamesinfo_winimax_2:
                        ligue1_games_nested_gamesinfo_winimax =  ligue1_games_nested_gamesinfo_winimax_3                                                                   
                                                                                                                        
            # TEST _ CHANGE Loop var to the live one here temporarily
            for matches in ligue1_games_nested_gamesinfo_winimax: #ligue1_games_nested_gamesinfo_winimax_live_footy:  # ligue1_games_nested_gamesinfo_winimax:                 #//*[@id="app-inner"]/span/div/div[2]/div/section/div/div[1]/div/div

                if matches.rect['height'] < 50.0:
                    #check if you get a non match day like - alternative betting type header
                    # (occues at the end of the ligue one games list on winimax pro ejemplo0)
                    # if not (any(char.isdigit() for char in matches.text)):
                    #    continue
                    if find_substring("BETS ON THE ", matches.text) or find_substring("UPCOMING ", matches.text) :
                        break
                    date = unidecode.unidecode(matches.text)   

                    continue

                # crappy way to filter out non -soccer events and only ligue1 teams :
            
                split_match_data_str = matches.text.split('\n')
                time.sleep(wait_time12)
                if len(split_match_data_str) >= 8:
                    #check_teams_in_str = [True for y in All_ligue1_team_list if find_substring(y,unidecode.unidecode(matches.text).lower())]

                    #if not check_teams_in_str:
                    #    continue

                    # poss replace this with 'soccer/football, Ligue1 ', the teams list etc (remove the not - negation of in !)
                    if '1 UberEats' not in matches.text: 
                        continue

                    teams = comon_TeamNames_mapper[unidecode.unidecode(split_match_data_str[2]).lower()] + ' - ' +  comon_TeamNames_mapper[unidecode.unidecode(split_match_data_str[3]).lower()]
                    competition   =  compettition_ #split_match_data_str[1]    

                    try :
                        teamAWinOdds  = float(split_match_data_str[6].replace(',','.'))
                        draw_odds     = float(split_match_data_str[8].replace(',','.'))
                        teamBWinOdds  = float(split_match_data_str[10].replace(',','.'))
                    except ValueError:                          
                        any_errors = False
                        print(" Value  Error  caught in your winamax parse func. block call --  :( ..... ")
                        continue

                    if teamAWinOdds == 0.0 or teamBWinOdds == 0.0 or draw_odds == 0.0:
                        print('found a missing odd in Wininmax -- equal to 0.0 as Its found, continuing ....\n')
                        continue

                    #if teams in locals() or teams in globals():    
                    full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamAWinOdds) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                    full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(draw_odds)
                    full_all_bookies_allLeagues_match_data[ winimax + '_' + date.lower() + '_' + competition.lower() + '_' + teams.lower()].append(teamBWinOdds)


        if  betclic in sites :
            print('in betclic ligue1 pre-match parsing .... \n \n')  

            time.sleep(wait_time12)
            time.sleep(wait_time12)

            # /html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details  
            ligue1_games_info_betclic = driver.find_elements_by_xpath(  '/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details/div') 
            ligue1_games_info_betclic_3 = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-live-sports/div/app-live-event-bucket-list/bcdk-vertical-scroller/div/div[2]/div/div/app-live-event-bucket/div/div')    
            #ligue1_games_info_betclic_2 = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-live-sports/div/app-live-event-bucket-list/bcdk-vertical-scroller/div/div[2]/div/div/app-live-event-bucket[1]/div/div/div[2]/div')
            ligue1_games_info_betclic_2 = driver.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-live-page/div/sports-live-event-bucket-list/bcdk-vertical-scroller/div/div[2]/div/div/sports-live-event-bucket[1]/div/div/div[2]/app-live-event')  
                                                               #/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-live-sports/div/app-live-event-bucket-list/bcdk-vertical-scroller/div/div[2]/div/div/app-live-event-bucket[1]/div/div/div[2]
                                                                      #[1]/div/div/div[2]/app-live-event[1]
            ## TODO : need to actually make call into zebet champ league page to get champ_league_games_nested_gamesinfo_zebet:
            #for matches in  ligue1_games_infozebet:
            #parts1 = ligue1_games_info_betclic[0].text.split('+')
            competition = compettition_

            if not ligue1_games_info_betclic:
                ligue1_games_info_betclic = ligue1_games_info_betclic_2

            ligue1_games_info_betclic = ligue1_games_info_betclic_3    
            for dates in  ligue1_games_info_betclic:

                ## check is sport block 'soccer' or 'football' first
                sport_info_element = dates.find_element_by_xpath('.//div[1]')

                if 'football' in sport_info_element.text.lower() or 'soccer' in sport_info_element.text.lower() :
                    gamesList = dates.find_elements_by_xpath('.//div[2]/app-live-event/a/div')
                else:
                    continue    

                for game in gamesList:    
                    info_per_match = game.text.split('\n')
       ## !!! this dates construct doesn seem to exist any more -- must use somthing else     -- infact your new _2 web element just has one long string for all games to parse...
       # -- so maybe use this directly   

                    date = unidecode.unidecode(info_per_match[0])
                    ## Live string needs another branch to handle - diff indices for teams and odds as per 'match' string then being :
                    # ®\n37' - 1ère  mt\bordeaux\n1 - 1\nlorient\nrésultat du match\nbord\neaux\n2,15\nn\nul\n2,35\nlor\nient\n3,15\nquelle équipe marquera le but 3 ?\nbord\neaux\n1,75\npas de\n but\n4,10\nlor\nient\n2,25\n67\nparis\n"
                    
                    #info_per_match = matchs.split('\n')
                    if len(info_per_match) >= 13 :

                        ## !!! LIVE games change to be done as swmn here...
                        ## Live string needs another branch to handle - diff indices for teams and odds as per 'match' string then being :
                        # ®\n37' - 1ère  mt\bordeaux\n1 - 1\nlorient\nrésultat du match\nbord\neaux\n2,15\nn\nul\n2,35\nlor\nient\n3,15\nquelle équipe marquera le but 3 ?\nbord\neaux\n1,75\npas de\n but\n4,10\nlor\nient\n2,25\n67\nparis\n"

                        full_nul_word = False
                        ## find index where draw ('NUL' au ffrancais) is as an anchor to get all the odds values from their indices
                        for k,bit in enumerate(info_per_match):
                            if bit == 'NUL':
                                draw_indx = k
                                full_nul_word = True
                            if k != len(info_per_match):
                                if bit == 'N' and info_per_match[k+1] == 'UL':
                                    draw_indx = k        
                        try:
                            
                            teamA_clean =  comon_TeamNames_mapper[unidecode.unidecode(info_per_match[2]).lower()]
                            teamB_clean =  comon_TeamNames_mapper[unidecode.unidecode(info_per_match[4]).lower()]
                            #check_teams_in_str = [y for y in comon_TeamNames_mapper.items() if find_substring(y,teamA_clean)]
                        except IndexError:
                            any_errors = False
                            print("Index Error  caught in your BETCLIC parse func. block call --  :( .....")
                            continue
                        try:
                            teamA = teamA_clean  #comon_TeamNames_mapper[teamA_clean]  
                            teamB = teamB_clean  #comon_TeamNames_mapper[teamB_clean]  
                        except KeyError:
                            any_errors = False
                            print("Kwy Error  caught in your BETCLIC parse func. block call --  :( .....")
                            continue

                        try:
                            
                            if full_nul_word:
                                teamAWinOdds = info_per_match[ draw_indx - 1]
                                draw_odds    = info_per_match[ draw_indx + 1] #8 ?]
                                teamBWinOdds = info_per_match[ draw_indx + 4] # 10 ?

                            else:
                                teamAWinOdds = info_per_match[ draw_indx - 1]
                                draw_odds    = info_per_match[ draw_indx + 2] #8 ?]
                                teamBWinOdds = info_per_match[ draw_indx + 5] # 10 ?                              

                        except IndexError:
                            any_errors = False
                            print("Index Error  caught in your BETCLIC parse func. block call --  :( .....")
                            continue

                        try:
                            full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA + ' - ' + teamB].append(float(teamAWinOdds.replace(',','.'))) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                            full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA + ' - ' + teamB].append(float(draw_odds.replace(',','.')))
                            full_all_bookies_allLeagues_match_data[ betclic + '_' + date.lower() + '_' + competition.lower() + '_' + teamA + ' - ' + teamB].append(float(teamBWinOdds.replace(',','.')))

                        except ValueError:
                            any_errors = False
                            print("Error  caught in your BETCLIC parse func. block call --  :( .....")
                            continue

        if  unibet in sites :
                # unibet tree struct to games elements:
                    print('in unibet ligue1 pre-match parsing .... \n \n')  
                    # Live ligue1 games...
                    wait_time = random.randint(1,2)
                    time.sleep(wait_time)
                    time.sleep(wait_time)

                    games_infoBlocks_0 = driver.find_elements_by_xpath('//*[@id="page__competitionview"]/div/div[1]/div[2]/div/div/div') 
                    time.sleep(wait_time)
                    games_infoBlocks_1 = driver.find_elements_by_xpath('/html/body/div[1]/div[2]/div[5]/div/section/div/section/div/section/div/div[2]/div[3]/ul/li/div')
                    # team names and competitio nshud be in here
                    #j = 0

                    time.sleep(wait_time)
                    games_infoBlocks = games_infoBlocks_0
                    if not games_infoBlocks_0:
                        games_infoBlocks = games_infoBlocks_1

                    for block in games_infoBlocks:

                        try:    
                            sep_games = block.text.split('LIVE')
                        except selenium.common.exceptions.StaleElementReferenceException:
                            print('selenium.common.exceptions.StaleElementReferenceException in unibet , continuing ....')
                            continue

                        for game_block in sep_games:

                            game_infos  = game_block.split('\n')

                            if len(game_infos) >= 13:
                                competition =  unidecode.unidecode(game_infos[0])
                                teamA_clean =  unidecode.unidecode(game_infos[2]).lower()
                                teamB_clean =  unidecode.unidecode(game_infos[3]).lower()
                            else:
                                continue    
                            
                            check_teams_in_str = [y for y in All_ligue1_team_list if find_substring(y,teamA_clean)]

                            if len(check_teams_in_str) < 1:
                                continue
                            else:
                                teamA = comon_TeamNames_mapper[teamA_clean]
                                teamB = comon_TeamNames_mapper[teamB_clean]

                            try:
                                oddsTeamA = float(game_infos[8].replace(',','.')) 
                                oddsDraw  = float(game_infos[10].replace(',','.'))  
                                oddsTeamB = float(game_infos[12].replace(',','.'))

                            except ValueError:
                                any_errors = False
                                print("Error  caught in your UNIBET parse func. block call --  :( .....")
                                continue   

                            full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teamA.lower() + ' - ' + teamB.lower()].append(oddsTeamA) #= teamAWinOdds + '_' + draw_odds + '_' + teamBWinOdds
                            full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teamA.lower() + ' - ' + teamB.lower()].append(oddsDraw)
                            full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teamA.lower() + ' - ' + teamB.lower()].append(oddsTeamB)

                            #odds of game are then in :
                            #game_block = game_block.find_element_by_xpath('.//[@id="b03b18c2-763c-44ea-aa2b-53835d043b8c"]/div')
                            ## full psath gfor this (odds) probly better
                            #/html/body/div[1]/div[2]/div[5]/div/section/div/section/div/section/div/div[1]/div[2]/div/div/div/    section/div/ul/li/div/div/li/div/ul/ul/li/div[2]/div[2]/div/section/div/div
                            #print(str(j + 1))
                        # 3 'span' elements in here with odds

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
        return full_all_bookies_allLeagues_match_data 
        
    items = full_all_bookies_allLeagues_match_data.items() 
    for item in items: 

        try:
            keys = item[0]
            values = item[1]

        except KeyError:        
            print("Error -- key value does not exist in the full_data dict. ! -- return False as a failure from the parsing function...")
            return full_all_bookies_allLeagues_match_data    
        
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
    return all_split_sites_data


def start_proxie_cycle():    

    PROXY_COUNTER = 0
    proxies = req_proxy.get_proxy_list()
    dont_recimpute_surebets = False
    dataDictChangdCounter = 0
    sure_bet_counter = 0

    k=13
    global all_split_sites_data
    all_split_sites_data_copy = {}

    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

    RAND_PROXY_JUMP = random.randint(1,5)

    while(True):

        if PROXY_COUNTER >= 2*len(proxies) - 1:
            proxies = req_proxy.get_proxy_list()

        PROXY = proxies[PROXY_COUNTER].get_address()

        webdriver.DesiredCapabilities.CHROME['proxy']={
        "httpProxy":PROXY,
        "ftpProxy":PROXY,
        "sslProxy":PROXY,
        "proxyType":"MANUAL",
        }

        PROXY_COUNTER += random.randint(1,RAND_PROXY_JUMP)
        k += 1

        data = parseSites_live(driver)   

        ## why did i do this/ change this from the rep-match method :  
        # if data:
        #     PROXY_COUNTER += 1    

        # else:

        #     PROXY_COUNTER += 1  
        #     print("Error i parsing function...retring... But needs diagnostics and/or a fix ! ...")
        #     pass

        #for dicts in data:
        # # remove key here...
        #     for key,val in dicts.items():
        #         if len(val) < 3:
        #             dicts.pop(key)

        if data == all_split_sites_data_copy:
            dont_recimpute_surebets = True
            dataDictChangdCounter += 1
            print(' #############################################################new data dict. has NOT been updated ...:( -- so no need to re-check surebets        ################################################################### .... ;)')
            #time.sleep(wait_time_idirNoChanges)
        else:
            dont_recimpute_surebets = False

        all_split_sites_data_copy = copy.deepcopy(data)
        # if all_split_sites_data == all_split_sites_data_copy:
        #     dont_recimpute_surebets = True
        #     dataDictChangdCounter += 1
        #     print(' #############################################################new data dict. has NOT been updated ...:( -- so no need to re-check surebets        ################################################################### .... ;)')
        #     time.sleep(wait_time_idirNoChanges)
        # else:
        #     dont_recimpute_surebets = False
        #     # print('lenght of NEWd dict = ' + str(len(all_split_sites_data)))
        #     print('  &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&  new data dict. has been updated ...:( -- so can check surebets ..     %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% .... ;)')
            
        #print('total num attempts/loops  = ' + str(globCounter) + '-- no. of times data changes & was updated in parsing = ' + str(dataDictChangdCounter))    
            #print('###############################################################################  Current Dict : ')
        
            # print(str(all_split_sites_data))
            # print(' ############################################################################### Current Dict FINISHED  ###############################################################################')
            # #print('new data dict. has been updated ...! :)')

        #local copy in infinite loop to check if its changed or not - then dont need to redo sure bets checks if not
        #all_split_sites_data_copy = data

        wait_time = random.randint(1,2)        
        time.sleep(wait_time)   
        if len(data) < 3 :
            print('*************************** Error - less than three bookies scrapped for games here ..., try again -- if this error persists raise a bug ******************************')
            #return False
            ## dont exit but continue as my try fetch 3 sites worth of data again...
            continue

        # if (globCounter % 10) == 0:
        #print('AVerage time to do parsings was = ' + str(total_time_parsing/globCounter)) 
        print('number of surebets found so far is = ' + str(sure_bet_counter))    

        if not dont_recimpute_surebets :
            start_surebet_timer = time.time()
            index = 0    
            ## TODO  - a biggg TODO  -- the following is just the combos of 3 but will also need to cater for when only 2 bookies are involved in a footy surebet :
            # i.e 1 bookie has the needed home win and draw odd and the other the awat=y win and also vice versa.
            #redundancy_bet_checklist = {}

            checxking_surebet_counts = 0
            for subset in itertools.combinations(data, 3):  
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
                            date =   key_str_split_by_underscore[1]
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
                            
                            checxking_surebet_counts += 1
                            print('Checking for surebets .... checxking_surebet_counts =  ' + str(checxking_surebet_counts)) 
                            print('Bookies in order of odds are : ' + bookie_1  + bookie_2 + bookie_3 )

                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2]
                            if check_is_surebet(home_win_odds, draw_odds, away_win_odds):  # encode bookie outcomes as 'W','D','L' wrt to the 1st team in the match descrpt. , i.e The 'hometeam' 
                                
                                # if  returnBetSizes:
                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE BET FOUND !  :)   *****************************************************************************')   
                                #     #surebet_odds_list = [home_win_odds, draw_odds, away_win_odds]                                 
                                #     #get_surebet_factor(surebet_odds_list) #  odds_A, odds_B):
                                #     #sure_betsto_place = return_surebet_vals(surebet_odds_list, stake_val)
                                #     send_mail_alert_gen_socer_surebet(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1,sure_betsto_place)

                                # else:      
                                #     send_mail_alert_gen_socer_surebet(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1)
                                print('Odds comboo is')
                                print(W_1)
                                print(D)
                                
                                # try:
                                #     profit = 1.0 - (1/subsetList[0][key][0] + 1/subsetList[1][key_bookkie2][1] + 1/subsetList[2][key_bookkie3][2]) 
                                # except ZeroDivisionError:
                                #     continue

                                #184 45238262
                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)
                                profit = (stake)/surebet_factor
                                proportionsABC_listRnd = [round(x,2) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3,W_1,D,teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, profit,home_win_odds, draw_odds, away_win_odds)
                                #print('Bet (sure)  kombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 
                                #print('Bet (sure)  kombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 'in the bookie ->' + bookie_1 + ' the draw at odds = '  + str(subsetList[1][key_bookkie2][1]) + ' in bookie ' + str(bookie_2) + ' and finally the other teams win odds @ ' + str(subsetList[2][key_bookkie3][2]) + str(bookie_3) + '  \n')
                                # these continues will avoid the sitch of 'same' surebet (swapoed one) being mailed out
                                #return_surebet_vals([subsetList[0][key][0],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][2]],1000)
                                continue
                            
                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][0],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][1] 
                            if check_is_surebet(home_win_odds, draw_odds, away_win_odds):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE BET FOUND !  :)   *****************************************************************************') 
                                
                                #profit = 1.0 - (1/subsetList[0][key][0] + 1/subsetList[1][key_bookkie2][1] + 1/subsetList[2][key_bookkie3][2]) 

                                #184 45238262
                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)

                                profit = (stake)/surebet_factor
                                #profit = round(stake*(-subsetList[0][key][0]*proportionsABC_list[0]  + subsetList[1][key_bookkie2][2]*proportionsABC_list[1] + subsetList[2][key_bookkie3][1]*proportionsABC_list[2]),3)
                                proportionsABC_listRnd = [round(x,2) for x in proportionsABC_list]
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3, W_1, W_2,teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, profit,home_win_odds, draw_odds, away_win_odds)
                                #print('Bet (sure)  kombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 
                                #send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,W_1,W_2,teamA_1, teamB_1, date,competition_1)
                                #print('Bet (sure)  sombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 'in the bookie ->' + bookie_1 + ' the away win at odds = '  + str(subsetList[1][key_bookkie2][2]) + ' in bookie ' + str(bookie_2) + ' and finally the draw odds @ ' + str(subsetList[2][key_bookkie3][1]) + str(bookie_3) + '  \n')
                                #return_surebet_vals([subsetList[0][key][0],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][1]],1000)
                                continue

                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][1],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][2]
                            if check_is_surebet(home_win_odds, draw_odds, away_win_odds):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE-BET FOUND !  :)   *****************************************************************************') 
                                
                                #profit = 1.0 - (1/subsetList[0][key][0] + 1/subsetList[1][key_bookkie2][1] + 1/subsetList[2][key_bookkie3][2]) 

                                #184 45238262
                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)

                                proportionsABC_listRnd = [round(x,2) for x in proportionsABC_list]
                                profit = (stake)/surebet_factor
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3, D, W_1, teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, profit,home_win_odds, draw_odds, away_win_odds)
                                #print('Bet (sure)  kombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 
                                
                                #send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,D,W_1,teamA_1, teamB_1, date,competition_1) 
                                #print('Bet (sure)  combo just found has the draw odds at ' + str(subsetList[0][key][1]) + 'in the bookie ->' + bookie_1 + ' the home win at odds = '  + str(subsetList[1][key_bookkie2][0]) + ' in bookie ' + str(bookie_2) + ' and finally the away team win odds @ ' +  str(subsetList[2][key_bookkie3][2]) + ' in the bookies ->' + str(bookie_3) + '  \n') 
                                #return_surebet_vals([subsetList[0][key][1],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][2]],1000)
                                continue

                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][1],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][0] 
                            if check_is_surebet(home_win_odds, draw_odds, away_win_odds):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SURE-BET FOUND !  :)   *****************************************************************************') 
                                
                                #profit = 1.0 - (1/subsetList[0][key][0] + 1/subsetList[1][key_bookkie2][1] + 1/subsetList[2][key_bookkie3][2]) 

                                #184 45238262
                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)

                                proportionsABC_listRnd = [round(x,2) for x in proportionsABC_list]
                                profit = (stake)/surebet_factor
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3,D,W_2,teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, profit,home_win_odds, draw_odds, away_win_odds)
                                #print('Bet (sure)  kombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 
                                
                                #send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,D,W_2,teamA_1, teamB_1, date,competition_1) 
                                #return_surebet_vals([subsetList[0][key][1],subsetList[1][key_bookkie2][2],subsetList[2][key_bookkie3][0]],1000)
                                continue

                            home_win_odds, draw_odds, away_win_odds = subsetList[0][key][2],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][1]
                            if check_is_surebet(home_win_odds, draw_odds, away_win_odds):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SUREBET FOUND !  :)   *****************************************************************************') 
                                
                                #profit = 1.0 - (1/subsetList[0][key][0] + 1/subsetList[1][key_bookkie2][1] + 1/subsetList[2][key_bookkie3][2]) 

                                #184 45238262
                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)

                                proportionsABC_listRnd = [round(x,2) for x in proportionsABC_list]

                                profit = (stake)/surebet_factor
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3,W_2,W_1,teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, profit,home_win_odds, draw_odds, away_win_odds)
                                #print('Bet (sure)  kombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 
                                
                                #send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,W_2,W_1,teamA_1, teamB_1, date,competition_1)  
                                #print('Bet (sure)  combo just found has the away team ' +  teamB_1  + ' win odds at ' + str(subsetList[0][key][2]) + 'in the bookie ->' + bookie_1 + ' the home team -> ' + teamA_1  +  '<- win at odds = '  + str(subsetList[1][key_bookkie2][0]) + ' in bookie ' + str(bookie_2) + ' and finally the draw odds @ ' +  str(subsetList[2][key_bookkie3][1]) + ' in the bookies ->' + str(bookie_3) + '  \n') 
                                #return_surebet_vals([subsetList[0][key][2],subsetList[1][key_bookkie2][0],subsetList[2][key_bookkie3][1]],1000)
                                continue                         

                            home_win_odds, draw_odds, away_win_odds =  subsetList[0][key][2],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][0]
                            if check_is_surebet(home_win_odds, draw_odds, away_win_odds):
                                sure_bet_counter += 1
                                print('*****************************************************************************  SUREBET FOUND !  :)   *****************************************************************************') 
                                
                                #profit = 1.0 - (1/subsetList[0][key][0] + 1/subsetList[1][key_bookkie2][1] + 1/subsetList[2][key_bookkie3][2]) 

                                #184 45238262
                                stake = 100.0
                                get_surebet_factor(home_win_odds, draw_odds, away_win_odds)
                                proportionsABC_list =  return_surebet_vals(home_win_odds, draw_odds, away_win_odds,stake = stake)

                                proportionsABC_listRnd = [round(x,2) for x in proportionsABC_list]
                                #profit = round(stake*(-subsetList[0][key][2]*proportionsABC_list[0]  + subsetList[1][key_bookkie2][1]*proportionsABC_list[1] + subsetList[2][key_bookkie3][0]*proportionsABC_list[2]),3)
                                
                                if surebet_factor == 0.0 or surebet_factor == 0:
                                    profit = 100
                                else:
                                    profit = (stake)/surebet_factor
                                
                                send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2 ,bookie_3,W_2,D,teamA_1,teamB_1, date,competition_1,proportionsABC_listRnd, profit,home_win_odds, draw_odds, away_win_odds)
                                #print('Bet (sure)  kombo just found has the wining home teams odds at ' + str(subsetList[0][key][0]) + 
                                
                                #send_mail_alert_gen_socer_surebet(bookie_1, bookie_2, bookie_3,W_2,D,teamA_1, teamB_1, date,competition_1)    
                                #return_surebet_vals([subsetList[0][key][2],subsetList[1][key_bookkie2][1],subsetList[2][key_bookkie3][0]],1000)
                                continue                        

                else:
                    print("Not enough bookies scraped correctly to look for 3 - way surebets...")

        if not dont_recimpute_surebets:

            end_surebet_timer = time.time()
            print("Time taken to just check for surebets besides parsing = " + str(end_surebet_timer - start_surebet_timer))


    return True    


if __name__ == '__main__':

    argv = sys.argv
    DEBUG_OUTPUT  = False
    
    #schtake = 1000
    #retval2 = check_for_sure_bets(float(schtake)) #argv[1]))
    
    the_dtriver = start_proxie_cycle()

    DONE = 1
    

    # if len(argv) >= 2 :

    #     if len(argv) == 8 :

    #         retVal = odds_alert_system(oddType= int(argv[1]), expect_oddValue= float(argv[2]), teamA= argv[3], teamB= argv[4], date= argv[5], competition= argv[6], Bookie1_used= argv[7])

    #     elif  len(argv) == 2 :

    #         retval2 = check_for_sure_bets(float(argv[1])) 

    #     else:

    #         #print("usage:  please indicate with  0 or a 1 in the first cmd line argument to the program wherether you wish to include debugging output prints in it's run or not; 0/1 corresponding to no/yes....")
    #         print("Usage : sportsbetAlertor_v1.py oddType (0 -home team win, 1 - a dra. 2 - away team win ) expect_oddValue teamA teamB competition Bookie1_used.    i.e 7 parameters on thye cmd line after the filename")
    #         print("Heres an Example --- sportsbetAlertor_v1.py  0 1.75  lyon  marseille  ligue1 Winamax")
    #         exit(1)
   
    # else:    
    #     #DEBUG_OUTPUT = bool(int(argv[1]))
    #     retval2 = check_for_sure_bets() #'unibet','zebet','winimaxc','W', 'D','marseilles','nantes','28/11/2020','ligue 1 UberEats')


