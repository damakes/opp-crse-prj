#Ohjelma Bone Collector
#Pelin ideana on kerätä tasolta kaikki luut, välttäen vaaralliset kosketukset ja edetä seuraavalle tasolle. 
#Kansiot:
#äänet-kansiosta löytyy ohjelmassa käytettävät ääni tiedostot
#img-kansioon on tallennettu ohjelmassa käytettävät visuaaliset elementit
#lähteet-kansiosta löytyy lähde materiaali
#tasot-kansioon on tallennettu Pelin kaikki tasot

########################################################################################################################

#Tuodaan Ohjelmaan Moduulit Pygame, auttamaan pelin rakentamisen sekä tiedostojen käytössä
#Otetaan moduulista käyttöön mixeri, hyödynnetään sitä pelin ääni tiedostojen muuntamisessaa ja käyttämisessä
#Tuodaan pickle jotta tasojen datan taltiointi olisi yksinkertaista, sekä se vähentää pyöritettävän datan määrää kerralla
#tuodaan os moduuli mikä auttaa hakemaan kansiosta määritettyä titetoa

import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path


#toistetaan ääni tiedostot
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()
clock = pygame.time.Clock() 
fps = 60

#muuttujat näytön korkeudelle / leveydelle
screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Bone Collector')#ikkunassa näkyvä ohjelman nimi


#määritetään pelin fontti
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)


#pelin muuttujat
tile_size = 50
game_over = 0
main_menu = True
level = 1
max_levels = 5
score = 0


#määritetään värit
white = (255, 255, 255)
blue = (0, 0, 255)


#ladataan: Ohjeet, tausta, sekä näppäin kuvakkeet.
#tehdään tuoduille kuville muuttujat
key_img = pygame.image.load('img/key.png')
bg_img = pygame.image.load('img/background.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')


#ladataan pelin musiikki ja asetetaan ääni 
#tehdään äänille muuttujat
pygame.mixer.music.load('äänet/pianokl.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound('äänet/great.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('äänet/bark.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('äänet/shriek.wav')
game_over_fx.set_volume(0.5)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


#Pelin levelin resetointi funktio
#palauttaa pelin elementit niiden aloituspaikoilleen
#tarkistetaan onko ladattavaa tasoa, mikäli on ladataan peli taso ja rakennetaan mailma
#rakennetaan kolikon seuranta näytölle
def reset_level(level):
    player.reset(100, screen_height - 130)
    morso_group.empty()
    platform_group.empty()
    coin_group.empty()
    lava_group.empty()
    exit_group.empty()

    
    if path.exists(f'tasot/level{level}_data'):
        pickle_in = open(f'tasot/level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)
    
    score_coin = Coin(tile_size // 2, tile_size // 2)
    coin_group.add(score_coin)
    return world

#Painike luokka
#tehdään methodi button luokaan, jossa funktion instanssi, jossa painiketta seurataan x ja y suunnassa, milloin sitä painetaan
#mikäli painiketta ei paineta mitään ei tapahdu
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
        

    #Piirretään näytölle kuva
    #haetaan hiiren koordinaatit, tarkistetaan sijainti ja klikkauskohdat
    #tarkistetaan onko hiiren koordinaatit näytöllä, mikäli on muuttuja = True
    #palautetaan toiminto
    def draw(self):
        action = False

        
        pos = pygame.mouse.get_pos()

        
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False


        
        screen.blit(self.image, self.rect)

        return action

#pelaaja luokka
#haetaan näppäimistön komennot
#Juoksevan koiran animaatio
#lisätään painovoima
#Tarkistetaan törmäykset
class Player():
    #Luokan pelaaja funktio, jossa (x,y)-koordinaatit asetettu nollaksi.
    def __init__(self, x, y):
        self.reset(x, y)
    #Tämä funktio tarkistaa onko ,pelaaja ilmassa,pelaaja kuollut, true/false.
    #Pelaajan kiihtyvyys 
    #Hakemalla tiedon ympäristöstä sekä näppäin komennoista. 
    #tarkista törmäykset  x suunnassa
    #tarkista törmäykset  y suunnassa
    #tarkistetaan taso jalkojen alla, jotta hyppääminen onnistuu, sekä taso yläpuolella
    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20

        if game_over == 0:
            
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True

            if key[pygame.K_SPACE] == False:
                self.jumped = False

            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1

            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1

            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            if self.counter > walk_cooldown:
                self.counter = 0    
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            self.in_air = True
            for tile in world.tile_list:
                
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
 
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0

                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False


            
            #Vihollisen kosketuksesta game_over arvo muuttuu 0 -> -1 ja peli päättyy
            if pygame.sprite.spritecollide(self, morso_group, False):
                game_over = -1
                game_over_fx.play()

            #laavan kosketuksesta game_over arvo muuttuu 0 -> -1 ja peli päättyy
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            #Tarkistetaan milloin pelaaja on oven kohdalla
            #Oven kohdalla game_over =  1, joka päästää pelaajan etenemään seuraavan ohjelman toimintoon 
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1


            #Tarkistetaan törmäykset alustojen kanssa
            for platform in platform_group:
                #törmäykset x suunnassa
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #törmäykset y suunnassa
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #tarkistetaan onko alapuolella alusta
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    #tarkistetaan onko yläpuolella alusta
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    #liiku sivuttain alustalla
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction


            #päivitetään pelaajan koordinaatit
            self.rect.x += dx
            self.rect.y += dy

        #mikäli Muuttujan arvo on -1, piirretään näytölle "Game over" ja nostetaan kuvake alhaalta näytön yläreuaan tapahtuma alueella.
        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2)
            if self.rect.y > 200:
                self.rect.y -= 5

        screen.blit(self.image, self.rect)

        return game_over

    #Peli objektiin instanssi, missä asetetaan kuvat oikealle/vasemmalle lisoille.
    #Luodaan animaatio pelaajan liikkeeseen, ladataan pelaajan kuvat
    #Tuodaan animaatiot liikkeessä oikealle sekä vasemmalle listoihin img_right/img_left 
    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 3):
            img_right = pygame.image.load(f'img/koira{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/haamu.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


#Mailman luokka
#Rakennetaan methodiin lista, johon tallennamme Mailman datan
#ladataan mailmaan elementit ja tehdääm muuttujat
#Muutetaan elemnttien kuvake kokoa soveltuvammaksi näytölle
#tarkistetaan muuttujan arvo, jonka jälkeen suoritetaan arvolle asetettu toiminto
#lisätään elementit listaan tile_list
#luodaan morso objekti, lisätään se morso_grouppiin
#luodaan laava objekti, lisätään se platform_grouppiin
#luodaan coin objekti, lisätään se coin_grouppiin
#luodaan exit objekti, lisätään se exit_grouppiin
#tasokohtaisesti ladattavien elementtien määrä suoritetaan
class World():
    def __init__(self, data):
        self.tile_list = []

        
        em1_img = pygame.image.load('img/elementti1.png')
        em2_img = pygame.image.load('img/elementti2.png')
        #lisätään listaan 
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(em1_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(em2_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    morso = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    morso_group.add(morso)
                if tile == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1


    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


#vihollis luokka
#tämä koodi toistuu ohjelmassa useasti, pohja luokka vihollis objekteille
#ladataan vihollis hahmo, sekä muutetaan hahmon kuvake näytölle sopivammaksi
#asetateaan liike suunnat viholliselle, sekä liikkeen pituudet
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/morso.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

#liikkuvan alustan pohja luokka
#tuodaan liikkuvan alustan kuva, muutetaan se näytölle sopivammaksi 
#asetetaan alustojen liike x-suunnassa ja y-suunnassa
#automatisoidaan liike, jotta liike on itsenäistä
#asetetaan liikkeen pituus
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/liikkuva_alusta.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y


    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1




#laavan pohja luokka
#tuodaan laavan kuvake, asetetaan se oikean kokoiseksi näytölle
#laavan vaikutus suunnat x ja y suunnassa
class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

#kolikon pohja luokka
#ladataan kansiosta kolikon kuva "luu",asetetaan se oikean kokoiseksi näytölle
#asetetaan se (x,y)-suunnassa
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/coin.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
#exit pohja luokka
#ladataan kuva kansiosta ja asetetaan sopivaksi näytölle
#asetetaan se (x,y)-suunnassa
class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


#luodaan näytölle tuotaville elementeille muuuttujat
player = Player(100, screen_height - 130)
morso_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

#tarkistetaan onko tasoja jäljellä
#mikäli tasoa ei läpäisty tuodaan näytölle restart napppula, mitä painamalla pelaaja voi yrittää suorittaa tason uudestaan 
#Tason läpäistyä pelaaja päästetään etenemään seuraavalle tasolle, mikäli taso oli viimeinen taso suoritetaan toiminto jossa näytölle tuodaan onnittelut ja pisteet
if path.exists(f'tasot/level{level}_data'):
    pickle_in = open(f'tasot/level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)


#asetetaan painikkeiden koordinaatit näytöltä
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

#Mikäli muuttuja on tosi on näytön päivitysnopeus 60
#koordinaatit pelaajan liikkumis kuvakkeelle
#koordinaatit taustalle
#tarkistetaan onko main_menu tosi tapauksissa
#päivitä pisteet
#tarkista onko kolikkoja kerätty
#mikäli pelaaja on kuollut on game_over arvo -1
#jos tämä ehto täyttyy resetoidaan pisteet, jonka jälkeen pelaaja voi yrittää uudestaan
#mikäli taso on läpäisty, on game_over arvo 1 ja pelaaja pääsee jatkamaan seuraavalle tasolle
#palautetaan tason arvot, sekä siirrytään seuraavalle tasolle
#mikäli suoritettu taso on viimeinen : piirretään näytölle "YOU WIN" sekä kerättyjen luitten määrä
#palautetaan tason elementit 
run = True
while run:

    clock.tick(fps)
    
    screen.blit(bg_img, (0, 0))
    screen.blit(key_img, (100, 100))

    if main_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()

        if game_over == 0:
            morso_group.update()
            platform_group.update()
 
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text(' X ' + str(score), font_score, white, tile_size - 10, 10)
        
        morso_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)
        

    
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        
        if game_over == 1:

            level += 1
            if level <= max_levels:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('YOU WIN!', font, blue, (screen_width // 2) - 90, screen_height // 2.5)
                draw_text('COLLECTED:'+str(score)+'/48', font_score, white,(screen_width // 2) - 50, screen_height // 2)
                if restart_button.draw():
                    level = 1
                    
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0
    #tarkistetaan tapahtuma
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
