import pygame
from pygame.locals import *
import random

pygame.init()

# creamos la ventana
width = 500
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Car Game')

gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)

road_width = 300
marker_width = 10
marker_height = 50

left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

road = (100, 0, road_width, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)

lane_marker_move_y = 0

player_x = 250
player_y = 400

clock = pygame.time.Clock()
fps = 120

gameover = False
speed = 2
score = 0

class Vehicle(pygame.sprite.Sprite):
    
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        #Escalamos la imagen asi no es mas grande que las lineas
        image_scale = 45 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))
        
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        
class PlayerVehicle(Vehicle):
    
    def __init__(self, x, y):
        image = pygame.image.load('./images/car.png')
        super().__init__(image, x, y)
        
        
class Motorcycle(Vehicle):
    def __init__(self, x, y, image):
        super().__init__(image, x, y)

# sprites
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# el vehiculo del jugador
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

# cargar las imagenes de los vehiculos
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = []
for image_filename in image_filenames:
    image = pygame.image.load('./images/' + image_filename)
    vehicle_images.append(image)
    
# cargar la imagen de choque
crash = pygame.image.load('./images/crash.png')
crash_rect = crash.get_rect()
speed_increase_rate = 0.0015
lane_change_speed = 2
score_to_change_vehicle = 20

keys_pressed_left = set()
keys_pressed_right = set()

running = True
while running:
    speed_increase = speed * speed_increase_rate

    clock.tick(fps)

    # Dentro del bucle principal, en la sección de eventos:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        # Manejar teclas presionadas
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                keys_pressed_left.add(event.key)
            elif event.key == K_RIGHT:
                keys_pressed_right.add(event.key)
        # Manejar teclas liberadas
        elif event.type == KEYUP:
            if event.key == K_LEFT:
                keys_pressed_left.discard(event.key)
            elif event.key == K_RIGHT:
                keys_pressed_right.discard(event.key)

    # Mover el vehículo basado en las teclas presionadas
    if K_LEFT in keys_pressed_left and player.rect.center[0] > left_lane:
        player.rect.x -= lane_change_speed * speed
    elif K_RIGHT in keys_pressed_right and player.rect.center[0] < right_lane:
        player.rect.x += lane_change_speed * speed

    # Verificar colisión después de cambiar de carril
    for vehicle in vehicle_group:
        if pygame.sprite.collide_rect(player, vehicle):
            gameover = True
            if K_LEFT in keys_pressed_left:
                player.rect.left = vehicle.rect.right
                crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
            elif K_RIGHT in keys_pressed_right:
                player.rect.right = vehicle.rect.left
                crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
            if event.key == K_LEFT:
                player.rect.left = vehicle.rect.right
                crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
            elif event.key == K_RIGHT:
                player.rect.right = vehicle.rect.left
                crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
    if score >= score_to_change_vehicle and not isinstance(player, Motorcycle):
    # Cambiar el vehículo a una moto
        motorcycle_image = pygame.image.load('./images/moto.png')
        player = Motorcycle(player.rect.center[0],  player.rect.center[1], motorcycle_image)
        player_group.empty()
        player_group.add(player)    
        # Ajustar la velocidad de aumento
        speed_increase_rate = 0.0007  # 0.07% de aumento por segundo
        speed_increase = speed * speed_increase_rate

            
    # pastooooo
    screen.fill(green)
    
    # el camino
    pygame.draw.rect(screen, gray, road)
    
    # marcamos los lados
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)
    
    # marcadores de carril
    lane_marker_move_y += speed * 2
    if lane_marker_move_y >= marker_height * 2:
        lane_marker_move_y = 0
    for y in range(marker_height * -2, height, marker_height * 2):
        pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        
    # el jugador
    player_group.draw(screen)
    
    # añadir un vehículo
    if len(vehicle_group) < 2:
        
        # asegurarse que hay suficiente espacio entre los vehículos
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height * 1.5:
                add_vehicle = False
                
        if add_vehicle:
            
            # seleccionar un carril aleatorio
            lane = random.choice(lanes)
            
            # seleccionar una imagen de vehículo aleatoria
            image = random.choice(vehicle_images)
            vehicle = Vehicle(image, lane, height / -2)
            vehicle_group.add(vehicle)
    
    # mover los vehículos
    for vehicle in vehicle_group:
        vehicle.rect.y += speed
        
        # remover el vehículo cuando se salga de la pantalla
        if vehicle.rect.top >= height:
            vehicle.kill()
            
            score += 1
            
            # aumentar la velocidad de juego al pasar 5 vehículos
            if score > 0 and score % 5 == 0:
                speed += 1
    
    # dibujar los vehículos
    vehicle_group.draw(screen)
    
    # mostrar el puntaje
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render('Score: ' + str(score), True, white)
    text_rect = text.get_rect()
    text_rect.center = (50, 400)
    screen.blit(text, text_rect)
    
    # comprobar si hay una colisión
    if pygame.sprite.spritecollide(player, vehicle_group, True):
        gameover = True
        crash_rect.center = [player.rect.center[0], player.rect.top]
            
    # mostrar el juego terminado
    if gameover:
        screen.blit(crash, crash_rect)
        
        pygame.draw.rect(screen, red, (0, 50, width, 100))
        
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Chocaste! Jugas de nuevo? ( S o N)', True, white)
        text_rect = text.get_rect()
        text_rect.center = (width / 2, 100)
        screen.blit(text, text_rect)
            
    pygame.display.update()

    # esperar la entrada del usuario (y o n)
    while gameover:
        
        clock.tick(fps)
        
        for event in pygame.event.get():
            
            if event.type == QUIT:
                gameover = False
                running = False
                
            if event.type == KEYDOWN:
                if event.key == K_s:
                    
                    gameover = False
                    speed = 2
                    score = 0
                    vehicle_group.empty()
                    player.rect.center = [player_x, player_y]
                elif event.key == K_n:
                    gameover = False
                    running = False

pygame.quit()