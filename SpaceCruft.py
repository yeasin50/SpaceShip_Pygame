import pygame
import  os
import time
import random
pygame.font.init()

#window frame
HEIGHT, WIDTH = 550, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Game")


RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "redShip.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "greenShip.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "blueShip.png"))

#myship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "myShip1.png"))
YELLOW_SPACE_SHIP = pygame.transform.scale(YELLOW_SPACE_SHIP,(70,60))

# bullets 
RED_LEASER = pygame.image.load(os.path.join("assets", "redBullet.png"))
GREEN_LEASER = pygame.image.load(os.path.join("assets", "greenBullet.png"))
BLUE_LEASER = pygame.image.load(os.path.join("assets", "blueBullet.png"))
YELLOW_LEASER = pygame.image.load(os.path.join("assets", "yellowBullet.png"))

BG = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "background-black.png")),
    (WIDTH, HEIGHT)
)


class Ship:
   
    CoolDown = 30 # half of fps
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
        self.score = 0
       
    

    def draw(self, win):
        WIN.blit(self.ship_img, (self.x, self.y))
        
        for laser in self.lasers:
            laser.draw(win)

    def move_laser(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -=10
                self.lasers.remove(laser)



    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return  self.ship_img.get_height()

    def cooldown(self):
        if self.cool_down_counter >= self.CoolDown:
            self.cool_down_counter = 0
        elif self.cool_down_counter> 0:
            self.cool_down_counter +=1


    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)

        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LEASER
        self.mask = pygame.mask.from_surface(self.ship_img) # for img poss
        self.max_health = health
        self.score = 0
    


    def move_laser(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.score = self.score + 1
                        print(self.score)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            

    def health_bar(self, win):
        pygame.draw.rect(win, (255,0,0), (self.x, self.y+ self.ship_img.get_height() +10, self.ship_img.get_width(), 10))
        pygame.draw.rect(win, (0,255,0), (self.x, self.y+ self.ship_img.get_height() +10, self.ship_img.get_width()* (self.health/self.max_health),  10))

    def draw(self, win):
        super().draw(win)
        self.health_bar(win) 


class Enemy(Ship):
    color_map = {
        "red": (RED_SPACE_SHIP, RED_LEASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LEASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LEASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.color_map[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel
    
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Laser: 
    def __init__(self, x, y, img):
        self.x = x+20 # may need to config for assets position
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))
        
    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >=0)

    def collision(self, obj):
        return collide(obj, self)



def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 3
    player_vel = 5
    main_font = pygame.font.SysFont("comicsans", 20)
    loss_font = pygame.font.SysFont("comicsans", 30)

    lost= False
    lost_count= 0

    player = Player(400, 350)

    enemies = []
    wave_length = 5
    enemy_vel = 1
    laser_vel = 4 

    clock = pygame.time.Clock()

    def redraw():
        WIN.blit(BG, (0, 0))

        #text
        lives_labe = main_font.render(f"Lives: {lives}", 1, (255,244,234))
        level_labe = main_font.render(f"Level: {level}", 1, (255,244,234))
        level_SCORE = main_font.render(f"SCORE: {player.score}", 1, (255,244,234))

        WIN.blit(lives_labe, (10, 10))
        WIN.blit(level_labe, ( WIDTH - level_labe.get_width() - 10, 10))
        WIN.blit(level_SCORE, ( WIDTH/2-40 , 20))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = loss_font.render("YOU Lost", 1, (244,244,242))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 300))

        pygame.display.update()


    while run:
        clock.tick(FPS) # same speed all device
        redraw()
        if lives <= 0 or player.health<=0:
            lost= True
            lost_count += 1

        if lost:
            if lost_count > FPS *3: 
                run = False
            else :
                continue


        if len(enemies) == 0:
            level += 1
            wave_length +=5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1550, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()


        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x + player_vel > 0: #LEFT
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:#up
            player.y -= player_vel
        if keys[pygame.K_s] and  player.y + player_vel + player.get_height() < HEIGHT:#down
            player.y += player_vel

        if keys[pygame.K_SPACE]:
             player.shoot()


        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_laser(laser_vel, player)

            if random.randrange(0, 3*60)==1:
                enemy.shoot()

            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
            
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                
            elif enemy.y + enemy.get_height()> HEIGHT:
                lives -= 1
                if enemy in enemies:
                    enemies.remove(enemy)
        
        player.move_laser(-laser_vel, enemies)

def main_menu():
    run = True
    title_font = pygame.font.SysFont("comicsans", 70)
    while run:
        WIN.blit(BG,(0,0))
        title_label = title_font.render("Press mouse to begin", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    
    pygame.quit()

main_menu()
