import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 400, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Load images
PURPLE_SPACE_SHIP = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "purple_ufo.png")), (45, 45))
BLUE_SPACE_SHIP = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "blue_ufo.png")), (45, 45))
RED_SPACE_SHIP = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "red_ufo.png")), (45, 45))

# Player player
HERO_SPACE_SHIP = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "spaceship_green.png")), (64, 64))
HERO_SPACE_SHIP_SMALL = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "spaceship_green.png")), (32, 32))


# Lasers
ENEMY_LASER = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "enemy-layzer.png")), (8, 8))
HERO_LASER = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "hero-layzer.png")), (16, 16))

# Background
BG = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "bg.png")), (WIDTH, HEIGHT))

# space sprites
PURPLE_PLANET = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "planet_purple.png")), (64, 64))

PURPLE_PLANET_SMALL = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "planet_purple.png")), (32, 32))

ORANGE_PLANET = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "planet_orange.png")), (100, 100))

ORANGE_PLANET_SMALL = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "planet_orange.png")), (80, 80))

GREY_METEOR = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "meteor_grey.png")), (16, 16))

SMALL_GREY_METEOR = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "meteor_grey.png")), (32, 32))


# explosion
EXPLOSION = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "explosionzoom.png")), (64, 64))

# buttons
BUT_W = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "but_W2.png")), (32, 32))
BUT_A = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "but_A2.png")), (32, 32))
BUT_S = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "but_S2.png")), (32, 32))
BUT_D = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "but_D2.png")), (32, 32))
BUT_SPACE = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "but_space2_not.png")), (120, 90))

# title
TITLE = pygame.image.load(
    os.path.join("assets", "TITLE.png"))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:

    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.explosion_img = None
        self.lasers = []
        self.cool_down_counter = 0
        self.planet_img = None

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+13, self.y, self.laser_img)
            laser2 = Laser(self.x+42, self.y+5, self.laser_img)

            self.lasers.append(laser)

            self.lasers.append(laser2)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = HERO_SPACE_SHIP
        self.laser_img = HERO_LASER
        self.explosion_img = EXPLOSION
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y +
                                               self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() +
                                               10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, ENEMY_LASER),
        "blue": (BLUE_SPACE_SHIP, ENEMY_LASER),
        "purple": (PURPLE_SPACE_SHIP, ENEMY_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Planet(Ship):
    COLOR_MAP = {
        "small_orange_planet": (ORANGE_PLANET_SMALL),
        "orange": (ORANGE_PLANET),
        "purple": (PURPLE_PLANET),
        "small_purple_planet": (PURPLE_PLANET_SMALL),
        "meteor": (GREY_METEOR),
        "small_meteor": (SMALL_GREY_METEOR)
    }

    def __init__(self, x, y, color_planet, health=100):
        super().__init__(x, y, health)
        self.ship_img = self.COLOR_MAP[color_planet]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 100
    level = 0
    lives = 3

    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    clock = pygame.time.Clock()

    enemies = []
    wave_length = 5
    enemy_vel = 1

    planets = []
    wave_length_planets = 2
    planet_vel = 0.5

    laser_vel = 5

    player = Player(200, 330)
    player_vel = 5

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))

        WIN.blit(HERO_SPACE_SHIP_SMALL, (10, 10))

        lives_label = main_font.render(
            f"x {lives}", 1, (255, 255, 255))

        level_label = main_font.render(
            f"Level: {level}", 1, (255, 255, 255))

        WIN.blit(lives_label, (HERO_SPACE_SHIP_SMALL.get_width()+10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for planet in planets:
            planet.draw(WIN)

        player.draw(WIN)

        for enemy in enemies:
            enemy.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height()+30 < HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        if len(enemies) == 0:
            level += 1
            wave_length += 2
            for i in range(wave_length):
                enemy = Enemy(random.randrange(
                    50, WIDTH-100), random.randrange(-1150, -100), random.choice(["red", "blue", "purple"])

                )
                enemies.append(enemy)

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*240) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                lives -= 1
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

        if len(planets) == 0:

            wave_length_planets = 3
            for i in range(wave_length_planets):
                planet = Planet(random.randrange(
                    50, WIDTH-100), random.randrange(-1150, -100), random.choice(["meteor", "small_meteor", "orange", "small_orange_planet", "purple", "small_purple_planet"])

                )
                planets.append(planet)

        for planet in planets[:]:
            planet.move(planet_vel)

            if planet.y + planet.get_height() > HEIGHT+100:

                planets.remove(planet)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 20)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render(
            "Press the mouse to begin...", 1, (255, 255, 255))

        title_label3 = title_font.render(
            "SPACE - Shoot", 1, (255, 255, 255))

        WIN.blit(TITLE, (-7, 0))

        WIN.blit(BUT_W, (130, 368))
        WIN.blit(BUT_A, (98, 400))
        WIN.blit(BUT_S, (130, 400))
        WIN.blit(BUT_D, (162, 400))
        WIN.blit(BUT_SPACE, (200, 370))

        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 470))

      #  WIN.blit(title_label3, (WIDTH/2 - title_label.get_width()/2, 290))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
