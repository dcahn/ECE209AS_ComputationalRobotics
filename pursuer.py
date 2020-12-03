from map import Map
import random

class Pursuer:
    def __init__(self, x, y, Map):
        self.x = x
        self.y = y
        self.map = Map

    # decode action
    def move(self, a):
        if a == 1:
            return -1, 0    # left
        elif a == 2:
            return 1, 0     # right
        elif a == 3:
            return 0, -1    # down
        elif a == 4:
            return 0, 1     # up
            
        return 0, 0         # invalid action

    # action
    def action(self, a):
        dx, dy = self.move(a)
        if (self.map.get_tile(self.x + dx, self.y + dy) == '.'):
            self.x += dx
            self.y += dy

    # policy (random action for now)
    def policy(self):
        return random.randint(1,4)
    
    # return postion of the pursuer
    def getPos(self):
        return self.x, self.y

    # print current position
    def print(self):
        print(self.x, self.y)

    # for debugging
    def mprint(self):
        print(self.map)
    




if __name__ == "__main__":

    # initial empty map with standard ghost house
    map = Map(31,16,"""
		||||||||||||||||
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|.........||||||
		|.........||||||
		|.........||||||
		|.........||||||
		|.........||||||
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		|...............
		||||||||||||||||
		""")
    
    # initial pursure
    p1 = Pursuer(5,5,map)

    # action test
    while True:
        p1.mprint()
        a = input("Enter action: ")
        p1.action(int(a))
        p1.print()
        
