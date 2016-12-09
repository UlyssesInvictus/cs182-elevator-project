from game import Agent
import random,util,time

class NaiveAgent(Agent):
    """Naive solution to elevator stategy:
    - If empty:
        - If waiting riders: immediately heads toward longest waiting rider.
          Breaks ties by nearest floor, then by going up.
        - If no riders: waits at current floor.
    - If has riders:
        - Travels to floor in queue requested by riders who got on.
        - Can drop off passengers and pick them up if on the way.
    """

    # we could make this code cleaner by building the surrounding class
    # but who cares?
    def getAction(self, state):
        actions = state.getLegalActions()
        # build list of actions per elevator for ease of use
        num_elevators = state.num_elevators
        actions_per_el = [set() for _ in range(num_elevators)]
        for a in actions:
            for e in range(num_elevators):
                actions_per_el[e].add(a[e])
        chosen_action = []
        # get list of all waiting riders
        all_riders = []
        for f in range(state.num_floors):
            for dest, wait in state.waiting_riders[f]:
                all_riders.append((f, dest, wait))
        for e in state.elevators:
            # if empty
            if len(e['riders']) == 0:
                if len(all_riders) == 0:
                    chosen_action.append('STALL')
                else:
                    # this is slow, but easy to code
                    # just resort the riders every time we need to figure out
                    # who to retrieve
                    # sort by decr. wait time, and then incr. dist from elevator
                    all_riders.sort(key=lambda x: (-x[2], abs(x[0] - e['floor'])))
