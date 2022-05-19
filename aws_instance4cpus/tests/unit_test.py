 import unittest
import sys,os
#sys.path.append('../') # r'C:\Users\MaaD\Desktop\pythonCode\sportsBettingProjects')
sys.path.append('aws_instance4cpus')
#import sportsBetAlertor_v1
#import chromedriver.exe
#from sportsBetAlertor_v1 import  check_is_surebet,get_surebet_factor, send_mail_alert_gen_socer_surebet_prportions
#from all_euro_footy_ligues_sportsBetAlertor_v1 import check_is_surebet, get_surebet_factor, check_all_sure_bet_combos, parseSites

from metaLeague_data import *
#from degug_euro2020Surebettor_formnerjstItalia import *

from legalCanadian_sportsBetAlertor_v1 import *

import selenium
from selenium import webdriver


class Testing(unittest.TestCase):

    # def test_string(self):
    #     a = 'some'7
    #     b = 'some'
    #     self.assertEqual(a, b)



    # def test_boolean(self):
    #     a = True
    #     b = True
    #     self.assertEqual(a, b)

    def test_check_is_actual_surebet(self):

        teamA_win_odds = 1.5
        teamB_win_odds = 6.0
        draw_odds      = 8.1

        retVal_test = check_is_surebet(teamA_win_odds,teamB_win_odds,draw_odds)

        exected_return_bool = True

        self.assertEqual(retVal_test, exected_return_bool)

    def test_check_is_actual_surebet_value(self):

        teamA_win_odds = 1.5
        teamB_win_odds = 6.0
        draw_odds      = 8.1

        retVal_test = get_surebet_factor(teamA_win_odds,teamB_win_odds,draw_odds)

        exected_return_float = 0.9567

        self.assertAlmostEqual(retVal_test, exected_return_float,places=3)


    def test_check_is_non_surebet(self):

        teamA_win_odds = 2.5
        teamB_win_odds = 1.25
        draw_odds      = 3.37

        # this three-wat is not a surebet as the formula should return 1.49673
        retVal_test = check_is_surebet(teamA_win_odds,teamB_win_odds,draw_odds)

        exected_return_bool = False

        self.assertEqual(retVal_test, exected_return_bool)


    def test_check_is_non_surebet_value(self):

        teamA_win_odds = 2.5
        teamB_win_odds = 1.25
        draw_odds      = 3.37

        # this three-wat is not a surebet as the formula should return 1.49673
        retVal_test = get_surebet_factor(teamA_win_odds,teamB_win_odds,draw_odds)

        exected_return_float = 1.497

        self.assertAlmostEqual(retVal_test, exected_return_float,places=3)


##  TESTS for Parsing function :  ##

    # def test_parsefunc_dict_num_values(self):

    #      self.assertEqual(retVal_test, exected_return_bool)

    
    # def test_send_mail_alert_gen_socer_surebet_prportions(self):

    #     bookie_1, bookie_2, bookie_3 = "unibet",  "betclic",  "zebet"
    #     bookie_one_outcome  ,bookie_2_outcome  = 'Away team (2nd team name on the betting card) to win', 'Home team (1st team name on the betting card) to win'
    #     #'Away team (2nd team name on the betting card) to win'

    #     proportions_list = 3*[0]
    #     teamA ,teamB , date , competition = 'lens', 'psg', 'fevrier 2021', 'ligue1'
    #     proportions_list[0], proportions_list[1] ,proportions_list[2], Profit = 0.27, 0.34, 0.39, 103.45 

    #     subsetList = [[0,0,0] for i in range(3)] 


    #     # subsetList[0][:], subsetList[1][:],subsetList[2][:]  =  [1.15, 7.25, 12.5], [1.17, 7.5, 13.0], [1.18, 7.0, 12.3]

    #     # expected_message = """From: From Person <from@fromdomain.com>
    #     # To: To Person <to@todomain.com>
    #     # Subject: SMTP e-mail test

    #     # Surebet Alert  :

    #     # Profit = """ + str(round( Profit ,3)) + """
        
    #     # Event: """ + str(competition) + """
    #     # Date: """  + str(date) + """
    #     # teamA: """ + str(teamA) + """
    #     # teamB: """ + str(teamB) + """

    #     # bookieTeamA: """ + str(bookie_2) + """   """  + str(round(proportions_list[1] *100.0, 2)) +   """ % -- odd_1 is = """  + str(subsetList[1][0]) + """     
    #     # bookieDraw: """  + str(bookie_3) +  """   """ + str(round(proportions_list[2] *100.0, 2)) +   """ % -- odd_2 is = """  + str(subsetList[2][1]) + """     
    #     # bookieTeamB: """ + str(bookie_1) + """   """  + str(round(proportions_list[0] *100.0, 2)) +    """ % -- odd_3 is = """ + str(subsetList[0][2]) 

    #     # retVals = send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2, bookie_3, bookie_one_outcome, bookie_2_outcome, teamA, teamB, date, competition, proportions_list, Profit, subsetList1[0][2], subsetList1[1][0], subsetList1[2][1])


    #     # self.assertEqual(retVals[1], expected_message)

    #     ## CASE 1:
    #     bookie_one_outcome  ,bookie_2_outcome  = 'Home team (1st team name on the betting card) to win', 'A draw between the team in the 90 minutes'

    #     subsetList[0][:],subsetList[1][:],subsetList[2][:] = [11.5, 1.15, 1.15], [1.15, 11.5, 1.15], [1.15, 1.15, 11.5]

    #     # expected_message = """From: From Person <from@fromdomain.com>
    #     # To: To Person <to@todomain.com>
    #     # Subject: SMTP e-mail test

    #     # Surebet Alert  :

    #     # Profit = """ + str(round( Profit ,3)) + """
        
    #     # Event: """ + str(competition) + """
    #     # Date: """  + str(date) + """
    #     # teamA: """ + str(teamA) + """
    #     # teamB: """ + str(teamB) + """

    #     # bookieTeamA: """ + str(bookie_2) + """   """  + str(round(proportions_list[1] *100.0, 2)) +   """ % -- odd_1 is = """  + str(subsetList[1][0]) + """     
    #     # bookieDraw: """  + str(bookie_3) +  """   """ + str(round(proportions_list[2] *100.0, 2)) +   """ % -- odd_2 is = """  + str(subsetList[2][1]) + """     
    #     # bookieTeamB: """ + str(bookie_1) + """   """  + str(round(proportions_list[0] *100.0, 2)) +    """ % -- odd_3 is = """ + str(subsetList[0][2]) 


    #     expected_message = """From: From Person <from@fromdomain.com>
    #     To: To Person <to@todomain.com>
    #     Subject: SMTP e-mail test

    #     Surebet Alert  :

    #     Profit = """ + str(round( Profit ,3)) + """
        
    #     Event: """ + str(competition) + """
    #     Date: """  + str(date) + """
    #     teamA: """ + str(teamA) + """
    #     teamB: """ + str(teamB) + """

    #     bookieTeamA: """ + str(bookie_1) + """   """  +  str(round(proportions_list[0]  *100.0,2)) + """ % -- odd_1 is = """  +  str(subsetList[0][0])  + """     
    #     bookieDraw: """  + str(bookie_2) + """   """  +  str(round(proportions_list[1] *100.0,2))  + """ % -- odd_2 is = """  +  str(subsetList[1][1])  + """     
    #     bookieTeamB: """ + str(bookie_3) + """   """  +  str(round(proportions_list[2] *100.0,2))  + """ % -- odd_3 is = """  +  str(subsetList[2][2])

    #     bookiesOutputList = [bookie_1, bookie_2, bookie_3]
    #     propsList         = [proportions_list[0], proportions_list[1], proportions_list[2]]
    #     oddsList          = [subsetList[0][0], subsetList[1][1], subsetList[2][2]]

    #     retVals = send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2, bookie_3, bookie_one_outcome, bookie_2_outcome, teamA, teamB, date, competition, proportions_list, Profit, subsetList[0][0], subsetList[1][1], subsetList[2][2])

    #     self.assertEqual(retVals[1], bookiesOutputList)  
    #     self.assertEqual(retVals[2], propsList)  
    #     self.assertEqual(retVals[3], oddsList)      

    #   ## CASE 2 :   bookie q - home win, bookie 2 - away win:
    #     #W_1 = 'Home team (1st team name on the betting card) to win'
    #     #W_2 = 'Away team (2nd team name on the betting card) to win'
    #     #D   = 'A draw between the team in the 90 minutes'
    #     bookie_one_outcome  ,bookie_2_outcome  = 'Home team (1st team name on the betting card) to win', 'Away team (2nd team name on the betting card) to win'
    #     subsetList[0][:],subsetList[1][:],subsetList[2][:] = [11.5, 1.15, 1.15], [1.15, 1.15, 11.5], [1.15, 11.5, 1.15]


    #     expected_message = """From: From Person <from@fromdomain.com>
    #     To: To Person <to@todomain.com>
    #     Subject: SMTP e-mail test

    #     Surebet Alert  :

    #     Profit = """ + str(round( Profit ,3)) + """ \n
        
    #     Event: """ + str(competition) + """ \n
    #     Date: """  + str(date) + """ \n
    #     teamA: """ + str(teamA) + """ \n
    #     teamB: """ + str(teamB) + """ \n

    #     bookieTeamA: """ + str(bookie_1) + """   """  + str(round(proportions_list[0] *100.0, 2)) +   """ % -- odd_1 is = """  + str(subsetList[0][0]) + """ \n    
    #     bookieDraw: """  + str(bookie_3) +  """   """ + str(round(proportions_list[2] *100.0, 2)) +   """ % -- odd_2 is = """  + str(subsetList[2][1]) + """ \n    
    #     bookieTeamB: """ + str(bookie_2) + """   """  + str(round(proportions_list[1] *100.0, 2)) +    """ % -- odd_3 is = """ + str(subsetList[1][2]) 

    #     bookiesOutputList = [bookie_1, bookie_3, bookie_2]
    #     propsList         = [proportions_list[0], proportions_list[2], proportions_list[1]]
    #     oddsList          = [subsetList[0][0], subsetList[2][1], subsetList[1][2]]

    #     retVals = send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2, bookie_3, bookie_one_outcome, bookie_2_outcome, teamA, teamB, date, competition, proportions_list, Profit, subsetList[0][0], subsetList[1][1], subsetList[2][2])

    #     self.assertEqual(retVals[1], bookiesOutputList)  
    #     self.assertEqual(retVals[2], propsList)  
    #     self.assertEqual(retVals[3], oddsList)      

    #     check= -1


    # #   ## CASE 3 :   bookie 1 - a draw bookie 2 - home win:

    #     bookie_one_outcome  ,bookie_2_outcome  = 'A draw between the team in the 90 minutes', 'Home team (1st team name on the betting card) to win'
    #     subsetList[0][:],subsetList[1][:],subsetList[2][:] = [1.15, 11.5, 1.15], [11.5, 1.15, 1.15], [1.15, 1.15, 11.5]
        
    #     # expected_message = """From: From Person <from@fromdomain.com>
    #     # To: To Person <to@todomain.com>
    #     # Subject: SMTP e-mail test

    #     # Surebet Alert  :

    #     # Profit = """ + str(round( Profit ,3)) + """
        
    #     # Event: """ + str(competition) + """
    #     # Date: """  + str(date) + """
    #     # teamA: """ + str(teamA) + """
    #     # teamB: """ + str(teamB) + """

    #     # bookieTeamA: """ + str(bookie_2) + """   """  + str(round(proportions_list[1] *100.0, 2)) +   """ % -- odd_1 is = """  + str(subsetList[1][0]) + """     
    #     # bookieDraw: """  + str(bookie_1) +  """   """ + str(round(proportions_list[0] *100.0, 2)) +   """ % -- odd_2 is = """  + str(subsetList[0][1]) + """     
    #     # bookieTeamB: """ + str(bookie_3) + """   """  + str(round(proportions_list[2] *100.0, 2)) +    """ % -- odd_3 is = """ + str(subsetList[2][2]) 

    
    #     bookiesOutputList = [bookie_2, bookie_1, bookie_3]
    #     propsList         = [proportions_list[1], proportions_list[0], proportions_list[2]]
    #     oddsList          = [subsetList[1][0], subsetList[0][1], subsetList[2][2]]

    #     retVals = send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2, bookie_3, bookie_one_outcome, bookie_2_outcome, teamA, teamB, date, competition, proportions_list, Profit, subsetList1[0][1], subsetList1[1][0], subsetList1[2][2])

    #     self.assertEqual(retVals[1], bookiesOutputList)  
    #     self.assertEqual(retVals[2], propsList)  
    #     self.assertEqual(retVals[3], oddsList)      





    #     self.assertEqual(retVals[1], expected_message) 

    # ## CASE 4 :   bookie 1 - a draw bookie 2 - away win:

    #     subsetList[0][:],subsetList[1][:],subsetList[2][:] = [1.15, 11.5, 1.15], [1.15, 1.15, 11.5], [11.5, 1.15, 1.15]
    
        
    #     expected_message = """From: From Person <from@fromdomain.com>
    #     To: To Person <to@todomain.com>
    #     Subject: SMTP e-mail test

    #     Surebet Alert  :

    #     Profit = """ + str(round( Profit ,3)) + """
        
    #     Event: """ + str(competition) + """
    #     Date: """  + str(date) + """
    #     teamA: """ + str(teamA) + """
    #     teamB: """ + str(teamB) + """

    #     bookieTeamA: """ + str(bookie_3) + """   """  + str(round(proportions_list[2] *100.0, 2)) +   """ % -- odd_1 is = """  + str(subsetList[2][0]) + """     
    #     bookieDraw: """  + str(bookie_1) +  """   """ + str(round(proportions_list[0] *100.0, 2)) +   """ % -- odd_2 is = """  + str(subsetList[0][1]) + """     
    #     bookieTeamB: """ + str(bookie_2) + """   """  + str(round(proportions_list[1] *100.0, 2)) +    """ % -- odd_3 is = """ + str(subsetList[1][2]) 

    #     retVals = send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2, bookie_3, bookie_one_outcome, bookie_2_outcome, teamA, teamB, date, competition, proportions_list, Profit, subsetList1[0][1], subsetList1[1][2], subsetList1[2][0])


    #     self.assertEqual(retVals[1], expected_message) 

    # ## CASE 5 :   bookie 1 - a way win bookie 2 - home win:

    #     subsetList[0][:],subsetList[1][:],subsetList[2][:] = [1.15, 1.15, 11.5], [11.5, 1.15, 1.15], [1.15, 11.5, 1.15]

    #     expected_message = """From: From Person <from@fromdomain.com>
    #     To: To Person <to@todomain.com>
    #     Subject: SMTP e-mail test

    #     Surebet Alert  :

    #     Profit = """ + str(round( Profit ,3)) + """
        
    #     Event: """ + str(competition) + """
    #     Date: """  + str(date) + """
    #     teamA: """ + str(teamA) + """
    #     teamB: """ + str(teamB) + """

    #     bookieTeamA: """ + str(bookie_2) + """   """  + str(round(proportions_list[1] *100.0, 2)) +   """ % -- odd_1 is = """  + str(subsetList[1][0]) + """     
    #     bookieDraw: """  + str(bookie_3) +  """   """ + str(round(proportions_list[2] *100.0, 2)) +   """ % -- odd_2 is = """  + str(subsetList[2][1]) + """     
    #     bookieTeamB: """ + str(bookie_1) + """   """  + str(round(proportions_list[0] *100.0, 2)) +    """ % -- odd_3 is = """ + str(subsetList[0][2]) 

    #     retVals = send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2, bookie_3, bookie_one_outcome, bookie_2_outcome, teamA, teamB, date, competition, proportions_list, Profit, subsetList1[0][2], subsetList1[1][0], subsetList1[2][1])


    #     self.assertEqual(retVals[1], expected_message) 


    # ## CASE 6 : bookie 1 - away win bookie 2 - a draw:

    #     subsetList[0][:],subsetList[1][:],subsetList[2][:] = [1.15, 1.15, 11.5], [11.5, 1.15, 1.15], [1.15, 11.5, 1.15]

    #     expected_message = """From: From Person <from@fromdomain.com>
    #     To: To Person <to@todomain.com>
    #     Subject: SMTP e-mail test

    #     Surebet Alert  :

    #     Profit = """ + str(round( Profit ,3)) + """
        
    #     Event: """ + str(competition) + """
    #     Date: """  + str(date) + """
    #     teamA: """ + str(teamA) + """
    #     teamB: """ + str(teamB) + """

    #     bookieTeamA: """ + str(bookie_3) + """   """  + str(round(proportions_list[2] *100.0, 2)) +   """ % -- odd_1 is = """  + str(subsetList[2][0]) + """     
    #     bookieDraw: """  + str(bookie_2) +  """   """ + str(round(proportions_list[1] *100.0, 2)) +   """ % -- odd_2 is = """  + str(subsetList[1][1]) + """     
    #     bookieTeamB: """ + str(bookie_1) + """   """  + str(round(proportions_list[0] *100.0, 2)) +    """ % -- odd_3 is = """ + str(subsetList[0][2]) 

    #     retVals = send_mail_alert_gen_socer_surebet_prportions(bookie_1, bookie_2, bookie_3, bookie_one_outcome, bookie_2_outcome, teamA, teamB, date, competition, proportions_list, Profit, subsetList1[0][2], subsetList1[1][1], subsetList1[2][0])


#     #     self.assertEqual(retVals[1], expected_message) 


# ## TEST # ? :  test a definite sure bet - given three typical sites data dict. :

#     def test_check_all_sure_bet_combos(self):
#         # purposefully encode in one surebet idir three bookies on the one common game
#         # I set france paris home win odd for chelsea v west brom to 1.334 from 1.2 actual, along with zebet and betclic's draw and awat win odds - should get 2 surebets , the first (draw zebet) = 0.99355
#         fake_dict_france_pari = {'france-pari_23 decembre_premier league_chelsea - west brom':[1.334, 6.5, 14.5], 'france-pari_23 decembre_premier league_crystal palace - chelsea':[7.5, 4.3, 1.38] }
        
#         fake_dict_zebet       = {'zebet_apr, 03 01:30 pm_premier league_chelsea - west brom':[1.19, 6.1, 12.5]} #, 

#         fake_dict_betclic     = {'betclic_03/04/2021 07:30_premier league_chelsea - west brom':[1.2, 5.85, 12.5], 'betclic_03/04/2021 07:30_premier league_crystal palace - chelsea':[7.15, 4.15, 1.4]}
#         fake_dict_cbet        = {'cbet_20 decembre_premier league_crystal palace - chelsea':[7.22, 4.19, 1.42]} 
#         fake_dict_pmu         = { 'paris-sportifs.pmu_samedi 03 avril_premier league_southampton - burnley':[1.9, 3.3, 3.7] }

#         input_faked_bookies_data = [ fake_dict_france_pari, fake_dict_zebet,  fake_dict_betclic, fake_dict_cbet, fake_dict_pmu ]
            
#         expect_surebet_val = 0.993559614
#         fake_dict_cpy = {}    

#         [retVal1,retVal2] = check_all_sure_bet_combos(all_split_sites_data = input_faked_bookies_data, globCounter=0, all_split_sites_data_copy = fake_dict_cpy, dataDictChangdCounter=0, total_time_parsing=0.0 ,sure_bet_counter=0)

#         self.assertEqual(retVal1, 1)  
#         self.assertAlmostEqual(retVal2[0], expect_surebet_val, places=5)  
#         #self.assertEqual(retVals[3], oddsList)      

3 wodidvhoiwhv  
## test on emailing function:

    def test_send_mail_alert(self):

        W_1 = 'Home team (1st team name on the betting card) to win'
        W_2 = 'Away team (2nd team name on the betting card) to win'
        D   = 'A draw between the team in the 90 minutes'

        bookie_1 = 'france-pari',
        bookie_2 = 'unibet'
        bookie_3 = 'zebet',
        bookie_one_outcome = W_2,
        bookie_2_outcome = D,
        teamA = 'liverpool',
        teamB = 'real madrid',
        Date = 'Juin 1 2021',
        competition = 'ligue des champions',
        proportions_list = [0.2113, 0.3987, 0.5643], 
        Profit= 1.15,
        odd1 = 2.1,
        odd2 = 3.7,
        odd3 = 9.5

        success_flag, mesage, [bookyTeamA,bookyDraw, bookyTeamB], [proportions_list_win1, proportions_draw, proportions_list_win2], [win1Odd, draw_odd, win2Odd]  \
              = send_mail_alert_gen_socer_surebet_prportions(bookie_1,bookie_2,bookie_3,bookie_one_outcome, bookie_2_outcome,teamA,teamB,Date,competition, proportions_list, Profit,odd1,odd2,odd3)

        self.assertEqual(retVal, True)

        self.assertEqual(bookyTeamB,'france-pari')
        self.assertEqual(bookyDraw,'unibet')

        self.assertEqual(bookyTeamA,'zebet')

    #self.assertEqual()

    def test_send_mail_alert(self):

        W_1 = 'Home team (1st team name on the betting card) to win'
        W_2 = 'Away team (2nd team name on the betting card) to win'
        D   = 'A draw between the team in the 90 minutes'

        bookie_1 = 'france-pari',
        bookie_2 = 'unibet'
        bookie_3 = 'zebet',
        bookie_one_outcome = W_1,
        bookie_2_outcome = D,
        teamA = 'liverpool',
        teamB = 'real madrid',
        Date = 'Juin 1 2021',
        competition = 'ligue des champions',
        proportions_list = [0.2113, 0.3987, 0.5643], 
        Profit= 1.15,
        odd1 = 2.1,
        odd2 = 3.7,
        odd3 = 9.5

        success_flag, mesage, [bookyTeamA,bookyDraw, bookyTeamB], [proportions_list_win1, proportions_draw, proportions_list_win2], [win1Odd, draw_odd, win2Odd]  \
              = send_mail_alert_gen_socer_surebet_prportions(bookie_1,bookie_2,bookie_3,bookie_one_outcome, bookie_2_outcome,teamA,teamB,Date,competition, proportions_list, Profit,odd1,odd2,odd3)

        self.assertEqual(retVal, True)

        self.assertEqual(bookyTeamA,'france-pari')
        self.assertEqual(bookyDraw,'unibet')

        self.assertEqual(bookyTeamB,'zebet')


    def test_send_mail_alert(self):

        W_1 = 'Home team (1st team name on the betting card) to win'
        W_2 = 'Away team (2nd team name on the betting card) to win'
        D   = 'A draw between the team in the 90 minutes'

        bookie_1 = 'france-pari',
        bookie_2 = 'unibet'
        bookie_3 = 'zebet',
        bookie_one_outcome = D,
        bookie_2_outcome = W_1,
        teamA = 'liverpool',
        teamB = 'real madrid',
        Date = 'Juin 1 2021',
        competition = 'ligue des champions',
        proportions_list = [0.2113, 0.3987, 0.5643], 
        Profit= 1.15,
        odd1 = 2.1,
        odd2 = 3.7,
        odd3 = 9.5

        success_flag, mesage, [bookyTeamA,bookyDraw, bookyTeamB], [proportions_list_win1, proportions_draw, proportions_list_win2], [win1Odd, draw_odd, win2Odd]  \
              = send_mail_alert_gen_socer_surebet_prportions(bookie_1,bookie_2,bookie_3,bookie_one_outcome, bookie_2_outcome,teamA,teamB,Date,competition, proportions_list, Profit,odd1,odd2,odd3)

        self.assertEqual(retVal, True)

        self.assertEqual(bookyTeamB,'zebet')
        self.assertEqual(bookyDraw,'france-pari')

        self.assertEqual(bookyTeamA,'unibet')

## TODO : fix expected outcomes for remaining mail tests here ...
    def test_send_mail_alert(self):

        W_1 = 'Home team (1st team name on the betting card) to win'
        W_2 = 'Away team (2nd team name on the betting card) to win'
        D   = 'A draw between the team in the 90 minutes'

        bookie_1 = 'france-pari',
        bookie_2 = 'unibet'
        bookie_3 = 'zebet',
        bookie_one_outcome = D,
        bookie_2_outcome = W_2,
        teamA = 'liverpool',
        teamB = 'real madrid',
        Date = 'Juin 1 2021',
        competition = 'ligue des champions',
        proportions_list = [0.2113, 0.3987, 0.5643], 
        Profit= 1.15,
        odd1 = 2.1,
        odd2 = 3.7,
        odd3 = 9.5

        success_flag, mesage, [bookyTeamA,bookyDraw, bookyTeamB], [proportions_list_win1, proportions_draw, proportions_list_win2], [win1Odd, draw_odd, win2Odd]  \
              = send_mail_alert_gen_socer_surebet_prportions(bookie_1,bookie_2,bookie_3,bookie_one_outcome, bookie_2_outcome,teamA,teamB,Date,competition, proportions_list, Profit,odd1,odd2,odd3)

        self.assertEqual(retVal, True)

        self.assertEqual(bookyTeamB,'unibet')
        self.assertEqual(bookyDraw,'france-pari')

        self.assertEqual(bookyTeamA,'zebet')


    def test_send_mail_alert(self):

        W_1 = 'Home team (1st team name on the betting card) to win'
        W_2 = 'Away team (2nd team name on the betting card) to win'
        D   = 'A draw between the team in the 90 minutes'

        bookie_1 = 'france-pari',
        bookie_2 = 'unibet'
        bookie_3 = 'zebet',
        bookie_one_outcome = W_2,
        bookie_2_outcome = W_1,
        teamA = 'liverpool',
        teamB = 'real madrid',
        Date = 'Juin 1 2021',
        competition = 'ligue des champions',
        proportions_list = [0.2113, 0.3987, 0.5643], 
        Profit= 1.15,
        odd1 = 2.1,
        odd2 = 3.7,
        odd3 = 9.5

        success_flag, mesage, [bookyTeamA,bookyDraw, bookyTeamB], [proportions_list_win1, proportions_draw, proportions_list_win2], [win1Odd, draw_odd, win2Odd]  \
              = send_mail_alert_gen_socer_surebet_prportions(bookie_1,bookie_2,bookie_3,bookie_one_outcome, bookie_2_outcome,teamA,teamB,Date,competition, proportions_list, Profit,odd1,odd2,odd3)

        self.assertEqual(retVal, True)

        self.assertEqual(bookyTeamB,'france-pari')
        self.assertEqual(bookyDraw,'zebet')

        self.assertEqual(bookyTeamA,'unibet')


    def test_send_mail_alert(self):

        W_1 = 'Home team (1st team name on the betting card) to win'
        W_2 = 'Away team (2nd team name on the betting card) to win'
        D   = 'A draw between the team in the 90 minutes'

        bookie_1 = 'france-pari',
        bookie_2 = 'unibet'
        bookie_3 = 'zebet',
        bookie_one_outcome = W_1,
        bookie_2_outcome = W_2,
        teamA = 'liverpool',
        teamB = 'real madrid',
        Date = 'Juin 1 2021',
        competition = 'ligue des champions',
        proportions_list = [0.2113, 0.3987, 0.5643], 
        Profit= 1.15,
        odd1 = 2.1,
        odd2 = 3.7,
        odd3 = 9.5

        success_flag, mesage, [bookyTeamA,bookyDraw, bookyTeamB], [proportions_list_win1, proportions_draw, proportions_list_win2], [win1Odd, draw_odd, win2Odd]  \
              = send_mail_alert_gen_socer_surebet_prportions(bookie_1,bookie_2,bookie_3,bookie_one_outcome, bookie_2_outcome,teamA,teamB,Date,competition, proportions_list, Profit,odd1,odd2,odd3)

        self.assertEqual(retVal, True)

        self.assertEqual(bookyTeamB,'unibet')
        self.assertEqual(bookyDraw,'zebet')

        self.assertEqual(bookyTeamA,'france-pari')


# tests on  parsing :
    # test the number of sites in the dictionary is equal tp three at least for surebet processing
    #also test that each key has 3 odds only.
    def test_parsing_1(self):
        # purposefully encode in one surebet idir three bookies on the one common game
        # I set france paris home win odd for chelsea v west brom to 1.334 from 1.2 actual, along with zebet and betclic's draw and awat win odds - should get 2 surebets , the first (draw zebet) = 0.99355

        USE_PROXIES = True
        # fake_dict_france_pari = {'france-pari_23 decembre_premier league_chelsea - west brom':[1.334, 6.5, 14.5], 'france-pari_23 decembre_premier league_crystal palace - chelsea':[7.5, 4.3, 1.38] }
        
        # fake_dict_zebet       = {'zebet_apr, 03 01:30 pm_premier league_chelsea - west brom':[1.19, 6.1, 12.5]} #, 

        # fake_dict_betclic     = {'betclic_03/04/2021 07:30_premier league_chelsea - west brom':[1.2, 5.85, 12.5], 'betclic_03/04/2021 07:30_premier league_crystal palace - chelsea':[7.15, 4.15, 1.4]}
        # fake_dict_cbet        = {'cbet_20 decembre_premier league_crystal palace - chelsea':[7.22, 4.19, 1.42]} 
        # fake_dict_pmu         = { 'paris-sportifs.pmu_samedi 03 avril_premier league_southampton - burnley':[1.9, 3.3, 3.7] }

        # input_faked_bookies_data = [ fake_dict_france_pari, fake_dict_zebet,  fake_dict_betclic, fake_dict_cbet, fake_dict_pmu ]
       
        drvr = webdriver.Chrome(executable_path=DRIVER_PATH) #, options = options

        if USE_PROXIES:
            PROXY_COUNTER = 0
            k = 33
            proxies = req_proxy.get_proxy_list()

        #initialize counters
        sure_bet_counter = 0
        total_time_parsing = 0.0
        globCounter=0
        dataDictChangdCounter = 0
        RAND_PROXY_JUMP = 13

        if USE_PROXIES:
            if PROXY_COUNTER >= len(proxies) - (2*RAND_PROXY_JUMP + 1):
                proxies = req_proxy.get_proxy_list()
                PROXY_COUNTER = 0
            PROXY = proxies[PROXY_COUNTER].get_address()
            #print("Proxy address = ******************************** %s ************************************ %d",PROXY,k)
            
            webdriver.DesiredCapabilities.CHROME['proxy']={
                "httpProxy":PROXY,
                "ftpProxy":PROXY,
                "sslProxy":PROXY,
                "proxyType":"MANUAL",
            }

        test1_websites_euro2020_links = [ betclic_EURO2021_link, france_pari_EURO2021_link, unibet_EURO2021_link ]
        boolean, resultant_data = parseSites(drvr, test1_websites_euro2020_links)

        # Test at least 3 sites's data :
        self.assertGreaterEqual(len(resultant_data),3)
        
        for dicts in resultant_data:         
            for keys, vals in dicts.items():
                num_odds_per = len(vals)
                self.assertEqual(num_odds_per, 3)

        return True


# #test 2 :

# #    def test_unit_test2(self):


# #         a = True
# #         b = True
# #         self.assertEqual(a, b)


# # #test 3 :

# #     def unit_test3(self):

#         a = True
#         b = True
#         self.assertEqual(a, b)



if __name__ == '__main__':
    print('Running unit tests on sportsbetting applicationb version 1....')
    unittest.main()








