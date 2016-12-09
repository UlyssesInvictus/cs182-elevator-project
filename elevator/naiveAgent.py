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
        # temp of actions in order per elevator
        chosen_actions = ["" for _ in range(num_elevators)]
        # split into empty and non-empty elevators
        empty, carrying = [], []
        for i in range(state.num_elevators):
            if len(state.elevators[i]['riders']) == 0:
                empty.append(i)
            else:
                carrying.append(i)
        # take care of the non-empty ones
        for i in carrying:
            # first, open if you have a reason to (determined by legal actions)
            # priority goes to up if both are available
            # otherwise continue as requested, checking for each direction
            # (should never have the case where both are possible and el.
            # has passengers in it)
            for a in ["OPEN_UP", "OPEN_DOWN", "UP", "DOWN"]:
                if a in actions_per_el[i]:
                    chosen_actions[i] = a
                    break
        # then, assign directions to empty elevators
        # sort list of all riders by waittime decr.
        # TODO: intelligently break ties?
        all_riders = []
        for f in range(state.num_floors):
            for dest, wait in state.waiting_riders[f]:
                all_riders.append((f, dest, wait))
        all_riders.sort(key=lambda x: -x[2])
        # assign elevators until gone
        while len(empty) > 0:
            # get the rider with longest wait
            candidate = all_riders[0]
            all_riders.remove(candidate)
            # find the closest elevator
            elevator_dists = [(e, abs(state.elevators[e]['floor'] - candidate[0])) for e in empty]
            elevator_dists.sort(key=lambda x: x[1])
            chosen_elevator = elevator_dists[0][0]
            empty.remove(chosen_elevator)
            # set a direction for the closest elevator
            if candidate[0] > state.elevators[chosen_elevator]['floor']:
                chosen_actions[chosen_elevator] = 'UP'
            elif candidate[0] < state.elevators[chosen_elevator]['floor']:
                chosen_actions[chosen_elevator] = 'DOWN'
            # notably, only open for rider on the same floor
            # if they're the longest waiting one!!
            elif candidate[1] > candidate[0]:
                chosen_actions[chosen_elevator] = 'OPEN_UP'
            else:
                chosen_actions[chosen_elevator] = 'OPEN_DOWN'
        return tuple(chosen_actions)
