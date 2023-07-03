class SearchNode:

    def __init__(self,parent=None,position=None,reward=0,total_reward=0,depth=0):
        self.parent = parent
        self.position = position
        
        self.depth = depth
        self.reward = reward
        self.total_reward = round(total_reward, 3)
    
    def in_parent(self, position):
        if self.parent is None:
            return False
        return True if self.position==position else self.parent.in_parent(position)

    def __str__(self) -> str:
        return self.parent.__str__() + "\n" + "\t"*self.depth + f"Node:[ Position: {self.position}; Reward: {self.reward}; Total Reward: {self.total_reward} ]"