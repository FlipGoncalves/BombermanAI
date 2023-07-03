import json
import asyncio
import websockets
import getpass
import os
import traceback

from clients import Client
from reinforcementAgentAI import AgentAI
from reinforcementConsts import Reinforcement

def update_map(game_map, state, enemy_directions, bomberman, powerup_pos):
    AgentAI.array_to_empty_map(game_map, bomberman)
    AgentAI.fill_empty_map_with_powerups(game_map, powerup_pos)
    AgentAI.fill_empty_map_with_exit(game_map, state["exit"], state["enemies"], bomberman)
    AgentAI.fill_empty_map_with_bombs(game_map, state["bombs"])
    AgentAI.fill_empty_map_with_walls(game_map, state["walls"], state["exit"])
    AgentAI.fill_empty_map_with_enemies(game_map, state["enemies"], enemy_directions)

async def agent_loop(server_address="localhost:8000", agent_name="84730"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        _, game_properties = await Client.recv_game_properties(websocket, agent_name)

        # Bomberman
        next_position = [0,0]
        lives = 3

        # bomb drop
        bomb_drop = False

        # Previous enemy positions
        prev_enemies = []
        prev_directions = {}

        # map
        game_map = AgentAI.create_empty_2d_array(game_properties["size"][0], game_properties["size"][1])
        AgentAI.array_to_empty_map(game_map, [0,0])

        while True:

            try:
                state = await Client.recv_game_state(websocket)
            except:
                print("Ending...")
                return

            # Stop the cycle if loose all lives or if stop receive server messages.
            if not state or lives == 0:
                print("Ending...")
                return

            if "lives" not in state.keys():
                continue
                
            # Update variable lives and levels
            lives = state["lives"]

            # bomberman position
            bomber_pos = state["bomberman"]

            # Fill the map with reinforcement learning values
            try:
                # Obtain enemy directions
                prev_directions = AgentAI.get_enemy_directions(state["enemies"], prev_enemies, prev_directions, game_map)

                # Clear and update the map
                update_map(game_map, state, prev_directions, bomber_pos, state["powerups"])

                # Update the previous enemy positions
                prev_enemies = state["enemies"]

            except Exception:
                tb = traceback.format_exc()
                print(tb)

            for row in game_map:
                print([int(x) for x in row])

            if not bomb_drop:
                path = await AgentAI.reinforcement_pathing(bomber_pos, game_map)
                node = path[1]
                next_position = [node.position[0] - bomber_pos[0], node.position[1] - bomber_pos[1]]

            key = ""
            if bomb_drop:
                key = "B"
            elif next_position[0] == -1:
                key = "a"
            elif next_position[0] == 1:
                key = "d"
            elif next_position[1] == -1:
                key = "w"
            elif next_position[1] == 1:
                key = "s"
            else:
                key = ""

            reward_next = game_map[node.position[1]][node.position[0]]
            possible_bombs = [Reinforcement.Destructive_Wall, Reinforcement.Destructive_Wall_Exit, Reinforcement.Enemy_Bomb]
            
            if not bomb_drop and reward_next in possible_bombs:
                bomb_drop = True

            next_position = [0,0]

            if bomb_drop and key == "B":
                bomb_drop = False

            await websocket.send(
                json.dumps({"cmd": "key", "key": key})
            )

# Not to touch...
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
