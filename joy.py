#!/usr/bin/env python3

import pygame

class Setup:
    size = (1600, 1200)
    log_size = (1600, 1200)
    fps = 30
    speed = 4
    scale = [log_size[0] / size[0], log_size[1] / size[1]]


class Color:
    black = (0, 0, 0)
    blue = (60, 100, 220)


class State:
    maxspeed = 10
    accel = 5
    slowdown = 1.3
    joy_thresh = 0.3

    def __init__(self):
        self.x = Setup.log_size[0] / 2
        self.y = Setup.log_size[1] / 2
        self.vec = [0, 0]

    def tick(self, xaxis, yaxis):
        vx = self.vec[0]
        vy = self.vec[1]

        if xaxis < -self.joy_thresh:
            vx = max(-self.maxspeed, vx - self.accel)
        elif xaxis > self.joy_thresh:
            vx = min(self.maxspeed, vx + self.accel)
        else:
            vx /= self.slowdown

        if yaxis < -self.joy_thresh:
            vy = max(-self.maxspeed, vy - self.accel)
        elif yaxis > self.joy_thresh:
            vy = min(self.maxspeed, vy + self.accel)
        else:
            vy /= self.slowdown

        self.x = max(0, min(Setup.log_size[0], self.x + vx))
        self.y = max(0, min(Setup.log_size[1], self.y + vy))
        self.vec = [vx, vy]

    def get_pos(self):
        return (int(self.x), int(self.y))


class App:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode(Setup.size)
        pygame.display.set_caption('Joystick')
        self.clock = pygame.time.Clock()
        self.state = State()

        pygame.joystick.init()
        num_joy = pygame.joystick.get_count()
        for j in range(num_joy):
            joy = pygame.joystick.Joystick(j)
            joy.init()
            print(f'joystick {j}: {joy.get_name()}')

    def stop(self):
        pygame.joystick.quit()
        pygame.quit()
        self.running = False

    def loop(self):
        self.clock.tick(Setup.fps)
        joystick = pygame.joystick.Joystick(0)
        xvalue = joystick.get_axis(0)
        yvalue = joystick.get_axis(1)
        self.state.tick(xvalue, yvalue)

    #def draw_player(self, x, y):
    #

    def render(self):
        self.display.fill(Color.black)
        x, y = self.state.get_pos()
        x = int(x * Setup.scale[0])
        y = int(y * Setup.scale[1])
        pygame.draw.rect(self.display, Color.blue, (x, y, 10, 10))
        pygame.display.update()

    def run(self):
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.stop()
                elif event.type == pygame.JOYAXISMOTION:
                    pass
                    # if event.joy == 0:
                    #    self.state = self.move(self.state, event.axis, event.value)
                    # print('joyaxismotion', event)
                elif event.type == pygame.JOYBUTTONDOWN:
                    pass
                    # print('joybuttondown', event)
                elif event.type == pygame.JOYBUTTONUP:
                    pass
                    # print('joybuttonup', event)
                elif event.type == pygame.JOYHATMOTION:
                    pass

            if not self.running:
                break

            self.loop()
            self.render()


if __name__ == '__main__':
    app = App()
    app.run()
