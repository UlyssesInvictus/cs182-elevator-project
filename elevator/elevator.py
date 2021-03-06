# elevator.py
# This code was developed from the Pacman AI projects developed
# for Berkeley's CS 188 homework assignments. The original attribution
# is below.
# ---------
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
elevator.py holds the logic for the elevator simulation along with the main
code to run a game. This file is divided into three sections:

  (i)  The elevator "game" state:
          This section contains all the parts of the code
          that describe how elevators function, including:
          - what information the game knows, mostly parameters
          - what information elevators and riders know
          - what elevators are allowed to do given their current position
            and riders
          - how the state will change given a series of actions selected
            for each elevator, especially how score changes
          - how riders arrive
  (ii)  The entirety of the Monte Carlo framework.
          It uses the same GameState class as RL and Naive methods, but
          doesn't use the driver in game.py and called by runGames()--
          instead, it manages all of the running itself.
  (iii) Framework to start a game:
          The final section contains the code for reading the command
          you use to set up the game, then starting up a new game.
          Check this section out to see all the options available to you.
"""

from game import Game
import util
import sys, types, time, random, os, copy
from qlearningAgents import *
from naiveAgent import *
from numpy.random import seed, poisson

###################################################
# YOUR INTERFACE TO THE PACMAN WORLD: A GameState #
###################################################

class GameState:
    """
    A GameState specifies the full game state, including the elevators,
    riders, and score changes.

    GameStates are used by the Game object to capture the actual state of the game and
    can be used by agents to reason about the game.

    Unlike the original Pacman project, the GameState is not a wrapper around
    a GameStateData object: it contains most of its information directly.

    Note that, unlike Pacman, the system of all elevators are considered
    a single agent acting at once.
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

    # get the actions possible for a single elevator based
    # on its floor and the riders it's carrying
    # there are four legel actions:
    # - UP, DOWN (move up or down)
    # - OPEN_UP, OPEN_DOWN (open while indicating the elevator intends to
    # go in that direction next; it's not a guarantee though!)
    # - STALL (just wait!)
    def getLegalActionsForSingleElevator(self, elevator_id):
        elevator = self.elevators[elevator_id]
        # Default to physical limitations.
        can_stall = True
        can_go_down = elevator['floor'] > 0
        can_go_up = elevator['floor'] < self.num_floors - 1
        must_open = False

        # Never stall or change direction on a rider.
        for rider in elevator['riders']:
            dest, wait = rider
            can_stall = False
            if dest < elevator['floor']:
                can_go_up = False
            elif dest > elevator['floor']:
                can_go_down = False
            else:
                must_open = True

        # Don't do stupid things based on a rider waiting outside
        # (Like open to go up if they're going down)
        can_open_down = False
        can_open_up = False
        for dest, wait in self.waiting_riders[elevator['floor']]:
            if dest < elevator['floor']:
                can_open_down = True
            if dest > elevator['floor']:
                can_open_up = True

        # generate final list
        actions = []
        if can_stall:
            actions.append("STALL")
        if can_go_down:
            actions.append("DOWN")
            if must_open or can_open_down:
                actions.append("OPEN_DOWN")
        if can_go_up:
            actions.append("UP")
            if must_open or can_open_up:
                actions.append("OPEN_UP")
        if must_open:
            if "UP" in actions:
                actions.remove("UP")
            if "DOWN" in actions:
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

    # ignore the "agentIndex" part--that's to keep the legacy agents happy
    # while passing in parameters
    def getLegalActions(self, agentIndex=0):
        """
        Returns the legal actions for the agent specified.
        """
        # note that a single "action" actually describes the actions for
        # all elevators--thus the need to generate all possible permutations
        lists = self.getCombinations(map(self.getLegalActionsForSingleElevator,
                                         range(self.num_elevators)))
        # pass tuples so actions can be hashed
        return [tuple(action_list) for action_list in lists]

    def generateSuccessor(self, action):
        """
        Returns the successor state after the specified agent takes the action.
        """
        successor = GameState(self)
        successor.timestep += 1
        # Elevator logic.
        for i in range(len(successor.elevators)):
            elevator = successor.elevators[i]
            if action[i] == "UP":
                elevator['floor'] += 1
            elif action[i] == "DOWN":
                elevator['floor'] -= 1
            elif action[i] == "OPEN_UP" or action[i] == "OPEN_DOWN":
                # Riders either get off or cause a waiting penalty.
                updated_riders = []
                for dest, wait in elevator['riders']:
                    if dest != elevator['floor']:
                        updated_riders.append((dest, wait + 1))
                    successor.score -= wait + 1
                elevator['riders'] = updated_riders
                # Waiting riders on the floor can get on.
                updated_waiting = []
                for dest, wait in successor.waiting_riders[elevator['floor']]:
                    if ((dest > elevator['floor']) == (action[i] == "OPEN_UP") and
                            (len(elevator['riders']) < self.elevator_capacity)):
                        elevator['riders'].append((dest, wait))
                    else:
                        updated_waiting.append((dest, wait))
                successor.waiting_riders[elevator['floor']] = updated_waiting
                elevator['riders'].sort(key=lambda x: -x[1])
        # Update waiting passenger wait times.
        for i in range(len(successor.waiting_riders)):
            floor_list = successor.waiting_riders[i]
            for j in range(len(floor_list)):
                dest, wait = floor_list[j]
                floor_list[j] = (dest, wait + 1)
                successor.score -= (wait + 1)
        # Add new arrivals.
        for src, dest in successor.generateArrivals(successor.timestep):
            successor.waiting_riders[src].append((dest, 0))
        # maintain sort invariant for correct hashing
        for i in range(len(successor.waiting_riders)):
            # sort by wait time, decreasing
            floor_list.sort(key=lambda x: -x[1])
        return successor

    def getScore(self):
        # see generateSuccessor
        return float(self.score)

    def generateArrivals(self, timestep):
        # TODO: possible extension--non-constant lambdas
        lGroundSource = self.traffic  # maybe exponential decay from time: 0 to end?
        lGroundDest = self.traffic  # maybe exponential decay from time: end to 0?
        lRandom = self.traffic  # maybe constant?

        # lots of riders are arriving at the ground: lambda = #/timestep
        groundSource = [(0, random.randint(1, self.num_floors-1))
                        for _ in range(poisson(lGroundSource))]
        # lots of riders also want to get to the ground: lambda = #/timestep
        groundDest = [(random.randint(1, self.num_floors-1), 0)
                      for _ in range(poisson(lGroundDest))]
        # lots of random other movement throughout
        randomRiders = []
        for _ in range(poisson(lRandom)):
            source = random.randint(0, self.num_floors-1)
            while True:
                dest = random.randint(0, self.num_floors-1)
                if dest != source:
                    break
            randomRiders += [(source, dest)]
        # combine all three!
        return groundSource + groundDest + randomRiders

    def deepCopy(self):
        state = GameState(self)
        return state

    def __init__(self, prev_state=None, num_elevators=1, num_floors=10,
                 capacity=20, traffic=0.25):
        """
        Generates a new state by copying information from its predecessor.
        """

        if prev_state is not None:
            # Parameters.
            self.num_elevators = prev_state.num_elevators
            self.num_floors = prev_state.num_floors
            self.elevator_capacity = prev_state.elevator_capacity
            self.generate_arrivals = prev_state.generate_arrivals
            # Simulation state.
            self.timestep = prev_state.timestep
            self.elevators = copy.deepcopy(prev_state.elevators)
            self.waiting_riders = copy.deepcopy(prev_state.waiting_riders)
            self.score = prev_state.score
            self.traffic = prev_state.traffic
        else:
            self.num_elevators = num_elevators
            self.num_floors = num_floors
            self.elevator_capacity = capacity
            self.generate_arrivals = lambda timestep: [(0, 5)]
            self.timestep = 0
            # each rider is (destination, waittime) tuple
            # source is unnecessary since it doesn't matter for riders in elev.
            # and waiting_riders contain it in the index
            self.elevators = [{"floor": 0, "riders": []} for _ in range(num_elevators)]
            # index of waiting_riders = floor
            self.waiting_riders = [[] for _ in range(self.num_floors)]
            self.score = 0
            self.traffic = traffic

    def __hash__(self):
        """
        Allows states to be keys of dictionaries.
        """
        data = [self.timestep, self.score]
        for elevator in self.elevators:
            data.append(elevator['floor'])
            data.append(tuple(elevator['riders']))
        for rider_list in self.waiting_riders:
            data.append(tuple(rider_list))
        return hash(tuple(data))

    def __str__(self):
        stats = 'Time: %d, Score: %d\n' % (self.timestep, self.score)
        elevators = ""
        for i in range(self.num_elevators):
            e = self.elevators[i]
            elevators += ("El. %d: Floor (%d), Riders (%d)\n" %
                          (i, e['floor'], len(e['riders'])))
        riders = ('Riders/floor: ' +
                  str([len(floor) for floor in self.waiting_riders]))
        return stats + elevators + riders


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
    parser.add_option('-f', '--fixRandomSeed', action='store_true', dest='fixRandomSeed',
                      help='Fixes the random seed to always play the same game', default=False)
    parser.add_option('-t', '--numTraining', dest='numTraining', type='int',
                      help=default('How many episodes are training (suppresses output)'), default=0)
    parser.add_option('-s', '--numSteps', dest='numSteps', type='int',
                      help=default('How many steps should the game run for?'), default=100)
    parser.add_option('-q', '--quiet', action='store_true', dest='quiet',
                      help=default('Silence the game state reports?'), default=False)
    parser.add_option('-a', '--agentType', dest='agentType',
                      help=default('Which agent to run?'), default='naive')
    parser.add_option('-e', '--numElevators', dest='numElevators',
                      help=default('How many elevators?'), default=4)
    parser.add_option('-x', '--numFloors', dest='numFloors',
                      help=default('How many floors?'), default=10)
    parser.add_option('-c', '--capacity', dest='capacity',
                      help=default('Capacity per elevator?'), default=20)
    parser.add_option('-z', '--traffic', dest='traffic',
                      help=default('Poisson lambda for traffic?'), default=0.25)
    # TODO: add more important properties
    # see init in GameState

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()

    # Fix the random seed
    if options.fixRandomSeed:
        seed(182)
        random.seed('cs182')

    args['numTraining'] = options.numTraining
    args['numGames'] = options.numGames
    args['numSteps'] = options.numSteps
    args['quiet'] = options.quiet
    args['agentType'] = options.agentType
    args['numElevators'] = int(options.numElevators)
    args['numFloors'] = int(options.numFloors)
    args['capacity'] = options.capacity
    args['traffic'] = options.traffic
    return args


def runMonteCarlo(num_timesteps=100, num_elevators=1, num_floors=10,
                  capacity=20, traffic=0.25):
    """
    Run a Monte Carlo simulation of elevators.
    Differs in output from the standard game driver, but
    relies on the same GameState and obeys the same logic.
    """
    def getPrunedActions(state, prev_action):
        actions = state.getLegalActions()
        if prev_action == None or random.random() > 0.8:
            return actions
        original_actions = actions[:]
        for i in range(len(prev_action)):
            if prev_action[i] == "UP" or prev_action[i] == "DOWN":
                new_actions = []
                keep_all = False
                for j in range(len(actions)):
                    if actions[j][i] == prev_action[i]:
                        new_actions.append(actions[j])
                    elif (actions[j][i] == "OPEN_UP" or
                            actions[j][i] == "OPEN_DOWN"):
                        keep_all = True
                if not keep_all:
                    actions = new_actions
        if len(actions) > 0:
            return actions
        return original_actions

    # Run to 100 timesteps.
    state = GameState(num_elevators=num_elevators, num_floors=num_floors,
                      capacity=capacity, traffic=traffic)
    prev_action = None

    while state.timestep < num_timesteps:
        actions = getPrunedActions(state, prev_action)
        if len(actions) == 1:
            state = state.generateSuccessor(actions[0])
            prev_action = actions[0]
        else:
            best_score = None
            best_action = None
            # TODO: allow passing of Monte Carlo sim. parameters
            for _ in range(100):
                # Remember the first action.
                first_action = random.choice(actions)
                sim_state = state.generateSuccessor(first_action)
                # Each simulation goes 20 timesteps out.
                action = None
                for _ in range(10):
                    action = random.choice(getPrunedActions(sim_state, action))
                    sim_state = sim_state.generateSuccessor(action)
                if best_score == None or sim_state.getScore() > best_score:
                    best_score = sim_state.getScore()
                    best_action = first_action
            # Take the best action.
            state = state.generateSuccessor(best_action)
            prev_action = best_action
    return state.getScore()

def runGames(numGames, numTraining, numSteps, quiet, agentType, numElevators,
             numFloors, capacity, traffic):
    """
    Main driver for running elevator simulations.
    Receives parameters from the command line and passes them to the
    Monte Carlo, RL, or naive simulations.
    If runnign RL or naive, then reports the average score.
    """

    import __main__

    games = []

    if agentType == 'monte':
        scores = []
        for i in range(100):
            score = runMonteCarlo(num_elevators=numElevators, num_floors=numFloors,
                         capacity=capacity, traffic=traffic)
            print 'Episode %d: score (%f)' % (i, score)
        print scores
        return
    elif agentType == 'rl':
        agent = QLearningAgent(numTraining=numTraining)
    else:
        agent = NaiveAgent()

    # TODO: things to pass into agent:
    # alpha    - learning rate (default 0.5)
    # epsilon  - exploration rate (default 0.5)
    # gamma    - discount factor (default 1)
    for i in range(numGames + numTraining):
        game = Game(agent)
        game.state = GameState(num_elevators=numElevators, num_floors=numFloors,
                               capacity=capacity, traffic=traffic)
        game.run(numSteps, quiet)
        if i >= numTraining:
            games.append(game)
            print 'Ran episode (%d/%d) of actual: score (%d)' % (i-numTraining+1, numGames, game.state.getScore())
        else:
            print 'Ran (%d/%d) of training: score (%d)' % (i, numTraining, game.state.getScore())

    scores = [game.state.getScore() for game in games]
    print 'Average Score:', sum(scores) / float(len(scores))
    print 'Scores:       ', ', '.join([str(score) for score in scores])
    return games

if __name__ == '__main__':
    """
    The main function called when elevator.py is run
    from the command line:

    > python elevator.py

    See the usage string for more details.

    > python elevator.py --help
    """
    args = readCommand(sys.argv[1:])  # Get game components based on input
    runGames(**args)

    pass
