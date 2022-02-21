import pygame
import math
import csv
import random
import os

# init pygame
pygame.init()
# const parameters for the program
WIDTH, HEIGHT=800, 800
WHITE=(255, 255, 255)
FPS=120
SECONDS_IN_FRAME=24 * 3600

# creating the display for the simulation
WIN=pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulation")
FONT=pygame.font.SysFont('comicsans', 16)

class Planet:
    """
    class representing a planet
    """
    AU=149.6e6 * 1000  # the average distance of earth to the sun used in this simulation as a repentance distance
    G=6.67428e-11  # the constant parameter of gravity
    SCALE=(WIDTH / 4) / AU  # a measure designed to make the relationship accurately on screen
    TIMESTEP=SECONDS_IN_FRAME  # starting with 1 day per frame

    def __init__(self, name, x, y, radios, color, mass):
        self.x=x
        self.y=y
        self.radios=radios
        self.color=color
        self.mass=mass
        self.name=name
        self.orbit=[]  # the previous point in space that this planet was
        self.x_vel=0
        self.y_vel=0

    def render(self, win):
        """
        render the planet into the screen
        """
        x=self.x * self.SCALE + WIDTH / 2  # scaling the point into the screen
        y=self.y * self.SCALE + HEIGHT / 2  # scaling the point into the screen
        if len(self.orbit) > 2:  # create a line that represents the jorbit of the planet
            update_points=[]

            for point in self.orbit:
                x_p, y_p=point
                x_p=x_p * self.SCALE + WIDTH / 2
                y_p=y_p * self.SCALE + HEIGHT / 2
                update_points.append((x_p, y_p))
            pygame.draw.lines(win, self.color, False, update_points, 2)
        pygame.draw.circle(win, self.color, (x, y), self.radios)
        name_text=FONT.render(self.name, 1, WHITE)
        win.blit(name_text, (x - name_text.get_width() / 2, y - name_text.get_height()))

    def attraction(self, other):
        """
        Calculates the gravitational force that the other body affects
        """
        other_x, other_y=other.x, other.y
        dis_x=(other_x - self.x)
        dis_y=(other_y - self.y)
        distance=math.sqrt(dis_x ** 2 + dis_y ** 2)
        force=self.G * self.mass * other.mass / distance ** 2  # using the equation G*(M1*M2)/R^2
        theta=math.atan2(dis_y, dis_x)  # the angle of the vector force
        force_x=math.cos(theta) * force  # the force on x scale
        force_y=math.sin(theta) * force  # the force on y scale
        return force_x, force_y

    def update_positions(self, planets):
        """
        update the planet position based on the forces that the other planets infloences
        """
        totals_fx=totals_fy=0
        for planet in planets:
            if planet == self:
                continue
            fx, fy=self.attraction(planet)
            totals_fx+=fx
            totals_fy+=fy
        self.x_vel+=totals_fx / self.mass * self.TIMESTEP
        self.y_vel+=totals_fy / self.mass * self.TIMESTEP
        self.x+=self.x_vel * self.TIMESTEP
        self.y+=self.y_vel * self.TIMESTEP
        point=(self.x, self.y)

        self.orbit.append(point)

        if len(self.orbit) > 800:
            self.orbit.remove(self.orbit[0])

    def inside_screen(self):
        x=self.x * self.SCALE + WIDTH / 2  # scaling the point into the screen
        y=self.y * self.SCALE + HEIGHT / 2  # scaling the point into the screen
        limits=100
        return -limits < x < WIDTH + limits and -limits < y < HEIGHT + limits


def get_planets_from_file():
    """
    creating planets from a csv file added to the pogram
    :return: the planets from the file
    """
    planets=[]
    if not os.path.isfile("plantes.csv"):  # if there is not file
        return planets
    with open("plantes.csv", "r") as planetsFile:
        reader=csv.DictReader(planetsFile)
        for planet in reader:
            name=planet['name']
            x=float(planet['X']) * Planet.AU
            y=float(planet['Y']) * Planet.AU
            radios=int(planet['radios'])
            color=(int(planet['R']), int(planet['G']), int(planet['B']))
            mass=float(planet['MASS'])
            y_val=float(planet['y_val'])
            x_vel=float(planet['x_vel'])
            p=Planet(name, x, y, radios, color, mass)
            p.y_vel=y_val
            p.x_vel=x_vel
            planets.append(p)
        return planets


def render_new_Planet(win, planet_size, planet_pos, mouse_pos, new_planet_color):
    pygame.draw.circle(win, new_planet_color, planet_pos, planet_size)
    pygame.draw.line(win, WHITE, planet_pos, mouse_pos)


def create_new_planet(planet_size, planet_pos, mouse_pos, planet_color, planet_num):
    val_x=100 * (planet_pos[0] - mouse_pos[0])
    val_y=100 * (planet_pos[1] - mouse_pos[1])
    x=(planet_pos[0] - WIDTH / 2) / Planet.SCALE
    y=(planet_pos[1] - HEIGHT / 2) / Planet.SCALE
    mass=5 * 10 ** (10 + planet_size)
    planet=Planet("new Planet " + str(planet_num), x, y, planet_size, planet_color, mass)
    planet.x_vel=val_x
    planet.y_vel=val_y
    return planet


def init_simulation():
    sun=Planet("sun", 0, 0, 30, (240, 240, 0), 1.99 * 10 ** 30)
    planets=[sun]
    planets.extend(get_planets_from_file())
    return planets


def render_screen(win):
    win.fill((0, 0, 0))
    render_time=round(Planet.TIMESTEP * FPS / SECONDS_IN_FRAME, 2)
    above_text="Simulation Time : "
    above_text_box=FONT.render(above_text, 1, WHITE)
    win.blit(above_text_box, (20, 20))
    below_text=str(render_time) + " days / second"
    below_text_box=FONT.render(below_text, 1, WHITE)
    win.blit(below_text_box, (20, 20 + above_text_box.get_height()))


def main():
    run=True
    clock=pygame.time.Clock()
    planets=init_simulation()
    pause_simulation=False
    new_planet_mode=False
    new_planet_pos=(0, 0)
    new_planet_size=10
    new_planet_color=(0, 0, 0)
    while run:
        clock.tick(FPS)
        render_screen(WIN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
            if event.type == pygame.KEYDOWN:
                key_down=event.unicode
                if key_down == 'r':
                    planets=init_simulation()
                    continue
                if key_down == 'd':
                    Planet.TIMESTEP*=1.1
                if key_down == 'a':
                    Planet.TIMESTEP*=1 / 1.1
                if key_down == 'w':
                    Planet.TIMESTEP+=SECONDS_IN_FRAME/FPS
                if key_down == 's':
                    Planet.TIMESTEP-=SECONDS_IN_FRAME/FPS
                if key_down == ' ':
                    pause_simulation=not pause_simulation
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not new_planet_mode:
                new_planet_mode=True
                new_planet_size=10
                new_planet_pos=pygame.mouse.get_pos()
                new_planet_color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and new_planet_mode:
                planets.append(
                    create_new_planet(new_planet_size, new_planet_pos, pygame.mouse.get_pos(), new_planet_color,
                                      len(planets)))
                new_planet_mode=False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                new_planet_mode=False
            if event.type == pygame.MOUSEWHEEL and new_planet_mode:
                new_planet_size+=event.y
        if new_planet_mode:
            render_new_Planet(WIN, new_planet_size, new_planet_pos, pygame.mouse.get_pos(), new_planet_color)
        for planet in planets:
            if not planet.inside_screen():
                planets.remove(planet)
                continue
            if not pause_simulation:
                planet.update_positions(planets)
            planet.render(WIN)
        pygame.display.update()
    pygame.quit()


if __name__ == "__main__":
    main()
