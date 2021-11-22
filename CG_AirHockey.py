import random
import tkinter as tk


RED, BLACK, WHITE, DARK_RED, BLUE = "red", "black", "white", "dark red", "blue"
ZERO = 2 #for boundary lines.
LOWER, UPPER = "lower", "upper"
Player1, Player2 = "Top", "Bottom"

START_SCORE = {Player1: 0, Player2: 0}
MAX_SCORE = 5 #Winning score.
SPEED = 20 #milliseconds between frame update.
FONT = "ms 50"
MAX_SPEED, PADDLE_SPEED = 15, 15


def str_dict(dic):
    return (Player1, dic[Player1], Player2, dic[Player2])
    
def rand():
    return random.choice(((1, 1), (1, -1), (-1, 1), (-1, -1))) 
    

        
class Equipment(object):
    def __init__(self, canvas, radius, position, color):
        self.can, self.radius = canvas, radius
        self.x, self.y = position
        
        self.Object = self.can.create_oval(self.x-self.radius, self.y-self.radius, 
                                    self.x+self.radius, self.y+self.radius, fill=color)

    def update(self, position): #to move the equipment
        self.x, self.y = position
        self.can.coords(self.Object, self.x-self.radius, self.y-self.radius,
                                     self.x+self.radius, self.y+self.radius)

    def __eq__(self, other): 
        overlapping = self.can.find_overlapping(self.x-self.radius, self.y-self.radius,
                                                self.x+self.radius, self.y+self.radius)
        return other.get_object() in overlapping
        
    def get_radius(self):
        return self.radius

    def get_position(self):
        return self.x, self.y

    def get_object(self):
        return self.Object



class Paddle(Equipment):
    def __init__(self, canvas, radius, position):
        Equipment.__init__(self, canvas, radius, position, RED)
        self.handle = self.can.create_oval(self.x-self.radius/2, self.y-self.radius/2,
                                self.x+self.radius/2, self.y+self.radius/2, fill=DARK_RED)

    def update(self, position): #to move the paddle
        Equipment.update(self, position)
        self.can.coords(self.handle, self.x-self.radius/2, self.y-self.radius/2,
                                   self.x+self.radius/2, self.y+self.radius/2)



class Background(object):
    def __init__(self, canvas, screen_dimensions, goal_w):
        self.can, self.goal_w = canvas, goal_w
        self.w, self.h = screen_dimensions
        self.draw_bg()
        
    def draw_bg(self):
        self.can.config(bg=WHITE, width=self.w, height=self.h)
        #middle circle
        d = self.goal_w/4
        self.can.create_oval(self.w/2-d, self.h/2-d, self.w/2+d, self.h/2+d,fill=WHITE, outline=BLUE)
        self.can.create_line(ZERO, self.h/2, self.w, self.h/2, fill=BLUE) #middle
        self.can.create_line(5, ZERO, 5, self.h, fill=BLUE) #left
        self.can.create_line(self.w, ZERO, self.w, self.h, fill=BLUE) #right

        #top
        self.can.create_line(0, 5 , self.w/2-self.goal_w/2, 5,fill=BLUE)
        self.can.create_line(self.w/2+self.goal_w/2, 5, self.w, 5,fill=BLUE)
    
        #bottom
        self.can.create_line(ZERO, self.h, self.w/2-self.goal_w/2, self.h, fill=BLUE)
        self.can.create_line(self.w/2+self.goal_w/2, self.h, self.w, self.h,fill=BLUE)

                                                    
    def is_position_valid(self, position, width, constraint=None):
        #width -> radius of puck 
        x, y = position
        #if puck is in goal, let it keep going in.
        if constraint == None and self.is_in_goal(position, width): #puck
            return True
        elif (x - width < ZERO or x + width > self.w or  #inside the board
            y - width < ZERO or y + width > self.h):
            return False
        elif constraint == LOWER: #paddle
            return y - width > self.h/2
        elif constraint == UPPER: #paddle
            return y + width < self.h/2
        else:
            return True    


    def is_in_goal(self, position, width):
        #width -> radius of puck #check
        #self.w -> width of screen
        x, y = position
        if (y - width <= ZERO and x - width > self.w/2 - self.goal_w/2 and 
                                    x + width < self.w/2 + self.goal_w/2):
            return Player1 #top
        elif (y + width >= self.h and x - width > self.w/2 - self.goal_w/2 and 
                                        x + width < self.w/2 + self.goal_w/2):
            return Player2 #bottom
        else:
            return False
            
    def get_screen(self):
        return self.w, self.h  

    def get_goal_w(self):
        return self.goal_w
        


class Puck(object):
    def __init__(self, canvas, background):
        self.background = background
        self.screen = self.background.get_screen() # to get screen width and height
        self.x, self.y = self.screen[0]/2, self.screen[1]/2
        self.can, self.w = canvas, self.background.get_goal_w()/12
        #goal_w = screen_width/3
        #self.w -> radius of puck = goal_width/12

        c, d = rand() 
        self.vx, self.vy = 4*c, 6*d # ->velocity in x and y directions
        self.a = .99 #friction
        self.cushion = self.w*0.25 
        
        self.puck = Equipment(canvas, self.w, (self.y, self.x),BLACK)
        

    def update(self):
        #air hockey table - puck never completely stops.
        if self.vx > 0.25: self.vx *= self.a
        if self.vy > 0.25: self.vy *= self.a
        
        x, y = self.x + self.vx, self.y + self.vy

        if not self.background.is_position_valid((x, y), self.w):
            #puck crossing the board boundaries
            #self.w -> radius of puck = goal_width/12
            if x - self.w < ZERO or x + self.w > self.screen[0]: # ->change direction
                self.vx *= -1
            if y - self.w < ZERO or y + self.w > self.screen[1]: # ->change direction
                self.vy *= -1
            x, y = self.x+self.vx, self.y+self.vy
            
        self.x, self.y = x, y
        self.puck.update((self.x, self.y)) #(equipment) class update function


    def hit(self, paddle, moving):
        x, y = paddle.get_position() #paddle is inheriting equipment which has get_position() returns x,y coords

        if moving:       
            if (x > self.x - self.cushion and x < self.x + self.cushion or 
                                                    abs(self.vx) > MAX_SPEED):
                xpower = 1 # ->not hit
            else:
                xpower = 5 if self.vx < 2 else 2
            if (y > self.y - self.cushion and y < self.y + self.cushion or 
                                                    abs(self.vy) > MAX_SPEED):
                ypower = 1 # ->not hit
            else:
                ypower = 5 if self.vy < 2 else 2
        else: # ->paddle not moving 
            xpower, ypower = 1, 1
            
        #to change direction     
        if self.x + self.cushion < x:
            xpower *= -1
        if self.y + self.cushion < y:
            ypower *= -1
        
        self.vx = abs(self.vx)*xpower
        self.vy = abs(self.vy)*ypower
    
    def __eq__(self, other):
        return other == self.puck

    def in_goal(self):
        return self.background.is_in_goal((self.x, self.y), self.w)



class Player(object):
    def __init__(self, master, canvas, background, puck, constraint):
        self.puck, self.background = puck, background
        self.constraint, self.v = constraint, PADDLE_SPEED
        screen = self.background.get_screen() # to get screen width and height
        self.x = screen[0]/2 #width/2
        self.y = 60 if self.constraint == UPPER else screen[1] - 50

        self.paddle = Paddle(canvas, self.background.get_goal_w()/7,
                                                            (self.x, self.y))
        self.up, self.down, self.left, self.right = False, False, False, False
        
        if self.constraint == LOWER:
            master.bind('<Up>', self.MoveUp)
            master.bind('<Down>', self.MoveDown)
            master.bind('<KeyRelease-Up>', self.UpRelease)
            master.bind('<KeyRelease-Down>', self.DownRelease)
            master.bind('<Right>', self.MoveRight)
            master.bind('<Left>', self.MoveLeft)
            master.bind('<KeyRelease-Right>', self.RightRelease)
            master.bind('<KeyRelease-Left>', self.LeftRelease)
        else:
            master.bind('<w>', self.MoveUp)
            master.bind('<s>', self.MoveDown)
            master.bind('<KeyRelease-w>', self.UpRelease)
            master.bind('<KeyRelease-s>', self.DownRelease)
            master.bind('<d>', self.MoveRight)
            master.bind('<a>', self.MoveLeft)
            master.bind('<KeyRelease-d>', self.RightRelease)
            master.bind('<KeyRelease-a>', self.LeftRelease)
        


    def update(self):
        x, y = self.x, self.y
        
        if self.up: y = self.y - self.v
        if self.down: y = self.y + self.v
        if self.left: x = self.x - self.v
        if self.right: x = self.x + self.v
        
        if self.background.is_position_valid((x, y), self.paddle.get_radius(), self.constraint):
            self.x, self.y = x, y
            self.paddle.update((self.x, self.y))

        if self.puck == self.paddle:
            moving = any((self.up, self.down, self.left, self.right)) #->returns true if paddle is moving
            self.puck.hit(self.paddle, moving)
    


    def MoveUp(self, callback=False):
        self.up = True
    def MoveDown(self, callback=False):
        self.down = True
    def MoveLeft(self, callback=False):
        self.left = True
    def MoveRight(self, callback=False):
        self.right = True
    def UpRelease(self, callback=False):
        self.up = False
    def DownRelease(self, callback=False):
        self.down = False
    def LeftRelease(self, callback=False):
        self.left = False
    def RightRelease(self, callback=False):
        self.right = False




class Home(object):
    def __init__(self, master, screen_dimensions, score=START_SCORE.copy()):
        #screen_dimensions : (width , height) of screen
        #frame -> widgets positioning
        #canvas -> drawing shapes
        self.frame = tk.Frame(master)
        self.frame.pack()
        self.can = tk.Canvas(self.frame)
        self.can.pack()
        #goal width = 1/3 of screen width
        background = Background(self.can, screen_dimensions, screen_dimensions[0]*0.33)
        self.puck = Puck(self.can, background)
        self.p1 = Player(master, self.can, background, self.puck, UPPER)
        self.p2 = Player(master, self.can, background, self.puck, LOWER)
        
        master.bind("<Return>", self.reset) 
        master.bind('<r>', self.reset) #restart
        
        master.title(str_dict(score))
        # master.title("Top 0 Bottom 0  LEVEL: 2")
        
        self.master, self.screen_dimensions, self.score = master, screen_dimensions, score
        
        self.update()
        
    def reset(self, callback=False):
        print(callback) 
        print(callback.keycode)
        if callback.keycode == 983154: #r key resets score.
            print("R pressed")
            self.score = START_SCORE.copy()
        self.frame.destroy()
        self.__init__(self.master, self.screen_dimensions, self.score)
        
    def update(self):
        self.puck.update()
        self.p1.update()
        self.p2.update()
        if not self.puck.in_goal():
            self.frame.after(SPEED, self.update) 
        else:
            winner = Player1 if self.puck.in_goal() == Player2 else Player2
            self.update_score(winner)
            
    def update_score(self, winner):
        self.score[winner] += 1
        self.master.title(str_dict(self.score))

        winnerName = "Player 1" if winner=="Top" else "Player 2"
        if self.score[winner] == MAX_SCORE:
            self.can.create_text(self.screen_dimensions[0]/2, self.screen_dimensions[1]/2,  font=FONT, 
                                                     text="%s wins!" % winnerName)
            self.score = START_SCORE.copy()
        else:
            self.can.create_text(self.screen_dimensions[0]/2, self.screen_dimensions[1]/2,  font=FONT, 
                                                 text="Point for %s" % winnerName)
                                                             


if __name__ == "__main__": 
    screen_dimensions = 700, 760
    root = tk.Tk()
    Home(root, screen_dimensions)
    root.mainloop()