
# PRÁCTICA 3: SENSADO Y ANÁLISIS INERCIAL

# Objetivo Terapéutico

# El juego está diseñado para incentivar el movimiento activo del brazo del usuario, promoviendo la movilidad de la extremidad 
# superior mediante la interacción con el entorno virtual. La mecánica del juego requiere que el jugador controle la nave espacial 
# moviendo el brazo en diferentes direcciones, lo que contribuye a la rehabilitación motora.

# Uso de Sensores Inerciales

# Se emplean acelerómetros y giroscopios para capturar el movimiento del brazo en tiempo real.
# La nave se desplaza en la pantalla en función de los datos obtenidos de estos sensores, permitiendo al usuario practicar 
# movimientos.

# Medición de Movimientos Clave para la Rehabilitación

# Se registran al menos dos tipos de movimientos:
# Movimientos en posiciones cardinales: Se analizan los desplazamientos del brazo en los ejes arriba-abajo y izquierda-derecha 
# a partir de los datos del acelerómetro.
# Movimientos de velocidad angular: Se mide la velocidad y aceleración del brazo utilizando el giroscopio, permitiendo evaluar 
# la calidad y fluidez del movimiento.

# Adaptabilidad del Juego al Proceso de Rehabilitación

# Dependiendo de la severidad de la lesión, se pueden ajustar los umbrales de detección del movimiento, facilitando la progresión terapéutica.
# La puntuación del juego proporciona retroalimentación inmediata, lo que motiva al usuario a mejorar su desempeño.


# INSTRUCCIONES PARA USAR EL JUEGO DE REHABILITACIÓN

# 1. Requisitos previos

# Antes de jugar, asegurarse tener lo siguiente:
# Un telefono inteligente con sensores inerciales (acelerómetro y giroscopio)
# Aplicación Sensor Server para la realizar una conexión entre el celular y la computadora (Solo para Android).
# La aplicación se obtuvo a partir del siguiente git hub: https://github.com/umer0586/SensorServer
# Antes de iniciar el juego, se deberá presionar el botón start en la aplicación Sensor Server para empezar a recibir datos.

# ¿Como jugar?
#  Controles del Juego
# Posición Inicial:
# Extiende los brazos y sostén el celular en posición horizontal con ambas manos.

# Mover la nave:

# Subir: Gira el celular inclinando ambas manos hacia la izquierda.
# Bajar: Gira el celular inclinando ambas manos hacia la derecha.
# Nota: Asegúrate de hacer los movimientos de manera fluida para un mejor control de la nave.

# Importación de librerias

import pygame
import json
import websocket
import threading
import random

# Inicializa Pygame
pygame.init()

# Configuración de gráficos
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Juego de Naves Espaciales")

#
bg_img = pygame.image.load('Practica 3/graphics/space_bg.png')
bg_img = pygame.transform.scale(bg_img, (800, 600))
bg_rect = bg_img.get_rect()

# Configura la nave
ship_img = pygame.image.load('Practica 3/graphics/spaceship.png')
ship_rect = ship_img.get_rect()
ship_rect.center = (400, 300)

#
enemy_img = pygame.image.load('Practica 3/graphics/enemy.png')
enemy_width = enemy_img.get_width()
enemy_height = enemy_img.get_height()

# Variables de movimiento
ship_speed = 5
speed_x = 0
speed_y = 0
score = 0
health = 100

# Lista de obstáculos (enemigos)
obstacles = []
obstacle_speed = 5

# Cargar el puntaje más alto desde un archivo
def load_high_score():
    try:
        with open('high_score.json', 'r') as f:
            return json.load(f)['high_score']
    except (FileNotFoundError, json.JSONDecodeError):
        return 0 

# Guardar el puntaje más alto en un archivo
def save_high_score():
    with open('high_score.json', 'w') as f:
        json.dump({"high_score": score}, f)

high_score = load_high_score()

# Función para mover la nave
def move_ship():
    global ship_rect
    ship_rect.y += speed_y

    # Limitar la posición de la nave para que no salga de la pantalla
    ship_rect.y = max(0, min(ship_rect.y, screen.get_height() - ship_rect.height))

    # Mantener la nave en el centro horizontal
    ship_rect.x = screen.get_width() // 2 - ship_rect.width // 2

# Función para crear nuevos obstáculos
def create_obstacle():
    x = screen.get_width()
    y = random.randint(0, screen.get_height() - enemy_height)
    return pygame.Rect(x, y, enemy_width, enemy_height)

# Función para mover los obstáculos
def move_obstacles():
    global score
    for obstacle in obstacles:
        obstacle.x -= obstacle_speed
        if obstacle.x + enemy_width < 0:
            obstacles.remove(obstacle)
            score += 1 

# Función para verificar colisiones
def check_collisions():
    global health
    for obstacle in obstacles:
        if ship_rect.colliderect(obstacle):
            health -= 10  # Reduce la salud si hay colisión
            obstacles.remove(obstacle)  # Elimina el obstáculo
            if health <= 0:
                return True  # Fin del juego si la salud llega a 0
    return False

# Función para actualizar la puntuación
def update_score():
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    
    # Mostrar el puntaje más alto
    high_score_text = pygame.font.Font(None, 36).render(f"High Score: {high_score}", True, (255, 255, 255))
    screen.blit(high_score_text, (10, 50))

# Función para mostrar la barra de salud
def draw_health():
    health_rect = pygame.Rect(10, 100, health, 20)
    pygame.draw.rect(screen, (255, 0, 0), health_rect)

# Función para mostrar Game Over
def show_game_over():
    global high_score
    font = pygame.font.Font(None, 72)
    game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    score_text = pygame.font.Font(None, 36).render(f"Final Score: {score}", True, (255, 255, 255))
    screen.blit(game_over_text, (250, 200))
    screen.blit(score_text, (320, 300))

    # Verificar y guardar el nuevo puntaje más alto
    if score > high_score:
        high_score = score

        # Pedir al jugador su nombre si tiene un nuevo récord
        player_name = input("¡Nuevo récord! Ingresa tu nombre: ")
        
        # Guardar el nombre y el puntaje más alto en el archivo
        with open('high_score.json', 'w') as f:
            json.dump({"high_score": high_score, "player_name": player_name}, f)

    # Mostrar el puntaje más alto
    high_score_text = pygame.font.Font(None, 36).render(f"High Score: {high_score}", True, (255, 255, 255))
    screen.blit(high_score_text, (320, 350))
    
    pygame.display.flip()
    pygame.time.wait(3000) 

# WebSocket: Manejo de mensajes del sensor
def on_message(ws, message):
    global speed_x, speed_y
    values = json.loads(message)['values']
    sensor_type = json.loads(message)['type']

    if sensor_type == "android.sensor.accelerometer":
        acceleration_x = values[0]  # Movimiento en X
        acceleration_y = values[1]  # Movimiento en Y

        # Ajustar la velocidad según la aceleración
        speed_x = acceleration_x * 0.7  # Ajuste en X
        speed_y = -acceleration_y * 0.7  # Ajuste en Y (invertido)

# WebSocket: Manejo de errores
def on_error(ws, error):
    print("Error:", error)

# WebSocket: Conexión cerrada
def on_close(ws, close_code, reason):
    print("Conexión cerrada:", close_code, reason)

# WebSocket: Conexión establecida
def on_open(ws):
    print("Conectado al servidor WebSocket")

# Función para conectar al WebSocket
def connect(url):
    ws = websocket.WebSocketApp(url,
                                 on_open=on_open,
                                 on_message=on_message,
                                 on_error=on_error,
                                 on_close=on_close)
    ws.run_forever()

# URL del servidor WebSocket
url = 'ws://192.168.101.102:8080/sensors/connect?types=["android.sensor.accelerometer","android.sensor.gyroscope","android.sensor.magnetic_field"]'

# Iniciar la conexión en un hilo separado
threading.Thread(target=connect, args=(url,), daemon=True).start()

# Función para mostrar el menú principal con imagen
def show_main_menu():
    global running
    font = pygame.font.Font(None, 48)

    # Cargar la imagen del menú
    menu_img = pygame.image.load('Practica 3/graphics/menu2.png')
    menu_img = pygame.transform.scale(menu_img, (800, 600))

    while True:
        screen.fill((0, 0, 0))

        # menú
        screen.blit(menu_img, (0, 0))

        # opciones del menú
        # title_text = font.render("Spaceship Game", True, (255, 255, 255))
        # screen.blit(title_text, (250, 150))
        
        start_text = font.render("1. Start Game", True, (255, 255, 255))
        screen.blit(start_text, (300, 250))
        
        high_score_text = font.render("2. High Score", True, (255, 255, 255))
        screen.blit(high_score_text, (300, 300))
        
        exit_text = font.render("3. Exit", True, (255, 255, 255))
        screen.blit(exit_text, (300, 350))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "start"
                elif event.key == pygame.K_2:
                    return "high_score"
                elif event.key == pygame.K_3:
                    running = False
                    return "exit"


# Bucle principal del juego
running = True
clock = pygame.time.Clock()

# Mostrar el menú principal
menu_selection = show_main_menu()

if menu_selection == "start":
    # Bucle principal del juego
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not pygame.display.get_init():
            running = False

        # Valores del acelerómetro
        move_ship()

        # Genera nuevos obstáculos con cierta probabilidad
        if random.random() < 0.02:
            obstacles.append(create_obstacle())

        # Mueve los obstáculos
        move_obstacles()

        # Verifica colisiones
        if check_collisions():
            show_game_over()
            running = False

        screen.blit(bg_img, bg_rect)
        screen.blit(ship_img, ship_rect)

        for obstacle in obstacles:
            screen.blit(enemy_img, obstacle.topleft)

        update_score()
        draw_health()

        pygame.display.flip()
        clock.tick(60)  # Control de FPS

elif menu_selection == "high_score":
    # Mostrar el puntaje más alto
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 48)
    high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    screen.blit(high_score_text, (300, 250))
    pygame.display.flip()
    pygame.time.wait(3000)

pygame.quit()


# Conclusión

# El desarrollo de este videojuego de rehabilitación basado en sensado y análisis inercial ofrece una forma interactiva y 
# motivadora para promover la movilidad del brazo. A través del uso de sensores inerciales, el sistema captura y analiza movimientos clave, 
# permitiendo evaluar la calidad y progresión del usuario en su proceso de recuperación.

# Además, la adaptabilidad del juego a diferentes niveles de movilidad permite personalizar la experiencia, facilitando la rehabilitación de manera 
# progresiva. La retroalimentación inmediata a través de la puntuación incentiva el compromiso del usuario, convirtiendo la terapia en una actividad 
# más dinámica y atractiva.