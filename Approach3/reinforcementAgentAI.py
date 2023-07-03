import math
import random

from reinforcementSearchNode import SearchNode

from enum import Enum 

class Reinforcement(float, Enum):
    Indestructive_Wall = -100,
    Destructive_Wall = 4,
    Enemy_Area = -15,
    Enemy_Position = -20,
    Enemy_Bomb = 10,
    Bomb_Damage = -5,
    Powerup = 5,
    Step = -0.01,
    Bomb_Drop_Position = -10,
    Exit = 50,
    Player = -0.01

class AgentAI:

    # Function that creates an empty 2d array
    @staticmethod
    def create_empty_2d_array(width, height):

        cost_map = []

        for i in range(0, height):
            tmp = []
            for j in range(0, width):
                tmp.append(0)
            cost_map.append(tmp)

        return cost_map

    # Function that creates an empty game map
    @staticmethod
    def array_to_empty_map(in_map):
        for i in range(0, len(in_map)):
            for j in range(0, len(in_map[0])):
                if i == 0 or i == len(in_map) - 1 or j == 0 or j == len(in_map[0]) - 1:
                    in_map[i][j] = Reinforcement.Indestructive_Wall
                elif i % 2 == 0 and j % 2 == 0:
                    in_map[i][j] = Reinforcement.Indestructive_Wall
                else:
                    in_map[i][j] = Reinforcement.Step

    # Function that fills a game map array with the walls, given their coordinates
    @staticmethod
    def fill_empty_map_with_walls(in_map, walls):

        i = 1

        for wall in walls:
            for i in range(1,5,1):
                for pos in calculate_coordinates(i):
                    if len(in_map) > wall[1]+pos[0] \
                        and len(in_map[wall[1]+pos[0]]) > wall[0]+pos[1] :
                        # and in_map[wall[1]+pos[0]][wall[0]+pos[1]] == Reinforcement.Step:
                        pos_reward = in_map[wall[1]+pos[0]][wall[0]+pos[1]]
                        if pos_reward == Reinforcement.Step:
                            in_map[wall[1]+pos[0]][wall[0]+pos[1]] += Reinforcement.Destructive_Wall/i
                        elif pos_reward > (Reinforcement.Destructive_Wall/i):
                            in_map[wall[1]+pos[0]][wall[0]+pos[1]] += (Reinforcement.Destructive_Wall/i)*0.01
                        elif pos_reward > 0 and pos_reward < (Reinforcement.Destructive_Wall/i):
                            in_map[wall[1]+pos[0]][wall[0]+pos[1]] = Reinforcement.Destructive_Wall/i + pos_reward*0.01

            in_map[wall[1]][wall[0]] = Reinforcement.Indestructive_Wall

    # Function that fills a game map array with the enemies, given their coordinates
    @staticmethod
    def fill_empty_map_with_enemies(in_map, enemies, enemy_directions, bomb_range):

        enemies_left = len(enemies)

        for enemy in enemies:
            for i in range(1,2,1):
                for pos in calculate_coordinates(i):
                    if len(in_map) > enemy["pos"][1]+pos[0] \
                        and len(in_map[enemy["pos"][1]+pos[0]]) > enemy["pos"][0]+pos[1] \
                        and in_map[enemy["pos"][1]+pos[0]][enemy["pos"][0]+pos[1]] != Reinforcement.Indestructive_Wall:
                            in_map[enemy["pos"][1]+pos[0]][enemy["pos"][0]+pos[1]] += Reinforcement.Enemy_Area

            for i in range(3,15-enemies_left,1):
                for pos in calculate_coordinates(i):
                    if len(in_map) > enemy["pos"][1]+pos[0] \
                        and len(in_map[enemy["pos"][1]+pos[0]]) > enemy["pos"][0]+pos[1] :
                        # and in_map[enemy["pos"][1]+pos[0]][enemy["pos"][0]+pos[1]] == Reinforcement.Step:
                        pos_reward = in_map[enemy["pos"][1]+pos[0]][enemy["pos"][0]+pos[1]]
                        if pos_reward == Reinforcement.Step:
                            in_map[enemy["pos"][1]+pos[0]][enemy["pos"][0]+pos[1]] += Reinforcement.Enemy_Bomb/i*0.1
                        elif pos_reward > (Reinforcement.Enemy_Bomb/i):
                            in_map[enemy["pos"][1]+pos[0]][enemy["pos"][0]+pos[1]] += (Reinforcement.Enemy_Bomb/(i-1))*0.01
                        elif pos_reward > 0 and pos_reward < (Reinforcement.Enemy_Bomb/i):
                            in_map[enemy["pos"][1]+pos[0]][enemy["pos"][0]+pos[1]] = (Reinforcement.Enemy_Bomb/(i-1) + pos_reward)*0.01
                            # in_map[enemy["pos"][1]+pos[0]][enemy["pos"][0]+pos[1]] += Reinforcement.Enemy_Bomb/(i-1)

            if enemy["id"] in enemy_directions and enemy_directions[enemy["id"]] != (0, 0):
                direction = enemy_directions[enemy["id"]]
                next_position = (enemy["pos"][0] + direction[0], enemy["pos"][1] + direction[1])
                for current_range in range(3, 3+bomb_range):
                    bomb_position = (next_position[0] + direction[0] * current_range,
                                     next_position[1] + direction[1] * current_range)
                    # If the position is within the map, and it is a valid move
                    if len(in_map) > bomb_position[1] >= 0:
                        if len(in_map[bomb_position[1]]) > bomb_position[0] >= 0:
                            if in_map[bomb_position[1]][bomb_position[0]] >= Reinforcement.Enemy_Bomb:
                                in_map[bomb_position[1]][bomb_position[0]] += Reinforcement.Enemy_Bomb*0.1
                            if in_map[bomb_position[1]][bomb_position[0]] >= Reinforcement.Step:
                                in_map[bomb_position[1]][bomb_position[0]] = Reinforcement.Enemy_Bomb

            in_map[enemy["pos"][1]][enemy["pos"][0]] = Reinforcement.Enemy_Position

    @staticmethod
    def get_enemy_directions(enemies, prev_enemies, prev_directions):
        directions = {}
        for enemy, prev_enemy in zip(enemies, prev_enemies):
            # Obtain the difference between the current and previous position
            difference = (enemy["pos"][0] - prev_enemy["pos"][0], enemy["pos"][1] - prev_enemy["pos"][1])
            # If we have a previous direction
            if enemy["id"] in prev_directions:
                # Keep the previous direction if the enemy didn't move
                directions[enemy["id"]] = prev_directions[enemy["id"]] if difference == (0, 0) else difference
            # If we don't have a previous direction
            else:
                # Update the directions dictionary
                directions[enemy["id"]] = difference
        return directions

    # Function that fills a game map array with the bombs, given their coordinates and radius
    @staticmethod
    def fill_empty_map_with_bombs(in_map, bombs):
        
        sides = [(0,1),(0,-1),(1,0),(-1,0)]
        
        for bomb in bombs:
            pos = bomb[0]
            radius = bomb[2]

            # if in_map[pos[1]][pos[0]] != Reinforcement.Indestructive_Wall:
            in_map[pos[1]][pos[0]] = Reinforcement.Bomb_Drop_Position
                

            for side in sides:
                for rad in range(1, radius+1):
                    if len(in_map) > pos[1]+side[1]*rad \
                        and len(in_map[pos[1]+side[1]*rad]) > pos[0]+side[0]*rad \
                        and in_map[pos[1]+side[1]*rad][pos[0]+side[0]*rad] != Reinforcement.Indestructive_Wall:
                            in_map[pos[1]+side[1]*rad][pos[0]+side[0]*rad] = Reinforcement.Bomb_Damage

    # Function that fills a game map array with the powerup, given their coordinates
    @staticmethod
    def fill_empty_map_with_powerups(in_map, powerups):
        
        if powerups:
            in_map[powerups[1]][powerups[0]] += Reinforcement.Powerup

    # Function that fills a game map array with the exit, given their coordinates if there are not enemies
    @staticmethod
    def fill_empty_map_with_exit(in_map, exit, enemies):

        if exit and not enemies:
            in_map[exit[1]][exit[0]] = Reinforcement.Exit
            for i in range(1,35,1):
                for pos in calculate_coordinates(i):
                    if len(in_map) > exit[1]+pos[0] \
                        and len(in_map[exit[1]+pos[0]]) > exit[0]+pos[1] \
                        and in_map[exit[1]+pos[0]][exit[0]+pos[1]] == Reinforcement.Step:
                            in_map[exit[1]+pos[0]][exit[0]+pos[1]] = Reinforcement.Exit - i


    # Function that fills a game map array with the exit, given their coordinates if there are not enemies
    @staticmethod
    def fill_empty_map_with_player(in_map, player):
        
        in_map[player[1]][player[0]] += Reinforcement.Player

    # Function that cleans a map to update walls and enemies
    @staticmethod
    def clear_map(in_map):
        for i in range(0, len(in_map)):
            for j in range(0, len(in_map[i])):
                if in_map[i][j] != Reinforcement.Indestructive_Wall:
                    in_map[i][j] = Reinforcement.Step
                    
    @staticmethod
    def get_path(node):
        if node.parent == None:
            return [node]
        path = AgentAI.get_path(node.parent)
        path += [node]
        return path

    # Function based off map
    @staticmethod
    async def reinforcement_pathing(bomber_pos, game_map):
        print("--- Started Searching")

        open_list = []
        # closed_list = []

        # open_list.append(inital_node)

        reward = game_map[bomber_pos[1]][bomber_pos[0]]
        initial_node = SearchNode(None, bomber_pos,reward,reward,0)

        open_list.append(initial_node)

        actions = [(1,0), (0,1), (-1,0), (0,-1), (0,0)]

        best_node = initial_node

        current_node = initial_node

        while open_list:
            current_node = open_list.pop(0)

            if current_node.depth <= 7:   
                for a in actions:
                    next_bomber_pos = (current_node.position[0] + a[0], current_node.position[1] + a[1])

                    if current_node.in_parent(next_bomber_pos):
                        continue
                    
                    reward = game_map[next_bomber_pos[1]][next_bomber_pos[0]]
                    if reward == Reinforcement.Indestructive_Wall or reward < -15:
                        continue

                    tot_reward = reward+current_node.total_reward
                    if tot_reward < -30:
                        continue

                    next_node = SearchNode(current_node, next_bomber_pos, reward, reward+current_node.total_reward, current_node.depth+1)

                    if best_node.reward < next_node.reward:
                        best_node = next_node
                    elif best_node.reward == next_node.reward and best_node.depth > next_node.depth:
                        best_node = next_node

                    # elif best_node.total_reward < next_node.total_reward:
                        # best_node = next_node
                    # if initial_node.reward > -0.1:
                    # else:
                        # if best_node.total_reward < next_node.total_reward:
                            # best_node = next_node
                        # elif next_node.total_reward > 0:
                            # best_node = next_node

                    # elif inital_node_reward < reward:
                    #     print("Where to place?")
                    #     solution_node = next_node
                    #     break

                        # if best_node == None:
                            # best_node = next_node
                        # elif next_node.total_reward > best_node.total_reward:
                            # best_node = next_node

                    open_list.append(next_node)

            # if best_node.position != initial_node.position:
                # break
            # if next_node.depth >= 2 and game_map[bomber_pos[1]][bomber_pos[0]] > 0:
            # if next_node.depth > 3 and best_node != None:
                # solution_node = best_node

        # if not best_node or best_node.total_reward < 0:
            open_list = sorted(open_list, key=lambda x: -x.depth)

        if best_node.depth == 0:
            if open_list:
                best_node = sorted(open_list, key=lambda x: (-x.total_reward))[0]
            elif not open_list:
                best_node = SearchNode(best_node, best_node.position, best_node.reward, best_node.total_reward, 1)

        # print(f"Best Node: {best_node}")
        
        print(f"--- Ended Searching")

        return AgentAI.get_path(best_node)

    
def calculate_coordinates(distance):
    coordinates = []

    for x in range(-distance, distance + 1):
        for y in range(-distance, distance + 1):
            if abs(x) + abs(y) <= distance:
                coordinates.append((x, y))

    return coordinates
