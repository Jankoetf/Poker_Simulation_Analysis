import numpy as np
from collections import deque, defaultdict
import math
from itertools import combinations
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
        Hand : [win count of hand, number of times hand is seen on table]
        
        So we have:
        HandMap:
            Hand : WinRate
        where WinRate is represented by:
            [win count of hand, number of times hand is seen on table]
        
            
    
    For example if there is a N players:
        If there is a win:
            Player who won get:
                [win count of hand + 1, number of times hand is seen on table + 1]
            N-1 players that lost get:
                [win count of hand, number of times hand is seen on table + 1]
                
        If There is a draw between M players:
            M players who draw get:
                [win count of hand + 1/M, number of times hand is seen on table + 1]
            N - M Players that lost get:
                [win count of hand, number of times hand is seen on table + 1]
"""

handMap = {}
for combination in combinations(deck, 2):
    handMap[combination] = [0, 0] # combination is zero times seen, and it won zero times



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
    def show_hierarchy(k):
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
        if cards == None: cards = self.all_7
        for card in self.all_7:
            rankMap[card[2]] = rankMap.get(card[2], 0) + 1
        #print(rankMap)
        
        rankList = [[count, power] for power, count in rankMap.items()]
        #print(rankList)
        rankList.sort(reverse = True)
        #print(rankList)
        
        
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
        #print(flush)
        if isItFlush:
            isItStraight, startCard = self.is_it_straight(flush)
            if isItStraight: return (Evaluate.hierarhy_function(4, 1, k) - 3*k + k/3)*16**5 + startCard, "Straight Flush"
            else: return (Evaluate.hierarhy_function(3, 1, k) - 3*k + 2*k/3)*16**5 + \
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
N = 500
#print(handMap)
for i in range(N):
    privateCombinations, comunityCards = dealing_cards(4) #4 players
    #print(privateCombinations, "river", comunityCards)
    
    scores = [Evaluate(private + comunityCards).total_score() for private in privateCombinations]
    win_score = max(scores)
    
    #print([hex(score) for score in scores])
    shared_win = 0 #how many players get points (from 1, to n)
    #print("shared", shared_win)
    for score in scores:
        if score == win_score: shared_win += 1
    
    
    for i, private in enumerate(privateCombinations):
        if scores[i] == win_score:
            if (private[0], private[1]) in handMap:
                handMap[(private[0], private[1])][1] += 1
                handMap[(private[0], private[1])][0] += 1/shared_win
            else:
                handMap[(private[1], private[0])][1] += 1
                handMap[(private[1], private[0])][0] += 1/shared_win
        else:
            if (private[0], private[1]) in handMap:
                handMap[(private[0], private[1])][1] += 1
            else:
                handMap[(private[1], private[0])][1] += 1
        

#print(handMap)
WinRate = {hand:(handMap[hand][0]/handMap[hand][1]*100 if handMap[hand][1] != 0 else -1) for hand in handMap}
print(WinRate)
WinRate_over50 = {hand:WinRate[hand] for hand in WinRate if WinRate[hand] > 35}
for item in WinRate_over50.items():
    pass
    #print(item)
#print(WinRate_over50, sep = "\n")


    
    
    
    
    
            
        
    
    

    
# #print("here")
# hands, river = dealing_cards(2)
# print(hands[0], river)

# #print(hands[0], river)
# E1 = Evaluate(hands[0] + river)
# #print(E1.is_it_straight_flush())
# #E1.total_score_without_straight_and_flush()
# E1.show_hierarchy(3)
# #E1.total_score()



    








    
    








