# multiAgents.py
# --------------
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

import random, util

from game import Agent

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"

        numAgents = gameState.getNumAgents()
        actions = gameState.getLegalActions(0)
        states = [gameState.generateSuccessor(0, a) for a in actions]
        minimaxIndex = -1
        minimaxScore = -10000000
        # go through states and run minmax on that state
        # doing this instead of just calling minmax on 0, bc I don't want to
        # deal with returning index in minmax
        for i in xrange(len(states)):
            score = minimax(1, numAgents, states[i], self.depth,
                            self.evaluationFunction)
            if score > minimaxScore:
                minimaxScore = score
                minimaxIndex = i

        return actions[minimaxIndex]


# make a helper recursive function
def minimax(currAgent, numAgents, state, depth, evalFunc):
    # stop if we hit the end or we won :) / lost :(
    if depth < 1 or state.isWin() or state.isLose():
        return evalFunc(state)
    # actions, states for current agent
    actions = state.getLegalActions(currAgent)
    bestScoreInitialized = False
    # run minimax on every state
    for a in actions:
        s = state.generateSuccessor(currAgent, a)
        # if we've checked every ghost, start over at next depth
        if currAgent == numAgents - 1:
            score = minimax(0, numAgents, s, depth - 1, evalFunc)
        # otherwise, just truck on forward through remaining agents
        else:
            score = minimax(currAgent + 1, numAgents, s, depth, evalFunc)
        # don't want to make any assumptions about init min/max score
        # so just check to see if we have a "best" yet
        if not bestScoreInitialized:
            bestScore = score
            bestScoreInitialized = True

        # max for pacman
        if currAgent == 0:
            bestScore = max(score, bestScore)
        # min for ghosts
        else:
            bestScore = min(score, bestScore)
    return bestScore


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        # very similar to regular minimax, so I'll comment only on diff
        numAgents = gameState.getNumAgents()
        actions = gameState.getLegalActions(0)
        states = [gameState.generateSuccessor(0, a) for a in actions]
        minimaxIndex = -1
        minimaxScore = -10000000
        # set init alpha low (max'ing on it)
        alpha = -10000000
        # set init beta high (min'ing on it)
        beta = 10000000
        for i in xrange(len(states)):
            score = alphabeta(1, numAgents, states[i], self.depth,
                              self.evaluationFunction, alpha, beta)
            if score > minimaxScore:
                minimaxScore = score
                minimaxIndex = i
            # no need to check for beta because we're at highest level
            alpha = max(minimaxScore, alpha)
        return actions[minimaxIndex]


# another helper recursive function
# very similar to above, so I'll only comment differences
def alphabeta(currAgent, numAgents, state, depth, evalFunc, alpha, beta):
    if depth < 1 or state.isWin() or state.isLose():
        return evalFunc(state)
    actions = state.getLegalActions(currAgent)
    bestScoreInitialized = False
    for a in actions:
        s = state.generateSuccessor(currAgent, a)
        if currAgent == numAgents - 1:
            score = alphabeta(0, numAgents, s, depth - 1,
                              evalFunc, alpha, beta)
        else:
            score = alphabeta(currAgent + 1, numAgents, s, depth,
                              evalFunc, alpha, beta)
        if not bestScoreInitialized:
            bestScore = score
            bestScoreInitialized = True
        if currAgent == 0:
            bestScore = max(score, bestScore)
            # quit if we know we can't be lower than beta already
            if bestScore > beta:
                return bestScore
            # set new alpha for lower leaves
            alpha = max(bestScore, alpha)
        else:
            bestScore = min(score, bestScore)
            # converse of beta
            if bestScore < alpha:
                return bestScore
            beta = min(bestScore, beta)
    return bestScore


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        # same idea as minimax, again--so I'll just comment when diff
        numAgents = gameState.getNumAgents()
        actions = gameState.getLegalActions(0)
        states = [gameState.generateSuccessor(0, a) for a in actions]
        minimaxIndex = -1
        minimaxScore = -10000000
        for i in xrange(len(states)):
            # no diff at root b/c pacman wants max
            score = expectimax(1, numAgents, states[i], self.depth,
                               self.evaluationFunction)
            if score > minimaxScore:
                minimaxScore = score
                minimaxIndex = i
        return actions[minimaxIndex]

def expectimax(currAgent, numAgents, state, depth, evalFunc):
    if depth < 1 or state.isWin() or state.isLose():
        return evalFunc(state)
    actions = state.getLegalActions(currAgent)
    # need this to get expectation
    numActions = float(len(actions))
    # we only have to max now, so I'm okay choosing arbitrary low
    if currAgent == 0:
        bestScore = -100000
    else:
        bestScore = 0
    for a in actions:
        s = state.generateSuccessor(currAgent, a)
        if currAgent == numAgents - 1:
            score = expectimax(0, numAgents, s, depth - 1, evalFunc)
        else:
            score = expectimax(currAgent + 1, numAgents, s, depth, evalFunc)
        # max for pacman
        if currAgent == 0:
            bestScore = max(score, bestScore)
        # expectation for ghosts over all actions
        else:
            bestScore += (score / numActions)
    return bestScore
