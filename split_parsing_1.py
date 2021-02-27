import requests
import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import random,time,os
supSon = time.time() 

from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
req_proxy = RequestProxy()
proxies = req_proxy.get_proxy_list()

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from metaLeague_data import *
import unidecode,datetime
import pickle
import scipy
import scipy.io
from scipy.io import savemat,loadmat
## TODO : must generalize this and add file to code bundle
DRIVER_PATH = r'./chromedriver' #the path where you have "chromedriver" file.


options = Options()
options.headless = True
#options.LogLevel = False
options.add_argument("--window-size=1920,1200")
#options.add_argument("--LogLevel=0")
#options.add_argument("user-agent= 'Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41' ")
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_6) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.698.0 Safari/534.24'")


driver2 = webdriver.Chrome(options=options, executable_path=DRIVER_PATH, service_args=["--verbose", "--log-path=D:\\qc1.log"])
    
num_from_master = 5
# initialize proxy count and create list of proxies from the prox generator
PROXY_COUNTER = num_from_master + 1
proxies = req_proxy.get_proxy_list()



if PROXY_COUNTER == len(proxies) - 1:
    proxies = req_proxy.get_proxy_list()

PROXY = proxies[PROXY_COUNTER].get_address()
#driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

webdriver.DesiredCapabilities.CHROME['proxy']={
    "httpProxy":PROXY,
    "ftpProxy":PROXY,
    "sslProxy":PROXY,
    "proxyType":"MANUAL",
}

global full_all_bookies_allLeagues_match_data, all_split_sites_data
PROXY_COUNTER += 1

start_subProcParserTimer = time.time()
for i,sites in enumerate(websites_ligue1_links_p2[0:]):

    #begin = timeit.timeit()  
    driver2.get(sites)
    #finish = timeit.timeit()
    compettition_ = 'ligue1'


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

        wait_time37 = random.randint(3,6)
        wait_time12 = random.randint(1,2)
        #print('second rand wait time = ' + str(wait_time37))
        time.sleep(wait_time37)  

        ligue1_games_nested_gamesinfo_unibet_1 =  driver2.find_elements_by_xpath('//*[@id="page__competitionview"]/div/div[1]/div[2]/div/div/div/div[3]/div[2]/div')  
        ligue1_games_nested_gamesinfo_unibet_2 =  driver2.find_elements_by_xpath('/html/body/div[1]/div[2]/div[5]/div/section/div/section/div/section/div[1]/div/div[2]/div/div/div[2]/div[2]/div[1]/div/div')                                                                            #//*[@id="page__competitionview"]/div/div[1]/div[2]/div/div/div/div[3]/div[2] 
        time.sleep(wait_time12)                                                        #//*[@id="page__competitionview"]/div/div[1]/div[2]/div/div/div/div[3]/div[2]
        ligue1_games_nested_gamesinfo_unibet_3 =  driver2.find_elements_by_xpath('//*[@id="page__competitionview"]/div[1]/div/div[2]/div/div/div[2]/div[2]/div')
        ligue1_games_nested_gamesinfo_unibet_4 =  driver2.find_elements_by_xpath('//*[@id="page__competitionview"]/div[1]/div/div[2]/div/div/div[2]/div[2]')
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
                
            # elif  ligue1_games_nested_gamesinfo_unibet_4 and len(ligue1_games_nested_gamesinfo_unibet_2[0].text) < len(ligue1_games_nested_gamesinfo_unibet_4[0].text) :   
            #     ligue1_games_nested_gamesinfo_unibet = ligue1_games_nested_gamesinfo_unibet_4

            elif   ligue1_games_nested_gamesinfo_unibet_2 and  not ligue1_games_nested_gamesinfo_unibet_4:
                ligue1_games_nested_gamesinfo_unibet = ligue1_games_nested_gamesinfo_unibet_2

            elif  not ligue1_games_nested_gamesinfo_unibet_2 and  ligue1_games_nested_gamesinfo_unibet_4:
                ligue1_games_nested_gamesinfo_unibet = ligue1_games_nested_gamesinfo_unibet_4

            elif  ligue1_games_nested_gamesinfo_unibet_2 and  ligue1_games_nested_gamesinfo_unibet_4:
                ligue1_games_nested_gamesinfo_unibet = ligue1_games_nested_gamesinfo_unibet_2    

            else:
                print('driver find element call return nothing ... try again or exit with no results for games in ligue 1 UNIBET...')
                ## TODO : implement another method - different path - maybe full Xpath to a known root easily or use Bueaty soup ...etc.
                continue
        
        for game_info in  ligue1_games_nested_gamesinfo_unibet:
        
            time.sleep(wait_time12)       
            date = 'today' # unidecode.unidecode(game_info.text.split('\n')[0])
            
            if unidecode.unidecode(date.lower()) not in french_dates_list:
                date = date_ 

            #matches_per_date = game_info.find_elements_by_xpath('.//div')

            parts = game_info.text.split('\n')

                    # if '%' not in parts[i+1]:
                    #     longer_info_match = False

            # delimit_2 = parts[i+1].split('\n')
            if len(parts) >= 9: # and len(delimit_2) >= 6 :

                #sep_team_names = parts[i].split('\n')[-2].split(' - ')

                # handle the case of 'sain-etienne'
                #if len(sep_team_names) > 2 and 'tienne' in sep_team_names:

                try:
                    teamA_raw = parts[2].strip()
                    teamB_raw = parts[8].strip()       
                except IndexError:
                    any_errors = False
                    print(" Index  Error  caught in mapper your unibet parse func. block call --  :( ..... ")
                    continue

                try:        
                    teams =  comon_TeamNames_mapper[unidecode.unidecode(teamA_raw).lower()] + ' - ' + comon_TeamNames_mapper[unidecode.unidecode(teamB_raw).lower()]
                except KeyError:
                    any_errors = False
                    print(" Key  Error  caught in mapper your unibet parse func. block call --  :( ..... ")
                    continue                       
                #unidecode.unidecode(parts[i].split('\n')[-2]).lower()

                try:
                    teamAWinOdds = parts[3]    #delimit_2[1].split(' ')[1]
                    draw_odds =    parts[6]    #delimit_2[2].split(' ')[1]                            
                    teamBWinOdds = parts[9]    #delimit_2[3].split(' ')[1]   
                except IndexError:
                    any_errors = False
                    print(" Index  Error  caught in mapper your unibet parse func. block call --  :( ..... ")
                    continue                         
                
                try:
                    full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(float(teamAWinOdds))   
                    full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(float(draw_odds))    
                    full_all_bookies_allLeagues_match_data[ unibet + '_' + date.lower() + '_' + competition.lower() + '_' + teams].append(float(teamBWinOdds))                        
                except ValueError:
                    any_errors = False
                    print(" Value  Error  caught in mapper your unibet parse func. block call --  :( ..... ")
                    continue



    start_france_pari = time.time()  
    if  france_pari in sites :
    # # zebet tree struct to games elements:    
        # live games parsing tips ...:

        # in live link - go to element : //*[@id="currentlive"]/div/div -> list of sub element are divs

## !!! NBBB !!!!
        ## the sub elements per game in here's text = 'Ligue 1 Uber Eats®\n1\n0\nMi-temps\nRennes\nLyon\n1\n1,62\nN\n2,88\n2\n4,33'

        # also note - other league games r mixed up with them so must do a continue in the loop if not a game idir ligue one teams, NOT a break!
        
        print('in france_pari ligue1 pre-match parsing .... \n \n')                                                 
        try:

            ligue1_games_info_france_pari_try_1 = driver2.find_elements_by_xpath('//*[@id="nb-sport-switcher"]/div[1]/div') 
    #       # TODO : need to actually make call into zebet champ league page t33o get champ_league_games_nested_gamesinfo_zebet:
            ligue1_games_info_france_pari_try_2 = driver2.find_elements_by_xpath('//*[@id="colonne_centre"]/div/div/div[2]/div')         
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
            #tot_france_pari +=  end_france_pari - start_france_pari
            print('time taken to process france_pari was = ' + str(end_france_pari - start_france_pari))    
        except NoSuchElementException:
            any_errors = False
            print("Error  caught in your FRANCE_PARI parse func. block call --  :( ..... ")
            continue

    start_betclic = time.time()            
    if  betclic in sites :
        print('in betclic ligue1 pre-match parsing .... \n \n')  

        # /html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details  
                                                                    
        ligue1_games_info_betclic   = driver2.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/app-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details/div')
        ## use this when generalizing leagues ...
        #ligue1_games_info_betclic_2  = driver2.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/app-left-menu/div/app-sports-nav-bar/div/div[1]/app-block/div/div[2]')    
        ligue1_games_info_betclic_1 = driver2.find_elements_by_xpath('/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-competition/bcdk-vertical-scroller/div/div[2]/div/div/app-sport-event-details/div[1]/div')


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

                    # game_info_france1  = dates.text.lower().split('ligue 1 uber eats')
                    # game_info_england1 = dates.text.lower().split('premier league')
                    # game_info_spain1   = dates.text.lower().split('liga primera')
                    # game_info_italy1   = dates.text.lower().split('serie a')
                    # game_info_germany1 = dates.text.lower().split('bundesliga')

                    # if len(game_info_france1) > 1:
                    #     game_info = game_info_france1

                    # elif len(game_info_england1) > 1:
                    #     game_info = game_info_england1    

                    # elif len(game_info_spain1) > 1:
                    #     game_info = game_info_spain1

                    # elif len(game_info_italy1) > 1:
                    #     game_info = game_info_italy1 

                    # elif len(game_info_germany1) > 1:
                    #     game_info = game_info_germany1

                    # else:
                    #     print('issue in getting any proper    matches data in betclic...')
                    #     pass

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
        #tot_betclic += end_betclic - start_betclic
        print('time taken to process betclic was = ' + str(end_betclic - start_betclic))                 


    #sites = "https://www.zebet.fr/en/competition/94-premier_league"
    if  zebet in sites and 'live' not in sites:
    # # zebet tree struct to games elements:                                                     
        print('in zebet ligue1 pre-match parsing .... \n \n')  
        try:
                                                                    #//*[@id="event"]/article[1]/div/div/div/div
            ligue1_games_infozebet = driver2.find_elements_by_xpath('//*[@id="event"]/article/div/div/div/div/div') 
            ## TODO : need to actually make call into zebet champ league page to get champ_league_games_nested_gamesinfo_zebet:

            #will have to take out and pprocess leagues separately for zebet.
            #prem_leagueGames_info =  driver2.find_elements_by_xpath('//*[@id="event"]/article/div/div/div/div/div/div[1]/div')                

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


    check = 1

    #Save data with Pickle
    # output = open('full_all_bookies_allLeagues_match_data', 'wb')
    # pickle.dump(full_all_bookies_allLeagues_match_data, output)
    # output.close()
    # print(' full_all_bookies_allLeagues_match_data : \n ')
    # print(srt(full_all_bookies_allLeagues_match_data) )    s

    filename = 'secndProcDataDicIncUnibet' + '.mat'
    with open(filename, 'wb') as f:
        pickle.dump(full_all_bookies_allLeagues_match_data, f, protocol=pickle.HIGHEST_PROTOCOL)

    # second_proc_data_dict = {}

    # second_proc_data_dict['unibet_andMoreData'] = full_all_bookies_allLeagues_match_data
    # filename = 'secndProcDataDicIncUnibet' + '.mat'

    # #os.getcwd() + '/' + 

    # scipy.io.savemat(filename,second_proc_data_dict, long_field_names=True)   

    doneSon = time.time() 
    print('total time in sub - process no. 2 parsing = ' + str(doneSon - supSon))
    zhite = 0        