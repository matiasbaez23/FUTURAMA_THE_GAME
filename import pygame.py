#=======================================#
#Importación de las bibliotecas
#=======================================#

import pygame
import random
import pygame.mixer

#=======================================#
# Inicializa Pygame y el reloj del juego
#=======================================#

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

#=======================================#
# Ventana del juego Y Cargar recursos: Esta sección inicializa Pygame, configura 
# la ventana del juego y carga los recursos necesarios como imágenes y sonidos.
#=======================================#

win_height = 720  # Altura de la ventana
win_width = 551  # Ancho de la ventana

window = pygame.display.set_mode((win_width, win_height))  # Crear la ventana del juego
nave_images = [pygame.image.load("assets/nave2.png"),  # Imagen de la nave en posición hacia abajo
               pygame.image.load("assets/nave2.png"),   # Imagen de la nave en posición media
               pygame.image.load("assets/nave2.png")]    # Imagen de la nave en posición hacia arriba
skyline_image = pygame.image.load("assets/fondo.jpg")  # Imagen del fondo
ground_image = pygame.image.load("assets/piso.png")  # Imagen del suelo
top_pipe_image = pygame.image.load("assets/pipe_top.png")  # Imagen del tubo superior
bottom_pipe_image = pygame.image.load("assets/pipe_bottom.png")  # Imagen del tubo inferior
game_over_image = pygame.image.load("assets/gameover.png")  # Imagen de "Game Over"
start_image = pygame.image.load("assets/start.png")  # Imagen de la pantalla de inicio
point_sound = pygame.mixer.Sound("assets/punto.mp3") # Sonido de punto
crash_sound = pygame.mixer.Sound("assets/golpe.mp3") # Sonido de choque
jump_sound = pygame.mixer.Sound("assets/jump.mp3")   # Sonido de salto 
game_over_sound = pygame.mixer.Sound("assets/gameover.mp3")  # Se introduce la 
                                                             # variable game_over_sound_played para controlar 
                                                             # si el sonido de "game over" ya se ha reproducido.
pygame.mixer.music.load("assets/musica.mp3")

#=======================================#
# Configuración del juego : esta parte del código establece valores iniciales y configuraciones 
# para diferentes aspectos del juego,
# como la velocidad de desplazamiento, la posición de inicio de la nave, la puntuación inicial, 
# la fuente para la puntuación y el estado del juego.
#=======================================#

scroll_speed = 1  # Velocidad de desplazamiento del fondo y tubos
nave_start_position = (100, 250)  # Posición inicial de la nave
score = 0  # Puntuación inicial
font = pygame.font.SysFont('Segoe', 26)  # Fuente para mostrar la puntuación
game_stopped = True  # Estado inicial del juego (detenido)

#=======================================#
# Configuración de la nave: Esta clase define el comportamiento y 
# las características de la nave espacial controlada por el jugador.
#=======================================#

class Nave(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = nave_images[0]  # Imagen inicial de la nave
        self.rect = self.image.get_rect()
        self.rect.center = nave_start_position  # Coloca la nave en la posición inicial
        self.image_index = 0  # Índice para la animación de la nave
        self.vel = 0  # Velocidad de la nave (para simular la gravedad)
        self.flap = False  # Estado de de vuelo (si la nave está volando o no)
        self.alive = True  # Estado de vida de la nave

    def update(self, user_input):
        # Animar la nave
        if self.alive:
            self.image_index += 1
        if self.image_index >= 30:
            self.image_index = 0
        self.image = nave_images[self.image_index // 10]

        # Gravedad y vuelo
        self.vel += 0.5  # Incrementa la velocidad para simular la gravedad
        if self.vel > 7:
            self.vel = 7  # Limita la velocidad máxima de caída
        if (self.rect.y < 500):
            self.rect.y += int(self.vel)  # Aplica la velocidad a la posición de la nave
        if self.vel == 0:
            self.flap = False  # Si la velocidad es 0, el aleteo se detiene

        # Rotar la nave según la velocidad
        self.image = pygame.transform.rotate(self.image, self.vel * -7)

        # Entrada del usuario (volar)
        if user_input[pygame.K_SPACE] and not self.flap and self.rect.y > 0 and self.alive:
            self.flap = True
            self.vel = -7  # Eleva la nave cuando el usuario presiona la barra espaciadora
            jump_sound.play()  # Reproduce el sonido de salto

#=======================================#
# Configuracion de la tubos : Esta clase define los tubos que actúan como obstáculos en el juego.
#=======================================#

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, image, pipe_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y  # Posición del tubo
        self.enter, self.exit, self.passed = False, False, False  # Estados para el cálculo de puntuación
        self.pipe_type = pipe_type  # Tipo de tubo ('top' o 'bottom')

    def update(self):
        # Mover el tubo
        self.rect.x -= scroll_speed  # Mueve el tubo hacia la izquierda
        if self.rect.x <= -win_width:
            self.kill()  # Elimina el tubo si sale de la pantalla

        # Puntuación
        global score
        if self.pipe_type == 'bottom':
            if nave_start_position[0] > self.rect.topleft[0] and not self.passed:
                self.enter = True  # Marca que la nave ha pasado el borde izquierdo del tubo
            if nave_start_position[0] > self.rect.topright[0] and not self.passed:
                self.exit = True  # Marca que la nave ha pasado el borde derecho del tubo
            if self.enter and self.exit and not self.passed:
                self.passed = True  # Marca que la nave ha pasado completamente el tubo
                score += 1  # Incrementa la puntuación
                point_sound.play()  # Reproduce el sonido de punto


#=======================================#
# Configuración del suelo : Esta clase define el suelo en el juego, que también actúa como un obstáculo para la nave.
#=======================================#

class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = ground_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y  # Posición del suelo

    def update(self):
        # Mover el suelo
        self.rect.x -= scroll_speed  # Mueve el suelo hacia la izquierda
        if self.rect.x <= -win_width:
            self.kill()  # Elimina el suelo si sale de la pantalla

#=======================================#
# Función quit_game() : Maneja la salida del juego cuando se detecta el evento de cierre de la ventana.
#=======================================#

def quit_game():
    # Salir del juego
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

#=======================================#
# Método principal del juego : Contiene la lógica principal del juego,
# incluyendo la configuración de los objetos del juego, manejo de la entrada del usuario, actualización de la pantalla,
# detección de colisiones y reinicio del juego cuando el jugador pierde.
#=======================================#

def main():
    global score, game_stopped

    # Detener la música de la pantalla de inicio
    pygame.mixer.music.stop()

    # Instanciar la nave
    nave = pygame.sprite.GroupSingle()
    nave.add(Nave())

    # Configurar los tubos
    pipe_timer = 0  # Temporizador para la generación de tubos
    pipes = pygame.sprite.Group()  # Grupo para gestionar los tubos

    # Instanciar el suelo inicial
    x_pos_ground, y_pos_ground = 0, 520
    ground = pygame.sprite.Group()
    ground.add(Ground(x_pos_ground, y_pos_ground))

    game_over_sound_played = False  # Variable para controlar la reproducción del sonido de "game over"

    run = True
    while run:
        # Salir del juego
        quit_game()

        # Reiniciar el fotograma
        window.fill((0, 0, 0))  # Limpia la ventana

        # Entrada del usuario
        user_input = pygame.key.get_pressed()  # Obtiene la entrada del usuario

        # Dibujar el fondo
        window.blit(skyline_image, (0, 0))

        # Generar el suelo
        if len(ground) <= 2:
            ground.add(Ground(win_width, y_pos_ground))  # Agrega nuevo suelo cuando el actual sale de la pantalla

        # Dibujar - Tubos, suelo y nave
        pipes.draw(window)  # Dibuja los tubos en la ventana
        ground.draw(window)  # Dibuja el suelo en la ventana
        nave.draw(window)  # Dibuja la nave en la ventana

        # Mostrar la puntuación con un color llamativo (amarillo)
        score_text = font.render('PUNTAJE: ' + str(score), True, pygame.Color(255, 255, 0))
        window.blit(score_text, (20, 20))

        # Actualizar - Tubos, suelo y nave
        if nave.sprite.alive:
            pipes.update()  # Actualiza la posición de los tubos
            ground.update()  # Actualiza la posición del suelo
        nave.update(user_input)  # Actualiza la posición y estado de la nave

        # Detección de colisiones
        collision_pipes = pygame.sprite.spritecollide(nave.sprites()[0], pipes, False)
        collision_ground = pygame.sprite.spritecollide(nave.sprites()[0], ground, False)
        if collision_pipes or collision_ground:
            if nave.sprite.alive:  # Check if nave was previously alive
                nave.sprite.alive = False  # La nave muere si colisiona con un tubo o con el suelo
                crash_sound.play()  # Reproduce el sonido de choque
            if not game_over_sound_played:  # Reproduce el sonido de "game over" si no se
                                            # ha reproducido antes
                game_over_sound.play()  # Reproduce el sonido de "game over" si no se ha
                                        # reproducido antes
                game_over_sound_played = True  # Marca que el sonido ya ha sido reproducido

            if collision_ground:
                window.blit(game_over_image, (win_width // 2 - game_over_image.get_width() // 2,
                                              win_height // 2 - game_over_image.get_height() // 2))
                if user_input[pygame.K_r]:
                    score = 0  # Reinicia la puntuación
                    game_over_sound_played = False  # Reinicia la variable de control de sonido
                    game_stopped = True  # Detiene el juego
                    menu()  # Regresa al menú

        # Generar tubos
        if pipe_timer <= 0 and nave.sprite.alive:
            x_top, x_bottom = 550, 550  # Posición inicial de los tubos
            y_top = random.randint(-600, -480)  # Altura aleatoria del tubo superior
            y_bottom = y_top + random.randint(100, 140) + bottom_pipe_image.get_height()  # Altura del tubo inferior
            pipes.add(Pipe(x_top, y_top, top_pipe_image, 'top'))
            pipes.add(Pipe(x_bottom, y_bottom, bottom_pipe_image, 'bottom'))
            pipe_timer = random.randint(180, 250)  # Temporizador para el siguiente par de tubos
        pipe_timer -= 1

        clock.tick(60)  # Controla la velocidad del juego
        pygame.display.update()  # Actualiza la pantalla


#=======================================#
# Menú : El menú inicia la música de fondo, dibuja la pantalla inicial con gráficos
# y espera que el usuario presione la barra espaciadora para iniciar el juego, actualizando continuamente la pantalla.
#=======================================#

def menu():
    global game_stopped

    # Reproducir la música de la pantalla de inicio
    pygame.mixer.music.play(-1)

    while game_stopped:
        quit_game()

        # Dibujar menú
        window.fill((0, 0, 0))
        window.blit(skyline_image, (0, 0))
        window.blit(ground_image, Ground(0, 520))
        window.blit(nave_images[0], (100, 250))
        window.blit(start_image, (win_width // 2 - start_image.get_width() // 2,
                                  win_height // 2 - start_image.get_height() // 2))

        # Entrada del usuario
        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_SPACE]:
            main()  # Inicia el juego

        pygame.display.update()


menu()  # Muestra el menú inicial
