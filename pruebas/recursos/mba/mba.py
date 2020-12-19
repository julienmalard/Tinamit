from mesa import Agent
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from tinamit.envolt.mba.mesa import EnvoltModeloMesa
from tinamit.envolt.mba import VariablesMBA, VarMBA, VarCuadMBA, VarAgenteMBA


def compute_gini(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    x = sorted(agent_wealths)
    N = model.num_agents
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return 1 + (1 / N) - 2 * B


class MoneyAgent(Agent):
    """ An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 1

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def give_money(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1

    def step(self):
        self.move()
        if self.wealth > 0:
            self.give_money()


class ModeloDinero(EnvoltModeloMesa):
    """A model with some number of agents."""

    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        # Create agents
        for i in range(self.num_agents):
            a = MoneyAgent(i, self)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.datacollector = DataCollector(
            model_reporters={"Gini": compute_gini},  # `compute_gini` defined above
            agent_reporters={"Wealth": "wealth"}
        )
        super().__init__(unid_tiempo='meses')

    def variables(símismo):
        return VariablesMBA([
            VarMBA("Gini", inic=0, ingr=False, egr=True, unid=None),
            VarAgenteMBA('wealth', inic=10, unid='ரூ'),
            VarCuadMBA('wealth cuad', unid='ரூ', inic=0)
        ])

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
