from reinforcementSearchNode import SearchNode
from reinforcementConsts import Reinforcement, Area, Speed

from reinforcementUtils import check_if_not_indestructible_wall, check_if_bomb_target, check_in_map

PROPAGATE_RANGE = 20


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

                # If the position is on the edge of the map, it is a wall
                if i == 0 or i == len(in_map) - 1 or j == 0 or j == len(in_map[0]) - 1:
                    in_map[i][j] = Reinforcement.Indestructible_Wall

                # If the position is even (x, y), it is a wall
                elif i % 2 == 0 and j % 2 == 0:
                    in_map[i][j] = Reinforcement.Indestructible_Wall

                # Otherwise, it is path (valid move)
                else:
                    in_map[i][j] = Reinforcement.Valid_Move

    # Function that fills a game map array with destructive walls, given their coordinates
    @staticmethod
    def fill_empty_map_with_walls(in_map, walls, bombs, no_reward):

        # All possible relative positions around a destructible wall
        area = Area.Range_One.value

        for wall in walls:

            # Update the map with the destructible wall
            in_map[wall[1]][wall[0]] = Reinforcement.Indestructible_Wall

            # If we don't need to destroy more walls,
            # We don't need to update the area around the destructible wall
            if no_reward:
                continue

            # Check if wall will be destroyed by a bomb
            if check_if_bomb_target(in_map, wall, bombs):
                continue

            # Update area around the destructible wall
            for positions in area:

                # Initialize decay factor
                decay_factor = 1

                for current_range in range(1, PROPAGATE_RANGE):

                    # Obtain possible position
                    pos = (wall[0] + positions[0] * current_range, wall[1] + positions[1] * current_range)

                    # If the position is within the map, and it is a valid move
                    if check_if_not_indestructible_wall(in_map, pos):

                        # Update the map with the destructible wall area (the closer, the higher the reward!)
                        in_map[pos[1]][pos[0]] += (Reinforcement.Reward / current_range ** 2) / decay_factor

                    else:

                        # Update the decay factor
                        decay_factor += 1

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

    # Function that fills a game map array with the enemies, given their coordinates
    @staticmethod
    def fill_empty_map_with_enemies(in_map, enemies, enemy_directions, bomb_radius, bomb_timeout=4):

        for enemy in enemies:

            # Obtain enemy position
            enemy_position = enemy["pos"]

            # Obtain enemy name
            enemy_name = enemy["name"]

            speed = Speed.SLOWEST.value
            wall_pass = False

            # Obtain enemy speed and wall pass
            if enemy_name == "Balloom":
                speed = Speed.SLOW.value
                wall_pass = False
            elif enemy_name == "Oneal":
                speed = Speed.SLOWEST.value
                wall_pass = False
            elif enemy_name == "Doll":
                speed = Speed.NORMAL.value
                wall_pass = False
            elif enemy_name == "Minvo":
                speed = Speed.FAST.value
                wall_pass = False
            elif enemy_name == "Kondoria":
                speed = Speed.SLOWEST.value
                wall_pass = True
            elif enemy_name == "Ovapi":
                speed = Speed.SLOW.value
                wall_pass = True
            elif enemy_name == "Pass":
                speed = Speed.FAST.value
                wall_pass = False

            # Update the map with the enemy position
            in_map[enemy_position[1]][enemy_position[0]] += Reinforcement.Damage

            # If the enemy is moving
            if enemy["id"] in enemy_directions and enemy_directions[enemy["id"]] != (0, 0):

                # Obtain enemy direction
                direction = enemy_directions[enemy["id"]]

                # Obtain opposite direction
                opposite_direction = (-direction[0], -direction[1])

                # Obtain target range
                target_range = bomb_radius + bomb_timeout

                # Consider the enemy speed
                for current_range in range(1, speed + 1):

                    # Obtain next position (in the direction of the enemy)
                    next_position = (enemy_position[0] + direction[0] * current_range,
                                     enemy_position[1] + direction[1] * current_range)

                    # If the position is within the map, and it is a valid move
                    if check_if_not_indestructible_wall(in_map, next_position):

                        # Update the map with the enemy damage
                        in_map[next_position[1]][next_position[0]] += Reinforcement.Damage

                    # If the position is an indestructible wall, don't check further in that direction
                    elif not wall_pass:
                        break

                for current_range in range(speed + 1, speed + 1 + target_range):

                    # Obtain bomb position (in the direction of the enemy)
                    bomb_position = (enemy_position[0] + direction[0] * current_range,
                                     enemy_position[1] + direction[1] * current_range)

                    # If the position is within the map, and it isn't an indestructible wall
                    if check_if_not_indestructible_wall(in_map, bomb_position):

                        # If it has a reward greater than Valid_Move
                        if in_map[bomb_position[1]][bomb_position[0]] >= Reinforcement.Valid_Move:
                            # Update the map with the enemy reward
                            in_map[bomb_position[1]][bomb_position[0]] += Reinforcement.Reward / (current_range - speed)

                    # If the position is an indestructible wall, don't check further in that direction
                    elif not wall_pass:

                        # Obtain bomb position (in the direction of the enemy)
                        bomb_position = (enemy_position[0] + direction[0] * current_range + 1,
                                         enemy_position[1] + direction[1] * current_range + 1)

                        # If the position is within the map, and it isn't an indestructible wall
                        if check_if_not_indestructible_wall(in_map, bomb_position):

                            # If it has a reward greater than Valid_Move
                            if in_map[bomb_position[1]][bomb_position[0]] >= Reinforcement.Valid_Move:
                                # Update the map with the enemy reward
                                in_map[bomb_position[1]][bomb_position[0]] += Reinforcement.Reward / (
                                            current_range - speed)

                        # Don't check further in that direction
                        break

                for current_range in range(speed + 1 + target_range, PROPAGATE_RANGE):

                    # Obtain bomb position
                    bomb_position = (enemy_position[0] + direction[0] * current_range,
                                     enemy_position[1] + direction[1] * current_range)
                    
                    # If the position is within the map, and it isn't an indestructible wall
                    if check_if_not_indestructible_wall(in_map, bomb_position):
                        in_map[bomb_position[1]][bomb_position[0]] += 0.5 / (current_range - speed)

                    # Update the map with slight enemy reward
                    for position in Area.Range_One.value:

                        if position != direction and position != opposite_direction:

                            for other_range in range(1, PROPAGATE_RANGE):

                                # Obtain possible position
                                pos = (bomb_position[0] + position[0] * other_range,
                                       bomb_position[1] + position[1] * other_range)

                                # If the position is within the map, and it isn't an indestructible wall
                                if check_if_not_indestructible_wall(in_map, pos):
                                    in_map[pos[1]][pos[0]] += 0.5 / other_range

                for current_range in range(speed + 1 + target_range, PROPAGATE_RANGE):

                    # Obtain bomb position
                    pos = (enemy_position[0] + opposite_direction[0] * current_range,
                           enemy_position[1] + opposite_direction[1] * current_range)

                    # Update the map with slight enemy reward
                    if check_if_not_indestructible_wall(in_map, pos):
                        in_map[pos[1]][pos[0]] += 0.08 / current_range

            # If we don't have information about the enemy direction / If the enemy is not moving
            else:

                for position in Area.Range_One.value:

                    # Consider the enemy speed
                    for current_range in range(1, speed + 1):

                        # Obtain possible position
                        pos = (enemy_position[0] + position[0] * current_range,
                               enemy_position[1] + position[1] * current_range)

                        if check_if_not_indestructible_wall(in_map, pos):
                            in_map[pos[1]][pos[0]] += Reinforcement.Damage

    # Function that fills a game map array with the bombs, given their coordinates and radius
    @staticmethod
    def fill_empty_map_with_bombs(in_map, bombs, consider_safety=True):

        # All possible relative positions around a bomb
        area = Area.Range_One.value

        for bomb in bombs:

            # Obtain bomb position
            bomb_position = bomb[0]

            # Obtain bomb countdown
            bomb_countdown = bomb[1]

            # Obtain bomb radius
            bomb_radius = bomb[2]

            # Update the map with the bomb
            in_map[bomb_position[1]][bomb_position[0]] = Reinforcement.Damage

            # Update area around the bomb
            for position in area:

                for current_range in range(1, bomb_radius + 1):

                    # Obtain possible position
                    pos = (bomb_position[0] + position[0] * current_range,
                           bomb_position[1] + position[1] * current_range)

                    # If the position is within the map, and it isn't an indestructible wall
                    if check_if_not_indestructible_wall(in_map, pos):
                        # Update the map with the bomb damage
                        # The closer the position is to the bomb, the worst the reward
                        in_map[pos[1]][pos[0]] = (4 / bomb_countdown) * Reinforcement.Damage / (current_range + 1)

                    # If we want to consider safe positions
                    if consider_safety:

                        for i in area:

                            # Obtain possible safe position
                            safe_pos = (pos[0] + i[0], pos[1] + i[1])

                            # If the position is within the map, and it isn't an indestructible wall
                            if check_if_not_indestructible_wall(in_map, safe_pos) \
                                    and in_map[safe_pos[1]][safe_pos[0]] >= Reinforcement.Valid_Move:
                                # Update the map with safe position
                                in_map[safe_pos[1]][safe_pos[0]] += Reinforcement.Reward / 2

    # Function that fills a game map array with the exit, given its coordinates
    @staticmethod
    def fill_empty_map_with_exit(in_map, exit_door):

        for i in range(0, len(in_map)):
            for j in range(0, len(in_map[0])):

                # Obtain distance to exit
                distance = (abs(exit_door[0] - j) + abs(exit_door[1] - i))

                if distance == 0:
                    in_map[i][j] = Reinforcement.Exit

                else:

                    # Check if the position is within the map, and it is a valid move
                    if check_if_not_indestructible_wall(in_map, (j, i)):
                        # Update the map with the exit
                        # in_map[i][j] = Reinforcement.Exit - distance

                        # Update the map with the exit
                        in_map[i][j] = Reinforcement.Exit / (distance + 1)

    # Function that fills a game map array with powerups, given their coordinates
    @staticmethod
    def fill_empty_map_with_powerups(in_map, powerups):

        # Update the map with the powerups
        for powerup in powerups:

            # print("Powerup:", powerup)
            # Avoid Flames powerup
            if powerup[1] == 'Flames':
                in_map[powerup[0][1]][powerup[0][0]] = Reinforcement.Indestructible_Wall
            else:
                in_map[powerup[0][1]][powerup[0][0]] += Reinforcement.Powerup

    # Function that fills a game map array with the player, given its coordinates
    @staticmethod
    def fill_empty_map_with_player(in_map, player):

        in_map[player[1]][player[0]] += Reinforcement.Player

    # Function that cleans a map to update walls and enemies
    @staticmethod
    def clear_map(in_map):
        for i in range(0, len(in_map)):
            for j in range(0, len(in_map[i])):

                # If the positions isn't an indestructible wall
                if check_if_not_indestructible_wall(in_map, (j, i)):
                    in_map[i][j] = Reinforcement.Valid_Move

    @staticmethod
    def get_path(node):
        if node.parent is None:
            return [node]
        path = AgentAI.get_path(node.parent)
        path += [node]
        return path

    # Function based off map
    @staticmethod
    def reinforcement_pathing(bomber_pos, prev_bomber_pos, game_map, n_enemies, finished_level):

        # print("---------------------------------------------- Started Searching")

        # List of open and closed nodes
        open_list = []
        closed_list = []

        # Start current node
        current_node = SearchNode(None, bomber_pos)

        # Add the starting node to the open list
        open_list.append(current_node)

        # Possible actions (don't move, move up, down, left, right)
        actions = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]

        # Initialize best reward
        best_reward = None

        # Initialize found ideal reward
        found_ideal_reward = False

        # Initialize improved
        improved = False

        # Initialize max depth
        # max_depth = 3 if finished_level else 15 - n_enemies
        max_depth = 3 if finished_level else 12

        # While there are nodes to explore (must be close enough to the bomberman)
        while open_list and not found_ideal_reward:

            # Obtain current node
            current_node = open_list.pop(0)

            # If the current node is too far away
            if current_node.depth > max_depth:
                continue

            # Update closed list
            closed_list.append(current_node)

            for a in actions:

                # Obtain the next position
                next_position = [current_node.position[0] + a[0], current_node.position[1] + a[1]]

                # If the next position is out of the map
                if not check_in_map(game_map, next_position):
                    continue

                # Avoid going to parent nodes (i.e. avoid going back)
                if current_node.in_parent(next_position):
                    continue

                # Obtain the reward of the next position
                reward = game_map[next_position[1]][next_position[0]]

                # If the reward isn't a valid move
                if reward == Reinforcement.Indestructible_Wall:
                    continue

                if finished_level:

                    # If the reward is the exit
                    if reward >= Reinforcement.Exit:
                        # Obtain the current total reward
                        total_reward = current_node.total_reward + reward

                        # Update the best reward
                        best_reward = SearchNode(current_node, next_position, reward, total_reward,
                                                 current_node.depth + 1)

                        found_ideal_reward = True
                        break

                # If the reward decreases the total reward
                if current_node.total_reward > 0 > reward:
                    continue

                # If the action is to not move and the reward isn't ideal
                if a == (0, 0) and reward < Reinforcement.Reward - 2:
                    reward += Reinforcement.Player

                # If the action is to move to the previous position and the reward isn't ideal
                if a != (0, 0) and next_position == prev_bomber_pos:
                    reward += Reinforcement.Player * (7 - prev_bomber_pos.index(next_position))

                # Obtain the current total reward
                total_reward = current_node.total_reward + reward

                # Skip if the node is already in the closed list and the current total reward is worse
                skip = False
                for x in closed_list:
                    if next_position == x.position:
                        if total_reward < x.total_reward:
                            skip = True
                            break
                if skip:
                    continue

                # If the reward is a valid move
                next_node = SearchNode(current_node, next_position, reward, total_reward,
                                       current_node.depth + 1)

                if not finished_level:

                    # Avoid going to negative rewards positions when the depth is greater than 5
                    if next_node.depth > 5 and (reward < Reinforcement.Valid_Move or total_reward < -5):
                        continue

                    # If found a destructible wall, enemy reward or exit
                    if (total_reward > 0 and reward >= Reinforcement.Reward - 2 and next_node.depth <= 2) or \
                            (total_reward >= Reinforcement.Reward + 10):
                        found_ideal_reward = True

                # Check if improved reward
                if best_reward:
                    improved = total_reward > best_reward.total_reward or \
                               (total_reward == best_reward.total_reward and next_node.depth <= best_reward.depth)

                # If the reward is better than the current best reward
                if not best_reward or improved or found_ideal_reward:

                    # Update best reward
                    best_reward = next_node
                    # print("Best reward: " + str(best_reward.total_reward) + " at depth " + str(best_reward.depth) +
                    #       " with position " + str(best_reward.position))

                    # Stop searching if found an ideal reward
                    if found_ideal_reward:
                        break

                # Add the next node to the open list
                open_list.append(next_node)

            # Sort the open list by total reward (greedy)
            # open_list = sorted(open_list, key=lambda x: x.total_reward, reverse=True)

            # Sort the open list by depth (breadth first)
            open_list = sorted(open_list, key=lambda x: x.depth, reverse=False)

        # print("---------------------------------------------- Finished Searching")

        # print("Bomberman position: " + str(bomber_pos))

        return AgentAI.get_path(best_reward)
