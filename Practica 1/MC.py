
import matplotlib.pyplot as plt
import random
import heapq
import math
import sys
from collections import defaultdict, deque, Counter
from itertools import combinations


FIFOQueue = deque

LIFOQueue = list

class PriorityQueue:
    """A queue in which the item with minimum f(item) is always popped first."""

    def __init__(self, items=(), key=lambda x: x): 
        self.key = key
        self.items = [] # a heap of (score, item) pairs
        for item in items:
            self.add(item)
         
    def add(self, item):
        """Add item to the queuez."""
        pair = (self.key(item), item)
        heapq.heappush(self.items, pair)

    def pop(self):
        """Pop and return the item with min f(item) value."""
        return heapq.heappop(self.items)[1]
    
    def top(self): return self.items[0][1]

    def __len__(self): return len(self.items)

class Node:
    "A Node in a search tree."
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.__dict__.update(state=state, parent=parent, action=action, path_cost=path_cost)

    def __repr__(self): return '<{}>'.format(self.state)
    def __len__(self): return 0 if self.parent is None else (1 + len(self.parent))
    def __lt__(self, other): return self.path_cost < other.path_cost
    
    
failure = Node('failure', path_cost=math.inf) # Indicates an algorithm couldn't find a solution.
cutoff  = Node('cutoff',  path_cost=math.inf) # Indicates iterative deepening search was cut off.
    
    
def expand(problem, node):
    "Expand a node, generating the children nodes."
    s = node.state
    for action in problem.actions(s):
        s1 = problem.result(s, action)
        cost = node.path_cost + problem.action_cost(s, action, s1)
        yield Node(s1, node, action, cost)
        

def path_actions(node):
    "The sequence of actions to get to this node."
    if node.parent is None:
        return []  
    return path_actions(node.parent) + [node.action]


def path_states(node):
    "The sequence of states to get to this node."
    if node in (cutoff, failure, None): 
        return []
    return path_states(node.parent) + [node.state]

def best_first_search(problem, f):
    "Search nodes with minimum f(node) value first."
    node = Node(problem.initial)
    frontier = PriorityQueue([node], key=f)
    reached = {problem.initial: node}
    while frontier:
        node = frontier.pop()
        if problem.is_goal(node.state):
            return node
        for child in expand(problem, node):
            s = child.state
            if s not in reached or child.path_cost < reached[s].path_cost:
                reached[s] = child
                frontier.add(child)
    return failure


def best_first_tree_search(problem, f):
    "A version of best_first_search without the `reached` table."
    frontier = PriorityQueue([Node(problem.initial)], key=f)
    while frontier:
        node = frontier.pop()
        if problem.is_goal(node.state):
            return node
        for child in expand(problem, node):
            if not is_cycle(child):
                frontier.add(child)
    return failure


def g(n): return n.path_cost


def astar_search(problem, h=None):
    """Search nodes with minimum f(n) = g(n) + h(n)."""
    h = h or problem.h
    return best_first_search(problem, f=lambda n: g(n) + h(n))


def astar_tree_search(problem, h=None):
    """Search nodes with minimum f(n) = g(n) + h(n), with no `reached` table."""
    h = h or problem.h
    return best_first_tree_search(problem, f=lambda n: g(n) + h(n))


def weighted_astar_search(problem, h=None, weight=1.4):
    """Search nodes with minimum f(n) = g(n) + weight * h(n)."""
    h = h or problem.h
    return best_first_search(problem, f=lambda n: g(n) + weight * h(n))

        
def greedy_bfs(problem, h=None):
    """Search nodes with minimum h(n)."""
    h = h or problem.h
    return best_first_search(problem, f=h)


def uniform_cost_search(problem):
    "Search nodes with minimum path cost first."
    return best_first_search(problem, f=g)


def breadth_first_bfs(problem):
    "Search shallowest nodes in the search tree first; using best-first."
    return best_first_search(problem, f=len)


def depth_first_bfs(problem):
    "Search deepest nodes in the search tree first; using best-first."
    return best_first_search(problem, f=lambda n: -len(n))


def is_cycle(node, k=30):
    "Does this node form a cycle of length k or less?"
    def find_cycle(ancestor, k):
        return (ancestor is not None and k > 0 and
                (ancestor.state == node.state or find_cycle(ancestor.parent, k - 1)))
    return find_cycle(node.parent, k)

def breadth_first_search(problem):
    "Search shallowest nodes in the search tree first."
    node = Node(problem.initial)
    if problem.is_goal(problem.initial):
        return node
    frontier = FIFOQueue([node])
    reached = {problem.initial}
    while frontier:
        node = frontier.pop()
        for child in expand(problem, node):
            s = child.state
            if problem.is_goal(s):
                return child
            if s not in reached:
                reached.add(s)
                frontier.appendleft(child)
    return failure


def iterative_deepening_search(problem):
    "Do depth-limited search with increasing depth limits."
    for limit in range(1, sys.maxsize):
        result = depth_limited_search(problem, limit)
        if result != cutoff:
            return result
        
        
def depth_limited_search(problem, limit=10):
    "Search deepest nodes in the search tree first."
    frontier = LIFOQueue([Node(problem.initial)])
    result = failure
    while frontier:
        node = frontier.pop()
        if problem.is_goal(node.state):
            return node
        elif len(node) >= limit:
            result = cutoff
        elif not is_cycle(node):
            for child in expand(problem, node):
                frontier.append(child)
    return result


def depth_first_recursive_search(problem, node=None):
    if node is None: 
        node = Node(problem.initial)
    if problem.is_goal(node.state):
        return node
    elif is_cycle(node):
        return failure
    else:
        for child in expand(problem, node):
            result = depth_first_recursive_search(problem, child)
            if result:
                return result
        return failure
class CannibalsProblem(object):   

    def __init__(self, initial, goal): 
        self.initial = initial
        self.goal = goal

    def is_goal(self, state):        return state == self.goal

    def action_cost(self, s, a, s1): return 1
    
    def h(self, node):               return 0
    
    def __str__(self):
        return '{}({!r}, {!r})'.format(
            type(self).__name__, self.initial, self.goal)

    def actions(self, state):
      possibleActions = []
      if state[0] == 'I':
        #Llevar 2 canibales a la orilla derecha
        if state[2] >= 2 and (state[4] + 2 <= state[3] or state[3] == 0) : 
          possibleActions.append("0,2")
        #Llevar 1 canibales a la orilla derecha
        if state[2] >= 1 and (state[4] + 1 <= state[3] or state[3] == 0) :
          possibleActions.append("0,1")
        #Llevar 2 misioneros a la orilla derecha
        if state[1] >= 2 and (state[2] <= state[1] - 2 or state[1] - 2 == 0) :
          possibleActions.append("2,0")
        #Llevar 1 misioneros a la orilla derecha
        if state[1] >= 1 and (state[2] <= state[1] - 1 or state[1] - 1 == 0) :
          possibleActions.append("1,0")
        #Llevar 1 misionero y 1 canibal a la orilla derecha
        if (state[1] >= 1 and state[2] >= 1) and state[4] + 1 <= state[3] + 1 :
          possibleActions.append("1,1")               
      else :
        #Llevar 2 canibales a la orilla izquierda
        if state[4] >= 2 and (state[2] + 2 <= state[1] or state[1] == 0) :
          possibleActions.append("0,2")
        #Llevar 1 canibales a la orilla izquierda
        if state[4] >= 1 and (state[2] + 1 <= state[1] or state[1] == 0) :
          possibleActions.append("0,1")
        #Llevar 2 misioneros a la orilla izquierda
        if state[3] >= 2 and (state[4] <= state[3] - 2 or state[3] - 2 == 0) :
          possibleActions.append("2,0")
        #Llevar 1 misioneros a la orilla izquierda
        if state[3] >= 1 and (state[4] <= state[3] - 1 or state[3] - 1 == 0) :
          possibleActions.append("1,0")
        #Llevar 1 misionero y 1 canibal a la orilla izquierda
        if (state[3] >= 1 and state[4] >= 1) and state[2] + 1 <= state[1] + 1 :
          possibleActions.append("1,1")
      return possibleActions

    def result(self, state, action):
      newState = list(state)
      if state[0] == 'I':
          if action == "0,2" :
            newState[2] = state[2] - 2
            newState[4] = state[4] + 2
            newState[0] = 'D'
          elif action == "0,1" :
            newState[2] = state[2] - 1
            newState[4] = state[4] + 1 
            newState[0] = 'D'          
          elif action == "2,0" :
            newState[1] = state[1] - 2
            newState[3] = state[3] + 2
            newState[0] = 'D'
          elif action == "1,0" :
            newState[1] = state[1] - 1
            newState[3] = state[3] + 1
            newState[0] = 'D'
          elif action == "1,1" :
            newState[2] = state[2] - 1
            newState[4] = state[4] + 1
            newState[1] = state[1] - 1
            newState[3] = state[3] + 1
            newState[0] = 'D'
      else :
          if action == "0,2" :
            newState[2] = state[2] + 2
            newState[4] = state[4] - 2
            newState[0] = 'I'
          elif action == "0,1" :
            newState[2] = state[2] + 1
            newState[4] = state[4] - 1   
            newState[0] = 'I'        
          elif action == "2,0" :
            newState[1] = state[1] + 2
            newState[3] = state[3] - 2
            newState[0] = 'I'
          elif action == "1,0" :
            newState[1] = state[1] + 1
            newState[3] = state[3] - 1
            newState[0] = 'I'
          elif action == "1,1" :
            newState[2] = state[2] + 1
            newState[4] = state[4] - 1
            newState[1] = state[1] + 1
            newState[3] = state[3] - 1   
            newState[0] = 'I'     
      return tuple(newState)    

p3 = CannibalsProblem(('I',3,3,0,0),('D',0,0,3,3))
sol3 = breadth_first_search(p3)
print("Secuencia de movimientos:")
print(path_actions(sol3))
print("Secuencia de estados:")
print(path_states(sol3))
movimientos = len(path_actions(sol3))
print ("Número de movimientos = " + str(movimientos))