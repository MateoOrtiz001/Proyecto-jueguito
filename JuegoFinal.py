
from pyglet.window import key
from pyglet.image import load, ImageGrid, Animation
from cocos.sprite import Sprite
from cocos.layer import Layer
from cocos.scene import Scene
from cocos.director import director
from cocos.euclid import Vector2
from random import choice
from collections import defaultdict
from cocos.text import Label
from cocos.actions import Delay, CallFunc
from cocos.collision_model import CollisionManagerBruteForce, AARectShape


#Definimos la clase "Actor" para definir a todos los objetos
class Actor(Sprite):
    def __init__(self,imagen,x,y):
        super().__init__(imagen)
        self.position = Vector2(x, y)
        self.cshape = AARectShape(self.position,
                                  self.width * 0.5,
                                  self.height * 0.5)

    #Definimos el la actualización de los movimienos
    def move_ver(self, offset):
        self.position += offset
        self.cshape.center += offset

    def move_hor(self, offset):
        self.position += offset
        self.cshape.center += offset

    def update(self,delta_t):
        pass

#Definimos la clase "Personaje"
class Personaje(Actor):
    pulsar_tecla = defaultdict(int)
    def __init__(self,imagen, x, y):
        super().__init__(imagen, x, y)
        self.esta_lanzado = False
        self.velocidad = Vector2(400,0)

#Definimos el comportamiento del personaje
    def update(self, delta_t) :
        x = 0
        y = 12
        pulsar = Personaje.pulsar_tecla

        if  pulsar[key.SPACE] and self.esta_lanzado == False:
            self.image = load('Personaje.png')
            self.esta_lanzado = True
        elif self.esta_lanzado == True:
            self.move_ver(Vector2(x,y))
        else:
            movimiento = pulsar[key.RIGHT] - pulsar[key.LEFT]
            if movimiento != 0:
                delta_x = (self.velocidad * movimiento * delta_t)[0]
                if self.x  <= self.parent.ancho_ventana - self.width/2 - delta_x:
                    if self.x - self.width/2 + delta_x > abs(delta_x):
                        self.move_ver(self.velocidad * movimiento * delta_t)

        if self.y > self.parent.alto_ventana or self.y < 0:
            self.kill()
            director.replace(Scene(GameOver()))

    def on_exit(self):
        self.do(Delay(1) + CallFunc(self.parent.lanzar_personaje))


#Definimos la clase "Enemigo"
class Enemigo(Actor):
    def __init__(self,imagen, x, y):
        super().__init__(imagen, x, y)
        self.velocidad = Vector2(-200,0)
        self.velocidad2 = Vector2(0,200)
        self.contador = 0
        self.dir = choice([-1,1])
        self.dir2 = choice([-1,1])

    def update(self,delta_t):
        if 10 < (self.position[0] +(self.dir * self.velocidad * delta_t)[0]) < 750:
            if self.contador < 120:
                self.move_ver(self.dir * self.velocidad * delta_t)
                self.contador += 1
            else:
                self.contador = 0
                self.dir = choice([-1,1])
        else:
            self.dir *= -1
        if 500 < (self.position[1] + (self.dir2 * self.velocidad2 * delta_t)[1]) < 640:
            if self.contador < 500:
                self.move_hor(self.dir2 * self.velocidad2 * delta_t)
            else:
                self.dir2 = choice([-1,1])
        else:
            self.dir2 *= -1 

#Definimos la clase "Etiqueta"

class Etiqueta(Label):
    def __init__(self,texto,x,y, c = (255,255,255,255), fz = 25):
        super().__init__(texto, (x,y), font_name = 'System', font_size = fz, color = c, anchor_x='center', anchor_y='center')

#DEFINIMOS LAS CAPAS
#Definimos la clase "Inicio"
class Inicio(Layer):
    is_event_handler = True
    contador = 0
    def __init__(self):
        super().__init__()
        self.add(Etiqueta('Pulsa cualquier botón del ratón para comenzar', 400,350))
    def on_mouse_release(self,x,y,buttons,modifiers):
        a = HUD()
        director.replace(Scene(MiCapa(a), a))

#Definimos la clase "GameOver"
class GameOver(Layer):
    def __init__(self):
        super().__init__()
        self.add(Etiqueta('GameOver', 400, 325))
        self.do(Delay(3) + CallFunc(lambda:director.replace(Scene(Inicio()))))

#Definimos la clase "Ganador"
class Ganador(Layer):
    is_event_handler = True

    def __init__(self):
        super().__init__()
        self.fondo = Sprite(load('Fondo3.png'), (400,325))
        self.add(self.fondo,z=0)
        self.add(Etiqueta('Has Ganado', 400, 325,(1,1,1,255), 60 ))
        self.add(Etiqueta('Pulsa cualquier botón del ratón para volver al inicio', 400, 255,(1,1,1,255),20))

    def on_mouse_release(self,x,y,buttons,modifiers):
        director.replace(Scene(Inicio()))

#Definimos la clase "HUD"
class HUD(Layer):
    def __init__(self):
        super().__init__()
        self.puntos = 0
        self.update()

    def update(self):
        self.children = []
        texto1 = 'MATA A LOS ENEMIGOS'
        etiqueta1 = Etiqueta(texto1, 220, 620, (1,1,1,255))
        texto2 = 'Puntos: ' + str(self.puntos)
        etiqueta_puntos = Etiqueta(texto2, 680, 620, (1,1,1,255))
        self.add(etiqueta1)
        self.add(etiqueta_puntos)
        if self.puntos == 20:
            director.replace(Scene(Ganador()))

#Definimos la clase "MiCapa" en donde se mostrará el entorno
class MiCapa(Layer):
    is_event_handler = True

    def on_key_press(self,k,_):
        Personaje.pulsar_tecla[k] = 1
    def on_key_release(self,k,_):
        Personaje.pulsar_tecla[k] = 0


    def __init__(self,HUD):
        super().__init__()
        self.ancho_ventana, self.alto_ventana = director.get_window_size()
        self.man_col = CollisionManagerBruteForce()
        self.HUD = HUD
        self.lanzar_personaje()
        self.enemigo()
        self.schedule(self.update)
        # Cargamos el fondo
        self.fondo = Sprite(load('Fondo3.png'), (400,325))
        self.add(self.fondo,z=0)

#Posicionamos al personaje en la pantalla
    def lanzar_personaje(self):
        self.personaje = Personaje('Personaje.png', self.ancho_ventana * 0.5 ,50)
        self.add(self.personaje, z = 1)

#Posicionamos los enemigos en pantalla
    def enemigo(self):
        for i in range(2):
            self.enemigo = Enemigo("Enemigo.png", self.ancho_ventana * 0.5, 560 - i*40)
            self.add(self.enemigo, z = 1)

#Llamamos a todos los métodos update()
    def update(self, dt):
        self.man_col.clear()
        for _, node in self.children:
            if isinstance(node, Actor):
                node.update(dt)
        for _, node in self.children:
            if isinstance(node, Actor):
                self.man_col.add(node)

        self.collide(self.personaje)

#Definimos el método de colisiones
    def collide(self, node):
        if node is not None:
            for other in self.man_col.iter_colliding(node):
                if self.children.count((1, other)) != 0:
                    other.kill()
                    if isinstance(other,Enemigo):
                        self.HUD.puntos += 10
                        self.HUD.update()
                if self.children.count((1, node)) != 0:
                    node.kill()
                seq = ImageGrid(load('Explosion.png'), 1,1)
                anim = Animation.from_image_sequence(seq, 0.05, False)
                self.sprite = Sprite(anim, (other.x, other.y))
                self.add(self.sprite)
                self.do(Delay(0.8) + CallFunc(self.sprite.kill))


if __name__ == '__main__':
    ventana = director.init(caption="Videojuego", width=800, height=650)
    ventana.set_location(300,50)
    director.run(Scene(Inicio()))
