
""" This is a template for an actor """

import pygame
import random
import math

import serge.actor
import serge.common
import serge.visual
import serge.blocks.behaviours

from theme import G

class Player(serge.blocks.actors.ScreenActor):
    def addedToWorld(self, world):
        super(Player, self).addedToWorld(world)
        # TODO set a particular color
        self.setSpriteName('default-car')
        self.setLayerName('main')
        #
        # Assign behaviour
        self.speed = G('player-speed')
        self.manager = world.findActorByName('behaviours')
        self.keyboard = serge.engine.CurrentEngine().getKeyboard()
        self.manager.assignBehaviour(
            self,
            KeyControl(),
            'player-movement'
            )
        #
        # Assign physical attributes
        self.force = 500
        pc = self.physical_conditions
        pc.mass = 1500
        pc.width = 48
        pc.height = 64
        pc.friction = 10
        #
        # Place the player properly
        self.moveTo(G('player-x'), G('player-y'))
        #
        # keys constants
        self.GO = 0
        self.BRAKE = 1
        self.LEFT = 2
        self.RIGHT = 3
        self.HANDBRAKE = 4
        self.keys = [0, 0, 0, 0, 0]

    def updateActor(self, interval, world):
        """ Update the car's speed and direction """
        #
        # Update forces and aquire speed
        body = self.physical_conditions.body
        body.reset_forces()
        self.speed = math.sqrt(body.velocity[0] ** 2 + body.velocity[1] ** 2)
        #
        # Handle turn left or turn right
        if self.keys[self.LEFT] and self.speed > 20:
            body.angle -= 0.04
            if not self.keys[self.HANDBRAKE]:
                temp_angle = body.angle - math.pi / 2
                body.apply_impulse(
                    (math.cos(temp_angle) * self.force * 0.02,
                     math.sin(temp_angle) * self.force * 0.02))
                self.brake(0.97)
            else:
                # The car slip
                body.angle -= 0.04
        if self.keys[self.RIGHT] and self.speed > 20:
            body.angle += 0.04
            if not self.keys[self.HANDBRAKE]:
                temp_angle = body.angle + math.pi / 2
                body.apply_impulse(
                    (math.cos(temp_angle) * self.force * 0.02,
                     math.sin(temp_angle) * self.force * 0.02))
                self.brake(0.97)
            else:
                # The car slip
                body.angle += 0.04

        #
        # Leave trace on the road
        if self.keys[self.HANDBRAKE] and self.speed > 200 and random.randint(1, 5) != 4:
            self.trace()
        #
        # the car go foward
        force_x = math.cos(body.angle) * self.force
        force_y = math.sin(body.angle) * self.force
        if self.keys[self.GO]:
            body.apply_force((force_x, force_y), (0, 0))
        if self.keys[self.BRAKE] or \
            (self.keys[self.HANDBRAKE] and self.speed < 200):
            self.brake(0.8)
        #
        # handle friction
        if body.velocity != (0, 0):
            self.brake(0.97)
        #
        # update camera
        # TODO WRAP it and make it more fluent.
        # TODO Rotate the camera according to the direction of the velocity
        camera = serge.engine.CurrentEngine().renderer.getCamera()
        dx, dy = self.getRelativeLocationCentered(camera)
        if dx < 100 and dx > -100 and dy < 100 and dy > -100:
            camera.update(10)
        else:
            while not (dx < 100 and dx > -100 and dy < 100 and dy > -100):
                camera.update(10)
                dx, dy = self.getRelativeLocationCentered(camera)
        #
        # save the last position
        self.last_pos = (self.x, self.y)

    def brake(self, value):
        """ Slow down the car """
        body = self.physical_conditions.body
        body.velocity[0] *= value
        body.velocity[1] *= value

    def trace(self):
        # TODO make two traces for both wheels
        """ Leave some trace on the road """
        world = serge.engine.CurrentEngine().getWorld('main-screen')
        ground = world.findActorByName('ground')
        ground_surface = ground._visual.getSurface()
        pygame.draw.line(
            ground_surface,
            (0x50, 0x50, 0x50),
            (self.last_pos[0] + G('track-width') / 2,
                self.last_pos[1] + G('track-height') / 2),
            (self.x + G('track-width') / 2,
                self.y + G('track-height') / 2),
            10
            )
        ground._visual.setSurface(ground_surface)

class KeyControl(serge.blocks.behaviours.Behaviour):
    """ Control the car with keyboard """

    def __call__(self, world, actor, interval):
        """ Control the car with A, S, D, W and the space key"""
        actor.keys[actor.HANDBRAKE] = actor.keyboard.isDown(pygame.K_SPACE)
        actor.keys[actor.LEFT] = actor.keyboard.isDown(pygame.K_a)
        actor.keys[actor.RIGHT] = actor.keyboard.isDown(pygame.K_d)
        actor.keys[actor.BRAKE] = actor.keyboard.isDown(pygame.K_s)
        actor.keys[actor.GO] = actor.keyboard.isDown(pygame.K_w)

