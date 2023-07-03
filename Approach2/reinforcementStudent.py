import json
import asyncio
import websockets
import getpass
import os

from clients import Client
from reinforcementAgentAI import AgentAI
from reinforcementConsts import Reinforcement, Powerups

import traceback


def print_game(game):
    for row in game:
        print(row)


def print_game_map(game_map):
    for row_idx, row in enumerate(game_map):
        # Convert Enum to int
        row = [int(x) for x in row]
        print(f"{row_idx}: {row}")


# Function to check if the level is over
def finished_level(state):
    # return not state["walls"] and not state["enemies"] and not state["bombs"]
    return not state["enemies"] and not state["bombs"] and state["exit"]


# Function to update the map
def update_map(game_map, state, enemy_directions, bomberman, powerups_flag):

    # Clear the map
    AgentAI.clear_map(game_map)

    # Add the bomberman to the map (Optional)
    # AgentAI.fill_empty_map_with_player(game_map, bomberman)

    # Default wallpass
    # wallpass = False

    # Default bomb radius
    bomb_radius = 3

    # Update bomb radius
    for powerup in state["powerups"]:
        if powerup[1] == 'Flames':
            bomb_radius += 1
        # elif powerup[1] == 'Wallpass':
        #     wallpass = True

    # Add the walls to the map
    if state["walls"]:
        AgentAI.fill_empty_map_with_walls(game_map, state["walls"], state["bombs"],
                                          no_reward=state["exit"] != [] and len(state["walls"]) < 8)

    # Ready to move level
    if finished_level(state):
        AgentAI.fill_empty_map_with_exit(game_map, state["exit"])

    else:

        # Note: Called after walls to overwrite walls rewards
        # Add the bombs to the map
        if state["bombs"]:
            AgentAI.fill_empty_map_with_bombs(game_map, state["bombs"])

        # Add the enemies to the map
        if state["enemies"]:
            AgentAI.fill_empty_map_with_enemies(game_map, state["enemies"], enemy_directions, bomb_radius)

        # Add powerups to the map
        if powerups_flag and state["powerups"]:
            AgentAI.fill_empty_map_with_powerups(game_map, state["powerups"])


async def agent_loop(server_address="localhost:8000", agent_name="84730"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        msg, game_properties = await Client.recv_game_properties(websocket, agent_name)

        # Initialize current level
        current_level = None

        # Powerups
        powerups_flag = True

        # Previous enemy positions
        prev_enemies = []

        # Enemy directions
        enemy_directions = []

        # Previous bomberman position
        prev_bomberman = []

        # Bomb Drop
        bomb_drop = False

        # Create the game map
        game_map = AgentAI.create_empty_2d_array(game_properties["size"][0], game_properties["size"][1])
        AgentAI.array_to_empty_map(game_map)

        while True:

            # Obtain the game state
            state = await Client.recv_game_state(websocket)

            # Debugging purposes
            # print(state)

            # Update the current level
            if not current_level or current_level != state["level"]:
                current_level = state["level"]

            # Update bomberman position
            bomberman = state["bomberman"]

            # Update max number of bombs
            max_bombs = 1 + len([powerup for powerup in state["powerups"] if powerup[0] == Powerups.Bombs.value])

            # Update bomberman lives
            lives = state["lives"]

            # Stop the cycle if the bomberman is dead or if the agent stopped sending messages
            if not state or lives == 0:
                break

            try:
                # Obtain enemy directions
                enemy_directions = AgentAI.get_enemy_directions(state["enemies"], prev_enemies, enemy_directions)

                # Clear and update the map
                update_map(game_map, state, enemy_directions, bomberman, powerups_flag)

                # Update the previous enemy positions
                prev_enemies = state["enemies"]

            except Exception:

                tb = traceback.format_exc()
                print(tb)

            # If no bomb drop, get the next position
            if not bomb_drop:

                # Obtain the path
                path = AgentAI.reinforcement_pathing(bomberman, prev_bomberman, game_map, len(state["enemies"]), finished_level(state))

                # print("Path: ", [node.position for node in path])

                # Obtain next node
                node = path[1]

                # Obtain next movement
                next_position = [node.position[0] - bomberman[0], node.position[1] - bomberman[1]]

                # print("Final node: ", path[-1].position)
                # print("Next node: ", node.position)

            # print("Next position: ", next_position)

            # Obtain next key
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

            # print("Key: ", key)

            # Check if the agent should drop a bomb
            if not bomb_drop and len(state["bombs"]) < max_bombs \
                    and node.reward >= Reinforcement.Reward - 2 and not finished_level(state):
                bomb_drop = True

            # Update the previous bomberman position
            if len(bomberman) > 7:
                prev_bomberman.pop(0)

            prev_bomberman.append(bomberman)

            # Reset the next position
            next_position = (0, 0)

            # Reset bomb drop
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
