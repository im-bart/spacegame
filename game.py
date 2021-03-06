#! python 3

import math
import pygame
from random import randrange, choice
from pprint import pprint

universe = {
	'alpha': [
		{
			'type': 'station',
			'pos': [23049, 12309]
		},
		{
			'type': 'gate',
			'pos': [1230, 130913],
			'dest': 'beta'
		}
	],
	'beta': [
		{
			'type': 'station',
			'pos': [13424, -35932]
		},
		{
			'type': 'gate',
			'pos': [2345, 12303],
			'dest': 'alpha'
		}
	]
}

grad = math.pi / 180
def radians_to_degrees(radians):
    return (radians / math.pi) * 180.0
def degrees_to_radians(degrees):
    return degrees * (math.pi / 180.0)


class Viewport:
	def __init__(self, width, height):
		self.width, self.height = int(width), int(height)
		self.update(0, 0, 0, 0, 0.0)

	def update(self, x, y, dx, dy, v):
		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy
		self.v = v

	def get_x(self, rx):
		return (rx - self.x) + self.width / 2

	def get_y(self, ry):
		return (ry - self.y) + self.height / 2

	def get_player_x(self):
		return self.x

	def get_player_y(self):
		return self.y


class Text(pygame.sprite.Sprite):
	id = 1
	collection = {}
	def __init__(self, content, position):
		self.id = Text.id
		Text.id += 1
		Text.collection[self.id] = self
		pygame.sprite.Sprite.__init__(self, self.groups)
		self.font = pygame.font.Font('resources/fonts/Volter__28Goldfish_29.ttf', 9)
		self.x, self.y = position[0], position[1]
		self.setContent(content)

	def update(self, viewport, frametime):
		pass

	def setContent(self, content):
		self.image = self.font.render(content, False, (255,255,255))
		self.rect = self.image.get_rect()
		self.rect.x = self.x
		self.rect.y = self.y

	def setPosition(self, position):
		self.x = position[0]
		self.y = position[1]
		self.rect.x = self.x
		self.rect.y = self.y

class OffscreenLabel(Text):
	def __init__(self, content, object):
		self.object = object
		Text.__init__(self, content, [-999,-999])

	def update(self, viewport, frametime):
		x0 = viewport.width / 2
		y0 = viewport.height / 2
		x1 = viewport.get_x(self.object.rx)
		y1 = viewport.get_y(self.object.ry)

		if (x1 + self.object.rect.width) > 0 and x1 < viewport.width and (y1 + self.object.rect.height) > 0 and y1 < viewport.height:
			self.setPosition([-900,-900])
			return

		m = (y0 - y1) / (x0 - x1)
		x2 = 1
		if x1 > x0:
			x2 = viewport.width - self.rect.width - 1
		y2 = m * (x2 - x1) + y1
		
		if y2 < 1:
			y2 = 1
			x2 = (y2 - y1) / m + x1
		if y2 > viewport.height - self.rect.height - 1:
			y2 = viewport.height - self.rect.height - 1
			x2 = (y2 - y1) / m + x1

		self.setPosition([x2, y2])

class Ship(pygame.sprite.Sprite):
	id = 1
	collection = {}
	def __init__(self, start = [0,0], direction = 0):
		self.id = Ship.id
		Ship.id += 1
		Ship.collection[self.id] = self
		pygame.sprite.Sprite.__init__(self, self.groups)
		self.rx = start[0]
		self.ry = start[1]
		self.direction = direction
		self.angle = degrees_to_radians(direction)
		self.dx = math.sin(self.angle)
		self.dy = math.cos(self.angle)
		self.speed = 0.0
		self.sprite = pygame.image.load('resources/sprites/rifter.png')
		self.image = self.sprite
		self.rect = self.image.get_rect()

	def turn(self, change):
		if (change > 0):
			self.direction -= 5
		else:
			self.direction += 5
		if self.direction > 360:
			self.direction -= 360
		if self.direction < 0:
			self.direction += 360
			
		self.angle = degrees_to_radians(self.direction)
		self.dx = math.sin(self.angle)
		self.dy = math.cos(self.angle)

	def accelerate(self):
		self.speed += 0.2
		if self.speed > 4.0:
			self.speed = 4.0

	def deccelerate(self):
		self.speed -= 0.2
		if self.speed < 0.0:
			self.speed = 0

	def update(self, viewport, frametime):
		if self.speed > 0.0:
			self.rx += self.dx * self.speed
			self.ry += self.dy * self.speed
			self.speed -= 0.1

		self.x = viewport.get_x(self.rx)
		self.y = viewport.get_y(self.ry)
		self.image = pygame.transform.rotate(self.sprite, self.direction - 180)
		self.rect = self.image.get_rect()
		self.rect.centerx = self.x
		self.rect.centery = self.y

	def __del__(self):
		# kill anything related here (such as text sprites)
		pass


class AI(Ship):
	def __init__(self, start, direction):
		Ship.__init__(self, start, direction)
		self.offscreenLabel = OffscreenLabel('NPC', self)

	def update(self, viewport, frametime):
		Ship.update(self, viewport, frametime)
		

class Player(Ship):
	def __init__(self, system, start = [0,0], direction = 0):
		Ship.__init__(self, start, direction)
		self.system = system

	def update(self, viewport, frametime):
		Ship.update(self, viewport, frametime)
		self.x = viewport.width / 2
		self.y = viewport.height / 2
		self.rect.centerx = self.x
		self.rect.centery = self.y
		viewport.update(self.rx, self.ry, self.dx, self.dy, self.speed)


class Structure(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self, self.groups)

	def update(self, viewport, frametime):
		pass

class Station(Structure):
	def __init__(self, name, position):
		Structure.__init__(self)
		self.rx = position[0]
		self.ry = position[1]
		self.sprite = pygame.image.load('resources/sprites/outpost.png')
		self.image = self.sprite
		self.offscreenLabel = OffscreenLabel(name, self)

	def update(self, viewport, frametime):
		self.x = viewport.get_x(self.rx)
		self.y = viewport.get_y(self.ry)
		self.rect = self.image.get_rect()
		self.rect.x = self.x
		self.rect.y = self.y


class Projectile(pygame.sprite.Sprite):
	lifetime_max = 10.0
	def __init__(self, owner):
		pygame.sprite.Sprite.__init__(self, self.groups)
		self.lifetime = 0.0
		self.owner = owner
		self.rx = self.owner.rx
		self.ry = self.owner.ry
		self.dx = self.owner.dx
		self.dy = self.owner.dy
		self.direction = self.owner.direction
		self.sprite = pygame.Surface((10,10))
		self.sprite.fill((0,0,0))
		pygame.draw.rect(self.sprite, (255,255,255), (4,0,1,10))
		self.x = self.owner.x
		self.y = self.owner.y
		self.image = pygame.transform.rotate(self.sprite, self.direction - 180)
		self.rect = self.image.get_rect()
		self.speed = 10.0

	def update(self, viewport, frametime):
		self.lifetime += frametime
		if (self.lifetime > Projectile.lifetime_max):
			self.kill()
		self.rx += self.dx * self.speed
		self.ry += self.dy * self.speed
		self.x = viewport.get_x(self.rx)
		self.y = viewport.get_y(self.ry)
		self.rect.centerx = self.x
		self.rect.centery = self.y


class Dust(pygame.sprite.Sprite):
	particles = []
	def __init__(self, viewport):
		pygame.sprite.Sprite.__init__(self, self.groups)
		self.viewport = viewport
		self.tl = int(viewport.width - viewport.width * 1.1)
		self.tr = int(viewport.width * 1.1)
		self.tt = int(viewport.height - viewport.height * 1.1)
		self.tb = int(viewport.height * 1.1)
		for i in range(200):
			particle = [randrange(self.tl, self.tr), 
						randrange(self.tt, self.tb),
						choice([0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.3, 0.3, 0.4, 0.5, 0.75, 1.0, 1.5, 2.0])]
			self.particles.append(particle)
		self.x = 0
		self.y = 0

	def update(self, viewport, frametime):
		self.image = pygame.Surface((viewport.width, viewport.height))
		# self.image.blit(backdrop, backdrop.get_rect())
		# self.image.fill((0,0,0))
		for particle in self.particles:
			particle[0] -= viewport.dx * viewport.v * particle[2]
			particle[1] -= viewport.dy * viewport.v * particle[2]
			
			if particle[0] < self.tl:
				particle[0] = randrange(viewport.width, self.tr)
			if particle[0] > self.tr:
				particle[0] = randrange(self.tl, 0)
			if particle[1] < self.tt:
				particle[1] = randrange(viewport.height, self.tb)
			if particle[1] > self.tb:
				particle[1] = randrange(self.tt, 0)
			
			if particle[2] >= 0.0:
				color = (20,20,20)
			if particle[2] >= 0.2:
				color = (40,40,40)
			if particle[2] >= 0.4:
				color = (80,80,80)
			if particle[2] >= 0.6:
				color = (100,100,100)
			if particle[2] >= 1.0:
				color = (140,140,140)
			if particle[2] >= 1.5:
				color = (180,180,180)
			if particle[2] >= 2.0:
				color = (220,220,220)
			self.image.fill(color, (particle[0],particle[1],1,1))

		self.rect = self.image.get_rect()
		self.x = 0
		self.y = 0


pygame.init()
# display = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
display = pygame.display.set_mode((1280,800), pygame.FULLSCREEN)
pygame.display.set_caption('Spacegame');
screenInfo = pygame.display.Info()
screenWidth, screenHeight = int(screenInfo.current_w / 2), int(screenInfo.current_h / 2)
screen = pygame.Surface((screenWidth, screenHeight))
# backdrop = pygame.image.load('resources/images/bg3.png')

EVENT_WARP = pygame.USEREVENT + 1
EVENT_JUMP = pygame.USEREVENT + 2

clock = pygame.time.Clock()
fps = 60
playtime = 0.0 # seconds
viewport = Viewport(screenWidth, screenHeight)

keys = [False, False, False, False, False] # up, down, left, right, space

shipGroup = pygame.sprite.Group()
structureGroup = pygame.sprite.Group()
textGroup = pygame.sprite.Group()
dustGroup = pygame.sprite.Group()
projectileGroup = pygame.sprite.Group()
everythingGroup = pygame.sprite.LayeredUpdates()

Text._layer = 11
Ship._layer = 10
Structure._layer = 9
Projectile._layer = 9
Dust._layer = 8

Ship.groups = shipGroup, everythingGroup
Structure.groups = structureGroup, everythingGroup
Text.groups = textGroup, everythingGroup
Projectile.groups = projectileGroup, everythingGroup
Dust.groups = dustGroup, everythingGroup

player = Player('alpha', [0,0], 0)
viewport.update(player.rx, player.ry, player.dx, player.dy, player.speed)
npc = AI([20,20], 0)
outpost = Station('Outpost 3A', [-120,-400])
ui_status = Text('Game started', [screenWidth / 2, 5])
ui_system_h = Text('Current system:', [8, 5])
ui_system_p = Text(player.system, [8, 17])
dust = Dust(viewport)

gameloop = True
while gameloop:
	frametime = clock.tick(fps) / 1000
	playtime += frametime
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			gameloop = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				keys[0] = True
			if event.key == pygame.K_s:
				keys[1] = True
			if event.key == pygame.K_a:
				keys[2] = True
			if event.key == pygame.K_d:
				keys[3] = True
			if event.key == pygame.K_SPACE:
				keys[4] = True
			if event.key == pygame.K_ESCAPE:
				gameloop = False
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_w:
				keys[0] = False
			if event.key == pygame.K_s:
				keys[1] = False
			if event.key == pygame.K_a:
				keys[2] = False
			if event.key == pygame.K_d:
				keys[3] = False
			if event.key == pygame.K_SPACE:
				keys[4] = False
			
	if keys[0]: # w
		player.accelerate()
	elif keys[1]: # s
		player.deccelerate()
	if keys[2]: # a
		player.turn(-1)
	elif keys[3]: # d
		player.turn(1)
	if keys[4]:
		Projectile(player)
		keys[4] = False;

	# uncomment if spacedust feels laggy:
	# viewport.update(player.rx, player.ry, player.dx, player.dy)
	ui_status.setContent(str(round(player.rx)) + ', ' + str(round(player.ry)))

	# move towards player
	# move away if player has firing solution (arctangent)

	npc.accelerate()
	if abs(player.rx - npc.rx) < 50 and abs(player.ry - npc.ry) < 50:
		npc.turn(-1)
	else:
		npc.turn(1)
	
	everythingGroup.update(viewport, frametime)
	everythingGroup.draw(screen)

	pygame.transform.scale(screen, (screenInfo.current_w, screenInfo.current_h), display)
	pygame.display.update()
	
pygame.quit()
exit(0)