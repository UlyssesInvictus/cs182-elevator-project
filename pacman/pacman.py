# pacman.py
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
Pacman.py holds the logic for the classic pacman game along with the main
code to run a game.  This file is divided into three sections:

  (i)  Your interface to the pacman world:
          Pacman is a complex environment.  You probably don't want to
          read through all of the code we wrote to make the game runs
          correctly.  This section contains the parts of the code
          that you will need to understand in order to complete the
          project.  There is also some code in game.py that you should
          understand.

  (ii)  The hidden secrets of pacman:
          This section contains all of the logic code that the pacman
          environment uses to decide who can move where, who dies when
          things collide, etc.  You shouldn't need to read this section
          of code, but you can if you want.

  (iii) Framework to start a game:
          The final section contains the code for reading the command
          you use to set up the game, then starting up a new game, along with
          linking in all the external parts (agent functions, graphics).
          Check this section out to see all the options available to you.

To play your first game, type 'python pacman.py' from the command line.
The keys are 'a', 's', 'd', and 'w' to move (or arrow keys).  Have fun!
"""
from game import Game
import util, layout
import sys, types, time, random, os

###################################################
# YOUR INTERFACE TO THE PACMAN WORLD: A GameState #
###################################################

class GameState:
    """
    A GameState specifies the full game state, including the food, capsules,
    agent configurations and score changes.

    GameStates are used by the Game object to capture the actual state of the game and
    can be used by agents to reason about the game.

    Much of the information in a GameState is stored in a GameStateData object.  We
    strongly suggest that you access that data via the accessor methods below rather
    than referring to the GameStateData object directly.

    Note that in classic Pacman, Pacman is always agent 0.
    """

    ####################################################
    # Accessor methods: use these to access state data #
    ####################################################

    # static variable keeps track of which states have had getLegalActions called
    explored = set()
    def getAndResetExplored():
        tmp = GameState.explored.copy()
        GameState.explored = set()
        return tmp
    getAndResetExplored = staticmethod(getAndResetExplored)

    def getLegalActions(self, agentIndex=0):
        """
        Returns the legal actions for the agent specified.
        """
        # TODO
        # this is the really important that lets learning work properly
        pass
        # example (abbreviated/cleaned) pacman code
        # if self.isWin() or self.isLose(): return []
        # return PacmanRules.getLegalActions( self )

    def generateSuccessor(self, agentIndex, action):
        """
        Returns the successor state after the specified agent takes the action.
        """
        # TODO
        # also especially important for modifying score and generating next state
        pass
        # example (abbreviated/cleaned) pacman code
        # if self.isWin() or self.isLose(): raise Exception('Can\'t generate a successor of a terminal state.')
        # state = GameState(self)
        # just change the state using pacman's defined actions
        # PacmanRules.applyAction( state, action )
        # state.data.scoreChange += -TIME_PENALTY # Penalty for waiting around
        # # Book keeping
        # state.data._agentMoved = agentIndex
        # state.data.score += state.data.scoreChange
        # GameState.explored.add(self)
        # GameState.explored.add(state)
        # return state

    def getLegalPacmanActions(self):
        # TODO
        # analogize to elevator
        pass

    def generatePacmanSuccessor(self, action):
        """
        Generates the successor state after the specified pacman move
        """
        # TODO:
        # analogize to elevator
        # return self.generateSuccessor(0, action)
        pass

    def getPacmanState(self):
        """
        Returns an AgentState object for pacman (in game.py)

        state.pos gives the current position
        state.direction gives the travel vector
        """
        # TODO:
        # analogize to "getElevatorState"
        # return self.data.agentStates[0].copy()
        pass

    def getGhostStates(self):
        # TODO:
        # analogize to "getAgentStates"
        # return self.data.agentStates[1:]
        pass

    def getNumAgents(self):
        # TODO
        pass

    def getScore(self):
        # TODO
        # also really important for letting RL calculate rewards properly
        # that lets RL work properly
        pass
        # probaly just going to be something like:
        # return float(self.score)
        # where actual score is managed by getSuccessor

    def isLose(self):
        # TODO
        pass

    def isWin(self):
        # TODO
        pass

    def __eq__(self, other):
        """
        Allows two states to be compared.
        """
        # TODO:
        pass


    def __hash__(self):
        """
        Allows states to be keys of dictionaries.
        """
        # TODO:
        pass
        # e.g.
        # for i, state in enumerate( self.agentStates ):
        #     try:
        #         int(hash(state))
        #     except TypeError, e:
        #         print e
        #         #hash(state)
        # return int((hash(tuple(self.agentStates)) + 13*hash(self.food) + 113* hash(tuple(self.capsules)) + 7 * hash(self.score)) % 1048575 )

    def __init__( self, prevState = None ):
        """
        Generates a new state by copying information from its predecessor.
        """
        # TODO: list all init properties here
        # will probably have to modify in some new arguments from the driver
        # and command line arguments, especially stuff like
        # num elevators, floors, passenger distribution function, etc.
        pass
        # example:
        # if prevState is not None:
        #     self.food = prevState.food.shallowCopy()
        #     self.capsules = prevState.capsules[:]
        #     self.agentStates = self.copyAgentStates( prevState.agentStates )
        #     self.layout = prevState.layout
        #     self._eaten = prevState._eaten
        #     self.score = prevState.score
        # self._foodEaten = None
        # self._foodAdded = None
        # self._capsuleEaten = None
        # self._agentMoved = None
        # self._lose = False
        # self._win = False
        # self.scoreChange = 0

    def deepCopy(self):
        state = GameState(self)
        # TODO: replicate with stuff in init
        # state.prop = self.prop etc.
        return state

#############################
# FRAMEWORK TO START A GAME #
#############################

def default(str):
    return str + ' [Default: %default]'

def parseAgentArgs(str):
    if str == None: return {}
    pieces = str.split(',')
    opts = {}
    for p in pieces:
        if '=' in p:
            key, val = p.split('=')
        else:
            key,val = p, 1
        opts[key] = val
    return opts

def readCommand(argv):
    """
    Processes the command used to run pacman from the command line.
    """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python pacman.py <options>
    EXAMPLES:   (1) python pacman.py
                    - starts an interactive game
                (2) python pacman.py --layout smallClassic --zoom 2
                OR  python pacman.py -l smallClassic -z 2
                    - starts an interactive game on a smaller board, zoomed in
    """
    parser = OptionParser(usageStr)

    parser.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    parser.add_option('-p', '--pacman', dest='pacman',
                      help=default('the agent TYPE in the pacmanAgents module to use'),
                      metavar='TYPE', default='KeyboardAgent')
    parser.add_option('-g', '--ghosts', dest='ghost',
                      help=default('the ghost agent TYPE in the ghostAgents module to use'),
                      metavar = 'TYPE', default='RandomGhost')
    parser.add_option('-f', '--fixRandomSeed', action='store_true', dest='fixRandomSeed',
                      help='Fixes the random seed to always play the same game', default=False)
    parser.add_option('-r', '--recordActions', action='store_true', dest='record',
                      help='Writes game histories to a file (named by the time they were played)', default=False)
    parser.add_option('-a','--agentArgs',dest='agentArgs',
                      help='Comma separated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"')
    parser.add_option('-x', '--numTraining', dest='numTraining', type='int',
                      help=default('How many episodes are training (suppresses output)'), default=0)
    # TODO: add more important properties
    # see init in GameState
    
    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()

    # Fix the random seed
    if options.fixRandomSeed:
        random.seed('cs188')

    # TODO: Choose a Pacman agent
    args['pacman'] = None
    # TODO: Choose a ghost agent
    ghostType = loadAgent(options.ghost, noKeyboard)
    args['ghosts'] = [ghostType( i+1 ) for i in range( options.numGhosts )]

    # Don't display training games
    if 'numTrain' in agentOpts:
        options.numQuiet = int(agentOpts['numTrain'])
        options.numIgnore = int(agentOpts['numTrain'])

    args['numGames'] = options.numGames

    return args


def runGames(layout, pacman, ghosts, numGames, numTraining=0, timeout=30):
    import __main__

    games = []

    for i in range(numGames):
        # TODO: properly define agents
        agents = [pacman] + ghosts[:layout.getNumGhosts()]
        initState = GameState()
        game = Game(agents)
        game.state = initState
        game.run()
        # TODO: need this part?
        games.append(game)

    if (numGames-numTraining) > 0:
        scores = [game.state.getScore() for game in games]
        wins = [game.state.isWin() for game in games]
        winRate = wins.count(True) / float(len(wins))
        print 'Average Score:', sum(scores) / float(len(scores))
        print 'Scores:       ', ', '.join([str(score) for score in scores])
        print 'Win Rate:      %d/%d (%.2f)' % (wins.count(True), len(wins), winRate)
        print 'Record:       ', ', '.join([ ['Loss', 'Win'][int(w)] for w in wins])

    return games

if __name__ == '__main__':
    """
    The main function called when pacman.py is run
    from the command line:

    > python pacman.py

    See the usage string for more details.

    > python pacman.py --help
    """
    args = readCommand(sys.argv[1:]) # Get game components based on input
    runGames(**args)

    pass
