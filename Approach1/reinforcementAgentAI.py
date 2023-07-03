import math
import random
import time

from reinforcementSearchNode import SearchNode
from reinforcementConsts import Area, Reinforcement
from reinforcementUtils import *

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
    def array_to_empty_map(in_map, bomberman):
        for i in range(0, len(in_map)):
            for j in range(0, len(in_map[0])):
                if i == 0 or i == len(in_map) - 1 or j == 0 or j == len(in_map[0]) - 1:
                    in_map[i][j] = Reinforcement.Indestructive_Wall
                elif i % 2 == 0 and j % 2 == 0:
                    in_map[i][j] = Reinforcement.Indestructive_Wall
                else:
                    in_map[i][j] = Reinforcement.Step
        
        in_map[bomberman[1]][bomberman[0]] = Reinforcement.Player if in_map[bomberman[1]][bomberman[0]] != Reinforcement.Indestructive_Wall else in_map[bomberman[1]][bomberman[0]]

    # Function that fills a game map array with the walls, given their coordinates
    @staticmethod
    def fill_empty_map_with_walls(in_map, walls, exit):

        positions = [(1,0),(-1,0),(0,1),(0,-1)]
        for wall in walls:
            for pos in positions:
                if len(in_map) > wall[1]+pos[0] \
                    and len(in_map[wall[1]+pos[0]]) > wall[0]+pos[1] \
                    and in_map[wall[1]+pos[0]][wall[0]+pos[1]] == Reinforcement.Step:
                        in_map[wall[1]+pos[0]][wall[0]+pos[1]] = Reinforcement.Destructive_Wall if not exit else Reinforcement.Destructive_Wall_Exit

            in_map[wall[1]][wall[0]] = Reinforcement.Indestructive_Wall
            
    @staticmethod
    def get_enemy_directions(enemies, prev_enemies, prev_dir, in_map):

        prev_directions = {}
        for enemy in enemies:
            prev_enemy = None

            for en in prev_enemies:
                if en["id"] == enemy["id"]:
                    prev_enemy = en
            if not prev_enemy:
                continue

            # Obtain the difference between the current and previous position
            difference = (enemy["pos"][0] - prev_enemy["pos"][0], enemy["pos"][1] - prev_enemy["pos"][1])

            if enemy["id"] in prev_dir.keys():
                prev_directions[enemy["id"]] = difference if difference != (0,0) else prev_dir[enemy["id"]]
            else:
                prev_directions[enemy["id"]] = difference

            pos = [enemy["pos"][0] + prev_directions[enemy["id"]][0], enemy["pos"][1] + prev_directions[enemy["id"]][1]]
            if check_if_valid_position(in_map, pos) and in_map[pos[1]][pos[0]] in [Reinforcement.Destructive_Wall, Reinforcement.Destructive_Wall_Exit, Reinforcement.Indestructive_Wall]:
                prev_directions[enemy["id"]] = (0,0)

        return prev_directions

    # Function that fills a game map array with the enemies, given their coordinates
    @staticmethod
    def fill_empty_map_with_enemies(in_map, enemies, enemy_directions):

        radius = 7
        for enemy in enemies:
            enemy_position = enemy["pos"]
            in_map[enemy_position[1]][enemy_position[0]] = Reinforcement.Enemy_Position

            for position in Area.Range_Two.value:
                pos = (enemy_position[0] + position[1], enemy_position[1] + position[0])

                if check_if_valid_move(in_map, pos):
                    in_map[pos[1]][pos[0]] = Reinforcement.Enemy_Position

            if enemy["id"] in enemy_directions:
                directions = [enemy_directions[enemy["id"]]]

                if directions[0] == (0,0):
                    directions = Area.Range_One.value

                for direction in directions:
                    next_position = (enemy_position[0] + direction[0], enemy_position[1] + direction[1])

                    if next_position == enemy_position:
                        continue

                    if check_if_valid_move(in_map, next_position):
                        in_map[next_position[1]][next_position[0]] = Reinforcement.Enemy_Position

                    bomb_pos = []
                    for i in range(2, 2+3):
                        bomb_position = (enemy_position[0] + i*direction[0], enemy_position[1] + i*direction[1])

                        if check_if_valid_move(in_map, bomb_position):
                            in_map[bomb_position[1]][bomb_position[0]] = Reinforcement.Enemy_Bomb
                            bomb_pos.append(bomb_position)

                    for bomb_position in bomb_pos:
                        max_row = radius*2 + 1
                        pos_row = [bomb_position[1]-radius, bomb_position[0]-radius]

                        for i in range(max_row):
                            for j in range(max_row):
                                pos = [pos_row[1]+j, pos_row[0]+i]
                                if check_if_not_indestructible_wall(in_map, pos) and check_if_not_enemy(in_map, pos) and check_if_not_destructible_wall(in_map, pos):
                                    dif = abs(pos[1]-bomb_position[1]) + abs(pos[0]-bomb_position[0])
                                    if dif <= radius + 1:
                                        in_map[pos[1]][pos[0]] += radius - dif + 1

    # Function that fills a game map array with the bombs, given their coordinates and radius
    @staticmethod
    def fill_empty_map_with_bombs(in_map, bombs):
        
        sides = [(0,1),(0,-1),(1,0),(-1,0)]
        for bomb in bombs:
            pos = bomb[0]
            radius = bomb[2]

            if in_map[pos[1]][pos[0]] != Reinforcement.Indestructive_Wall:
                in_map[pos[1]][pos[0]] = Reinforcement.Bomb_Drop_Position

            for side in sides:
                for rad in range(1, radius+1):
                    if len(in_map) > pos[1]+side[1]*rad \
                        and len(in_map[pos[1]+side[1]*rad]) > pos[0]+side[0]*rad \
                        and in_map[pos[1]+side[1]*rad][pos[0]+side[0]*rad] != Reinforcement.Indestructive_Wall:
                        in_map[pos[1]+side[1]*rad][pos[0]+side[0]*rad] = Reinforcement.Bomb_Damage*(1/rad)

    # Function that fills a game map array with the powerup, given their coordinates
    @staticmethod
    def fill_empty_map_with_powerups(in_map, powerups):
        
        if powerups:
            if powerups[0][1] in ["Detonator", "Wallpass", "Bombpass"]:
                in_map[powerups[0][0][1]][powerups[0][0][0]] = -100
            else:
                in_map[powerups[0][0][1]][powerups[0][0][0]] = Reinforcement.Powerup

    # Function that fills a game map array with the exit, given their coordinates if there are not enemies
    @staticmethod
    def fill_empty_map_with_exit(in_map, exit, enemies, bomberman):
        
        not_good_places = [Reinforcement.Indestructive_Wall, Reinforcement.Destructive_Wall, Reinforcement.Destructive_Wall_Exit, Reinforcement.Exit, Reinforcement.Player]
        if exit and not enemies:
            in_map[exit[1]][exit[0]] = Reinforcement.Exit
            in_map[bomberman[1]][bomberman[0]] = Reinforcement.Player

            for i in range(len(in_map)):
                for j in range(len(in_map[i])):
                    # count = 0
                    # for direction in Area.Range_One.value:
                    #     if not check_if_valid_position(in_map, [direction[0]+j, direction[1]+i]) or in_map[direction[1]+i][direction[0]+j] in not_good_places:
                    #         count += 1
                    # if count >= 3:
                    #     in_map[i][j] = -100 if in_map[i][j] not in [Reinforcement.Exit, Reinforcement.Player] else in_map[i][j]
                    # else:
                        dif = [abs(exit[1] - i), abs(exit[0] - j)]
                        if Reinforcement.Exit - sum(dif) > 0 and in_map[i][j] not in not_good_places:
                            in_map[i][j] = Reinforcement.Exit - sum(dif)

    # Function to get node successors      
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
        now = time.time()

        open_list = []
        closed_list = []

        current_node = SearchNode(None, bomber_pos)
        open_list.append(current_node)

        actions = [(1,0), (0,1), (-1,0), (0,-1), (0,0)]
        solution_node = None

        while open_list and current_node.depth < 16:

            current_node = open_list[0]
            open_list.remove(current_node)
            closed_list.append(current_node)

            if current_node.reward > 0:
                solution_node = current_node
                break

            for a in actions:
                next_bomber_pos = [current_node.position[0] + a[0], current_node.position[1] + a[1]]

                if current_node.in_parent(next_bomber_pos):
                    continue
                
                if not check_if_valid_position(game_map, next_bomber_pos):
                    continue

                reward = game_map[next_bomber_pos[1]][next_bomber_pos[0]]

                if reward == Reinforcement.Indestructive_Wall or reward == Reinforcement.Enemy_Position:
                    continue

                tot_reward = reward+current_node.total_reward
                if tot_reward < -20:
                    continue

                skip = False
                remove = []
                for x in closed_list:
                    if next_bomber_pos == x.position:
                        if tot_reward <= x.total_reward: 
                            skip = True
                            break
                        else:
                            remove.append(x)
                if skip:
                    continue

                for x in remove:
                    closed_list.remove(x)

                next_node = SearchNode(current_node, next_bomber_pos, reward, tot_reward, current_node.depth+1)

                open_list.append(next_node)

            open_list = sorted(open_list, key=lambda x: x.total_reward, reverse=True)

        if not solution_node:
            if open_list:
                solution_node = sorted(open_list, key=lambda x: x.total_reward, reverse=True)[0]
            else:
                solution_node = SearchNode(SearchNode(None, bomber_pos), bomber_pos, 0, 0, 1)
        
        # print(f"--- Search: {time.time()-now}")

        return AgentAI.get_path(solution_node) # if solution_node else AgentAI.get_path(sorted(open_list, key=lambda x: x.total_reward, reverse=True)[0])
