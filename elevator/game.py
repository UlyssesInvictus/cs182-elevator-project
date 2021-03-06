# game.py
# -------
# This code was developed from the Pacman AI projects developed
# for Berkeley's CS 188 homework assignments. The original attribution
# is below.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import *
import time, os
import traceback
import sys

#######################
# Parts worth reading #
#######################

class Agent:
    """
    An agent must define a getAction method, but may also define the
    following methods which will be called if they exist:

    def registerInitialState(self, state): # inspects the starting state
    """
    def __init__(self, index=0):
        self.index = index

    def getAction(self, state):
        """
        The Agent will receive a GameState (from either {pacman, capture, sonar}.py) and
        must return an action from Directions.{North, South, East, West, Stop}
        """
        raiseNotDefined()

####################################
# Parts you shouldn't have to read #
####################################

class Game:
    """
    The Game manages the control flow, soliciting actions from agents.
    """

    def __init__(self, agent, startingIndex=0):
        self.agent = agent
        self.startingIndex = startingIndex
        self.gameOver = False
        self.moveHistory = []
        # below is implicitly set by elevator.py in runGames
        # self.state = some GameState()

    def getProgress(self):
        if self.gameOver:
            return 1.0
        else:
            return 0.0

    def run(self, num_steps, quiet):
        """
        Main control loop for game play.
        """
        self.num_moves = 0

        # inform learning agents of the game start
        agent = self.agent
        agent.registerInitialState(self.state.deepCopy())

        while not self.gameOver:
            # Generate an observation of the state
            observation = agent.observationFunction(self.state.deepCopy())
            if not quiet:
                print observation
            # Solicit an action
            action = agent.getAction(observation)
            # explicitly done in PacmanQLearningAgent
            # but for some reason we need to do it here...very weird...
            # (compare QLearningAgent.getAction and PacmanQLA.getAction)
            agent.doAction(observation, action)
            # Execute the action
            self.moveHistory.append((0, action))
            self.state = self.state.generateSuccessor(action)
            # Track progress
            self.num_moves += 1
            if self.num_moves > num_steps:
                self.gameOver = True

        # inform a learning agent of the game result
        agent.final(self.state)
