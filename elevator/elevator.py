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
import sys, types, time, random, os, copy

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

    def getLegalActionsForSingleElevator(self, elevator_id):
        elevator = self.elevators[elevator_id]
        # Default to physical limitations.
        can_stall = True
        can_go_down = elevator.floor > 0
        can_go_up = elevator.floor < self.numFloors - 1

        # Never stall or change direction on a rider.
        for rider in elevator.riders:
            can_stall = False
            if rider.dest < elevator.floor:
                can_go_up = False
            elif rider.dest > elevator.floor:
                can_go_down = False
            else:
                must_open = True

        actions = []
        if can_stall:
            actions.append("STALL")
        if can_can_go_down:
            actions.append("DOWN")
            actions.append("OPEN_DOWN")
        if can_can_go_up:
            actions.append("UP")
            actions.append("OPEN_UP")
        if must_open:
            actions.remove("UP")
            actions.remove("DOWN")
        return actions

    # Maps a list of lists to a list of selections from each list.
    def getCombinations(self, lists):
        if len(lists) == 0:
            return [[]]
        combinations = []
        # Combine things in the first list with every combinations of the rest.
        for suffix in self.getCombinations(lists[1:]):
            for prefix in lists[0]:
                combination = [prefix]
                combination.extend(suffix)
                combinations.append(combination)
        return combinations

    def getLegalActions(self, agentIndex=0):
        """
        Returns the legal actions for the agent specified.
        """
        lists = getCombinations(map(range(k), getLegalActionsForSingleElevator))
        return [tuple(action_list) for action_list in lists]

    def generateSuccessor(self, agentIndex, action):
        """
        Returns the successor state after the specified agent takes the action.
        """
        successor = GameState(self)
        successor.timestep += 1
        # Elevator logic.
        for i in len(successor.elevators):
            elevator = successor.elevators[i]
            if action[i] == "UP":
                elevator.floor += 1
            elif action[i] == "DOWN":
                elevator.floor -= 1
            elif action[i] == "OPEN_UP" or action[i] == "OPEN_DOWN":
                # Riders either get off or cause a waiting penalty.
                updated_riders = []
                for dest, wait in elevator.riders:
                    if dest != elevator.floor:
                        updated_riders.append((dest, wait + 1))
                    successor.score -= wait + 1
                elevator.riders = updated_riders
                # Waiting riders on the floor can get on.
                updated_waiting = []
                for dest, wait in successor.waiting_riders[elevator.floor]:
                    if ((dest > elevator.floor) == (action[i] == "OPEN_UP") and
                            (len(elevator.riders) < c)):
                        elevator.riders.append((dest, wait))
                    else:
                        updated_waiting.append((dest, wait))
                successor.waiting_riders[elevator.floor] = updated_waiting
        # Update waiting passenger wait times.
        for floor_list in successor.waiting_riders:
            for dest, wait in len(floor_list):
                floor_list[i] = (dest, wait + 1)
                successor.score -= (wait + 1)
        # Add new arrivals.
        for src, dest in successor.generateArrivals(successor.timestep):
            successor.waiting_riders[src].append((dest, 0))
        return successor

    def getScore(self):
        # see generateSuccessor
        return return float(self.score)

    def __init__(self, prevState=None):
        """
        Generates a new state by copying information from its predecessor.
        """
        # State is:
        # *parameters*
        # -numFloors (n)
        # -numElevators (k)
        # -elevatorCapacity (c)
        # -generateArrivals (function to generate src/dest pairs for people arriving at a timestep)
        # *state*
        # timestep = 0
        # -waiting_riders = [[] for _ in range(n)] : lists by floor of dest/wait_time triples
        # -elevators = [{floor: 0, riders: []} for _ in range(k)] : riders is a list of dest/wait_time pairs
        # -score = 0

        # TODO: some initial generateArrivals functions:
        # -people just go up to random floors, arriving with poisson distribution for some rate
        # -people just leave from random floors, arriving with poisson distribution for some rate
        # -people move from random floors to random floors, poisson
        # -union samples from the first three distributions with fixed rates
        # -union samples from the first three distributions with rates that vary periodically by timestep

        if prevState is not None:
            # Parameters.
            self.numElevators = prevState.numElevators
            self.numFloors = prevState.numFloors
            self.elevatorCapacity = prevState.elevatorCapacity
            self.generateArrivals = prevState.generateArrivals
            # Simulation state.
            self.timestep = prevState.timestep
            self.elevators = copy.deepCopy(prevState.elevators)
            self.waiting_riders = copy.deepCopy(prevState.waiting_riders)
            self.score = prevState.score
        else:
            self.numElevators = 1
            self.numFloors = 10
            self.elevatorCapacity = 10
            self.generateArrivals = lambda timestep: [(0, 5)]
            self.timestep = 0
            self.elevators = [{floor: 0, riders: []} for _ in range(self.numElevators)]
            self.waiting_riders = [[] for _ in range(n)]
            self.score = 0

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
