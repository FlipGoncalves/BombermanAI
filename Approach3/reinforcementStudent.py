import math
import sys
import json
import asyncio
import websockets
import getpass
import os
import time
import random
import traceback

from clients import Client
from reinforcementAgentAI import AgentAI

async def agent_loop(server_address="localhost:8000", agent_name="84730"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        msg, game_properties = await Client.recv_game_properties(websocket, agent_name)

        # level
        current_level = 0

        # Powerups
        powerup_last_pos = []
        powerup = None
        bomb_counter = 1
        bomb_range = 3

        # Bomberman
        next_position = [0,0]
        lives = 3

        # bomb drop
        bomb_drop = False

        # enemies
        prev_enemies = []
        enemy_direction = []

        # map
        game_map = AgentAI.create_empty_2d_array(game_properties["size"][0], game_properties["size"][1])
        AgentAI.array_to_empty_map(game_map)


        while True:

            state = await Client.recv_game_state(websocket)

            # print(state)

            # Update variable lives and levels
            lives = state["lives"]

            if current_level < state["level"]:
                current_level = state["level"]

            # Stop the cycle if loose all lives or if stop receive server messages.
            if not state or lives == 0:
                break

            # bomberman position
            bomber_pos = state["bomberman"]

            # powwerup
            if state["powerups"]:
                powerup = state["powerups"][0][1]
                powerup_last_pos = state["powerups"][0][0]

            # Fill the map with reinforcement learning values
            try:
                enemy_direction = AgentAI.get_enemy_directions(state["enemies"], prev_enemies, enemy_direction)

                AgentAI.clear_map(game_map)
                AgentAI.fill_empty_map_with_player(game_map, bomber_pos)
                AgentAI.fill_empty_map_with_bombs(game_map, state["bombs"])
                AgentAI.fill_empty_map_with_enemies(game_map, state["enemies"], enemy_direction, bomb_range)
                AgentAI.fill_empty_map_with_walls(game_map, state["walls"])
                AgentAI.fill_empty_map_with_powerups(game_map, powerup_last_pos)
                AgentAI.fill_empty_map_with_exit(game_map, state["exit"], state["enemies"])


                prev_enemies = state["enemies"]
            except Exception:
                tb = traceback.format_exc()
                print(tb)

            # dependning on powerup type
            if powerup_last_pos == state["bomberman"]:
                if powerup == "Bombs":
                    bomb_counter += 1
                elif powerup == "Flames":
                    bomb_range += 1
                elif powerup == "Speed":
                    speed += 1
                elif powerup == "Detonator":
                    pass

                powerup_last_pos = []

            if not bomb_drop:
                path = await AgentAI.reinforcement_pathing(bomber_pos, game_map)
                node = path[1]
                next_position = [node.position[0] - bomber_pos[0], node.position[1] - bomber_pos[1]]

            key = ""
            if bomb_drop:
                print("Yes Rico, kaboom")
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

            next_position = [0,0]

            if not bomb_drop and node.reward > 3.9 and not powerup_last_pos == next_position and node.reward < 15:
                print("Kaboom??")
                bomb_drop = True

            if bomb_drop and key == "B":
                print("KABOOM")
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
