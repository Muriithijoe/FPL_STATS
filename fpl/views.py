from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.db.models import Q

import requests
import statistics
import time


""" LANDING PAGE """
def stats(request):

  # gws= [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]

  # team_code= 16628
  # team_code= 1308979 #me
  # team_code= 3922919 #dan
  # team_code= 2462715 #max

  if 'team' in request.GET and request.GET['team']:
    team_code = int((request.GET.get('team')).strip())

  """ API CALLS """
  # GENERAL TEAM INFO
  response= requests.get(f'https://fantasy.premierleague.com/drf/entry/{team_code}')
  team= response.json()

  bootstrap_static_request= requests.get('https://fantasy.premierleague.com/drf/bootstrap-static')
  bootstrap_static= bootstrap_static_request.json()


  """ GAMEWEEKS ACTIVE """
  current = team["entry"]["current_event"] 
  start = team["entry"]["started_event"]
  
  gws = list(range(start, (current+1)))
  print(gws)

  """ BASIC INFO """
  team_name= team["entry"]["name"]

  manager_name= team["entry"]["player_first_name"] + " " + team["entry"]["player_last_name"]

  gameweeks_played= len(gws)

  total_points= team["entry"]["summary_overall_points"]

  overall_rank= team["entry"]["summary_overall_rank"]

  top_percent= int((overall_rank/(bootstrap_static["total-players"]))*100)

  team_value= (team["entry"]["value"])/10

  in_bank= (team["entry"]["bank"])/10




  """ GAMEWEEK PERFORMANCE (POINTS + RANK) """
  all_gw_points= {}
  all_gw_points_list= []

  all_avggw_points_list= []

  all_gw_ranks= {}
  all_gw_ranks_list= []
  
  all_pergw_ranks_list= []

  transfer_hits= []

  counter= 1
  for gw in gws:

    gw_request= requests.get(f'https://fantasy.premierleague.com/drf/entry/{team_code}/event/{gw}/picks')
    gw= gw_request.json()

    single_gw_points= gw["entry_history"]["points"]
    single_avggw_points= gw["event"]["average_entry_score"]

    all_gw_points[counter]= single_gw_points

    all_gw_points_list.append(single_gw_points)
    all_avggw_points_list.append(single_avggw_points)
    
    single_gw_rank= gw["entry_history"]["overall_rank"]
    single_pergw_rank= gw["entry_history"]["rank"]

    all_gw_ranks[counter]= single_gw_rank

    all_gw_ranks_list.append(single_gw_rank)
    all_pergw_ranks_list.append(single_pergw_rank)


    transfer_hits.append(gw["entry_history"]["event_transfers_cost"])


    counter+=1







  """ RANK + SCORE TRENDS """
  average_gameweek_points= int(statistics.median(all_gw_points_list))

  highest_gameweek_points=  max(all_gw_points_list)

  lowest_gameweek_points= min(all_gw_points_list)

  
  average_gameweek_rank= int(statistics.median(all_gw_ranks_list))

  highest_gameweek_rank= min(all_gw_ranks_list)

  lowest_gameweek_rank= max(all_gw_ranks_list)




  """ CAPTAINCY """
  formations= [
    {
      'formation':'3-4-3',
      'count':0,
      'points':[],
      'median':0
    },
    {
      'formation':'3-5-2',
      'count':0,
      'points':[],
      'median':0
    },
    {
      'formation':'4-3-3',
      'count':0,
      'points':[],
      'median':0
    },
    {
      'formation':'4-4-2',
      'count':0,
      'points':[],
      'median':0
    },
    {
      'formation':'4-5-1',
      'count':0,
      'points':[],
      'median':0
    },
    {
      'formation':'5-4-1',
      'count':0,
      'points':[],
      'median':0
    },
    {
      'formation':'5-2-3',
      'count':0,
      'points':[],
      'median':0
    },
    {
      'formation':'5-3-2',
      'count':0,
      'points':[],
      'median':0
    },
  ]


  total_captain_points= 0

  all_captain_points_list= []

  avg_captain_points= 0

  total_vice_captain_points= 0

  total_top_scorer_points= 0

  total_benched_points= 0

  avg_benched_points_list= []

  avg_benched_points= 0

  chips_used= []

  captains= {}

  auto_subs= []

  
  n= 0
  for num in gws:
    
    captain_request= requests.get(f'https://fantasy.premierleague.com/drf/entry/{team_code}/event/{num}/picks')
    captain= captain_request.json()

    for qw in captain["automatic_subs"]:
      auto_subs.append(qw["element_out"])


    chip= captain["active_chip"]
    if  chip != "":
      chips_used.append(chip)


    for d in captain["picks"]:
      if d["multiplier"] == 2:
        captain_no= d["element"]
        points_request= requests.get(f'https://fantasy.premierleague.com/drf/element-summary/{captain_no}')
        points= points_request.json()
        to_add= ((points["history"][num-1]["total_points"])*2)
        all_captain_points_list.append(to_add)
        total_captain_points+=to_add

        capn= 0

        captains[d["element"]] = {
          'id': d["element"],
          'name': capn,
          'points':[],
        }
      


    for b in captain["picks"]:
      if b["is_vice_captain"] == True:
        vice_captain_no= b["element"]
        vcpoints_request= requests.get(f'https://fantasy.premierleague.com/drf/element-summary/{vice_captain_no}')
        vcpoints= vcpoints_request.json()
        too_add= ((vcpoints["history"][num-1]["total_points"])*2)
        total_vice_captain_points+=too_add


    all_players= []
    for p in captain["picks"]:
      player_no= p["element"]
      all_players.append(player_no)

  
    all_points= []
    for player in all_players:
      player_points_request= requests.get(f'https://fantasy.premierleague.com/drf/element-summary/{player}')
      player_points= player_points_request.json()
      all_points.append((player_points["history"][num-1]["total_points"]))   
    total_top_scorer_points+=((max(all_points))*2)


    benched_players=all_players[11:]
    benched_points=[]
    for bplayer in benched_players:
      bpoints_request= requests.get(f'https://fantasy.premierleague.com/drf/element-summary/{bplayer}')
      bpoints= bpoints_request.json()
      benched_points.append((bpoints["history"][num-1]["total_points"]))
    plus_points = sum(benched_points)      
    total_benched_points+=(plus_points)
    avg_benched_points_list.append(plus_points)

    start = time.clock()
    players= all_players[1:11]
    player_elems= []
    for player in players:
      for elem in bootstrap_static["elements"]:
        if player == elem["id"]:
          player_elems.append(elem["element_type"])
    print(time.clock() - start)
    

    df= 0
    md= 0
    fd= 0
    for elem in player_elems:
      if elem == 2:
        df+=1
      elif elem == 3:
        md+=1
      elif elem == 4:
        fd+=1

    gw_formation = f'{df}-{md}-{fd}' 
    
    
    for fmt in formations:
        if gw_formation == fmt['formation']:
          fmt['count']+=1
          fmt['points'].append(all_gw_points_list[n])
          n+=1

  percent_captain_points= int((total_captain_points/total_points)*100)

  avg_benched_points= statistics.median(avg_benched_points_list)

  avg_captain_points= statistics.median(all_captain_points_list)


  for fut in formations:
    if fut['count'] > 0: 
      fut['median']= statistics.median(fut['points'])
  
  print(formations)

  """ TRANSFERS  """
  # transfer hits - GAMEWEEK PERFORMANCE

  total_transfers=team["entry"]["total_transfers"]
  
  total_points_hits= (sum(transfer_hits)) * -1

  

  return render(request, 'stats.html',{
                        
                        # BASIC INFO
                        'team':team,
                        'team_name':team_name,
                        'manager_name':manager_name,
                        'gameweeks_played':gameweeks_played,
                        'total_points':total_points,
                        'overall_rank':overall_rank,
                        'top_percent':top_percent,
                        'team_value':team_value,
                        'in_bank':in_bank,
# 
                        # RANK + SCORE TRENDS
                        'average_gameweek_points':average_gameweek_points,
                        'highest_gameweek_points':highest_gameweek_points,
                        'lowest_gameweek_points':lowest_gameweek_points,
                        'average_gameweek_rank':average_gameweek_rank,
                        'highest_gameweek_rank':highest_gameweek_rank,
                        'lowest_gameweek_rank':lowest_gameweek_rank,

                        # GAMEWEEK PERFORMANCE
                        'all_gw_points':all_gw_points,
# 
                        # CAPTAINCY
                        'total_captain_points':total_captain_points,
                        'percent_captain_points':percent_captain_points,
                        'total_vice_captain_points':total_vice_captain_points,
                        'total_top_scorer_points':total_top_scorer_points,
                        'total_benched_points':total_benched_points,
                        'avg_benched_points':avg_benched_points,
# 
                        # CHIPS
                        'chips_used':chips_used,
                        #  TRANSFERS
                        'total_transfers':total_transfers,
                        'total_points_hits':total_points_hits,
# 
                        # FORMATIONS
                        'formations':formations,
# 
                        # CHARTS
                        'gws':gws,
                        'all_gw_ranks_list':all_gw_ranks_list,
                        'all_pergw_ranks_list':all_pergw_ranks_list,
                        'all_gw_points_list':all_gw_points_list,
                        'all_avggw_points_list':all_avggw_points_list,
                        'all_captain_points_list':all_captain_points_list,
                        'avg_captain_points':avg_captain_points,



  })




def chart(request):

  team_code=123456789

  return render(request, 'chart.html',{
                'team_code':team_code
                })
  



def home(request):


  return render(request, 'index.html')