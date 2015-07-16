import logging


def steels_experiment_continuation(simulation, networks, iteration_number, dump_freq):

    agents = simulation.get_agents()
    for agent in agents:
        logging.debug(agent)
        for network in networks:
            network["graph"].add_agent(agent)

    simulation.set_networks(networks)
    results = simulation.continue_(iteration_number, dump_freq)

    return results, simulation
