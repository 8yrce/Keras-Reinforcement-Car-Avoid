#Setup for the car_avoid program set

# import the pygame module, so you can use it
import pygame
import random
import argparse


#Setting up arg parser
parser = argparse.ArgumentParser()
parser.add_argument("--interactive", action="store_true", help="Interactive mode", required = False)
args = parser.parse_args()


"""
Env stuff we need for it to work without issue with existing openai code

- step(action) - moves the sim forward using the action input
- reset - resets the sim
- render - starts the sim and displays
- sample - provides a sample valid rando input action 

"""

WIDTH = 1080
HEIGHT = 720

START_X = WIDTH/2
START_Y = HEIGHT-100

GOAL_INCREMENT = 10
GOAL = START_X - GOAL_INCREMENT
LAST_REWARD_X = 0
LAST_REWARD_Y = 0

START_REWARD = 100
reward = START_REWARD

obstacle_pic_1 = pygame.image.load("obstacle.jpg")

#Car object 
class Car():
    def __init__(self, X=START_X, Y=START_Y):
        self.x = X
        self.y = Y
        self.speed = 5
        self.fast_speed = 10
        self.can_move_left = 1
        self.can_move_right = 1

    def set_x(self,X):
        self.x = X

    def set_y(self,Y):
        self.y = Y

    def set_speed(self,S):
        self.speed = S

    def get_x(self):
        return int(self.x)

    def get_y(self):
        return int(self.y) 

    def get_speed(self):
        return int(self.speed) 

    def get_fast_speed(self):
        return int(self.fast_speed)

#init some objects
car = Car()

#obstacle object
class Obstacle(object):
    def __init__(self, X=0, Y=0):
        self.x = X
        self.y = Y
        self.speed = 10

    def set_x(self,X):
        self.x = X

    def set_y(self,Y):
        self.y = Y

    def set_speed(self,S):
        self.speed = S

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_speed(self):
        return self.speed 

#init some objects
obstacle_1 = Obstacle()
obstacles = [obstacle_1]

"""
#Screen
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
car_pic = pygame.image.load("car.png")
background = pygame.image.load("avoid_track.jpg")
obstacle_pic_1 = pygame.image.load("obstacle.jpg")
"""

def reset(background, car_pic, SCREEN):
    SCREEN.blit(background, (0,0))
    SCREEN.blit(car_pic, ((START_X),(START_Y)))
    #obstacle is reset off screen by the blitting of the background and not the obstacle
    obstacle_1.x = 0
    obstacle_1.y = HEIGHT

    car.set_x(START_X)
    car.set_y(START_Y)
    car.can_move_left = 1
    car.can_move_right = 1
    
    pygame.display.flip()
    
    global GOAL
    GOAL = START_X - GOAL_INCREMENT
    
    global LAST_REWARD_Y
    global LAST_REWARD_X
    LAST_REWARD_Y = 0
    LAST_REWARD_X = 0

    #Return everything that would normally be in our observation
    return [1,0,0,1,1,0,0] # aka reward 1 and y collision 0 / x_collision 0, obj.x, obj.y, car.x, car.y
  

#Returns sample action for agent ( LF/L/R/RF )
def sample():
    a = random.randrange(0,4)
    #print(a)
    #sample = [0,0,0,0]
    #sample[a] = 1
    return a

#    Can be called from the ai side to 'step' the sim forward with x action
#    PARAMS: action, a set a values for what the agent should do ( 0,0,1 )
def step(action, display, SCREEN, car_pic, car, background, easy_mode):
    return(ai_play(action, display, SCREEN, car_pic, car, background, easy_mode))

#Car movement
"""
def move_up(car):
    if(car.y-1 > 0 ):
        car.y = car.y - 2

def move_down(car):
    if(car.y+1 < HEIGHT ):
        car.y = car.y + 2
"""

def move_left(car, fast):
    x = int(car.get_x())

    if fast:
        speed = car.get_fast_speed()
    else:
        speed = car.get_speed()

    if(x-2 > 0 ) and car.can_move_left == 1:
        car.can_move_right = 1  # if move left, we can now right again
        car.set_x(x-car.get_speed())
    else:
        car.can_move_left = 0   # if at edge, no more left until we get off the edge

def move_right(car, fast):
    x = int(car.get_x())
    
    if fast:
        speed = car.get_fast_speed()
    else:
        speed = car.get_speed()


    if(x+2 < WIDTH - 95 ) and car.can_move_right == 1:
        car.can_move_left = 1   # if move right, we can now move left again
        car.set_x(x+speed)
    else:
        car.can_move_right = 0  #if at right edge, dont let it go right
        
def update_display(screen, background, car_pic, car, obstacle_1):
    #screen.fill((0,0,0))
    screen.blit(background, (0,0))
    screen.blit(car_pic, ((car.get_x()),(car.get_y())))
    if obstacle_1.get_x() != -1:
        screen.blit(obstacle_pic_1, (obstacle_1.get_x(), obstacle_1.get_y()) )
    pygame.display.flip()

#Check and see if any part of our box is touching part of the map that is not safe color
def check_boundary(car, screen, obstacles):
    d = 0
    y_collision = 0
    x_collision = 0
    for o in obstacles:
        bx = o.get_x()
        by = o.get_y()
        bx270 = bx + 270
        by180 = by + 180
        cx = car.get_x()
        cy = car.get_y()
        cx95 = cx+95
        cy30 = cy+30

        #Check x for collision
        # range for where box is, range for where agent is ( 100 - 200 || 70 - 110 )
        # current issue, no handling for if the val + size is within range
        #if bx > cx and bx < cx95 or cx > bx and cx < bx270:
        if cx95 < bx or bx270 < cx:
            y_collision = 0
        else:
            y_collision = 1
            #print("Y collision: bx:{} cx:{} cx95:{}   cx:{} bx:{} bx270:{} ".format(bx,cx,cx95,cx,bx,bx270) )
            #check y for collision
            if cy30 > by180 and cy < by180 or by180 > cy30 and by < cy30:
                x_collision = 1
                #print("X collision")
                d = 1
                break
    return d, y_collision, x_collision

    #Check and see if any part of our agent has touched a reward
# Ok so new reward structure, reward for hitting the checkpoints instead of how long to hit them
def check_reward(d, y_collision, x_collision, car):
    r = 0
    if d == 0 and y_collision == 0:
        r += 1
    
    elif y_collision != 0 and d == 0 or x_collision != 0 and d == 0:
        r -= 1

    else:
        r += 0

    return r
    
#Creates and manages the obstacles every time we step
def obstacle_manager(obstacles, car, easy_mode):
    r_obstacles = []
    for o in obstacles:   
        if o.get_y() < HEIGHT - o.speed:
            o.set_y(o.get_y()+ o.speed)

        elif easy_mode:
            o.set_x(car.get_x()- (135-47.5) ) # this makes sure it puts it in the middle so each dir has an equal chance of being picked
            o.set_y(0)

        else:
            #o.set_x( random.randrange(0,WIDTH) - 135 ) 
            o.set_x( car.get_x() - (random.randrange(0,350)) ) # attempt at making it random while still following player
            o.set_y(0)
        r_obstacles.append(o)
    #print("X:Y",obstacle_1.get_x(), obstacle_1.get_y())
    return r_obstacles

def ai_play(action, display, SCREEN, car_pic, car, background, easy_mode):
    #apply to env, spit back observation, reward, done, info
    global GOAL

    """
        Movement handler
    """
    #left fast, left, right, fast right
    if action == 0:
        move_left(car,True)
        #print("left")

    elif action == 1:
        move_left(car, False)
        #print("left fast")

    elif action == 2:
        move_right(car, False)
        #print("right")

    elif action == 3:
        move_right(car, True)
        #print("right fast")


    """
        Obstacle handler
    """
    global obstacles
    obstacles = obstacle_manager(obstacles, car, easy_mode)



    """
        Display handler
    """
    if display:
        update_display(SCREEN, background, car_pic, car, obstacle_1)
    


    """
        Collision / Reward handler
    """
    d, y_collision, x_collision = check_boundary(car, SCREEN, obstacles)
    reward = check_reward(d, y_collision, x_collision, car)

    if d == 1:  # if we are dead ( aka hit detected )
        reward = -300
    

    """
        Return stuff
    """    
    i = 0 #dont know what these two really do 
    o = [reward, y_collision, x_collision, obstacles[0].get_x(), obstacles[0].get_x()+270, car.get_x(), car.get_x()+95]  # add in info about upcomong pxls here ( DONE ), add if can move left / right bool
    return o,reward,d,i

def init():
    # initialize the pygame module
    pygame.init()
    pygame.display.set_caption("minimal program")
     # create a surface on screen
    SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))

    #Screen
    car_pic = pygame.image.load("car.png")
    background = pygame.image.load("avoid_track.jpg")
    
    
    # define a variable to control the main loop
    running = True
    
    global car    

    return pygame, SCREEN, car_pic, background, running, car

# define a main function
def main():
     
    pygame, screen, car_pic, background, running, car = init()

    update_display(screen, background, car_pic, car)

    # main loop
    while running:
        
        #Check control type
        
        if args.interactive: #aka we are playing the game in interactive mode
            #Check key holds 
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                move_left(car)
                update_display(screen, background, car_pic, car)
                #Check boundaries
                check_boundary(car,screen)

            if keys[pygame.K_RIGHT]:
                move_right(car)
                update_display(screen, background, car_pic, car)
                #Check boundaries
                check_boundary(car,screen)

            if keys[pygame.K_UP]:
                move_up(car)
                update_display(screen, background, car_pic, car)
                #Check boundaries
                check_boundary(car,screen)
            
            if keys[pygame.K_DOWN]:
                move_down(car)
                update_display(screen, background, car_pic, car)
                #Check boundaries
                check_boundary(car,screen)


        # event handling, gets all event from the event queue
        for event in pygame.event.get():

            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
     
     
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
#if __name__=="__main__":
    # call the main function
 #   main()
 #Checking for interactive mode
if args.interactive:
    main()