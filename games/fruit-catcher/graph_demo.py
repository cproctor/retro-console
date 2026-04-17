from retro.game import Game
from retro.graph import Graph
from retro.agent import ArrowKeyAgent

class Player(ArrowKeyAgent):
    """Player is a subclass of ArrowKeyAgent, so it inherits all of that 
    class's attributes. However, I'm redefining `try_to_move`: Player
    only moves if the new position is on the board and unoccupied.
    """
    def try_to_move(self, position, game):
        if game.on_board(position) and game.is_empty(position):
            self.position = position

g = Graph()
g.get_or_create_edge(15, 16, 16, 16)
g.get_or_create_edge(16, 16, 16, 14)
g.get_or_create_edge(16, 14, 13, 14)
g.get_or_create_edge(13, 14, 13, 18)
g.get_or_create_edge(13, 18, 18, 18)
g.get_or_create_edge(18, 18, 18, 12)
g.get_or_create_edge(18, 12, 11, 12)
g.get_or_create_edge(11, 12, 11, 20)
g.get_or_create_edge(11, 20, 20, 20)
g.get_or_create_edge(20, 20, 20, 10)
g.get_or_create_edge(20, 10,  9, 10)
g.get_or_create_edge( 9, 10,  9, 22)
g.get_or_create_edge( 9, 22, 22, 22)
g.get_or_create_edge(22, 22, 22, 10)
agents = g.get_agents()
for agent in agents:
    agent.color = "gray_on_black"

player = Player()
player.position = (15, 15)
agents.append(player)

game = Game(agents, {}, board_size=(30, 30))
game.play()



