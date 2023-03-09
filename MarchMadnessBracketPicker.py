#using the march madness predictor program, this will attempt to find the most profitable bracket
#this will simulate a variety of outcomes to find which yields the most predicted points
#predicted points are determined by multiplying the possible points gained by the probability of that team winning
#whichever has greatest sum of return is the best
#NOTE I simulated what would happen if the highest seed won every game, and got a TERRIBLE result

import math
import random
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
import lxml
import collections
from scipy.stats import norm

path = "/Users/lancehendricks/Documents/Kenpoms/latestkenpom.html"

#insert file location below here:
#/Users/lancehendricks/Documents/Kenpoms/latestkenpom.html
with open(path) as fp:
    soup = BeautifulSoup(fp, 'html.parser')
table_html = soup.find_all('table', {'id': 'ratings-table'})

thead = table_html[0].find_all('thead')

table = table_html[0]
for x in thead:
    table = str(table).replace(str(x), '')

#print(table)

#define df (dataframe)
df = pd.read_html(table)[0]

#finds Adjusted Offensive Efficiency of team
def AdjOSearch(Team):
    AdjO = float(df[df[1] == Team][5])
    return(AdjO)

#finds Adjusted Defensive Efficiency of team
def AdjDSearch(Team):
    AdjD = float(df[df[1] == Team][7])
    return(AdjD)

def AdjTSearch(Team):
    AdjD = float(df[df[1] == Team][9])
    return(AdjD)

def sep(TeamName):
        Seed = ''
        Name = ''
        for t in TeamName:

            try:
                Seed = Seed + str(int(t))
            except ValueError:
                Name = Name + t

        l = len(Name)
        Name = Name[:l-1]

        if Seed:
            return Name, int(Seed)

        else:
            return Name, False


AvgOE = df[5].mean()
AvgDE = df[7].mean()
AvgE = (AvgOE + AvgDE) / 2
AvgT = df[9].mean()

#from now on, we're using the normal model! log5 and pythag are no more!
def predictedpoints(A, B, round, winner):
    TeamA = sep(A)[0]
    ASeed = sep(A)[1]
    TeamB = sep(B)[0]
    BSeed = sep(B)[1]

    AdjOA = AdjOSearch(TeamA)
    AdjDA = AdjDSearch(TeamA)
    AdjOB = AdjOSearch(TeamB)
    AdjDB = AdjDSearch(TeamB)
    AdjTA = AdjTSearch(TeamA)
    AdjTB = AdjTSearch(TeamB)
    
    ProjT = (AdjTA + AdjTB) - AvgT
    AOE = (AdjOA + AdjDB) - AvgE
    BOE = (AdjOB + AdjDA) - AvgE
    APoints = AOE * (ProjT / 100)
    BPoints = BOE * (ProjT / 100)
    #if B is supposed to score more, this will be positive
    BMargin = BPoints - APoints
    z = (0 - BMargin) / 11
    AdjAProb = norm.cdf(z)
    
    initialpoints = 2**round

    AReturn = initialpoints * ASeed
    BReturn = initialpoints * BSeed
    #used to generate random numbers here. Eliminated that by generating ONE random number in individual game stage to get rid of possibility of mismatching team with return.
    if AdjAProb > winner:
        return A, AReturn

    else:
        return B, BReturn

    

#edit the below 'teams' list according to what teams are in the tournament (and what their seed is)


sims = int(input('How many tournaments do you want to simulate? '))

#the following for loop conducts the simulations. If the return is greater than the original, that tournament result and its return is printed
#if the return is lesser, it disregards and goes to the next one

Return = 0

#63 games in each tournament
roundteams = []
winnings = []
for i in range(0, sims):
    
    #update the below line once the actual bracket is released
    teams = ["Kansas 1", "Southeast Missouri St. 16", "Missouri 8", "Memphis 9", "Miami FL 5", "VCU 12", "Indiana 4", "Toledo 13", "Kentucky 6", "Penn St. 11", "Marquette 3", "Kennesaw St. 14", "Michigan St. 7", "N.C. State 10", "Arizona 2", "UNC Asheville 15", "UCLA 1", "Texas A&M Corpus Chris 16", "Florida Atlantic 8", "Auburn 9", "Duke 5", "Charleston 12", "Xavier 4", "Utah Valley 13", "San Diego St. 6", "Pittsburgh 11", "Gonzaga 3", "Furman 14", "Northwestern 7", "Providence 10", "Texas 2", "Vermont 15", "Alabama 1", "Northern Kentucky 16", "Illinois 8", "West Virginia 9", "TCU 5", "Drake 12", "Virginia 4", "Yale 13", "Saint Mary's 6", "Mississippi St. 11", "Kansas St. 3", "UC Irvine 14", "Texas A&M 7", "USC 10", "Purdue 2", "Colgate 15", "Houston 1", "Howard 16", "Maryland 8", "Arkansas 9", "Iowa St. 5", "Oral Roberts 12", "Connecticut 4", "Iona 13", "Creighton 6", "Rutgers 11", "Tennessee 3", "Louisiana 14", "Iowa 7", "Boise St. 10", "Baylor 2", "Montana St. 15"]
    teamnumber = len(teams)
    totalrounds = int(math.log(teamnumber, 2))

    winnings0 = []

    for round in range(0, totalrounds):
    
        #the following erases the previous nextround list. At the end of the previous iteration we switched nextround over to teams, so we can reset this.
        nextround = []
        Aindex = 0
        Bindex = 1
    
        #calculate # of teams in round
        teamnum = 2**(totalrounds - round)
    
        #print('teamnum: ' + str(teamnum))
        #print(round)
    
        #run all games in round
        while Bindex <= (teamnum-1):
            #print(Aindex)
            #print(Bindex)
            winner = random.randint(0,100) / 100
            team = predictedpoints(teams[Aindex], teams[Bindex], round, winner)[0]
            winnings0 = predictedpoints(teams[Aindex], teams[Bindex], round, winner)[1]
            roundteams.append(team)
            nextround.append(team)
            winnings.append(winnings0)
            #print(team)
            #go to next game
            Aindex = Aindex + 2
            Bindex = Bindex + 2
        #switch winning teams to list of remaining competitors
        teams = nextround

    print(i+1)


#for every game i in every tournament, find how often each team appears. Within each game iteration, also 
for game in range(0,63):
    winnerlist = []
    print("Game: " + str(game))
    for tournament in range(0, sims):
        winnerlist.append(roundteams[game + tournament * 63])

    cnt = collections.Counter()
    for team in winnerlist:
        cnt[team] += 1

    uniquewinners = []
    uniquereturns = []
    uniqueoverall = []


    for team in cnt:    
        prob = cnt[team] / sims
        teamseed = sep(team)[1]

        if game <= 31:
            round = 0

        elif game <= 47:
            round = 1
    
        elif game <= 55:
            round = 2

        elif game <= 59:
            round = 3
        
        elif game <= 61:
            round = 4

        else:
            round = 5

        teamwinnings = prob * teamseed * 2**round
        uniquewinners.append(team)
        uniquereturns.append(teamwinnings)
        uniqueoverall.append(team)
        uniqueoverall.append(str(teamwinnings))

    print(uniqueoverall)
    print(uniquewinners[max(range(len(uniquereturns)), key=uniquereturns.__getitem__)])