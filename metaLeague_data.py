from collections import defaultdict


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

#def data_initializations():

# Cbet general home page link :
# 
cbet_sports_link = "https://cbet.gg/en/sportsbook/prematch"   


###  *********************************** CHAMPION'S LEAGUE lINKS *****************************
#list of website links (most general for football mathces-1st few are for champions league)
france_pari_champions_league_link =  "https://www.france-pari.fr/competition/6674-parier-sur-ligue-des-champions"
# d lads dont want this site as it's shite.
#vbet_champions_league_link        = "https://www.vbet.fr/paris-sportifs?btag=147238_l56803&AFFAGG=#/Soccer/Europe/566/17145852"
unibet_champions_league_link       = "https://www.unibet.fr/sport/football/ligue-des-champions"
zebet_champions_league_link        = "https://www.zebet.fr/fr/competition/6674-ligue_des_champions"
winimax_champions_league_link      = "https://www.winamax.fr/en/sports-betting/sports/1/800000006"
#passionsports__champions_ligue_link = "" 
#sportsbwin_champs_ligue_link       = "https://sports.bwin.fr/fr/sports/football-4/paris-sportifs/europe-7/ligue-des-champions-0:3"

passionsports_champions_league_link  = 'https://www.enligne.parionssport.fdj.fr/paris-football/coupes-d-europe/championsleague?filtre=22906' 
#sportsbwin_premier_league_pre       = '' 
cbet_champions_league_link           = 'https://cbet.gg/en/sportsbook/prematch#/prematch'  
sportifs_pmu_champions_league_link   = 'https://paris-sportifs.pmu.fr/pari/pari/competition/20/football/ligue-des-champions'
betclic_champions_league_link        = 'https://www.betclic.fr/football-s1/ligue-des-champions-c8'

###  *********************************** premier league  lINKS *****************************

france_pari_premier_league_pre    = 'https://www.france-pari.fr/competition/94-parier-sur-premier-league'
unibet_premier_league_pre         = 'https://www.unibet.fr/sport/football/angleterre/premier-league' 
zebet_premier_league_pre          = 'https://www.zebet.fr/en/competition/94-premier_league' 
winimax_premier_league_pre        = 'https://www.winamax.fr/en/sports-betting/sports/1/1' 
passionsports_premier_league_pre  = 'https://www.enligne.parionssport.fdj.fr/paris-football/angleterre/premier-league?filtre=22950' 
#sportsbwin_premier_league_pre     = '' 
cbet_premier_league_pre           = 'https://cbet.gg/en/sportsbook/prematch#/prematch'  
sportifs_pmu_premier_league_pre   = 'https://paris-sportifs.pmu.fr/pari/competition/13/football/premier-league'
betclic_premier_league_pre        = 'https://www.betclic.fr/football-s1/angl-premier-league-c3'

all_premier_league_sites = [ france_pari_premier_league_pre, unibet_premier_league_pre, zebet_premier_league_pre, winimax_premier_league_pre, passionsports_premier_league_pre, sportifs_pmu_premier_league_pre, betclic_premier_league_pre ] # ,cbet_premier_league_pre

# ###  *********************************** La Liga  lINKS *****************************

france_pari_la_liga_pre    = 'https://www.france-pari.fr/competition/306-parier-sur-laliga'
unibet_la_liga_pre         = 'https://www.unibet.fr/sport/football/espagne/liga' 
zebet_la_liga_pre          = 'https://www.zebet.fr/en/competition/306-primera_division' 
winimax_la_liga_pre        = 'https://www.winamax.fr/en/sports-betting/sports/1/32' 
passionsports_la_liga_pre  = 'https://www.enligne.parionssport.fdj.fr/paris-football/espagne/liga-primera' 
#sportsbwin_la_liga_pre     = '' 
cbet_la_liga_pre           = 'https://cbet.gg/en/sportsbook/prematch#/prematch'  
sportifs_pmu_la_liga_pre   = 'https://paris-sportifs.pmu.fr/pari/competition/322/football/la-liga'
betclic_la_liga_pre        = 'https://www.betclic.fr/football-s1/espagne-liga-primera-c7'

all_la_liga_sites = [  france_pari_la_liga_pre , unibet_la_liga_pre, zebet_la_liga_pre, winimax_la_liga_pre , passionsports_la_liga_pre, sportifs_pmu_la_liga_pre, betclic_la_liga_pre ] #, cbet_la_liga_pre

# ###  *********************************** Serie A'   lINKS *****************************

france_pari_serie_a_pre     = 'https://www.france-pari.fr/competition/305-parier-sur-serie-a'
unibet_serie_a_pre          = 'https://www.unibet.fr/sport/football/italie/serie-a' 
zebet_serie_a_pre           = 'https://www.zebet.fr/en/competition/305-serie_a' 
winimax_serie_a_pre         = 'https://www.winamax.fr/en/sports-betting/sports/1/31' 
#sportsbwin_serie_a_pre      = '' 
cbet_serie_a_pre            = 'https://cbet.gg/en/sportsbook/prematch#/prematch'  
sportifs_pmu_serie_a_pre    = 'https://paris-sportifs.pmu.fr/pari/competition/308/football/italie-s%C3%A9rie'
betclic_serie_a_pre         = 'https://www.betclic.fr/football-s1/italie-serie-a-c6'

serie_a_links = [ france_pari_serie_a_pre, unibet_serie_a_pre, zebet_serie_a_pre, winimax_serie_a_pre, sportifs_pmu_serie_a_pre, betclic_serie_a_pre ] # ,cbet_serie_a_pre, passionsports_serie_a_pre

# ###  *********************************** Bundesliga  lINKS *****************************

france_pari_bundesliga_pre    = 'https://www.france-pari.fr/competition/268-parier-sur-bundesliga'
unibet_bundesliga_pre         = 'https://www.unibet.fr/sport/football/allemagne/bundesliga' 
zebet_bundesliga_pre          = 'https://www.zebet.fr/en/competition/268-bundesliga' 
winimax_bundesliga_pre        = 'https://www.winamax.fr/en/sports-betting/sports/1/30' 
passionsports_bundesliga_pre  = 'https://www.enligne.parionssport.fdj.fr/paris-football/allemagne/bundesliga-1?filtre=22968' 
# sportsbwin_bundesliga_pre    = '' 
cbet_bundesliga_pre           = 'https://cbet.gg/en/sportsbook/prematch#/prematch'  
betclic_bundersliga_pre       = 'https://www.betclic.fr/football-s1/allemagne-bundesliga-c5'
sportifs_pmu_bundesliga_pre   = 'https://paris-sportifs.pmu.fr/pari/competition/32/football/bundesliga'

bundesliga_links = [ france_pari_bundesliga_pre, unibet_bundesliga_pre, zebet_bundesliga_pre, winimax_bundesliga_pre, passionsports_bundesliga_pre, betclic_bundersliga_pre, sportifs_pmu_bundesliga_pre] # ,cbet_bundesliga_pre

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
# betclic_ligue1_live       = "https://www.betclic.fr/football-s1/ligue-1-uber-eats-c4"
# france_pari_ligue1_live   = "https://www.france-pari.fr/competition/96-parier-sur-ligue-1-uber-eats"
# unibet_ligue1_live        = "https://www.unibet.fr/sport/football/france-foot/ligue-1-ubereats-france"
# zebet_ligue1_live         = "https://www.zebet.fr/en/competition/96-ligue_1_uber_eats"
winimax_ligue1_live         = "https://www.winamax.fr/en/sports-betting/live"

# passionsports_ligue1_live = "https://www.enligne.parionssport.fdj.fr/paris-football/france/ligue-1-uber-eats?filtre=22892"
# sportsbwin_ligue1_live    = "https://sports.bwin.fr/fr/sports/football-4/paris-sportifs/france-16/ligue-1-4131"
# cbet_ligue1_link          = "https://cbet.gg/en/sportsbook/prematch#/prematch"
# paris_sportifs_pmu_live   = "https://paris-sportifs.pmu.fr/pari/competition/169/football/ligue-1-uber-eats"


#betclic_ligue1_link       = ""
#pokerstarsSports_ligue1_link = ""
#pasinoBet_ligue1_link        = ""

###  *********************************** EUROPA LEAGUE lINKS *****************************
#list of website links (most general for football mathces-1st few are for champions league)
france_pari_europa_league_link      =  "https://www.france-pari.fr/competition/6675-parier-sur-europa-ligue"   #(?? - check this !!)
# d lads dont want this site as it's shite.
#vbet_champions_league_link        = "https://www.vbet.fr/paris-sportifs?btag=147238_l56803&AFFAGG=#/Soccer/Europe/566/17145852"
unibet_europa_league_link           = "https://www.unibet.fr/sport/football/europa-league/europa-league-matchs"
zebet_europa_league_link            = "https://www.zebet.fr/en/competition/6675-europa_league"
winimax_europa_league_link          = "https://www.winamax.fr/en/sports-betting/sports/1/800000007"
passionsports_europa_league_link    = "https://www.enligne.parionssport.fdj.fr/paris-football"
sportsbwin_europa_league_link       = "https://sports.bwin.fr/fr/sports/football-4/paris-sportifs/europe-7/europa-league-0:5"    
betclic_europa_league_link          = "https://www.betclic.fr/football-s1/ligue-europa-c3453"

epl_links =  [ france_pari_premier_league_pre, unibet_premier_league_pre, zebet_premier_league_pre, winimax_premier_league_pre, passionsports_premier_league_pre, 
                sportifs_pmu_premier_league_pre, betclic_premier_league_pre ] # ,cbet_premier_league_pre#

## name consistent Champions and Europa league team names:
#England
#manchester_utd   = "manchester united"
xtra_champ_league_maping = { 'manchester city' : "manchester city"
, 'chelsea'         : "chelsea"
, 'liverpool'       : "liverpool"
, 'real'            : "real madrid"
, 'barcelone'       : "barcelona"
, 'fc barcelone'    : "barcelona"
, 'sevilla'         : "sevilla"
, 'fc sevilla'         : "sevilla"

, 'seville'         : "sevilla"
, 'fc seville'         : "sevilla"
,"porto"       : "porto"
,"fc porto"       : "porto"
, 'atletico madrid' : "atletico madrid"
, 'juventus'        : "juventus"  
, 'juventus turin'  : "juventus"  
, 'atalanta'         : "atalanta" 
, 'atalanta bergame' : "atalanta"  
, 'lazio'           : "lazio"
, 'fc lazio'           : "lazio"
, 'lazio rome'           : "lazio"
, 'lazio roma'           : "lazio"
, 'bayern munich'   : "bayern munich"
, 'fc bayern munich'   : "bayern munich" 
, 'bayern munich fc'   : "bayern munich" 
, 'bayern munchen'   : "bayern munich" 
, 'borussia dortmund'        : "dortmund" 
, 'dortmund'              : "dortmund"
, "borussia m'gladbach" : "munchengladbach"
, "borussia monchengladbach" : "munchengladbach"
, "b. monchengladbach" : "munchengladbach"
, "b. m'gladbach" : "munchengladbach"
, "borussia munchengladbach" : "munchengladbach"
, "m'gladbach" : "munchengladbach"
, "bor m'gladbach" : "munchengladbach"
, 'rb leipzig'         : "leipzig"
, 'leipzig'            : "leipzig"
, 'paris st germain'   : "paris st germain" }

# ## russia/Ukraine
# shaktar          = "shaktar donetsk"
# dynamo_kiev      = "dynamo kiev"
# krasnodar        = "fc krasnodar"

# ## Portugal / Greece / Turkey / Holland / Austria / Belgium/ Hungary  Denmark
# porto                = "fc porto"
# olympiakos           = "olympiakos"
# ajax                 = "ajax"
# salzburg             = "rb salzburg"
# club_brugge          = "club brugge"


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
Bordeaux      =  'bordeaux'
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


comon_TeamNames_mapper = {'stade brestois': 'brest', 'brestois': 'brest', 'olympiue lyonnais':'lyon', 'olympiue lyon':'lyon','paris saint-germain':'psg','paris saint germain':'psg','paris st-germain':'psg','paris st germain':'psg'
                    ,'paris sg':'psg','paris s g':'psg','psg':'psg','girondins de bordeaux':'bordeaux','girondins bordeaux':'bordeaux','bordeaux':'bordeaux','ogc nice':'nice','stade rennais':'rennes', 'rennais':'rennes', 'as saint-etienne':'st etienne', 
                    'saint etienne':'st etienne','saint-etienne':'st etienne', 'st-etienne':'st etienne','as st-etienne':'st etienne', 'st etienne':'st etienne', 'angers sco':'angers','fc metz':'metz','rc strasbourg':'strasbourg'
                    ,'rc lens':'lens','racing club de lens':'lens','as monaco':'monaco','dijon fco':'dijon','olympique de marseille':'marseille', 'olympique marseille':'marseille','st etienne':'st etienne',
                    'losc lille':'lille','fc nantes':'nantes','stade de reims':'reims', 'stade reims':'reims','nimes olympique':'nimes','olympique nimes':'nimes','montpellier hsc':'montpellier','montpellier':'montpellier','Montpellier':'montpellier','fc lorient':'lorient'
                    , PSG :  'psg', Montpellier:'montpellier', Marseille: 'marseille', Monaco:'monaco', Lyon: 'lyon', Metz: 'metz', lens: 'lens', lille:'lille', dijon:'dijon',Nice: 'nice',
                        Nimes:'nimes', Rennes: 'rennes', Strasbourg:'strasbourg', Nantes:  'nantes', Bordeaux:'bordeaux', Angers:  'angers', Brest:   'brest', Reims:   'reims', Lorient: 'lorient','racing strasbourg':'strasbourg','rc strasbourg alsace':'strasbourg'}


#same order as data structures in their list
websites_champs_league_links = [france_pari_champions_league_link, unibet_champions_league_link, zebet_champions_league_link,winimax_champions_league_link, passionsports_champions_league_link, cbet_champions_league_link,
                                betclic_champions_league_link ] # , sportifs_pmu_champions_league_link


websites_europa_league_links = [france_pari_europa_league_link, unibet_europa_league_link, zebet_europa_league_link, winimax_europa_league_link, passionsports_europa_league_link, betclic_europa_league_link, cbet_champions_league_link]
# Note : cbet links all the same anyway so I just thre in its 'champs_league' one here 
 # , sportsbwin_europa_league_link] # 6 links


websites_ligue1_links_p1     = [winimax_ligue1_link, passionsports_ligue1_link, paris_sportifs_pmu, cbet_ligue1_link]
websites_ligue1_links_p2     = [betclic_ligue1_link, france_pari_ligue1_link, zebet_ligue1_link,unibet_ligue1_link] #
# cbet_ligue1_link 7 links m       # betclic_ligue1_link is empty for now
#sportsbwin_ligue1_link
websites_ligue1_links        = [passionsports_ligue1_link, paris_sportifs_pmu, france_pari_ligue1_link, zebet_ligue1_link,betclic_ligue1_link, winimax_ligue1_link, unibet_ligue1_link, cbet_ligue1_link]
#websites_ligue1_links        = [france_pari_ligue1_link, unibet_ligue1_link,zebet_ligue1_link, passionsports_ligue1_link, paris_sportifs_pmu] # 7 links m       # betclic_ligue1_link is empty for now

#websites_ligue1_links        = [cbet_ligue1_link] # 7 links m       # betclic_ligue1_link is empty for now
#websites_ligue1_links        = [france_pari_ligue1_link, unibet_ligue1_link,zebet_ligue1_link,paris_sportifs_pmu] # 7 links m       # betclic_ligue1_link is empty for now

# reference_champ_league_games_url = str(websites_champs_league_links[0])
# driver.get(reference_champ_league_games_url)

# some vars for parsing the games data - strings.
#initialize data with todays date - better than empty string
date_ = '31 mai'
compettition = 'Ligue des Champions'    

# TODO :rename like actual sites 
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

france_ligue1      = 'ligue1'
england_premier    = 'premier league'
spain_la_liga      = 'la liga'
italy_serie_a      = 'serie a'
germany_bundesliga = 'bundesliga'

## Serie A

## La Liga 

la_Liga_commonName_mapping = { 'Alavés' : 'alaves',  
'athletic'  : 'athlethic bilbao', 
'atlético'  : 'athletico madrid', 
'barcelona'  :      'barcelona ',
'cádiz'  :               'cadiz',
'cadiz'  :               'cadiz', 
'celta vigo '  :  'celta vigo', 
'eibar'  :               'eibar', 
'elche'  :               'elche',
'getafe'  :             'getafe',
'granada'  :           'granada',
'huesca'  :             'huesca',
'levante'  :             'levante',
'osasuna'  :             'osasuna',
'real betis'  :          'betis',	
'real madrid'  :    ' real madrid',
'real sociedad' :       'sociedad',
'sevilla' : 'sevilla',
'valencia' : 'valencia',
'valladolid' : 'valladolid',
'villarreal' : 'villarreal'
,'levante ud':'levante', 'athletico de madrid':'athletico madrid'
,'getafe cf': 'getafe'
,'elche cf' : 'elche'
,'sd eibar': 'eibar'   
,'valencia cf' : 'valencia'
,'real valladolid' : 'valladolid'
,'fc barcelona' : 'barcelona'
,'fc barcelone' : 'barcelona'
,'barcelone' : 'barcelona'
, 'deportivo alaves': 'alaves'
,'sd huesca' : 'heusca'      
, 'granada cf': 'granada'
,'villarreal cf':  'villarreal'
,'ca osasuna': 'osasuna'    
,'sevilla fc': 'sevilla'
,'ath. bilbao': 'athletic bilbao'
,'atl. madrid' : 'atheletico madrid'}
# 
# 
# 
# 
#
# }

# upper_case_europa_teamList = [Wolfsberg , Tottenham ,
# Dynamo Kyiv , Club Brugge ,
# Real Sociedad,   Manchester United,
# Benfica,  Arsenal, 
# Crvena zvezda,   AC Milan ,
# Antwerp,   Rangers, 
# ,Slavia Praha ,  Leicester ,
# Salzburg ,  Villarreal ,
# Braga,   Roma, 
# Krasnodar ,  Dinamo Zagreb ,
# Young Boys,  Leverkusen,
# Molde,  Hoffenheim,
# Granada,  Napoli,
# Maccabi Tel-Aviv, Shakhtar Donetsk, 
# LOSC Lille, Ajax, 
# Olympiacos, PSV Eindhoven]


comon_team_maping_europa = {'wolfsberg' : 'wolfsberg' , 'wolfsberg fc' : 'wolfsberg', 'wolfsberger' : 'wolfsberg', 'wolfsberger fc' : 'wolfsberg' ,'wolfsberger ac' : 'wolfsberg',  'tottenham' :  'tottenham', 'tottenham hotspurs' :  'tottenham',     
'dynamo kyiv'  : 'dynamo kyiv' , 'dynamo kiev'  : 'dynamo kyiv', 'club brugge' :  'club brugge', 'club bruges' :  'club brugge', 'fc bruges' :  'club brugge',     
'real sociedad' : 'real sociedad' , 'manchester united' :  'manchester united',
'benfica'  : 'benfica' , 'sl benfica'  : 'benfica', 'benfica lisbon'  : 'benfica', 'arsenal' : 'arsenal', 'arsenal fc' : 'arsenal',               
'crvena zvezda' : 'crvena zvezda' , 'red star belgrade' : 'crvena zvezda', 'etoile rouges belgrade' : 'crvena zvezda',
'ac milan' :  'ac milan','ac milano' :  'ac milan', 'milan ac' :  'ac 9milan',               
'antwerp'  : 'antwerp' , 'royal antwerp fc'  : 'antwerp', 'antwerp fc'  : 'antwerp', 'royal antwerp'  : 'antwerp', 'anvers'  : 'antwerp', 'rangers' : 'rangers',
 'rangers fc' : 'rangers', 'glasgow rangers fc' : 'rangers', 'glasgow rangers' : 'rangers',              
'slavia praha'  : 'slavia prague' , 'slavia prague'  : 'slavia prague',
'leicester' :  'leicester' , 'leicester fc' :  'leicester', 'leicester city' :  'leicester' , 'leicester city fc' :  'leicester' ,                 
'salzburg'  : 'salzburg' , 'red bull salzburg'  : 'salzburg', 'fc red bull salzburg'  : 'salzburg', 'rb salzburg' : 'salzburg',  'rb salzbourg' : 'salzburg',  'salzbourg' : 'salzburg', 'red bull salzbourg'  : 'salzburg',    
'villarreal' : 'villarreal', 'villarreal cf' : 'villarreal',               
'braga': 'braga', 'sporting clube de braga': 'braga', 'sc braga': 'braga', 'sporting club de braga': 'braga', 'sporting braga': 'braga',       
 'roma' : 'roma', 'as roma' : 'roma', 'as rome' : 'roma', 'rome' : 'roma',                          
'krasnodar': 'krasnodar' , 'krasnodar fc': 'krasnodar', 'fc krasnodar': 'krasnodar' 
,'dinamo zagreb' : 'dinamo zagreb', 'gnk dinamo zagreb' : 'dinamo zagreb',          
'young boys': 'young boys', 'bsc young boys': 'young boys', 'young boys berne': 'young boys'
,'leverkusen' : 'leverkusen', 'bayer leverkusen' : 'leverkusen'               
,'molde' : 'molde', 'fc molde' : 'molde'      
,'hoffenheim' : 'hoffenheim', 'tsg 1899 hoffenheim' : 'hoffenheim', 'tsg hoffenheim' : 'hoffenheim',              
'granada' : 'granada', 'grenade' : 'granada', 'cf grenade' : 'granada', 'cf granada' : 'granada', 'granada cf' : 'granada', 'napoli' :  'napoli',  'ssc napoli' :  'napoli', 's.s.c. napoli' :  'napoli', 'naples' :  'napoli',         
'maccabi tel-aviv' :  'maccabi tel-aviv', 'maccabi tel aviv' :  'maccabi tel aviv', 'maccabi tel aviv fc' :  'maccabi tel-aviv'   
,'shakhtar donetsk'  :  'shakhtar donetsk', 'fc shakhtar donetsk'  :  'shakhtar donetsk', 
'losc lille' :  'lille',
'lille' :  'lille'   
,'ajax'  :  'ajax','ajax amsterdam'  :  'ajax', 
'olympiacos' :  'olympiacos', 'olympiacos fc' :  'olympiacos', 'olympiakos' :  'olympiacos',
' psv eindhoven'  :  ' psv eindhoven', 'psv'  :  ' psv eindhoven'}

 
## premiership

EPL_commonName_mapping = {'man utd': 'manchester united','manchesterutd': 'manchester united','man city':'manchester city','manchester city':'manchester city','sheff utd':'sheffield united','sheffield utd':'sheffield united' \
        ,'west bromwich albion':'west brom','brighton & hove albion':'brighton','wolverhampton wanderers':'wolves'}


commonName_mapping = {'man utd': 'manchester united','manchester utd': 'manchester united', 'manchester united': 'manchester united', 'man city':'manchester city','manchester city':'manchester city','sheff utd':'sheffield united','sheffield utd':'sheffield united' \
    , 'sheffield united': 'sheffield united','west bromwich albion':'west brom', 'west bromwich':'west brom', 'brighton & hove albion':'brighton','wolverhampton wanderers':'wolves','wolverhampton':'wolves','chelsea': 'chelsea', 'chelsea fc': 'chelsea','liverpool' : 'liverpool', 'liverpool fc': 'liverpool'}


# commonPremLeagueTeamName_mapper = {  Crystal Palace
# :,  'West Ham'
# :, 'Newcastl'
# :, 'Leeds'
# :, 'Southamp'
# :, 'Arsenal
# :, 'West Bro'3
# :, 'Man City'
# :, 'Burnley'
# :, 'Aston Villa'
# :, 'Chelsea'
# :, 'Wolves'
# :, 'Brighton'
# :, 'Fulham'
# :, 'Everton'
# :, 'Leiceste'
# :, 'Man Utd
# :, 'Sheff Utd'
# :, 'Tottenha'
# :, 'Liverpoo'
#  'Newcastle':, 'Leeds'
#  :,'Crystal Palace':, 'West Ham'
#  :,'West Brom':, 'Manchester City'
#  :,'Southampton':, 'Arsenal'
#  :,'Burnley':, 'Aston Villa'
#  :,'Chelsea':, 'Wolves'
#  :,'Brighton':, 'Fulham'
#  :,'Manchester United':, 'Sheffield United'
#  :,'Everton':, 'Leicester'
#  :,'Tottenham':, 'Liverpool'
#  :,'Everton':, 'Newcastle'
#  :,'West Brom':, 'Fulham'
#  :,'Manchester City':, 'Sheffield United'
#  :,'Crystal Palace':, 'Wolves'
#  :,'Arsenal':, 'Manchester United'
#  :,'Southampton':, 'Aston Villa'
#  :,'Chelsea':, 'Burnley'
#  :,'Leicester':, 'Leeds'
#  :,'West Ham':, 'Liverpool'
#  :,'Brighton', 'Tottenham'   }


## Bundesliga



