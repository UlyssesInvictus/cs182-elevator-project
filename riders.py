# Riders are {source, destination, timestep}.
def simulate(n, k, c, riders, agent):
    # Ride times are set on passenger arrival.
    ride_times = [-1 for _ in riders]
    # Elevator state is {floor, rider_ids}.
    elevators = [{floor: 0, rider_ids: []} for _ in range(k)]

    waiting_riders = [[] for _ in range(n)]
    next_rider = 0

    timestep = 0
    while -1 in ride_times:
        # Release new riders.
        while (next_rider < len(next_rider) and
                riders[next_rider].timestep <= timestep):
            waiting_riders[riders[next_rider].source].append(next_rider)
            next_rider += 1
        # Update each elevator based on the agent's specified actions.
        # TODO: defensively copy states so the agent can't cheat.
        actions = agent(timestep, elevators, waiting_riders)
        for i in range(k):
            # Move up or down for the timestep.
            if actions[i] == UP and elevators[i].floor < k:
                elevators[i].floor++
            if actions[i] == DOWN and elevators[i].floor > 0:
                elevators[i].floor--
            # Open for the timestep.
            if actions[i] == OPEN_UP or actions[i] == OPEN_DOWN:
                for r in elevators[i].rider_ids:
                    if riders[r].destination == elevators[i].floor:
                        elevators[i].remove(r)
                        ride_times[r] = timestep - riders[r].timestep
                    for r in waiting_riders[elevators[i].floor]:
                        if ((riders[r].destination > riders[r].source) ==
                                (actions[i] == OPEN_UP)):
                            waiting_riders[elevators[i].floor].remove(r)
                            elevators[i].rider_ids.append(r)
                if actions[i] == OPEN_UP:
                    # TODO: ???
                    pass
                # Default action is to stay still with doors closed.
        timestep += 1
    return ride_times
