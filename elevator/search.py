# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util


class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return [s, s, w, s, w, w, s, w]


class StateDict:
    """
    Annoyingly, the states we're likely to encounter won't always
    be immutable. Correspondingly, this means we can't always use a normal
    dictionary to keep track of states and their predecessor states,
    actions, costs. This class encapsulates using both a dict and a stupid
    list of tuples.
    """
    def __init__(self, isEasy=True):
        # I don't want to use anything more complex than a list
        # in which searching is ungodly slow, so as much as possible
        # let's try using an actual dictionary
        self.isEasy = isEasy
        if isEasy:
            self.states = dict()
        else:
            self.states = []

    def getState(self, state):
        if self.isEasy:
            return self.states[state]
        else:
            for s in self.states:
                if s[0] == state:
                    return s[1]
            # we should raise an error...but I'm lazy
            return None

    def updateState(self, state, val):
        if self.isEasy:
            self.states[state] = val
        else:
            for s in self.states:
                if s[0] == state:
                    s[1] = val
                    return
            # we can't find it, so add it to list
            self.states += [[state, val]]

    def getKeys(self):
        if self.isEasy:
            return self.states.keys()
        else:
            return map(lambda x: x[0], self.states)


def recreatePath(state_dict, end):
    """
    Recreate the list of actions required to reach the end.
    Requires a dictionary mapping states to tuples of previous states and
    the actions from that state to the key state, as well as
    the end state from which to begin.
    Assumes dictionary contains a 'start' key that maps to a
    (None, None) tuple.
    """
    actions = []
    curr_node = end
    while True:
        state_val = state_dict.getState(curr_node)
        if state_val[0] is None:
            return actions
        actions = [state_val[1]] + actions
        curr_node = state_val[0]


def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    start_node = problem.getStartState()
    frontier = util.Stack()
    frontier.push(start_node)
    # map all the states we see to the state and action we used to get there
    # incidentally also tracking the states we've seen so far
    try:
        # see StateDict for explanation of why we have to do this
        hash(start_node)
        state_dict = StateDict()
    except:
        state_dict = StateDict(False)
    state_dict.updateState(start_node, (None, None))
    while not frontier.isEmpty():
        curr_node = frontier.pop()
        if problem.isGoalState(curr_node):
            return recreatePath(state_dict, curr_node)
        for triple in problem.getSuccessors(curr_node):
            if triple[0] not in state_dict.getKeys():
                frontier.push(triple[0])
                state_dict.updateState(triple[0], (curr_node, triple[1]))
    # we got to the end without returning a path :(
    # there must not be a path...
    return None


def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    start_node = problem.getStartState()
    # exact same as DFS, but use a queue instead
    # we could make this more modular but extracting to a single method
    # and passing a reference to the relevant class, but I still have to
    # modify this code for UCS and A*...and I'm also just lazy
    frontier = util.Queue()
    frontier.push(start_node)
    try:
        hash(start_node)
        state_dict = StateDict()
    except:
        state_dict = StateDict(False)
    state_dict.updateState(start_node, (None, None))
    if problem.isGoalState(start_node):
        return []
    while not frontier.isEmpty():
        curr_node = frontier.pop()
        if problem.isGoalState(curr_node):
            return recreatePath(state_dict, curr_node)
        for triple in problem.getSuccessors(curr_node):
            if triple[0] not in state_dict.getKeys():
                frontier.push(triple[0])
                state_dict.updateState(triple[0], (curr_node, triple[1]))
    return None


def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    start_node = problem.getStartState()
    # two differences from (D/B)FS:
    # use a priority queue instead of queue/stack
    # and if the cost to a node we've seen before is lower
    # we can update the cost/path to that node
    frontier = util.PriorityQueue()
    frontier.push(start_node, 0)

    try:
        hash(start_node)
        state_dict = StateDict()
    except:
        state_dict = StateDict(False)
    state_dict.updateState(start_node, (None, None, 0))

    if problem.isGoalState(start_node):
        return []
    while not frontier.isEmpty():
        curr_node = frontier.pop()
        if problem.isGoalState(curr_node):
            return recreatePath(state_dict, curr_node)
        for triple in problem.getSuccessors(curr_node):
            cost_to_child = state_dict.getState(curr_node)[2] + triple[2]
            if (triple[0] not in state_dict.getKeys() or
                    state_dict.getState(triple[0])[2] > cost_to_child):
                # the staff were nice enough to consolidate both pushing and
                # updating in the same function, so we can do that without
                # worrying whether the node's already present or just better
                frontier.update(triple[0], cost_to_child)
                # and I'll use the same strategy
                state_dict.updateState(triple[0],
                                       (curr_node, triple[1], cost_to_child))
    return None


def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0


def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    start_node = problem.getStartState()
    # two differences from (D/B)FS:
    # use a priority queue instead of queue/stack
    # and if the cost to a node we've seen before is lower
    # we can update the cost/path to that node
    frontier = util.PriorityQueue()
    frontier.push(start_node, heuristic(start_node, problem))

    try:
        hash(start_node)
        state_dict = StateDict()
    except:
        state_dict = StateDict(False)
    state_dict.updateState(start_node, (None, None,
                                        heuristic(start_node, problem)))
    while not frontier.isEmpty():
        curr_node = frontier.pop()
        if problem.isGoalState(curr_node):
            return recreatePath(state_dict, curr_node)
        path_cost_to_curr = (state_dict.getState(curr_node)[2] -
                             heuristic(curr_node, problem))
        for triple in problem.getSuccessors(curr_node):
            cost_to_child = (path_cost_to_curr + triple[2] +
                             heuristic(triple[0], problem))
            if (triple[0] not in state_dict.getKeys() or
                    state_dict.getState(triple[0])[2] > cost_to_child):
                frontier.update(triple[0], cost_to_child)
                state_dict.updateState(triple[0],
                                       (curr_node, triple[1], cost_to_child))
    return None


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
