import numpy as np
from collections import deque, defaultdict
import math
from itertools import combinations
import matplotlib.pyplot as plt
import pandas as pd
#import heapq

'''
Card representation:
(Rank, Suit, Power - hierarchy in poker of individual cards)
(1, "♠", 15), (2, "♠", 2),  ... (1, "❤", 15), (2, "❤",2) ... (1, "♣", 15), (2, "♣", 2), ... (1, "♦", 15) ... (14, '♦', 14)

'''

suits = {1:"♠", 2:"❤", 3:"♣", 4:"♦"}
deck = []

for i in range(1, 5):
    suit = suits[i]
    for j in range(1, 15):
        if j == 11: continue
        card = (j, suit, 15 if j == 1 else j+1 if j < 11 else j)
        deck.append(card)
        
#print(deck)


"""
Hand:
    There are 1326 different combinations of 2 cards:
    ((1, "♠", 15), (1, "♣", 15)), ((1, "♠", 15), (1, "❤", 15)) ... ((2, "♦", 2), (2, "♣", 2))
"""
all_hands = math.factorial(52)/math.factorial(52-2)/math.factorial(2)
#print(all_hands) #using math.factorial

N = 0
for combination in combinations(deck, 2): N += 1
#print(N) # using itertools.combinations

#examples of hand
for i, combination in enumerate(combinations(deck, 2)):
    #print(combination)
    if i > 5: break

"""
HandMap:
    Every Hand will be mapped to WinRate which is represented by:
        Hand : [win count of hand, tie count of hand, number of times hand is seen on table]
        
        So we have:
        HandMap:
            Hand : WinRate
        where WinRate is represented by:
            [win count of hand, tie count,  number of times hand is seen on table]
"""

handMap = {}
for combination in combinations(deck, 2):
    handMap[combination] = [0, 0, 0] # it won zero times,  tied zero times, combination is zero times seen



""" Dealing: """
def dealing_cards(n_players):
    permutation = np.random.permutation(deck)
    permutation = [(int(elem[0]), elem[1], int(elem[2])) for elem in permutation]
    playersHand = []
    
    for i in range(n_players):
        hand = [tuple(permutation[i*2]), tuple(permutation[i*2+1])]
        playersHand.append(hand)
    
    river = []
    for i in range(5):
        river.append(tuple(permutation[n_players*2+i]))
    
    return playersHand, river


"""Evaluate Hand"""

class Evaluate: 
    def __init__(self, all_7):
        #print(all_7)
        self.all_7 = all_7
        self.all_sorted = sorted(all_7, key = lambda item: item[2],  reverse = True)
        #print(self.all_sorted, "\n")
        
        #self.all_sorted = [(14, '♠', 14), (13, '♠', 13), (12, '❤', 12), (11, '♠', 11), \
                           #(4, '♠', 10), (3, '❤', 9), (2, '♠', 8)]
      
    @staticmethod
    def show_hierarchy(k = 3):
        hierarchy = {}
        show_straight = True
        
        hierarchy["❤10-9-8-7-6❤"] = Evaluate.hierarhy_function(4, 1, k) - 3*k + k/3
        for x in range(4, 0, -1):
            for y in range(3, 0, -1):
                if (x, y) == (3, 1) and show_straight:
                    hierarchy["♠♠♠♠♠"] = Evaluate.hierarhy_function(x, y, k) - 3*k + 2*k/3
                    hierarchy["10-9-8-7-6"] = Evaluate.hierarhy_function(x, y, k) - 3*k + k/3
                    show_straight = False
                    
                hierarchy[(x, y)] = Evaluate.hierarhy_function(x, y, k) - 3*k
        
        print(hierarchy)
        
    
    @staticmethod
    def hierarhy_function(x, y, k):
        if x == 4 or x == 1: y = 1
        if (x == 3 or x == 2) and y > 2: y = 2
        
        return k*2*x + k*y
        
       
    def total_score_without_straight_and_flush(self, cards = None, k = 3, onlyAdditional = False):
        rankMap = {}
        #if cards != None: print("here", cards)
        if cards == None: cards = self.all_7
        
        for card in cards:
            rankMap[card[2]] = rankMap.get(card[2], 0) + 1
        #print(rankMap)
        
        rankList = [[count, power] for power, count in rankMap.items()]
        #print("pre", rankList)
        #print(rankList)
        rankList.sort(reverse = True)
        #print(rankList)
        #print("post", rankList)
        
        base_score = (Evaluate.hierarhy_function(rankList[0][0], rankList[1][0], k) - 3*k)*(16)**5
        #print(hex(base_score))
        
        additional_score = 0
        j = 0
        
        for i in range(5):
            additional_score += rankList[j][1]*16**(5-i-1) 
            rankList[j][0] -= 1
            if rankList[j][0] == 0:
                j += 1
        #print(hex(additional_score))
        if onlyAdditional: return additional_score
        
        total_score = base_score + additional_score
        #print(hex(total_score))
        return total_score
        
        
    
    def is_it_straight_flush(self, k = 3):
        isItFlush, flush = self.is_it_flush()
        
        #if isItFlush: print(flush)
        #print(flush)
        if isItFlush:
            isItStraight, startCard = self.is_it_straight(flush)
            if isItStraight: return (Evaluate.hierarhy_function(4, 1, k) - 3*k + k/3)*16**5 + startCard, "Straight Flush"
            else:
                #print(hex(int(Evaluate.hierarhy_function(3, 1, k) - 3*k + 2*k/3)*16**5))
                #print(hex(int(self.total_score_without_straight_and_flush(flush, k, onlyAdditional=True))))
                return (Evaluate.hierarhy_function(3, 1, k) - 3*k + 2*k/3)*16**5 + \
                    self.total_score_without_straight_and_flush(flush, k, onlyAdditional=True), "Only Flush"
        
        isItStraight, startCard = self.is_it_straight()
        if isItStraight:
            return (Evaluate.hierarhy_function(3, 1, k) - 3*k + k/3)*16**5 + startCard, "Only straight"
        else: return -1, "Nothing"
                
            
            
    def is_it_flush(self):
        suitMap = {}
        for card in self.all_sorted:
            if card[1] not in suitMap: suitMap[card[1]] = [[card], 1]
            else: 
                suitMap[card[1]][0].append(card)
                suitMap[card[1]][1] += 1
        #print(suitMap, "\n")
        
        for suit in suitMap:
            if suitMap[suit][1] >= 5:
                return True, suitMap[suit][0]
            
        return False, "there is no flush here"
                
        
    
    def is_it_straight(self, array = None):
        if array == None: array = self.all_sorted
        array = [item[2] for item in array]
        if array[0] == 15: array.append(1)
        filtered = []
        for card_rank in array:
            if filtered and filtered[-1] == card_rank:
                continue
            else: filtered.append(card_rank)
        
        n = len(filtered)
        if n < 5: return False, "There is less than 5 different cards"
        
        i = 0
        start_card = None
        
        while(i < n):
            start_card = filtered[i]
            for k in range(1, 6):
                if k == 5: return True, start_card
                if i + k >= n: return False, "Close"
                if filtered[i+k] + 1 != filtered[i + k - 1]: break
            
            i = i+k
            start_card = filtered[i]
            
        return False, "There is no straight here"
    
    def total_score(self):
        #print("eeeej", self.is_it_straight_flush())
        #print("kkkkkkkkkk", self.total_score_without_straight_and_flush())
        score_sf, sf = self.is_it_straight_flush()
        score_rank = self.total_score_without_straight_and_flush()
        if sf:    
            total = max(score_sf, score_rank)
        else: total = score_rank
        return total
    
    
"""Simulatiion"""   
N = 500000
#print(handMap)
for i in range(N):
    privateCombinations, comunityCards = dealing_cards(4) #4 players
    #print(privateCombinations, "river", comunityCards)
    
    scores = [Evaluate(private + comunityCards).total_score() for private in privateCombinations]
    win_score = max(scores)
    #print([hex(int(score)) for score in scores])
    shared_win = 0 #how many players get points (from 1, to n)
    #print("shared", shared_win)
    for score in scores:
        if score == win_score: shared_win += 1
    
    for i, private in enumerate(privateCombinations):
        temp = (private[0], private[1]) if (private[0], private[1]) in handMap else (private[1], private[0])
        if scores[i] == win_score:
            if shared_win == 1:
                handMap[temp][0] += 1
            else:
                handMap[temp][1] += 1
                
            handMap[temp][2] += 1
        else:
            handMap[temp][2] += 1
                
          
            
        

#print(handMap)
WinRate = {}
for hand in handMap:
    win_rate = (handMap[hand][0]/handMap[hand][2]*100 if handMap[hand][2] != 0 else -1)
    tie_rate = (handMap[hand][1]/handMap[hand][2]*100 if handMap[hand][2] != 0 else -1)
    WinRate[hand] = [win_rate, tie_rate]

#print(WinRate)
WinRate_over50 = {hand:WinRate[hand] for hand in WinRate if WinRate[hand][0] > 50}
for item in WinRate_over50.items():
    pass
    #print(item)

for w in WinRate.items():
    #print(w)
    pass


Important_WinRate = {}
for i in range(14, 0, -1):
    if i == 11:
        continue
    for j in range(i, 0, -1):
        if j != 11: 
            Important_WinRate[(i, j, "diff_color")] = [0, 0]
            if i != j: Important_WinRate[(i, j, "same_color")] = [0, 0]


for hand in WinRate:
    larger, smaller = (hand[0][0], hand[1][0]) if hand[0][0] >= hand[1][0] else (hand[1][0], hand[0][0])
    diff = "diff_color" if hand[0][1] != hand[1][1] else "same_color"

    Important_WinRate[(larger, smaller, diff)][0] += WinRate[hand][0]
    Important_WinRate[(larger, smaller, diff)][1] += WinRate[hand][1]


for hand in Important_WinRate:
    #print(hand)
    if hand[0] == hand[1]:
        Important_WinRate[hand][0] /= 6
        Important_WinRate[hand][1] /= 6
    elif hand[2] == "same_color":
        Important_WinRate[hand][0] /= 4
        Important_WinRate[hand][1] /= 4
    else:
        Important_WinRate[hand][0] /= 12
        Important_WinRate[hand][1] /= 12
        
print(Important_WinRate)
        

def Analize_WinRate(hashmap):
    win_rates = [value[0] for value in Important_WinRate.values()]
    tie_rates = [value[1] for value in Important_WinRate.values()]
    
    # Set up the figure and axes for the histograms
    fig, ax = plt.subplots(1, 2, figsize=(14, 7))  # 1 row, 2 columns of charts
    
    # Histogram for Win Rates
    ax[0].hist(win_rates, bins=50, color='blue', alpha=0.7)
    ax[0].set_title('Histogram of Win Rates')
    ax[0].set_xlabel('Win Rate (%)')
    ax[0].set_ylabel('Frequency')
    
    # Histogram for Tie Rates
    ax[1].hist(tie_rates, bins=50, color='green', alpha=0.7)
    ax[1].set_title('Histogram of Tie Rates')
    ax[1].set_xlabel('Tie Rate (%)')
    ax[1].set_ylabel('Frequency')
    
    # Show plots
    plt.tight_layout()
    plt.show()
    
Analize_WinRate(WinRate)
Analize_WinRate(Important_WinRate)
    

data = [{'Rank1': k[0], 'Rank2': k[1], 'Color': k[2], 'Win Rate': v[0], 'Tie Rate': v[1]} for k, v in Important_WinRate.items()]
df = pd.DataFrame(data)
df.to_excel('WinRateData.xlsx', index=False)


    








    
    








