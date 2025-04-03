#!/usr/bin/python3

# All the Bunnies in the Meadow Die: an illustration by simulation

# this code uses tabs for indentation, set your editor appropriately.

import pygame
import matplotlib.pyplot as plt
import random

# options. defaults create a square fenced meadow that can support about 1000 bunnies, displayed as an 800x800 window.
RANDOM_SEED = None
MEADOW_WIDTH = 100
MEADOW_HEIGHT = 100
PATCH_DRAW_SIZE = 8
GREENS_COLOR = (0, 200, 0)
DIRT_COLOR = (100, 100, 0)
BUNNY_COLOR = (255, 255, 255)
SHOW_BUNNY_HIGHLIGHTS = False
MALE_BUNNY_HIGHLIGHT_COLOR = (0, 0, 255)
FEMALE_BUNNY_HIGHLIGHT_COLOR = (255, 0, 0)
MEADOW_WRAPS_AROUND = False
MAX_GREENS_PER_PATCH = 100
GREENS_GROWTH_RATE = 0.0155
STARTING_BUNNIES_MALE = 10
STARTING_BUNNIES_FEMALE = 10
BUNNY_MINIMUM_HOPS_PER_TURN = 2
BUNNY_MAXIMUM_HOPS_PER_TURN = 10
BUNNY_STARTING_ENERGY = 100
BUNNY_HUNGER = 10
BUNNY_MATING_CHANCE = 0.2
SCALE_MATING_CHANCE_WITH_ENERGY = True
BUNNY_MATING_MINIMUM_RECOVERY_TIME = 100
BUNNY_MINIMUM_LITTER_SIZE = 2
BUNNY_MAXIMUM_LITTER_SIZE = 10
BUNNY_MINIMUM_NATURAL_LIFESPAN = 30 * BUNNY_MATING_MINIMUM_RECOVERY_TIME
BUNNY_MAXIMUM_NATURAL_LIFESPAN = 40 * BUNNY_MATING_MINIMUM_RECOVERY_TIME
# end of options. these constants are used with reckless global-scope abandon below.

def main():
	random.seed(RANDOM_SEED)
	pygame.init()
	surface = pygame.display.set_mode((MEADOW_WIDTH * PATCH_DRAW_SIZE, MEADOW_HEIGHT * PATCH_DRAW_SIZE))
	meadow = Meadow()
	bunnies = meadow.get_bunnies()
	population_data = []
	time_count = 0
	running = True
	while running and bunnies:
		for event in pygame.event.get():	# poll for events
			if event.type == pygame.QUIT:	# the user clicked X to close the window
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
		time_count += 1
		population_data.append(len(bunnies))
		# first, grow the greens and remove any dead bunnies
		for i in range(MEADOW_WIDTH):
			for j in range(MEADOW_HEIGHT):
				this_patch = meadow.get_patch((i,j))
				this_patch.grow_greens()
				for b in this_patch.bunnies:
					if not b.is_alive(): this_patch.move_out(b)
		# then the bunnies do their bunny thing
		bunnies = meadow.get_bunnies()
		for b in bunnies:
			b.hunger()
			if b.is_alive():
				for i in range(b.speed):
					b.hop(meadow)
					b.mate(meadow, time_count)
				b.eat(meadow)
			if b.birth_time + b.lifespan < time_count:
				b.die()
		pygame.display.set_caption("Time: " + str(time_count) + " Population: " + str(len(bunnies)))
		render(surface, meadow)
	pygame.quit()
	if running:
		fig, ax = plt.subplots()
		fig.canvas.manager.set_window_title("Result")
		ax.set(xlabel="Time", ylabel="Bunnies", title="All the bunnies in the meadow die.")
		ax.plot(population_data, color="red")
		ax.legend(["Bunny population"])
		plt.show()

def render(surface, meadow):
	surface.fill("black")
	for i in range(MEADOW_WIDTH):
		for j in range(MEADOW_HEIGHT):
			square = pygame.Rect(i * PATCH_DRAW_SIZE, j * PATCH_DRAW_SIZE, PATCH_DRAW_SIZE, PATCH_DRAW_SIZE)
			pygame.draw.rect(surface, meadow.get_patch((i,j)).color(), square)
			if meadow.get_patch((i,j)).bunnies:
				pygame.draw.circle(surface, BUNNY_COLOR, ((i + 0.5) * PATCH_DRAW_SIZE, (j + 0.5) * PATCH_DRAW_SIZE), PATCH_DRAW_SIZE * 0.4)
				first_bunny = meadow.get_patch((i,j)).bunnies[0]
				if SHOW_BUNNY_HIGHLIGHTS:
					if first_bunny.sex == "male":
						pygame.draw.circle(surface, MALE_BUNNY_HIGHLIGHT_COLOR, ((i + 0.5) * PATCH_DRAW_SIZE, (j + 0.5) * PATCH_DRAW_SIZE), PATCH_DRAW_SIZE * 0.4, width=1)
					else:	# female
						pygame.draw.circle(surface, FEMALE_BUNNY_HIGHLIGHT_COLOR, ((i + 0.5) * PATCH_DRAW_SIZE, (j + 0.5) * PATCH_DRAW_SIZE), PATCH_DRAW_SIZE * 0.4, width=1)
	pygame.display.flip()

class Patch:
	def __init__(self):
		self.greens = MAX_GREENS_PER_PATCH
		self.bunnies = []
	def move_in(self, bunny):
		self.bunnies.append(bunny)
	def move_out(self, bunny):
		self.bunnies.remove(bunny)
	def grow_greens(self):
		self.greens += self.greens * GREENS_GROWTH_RATE
		if self.greens > MAX_GREENS_PER_PATCH: self.greens = MAX_GREENS_PER_PATCH
	def get_eaten(self, desired_amount):
		amount_eaten = desired_amount
		if amount_eaten > self.greens: amount_eaten = self.greens
		self.greens -= amount_eaten
		return amount_eaten
	def color(self):
		alive_ratio = self.greens / MAX_GREENS_PER_PATCH
		r = (GREENS_COLOR[0] * alive_ratio) + (DIRT_COLOR[0] * (1 - alive_ratio))
		g = (GREENS_COLOR[1] * alive_ratio) + (DIRT_COLOR[1] * (1 - alive_ratio))
		b = (GREENS_COLOR[2] * alive_ratio) + (DIRT_COLOR[2] * (1 - alive_ratio))
		return (r, g, b)

class Meadow:
	def __init__(self):
		self.patches = []
		for i in range(MEADOW_WIDTH):
			self.patches.append([])
			for j in range(MEADOW_HEIGHT):
				self.patches[i].append(Patch())
		for i in range(STARTING_BUNNIES_MALE):
			random_position = (random.randrange(MEADOW_WIDTH), random.randrange(MEADOW_HEIGHT))
			self.get_patch(random_position).move_in(Bunny(-1 * BUNNY_MATING_MINIMUM_RECOVERY_TIME, random_position, sex="male"))
		for i in range(STARTING_BUNNIES_FEMALE):
			random_position = (random.randrange(MEADOW_WIDTH), random.randrange(MEADOW_HEIGHT))
			self.get_patch(random_position).move_in(Bunny(-1 * BUNNY_MATING_MINIMUM_RECOVERY_TIME, random_position, sex="female"))
	def get_bunnies(self):
		bunny_list = []
		for i in range(MEADOW_WIDTH):
			for j in range(MEADOW_HEIGHT):
				for b in self.get_patch((i,j)).bunnies:
					if b.is_alive: bunny_list.append(b)
		return sorted(bunny_list, key=lambda b: b.id)
	def get_patch(self, position):
		x, y = position
		return self.patches[x][y]
	def get_neighbor_position(self, position, direction):
		x, y = position
		neighbor_position = None
		if direction == "N":
			if y > 0 or MEADOW_WRAPS_AROUND:
				neighbor_position = (x, (y-1) % MEADOW_HEIGHT)
		elif direction == "NE":
			if (x < (MEADOW_WIDTH - 1) and y > 0) or MEADOW_WRAPS_AROUND:
				neighbor_position = ((x+1) % MEADOW_WIDTH, (y-1) % MEADOW_HEIGHT)
		elif direction == "E":
			if x < (MEADOW_WIDTH - 1) or MEADOW_WRAPS_AROUND:
				neighbor_position = ((x+1) % MEADOW_WIDTH, y)
		elif direction == "SE":
			if (x < (MEADOW_WIDTH - 1) and y < (MEADOW_HEIGHT - 1)) or MEADOW_WRAPS_AROUND:
				neighbor_position = ((x+1) % MEADOW_WIDTH, (y+1) % MEADOW_HEIGHT)
		elif direction == "S":
			if y < (MEADOW_HEIGHT - 1) or MEADOW_WRAPS_AROUND:
				neighbor_position = (x, (y+1) % MEADOW_HEIGHT)
		elif direction == "SW":
			if (x > 0 and y < (MEADOW_HEIGHT - 1)) or MEADOW_WRAPS_AROUND:
				neighbor_position = ((x-1) % MEADOW_WIDTH, (y+1) % MEADOW_HEIGHT)
		elif direction == "W":
			if x > 0 or MEADOW_WRAPS_AROUND:
				neighbor_position = ((x-1) % MEADOW_WIDTH, y)
		elif direction == "NW":
			if (x > 0 and y > 0) or MEADOW_WRAPS_AROUND:
				neighbor_position = ((x-1) % MEADOW_WIDTH, (y-1) % MEADOW_HEIGHT)
		return neighbor_position

class Bunny:
	id = 0
	def __init__(self, birth_time, position, energy=BUNNY_STARTING_ENERGY, sex=None):
		Bunny.id += 1
		self.id = Bunny.id
		self.birth_time = birth_time
		self.position = position
		self.energy = energy
		self.sex = sex
		if not self.sex: self.sex = random.choice(["male", "female"])
		self.last_mate_time = birth_time
		self.speed = random.randint(BUNNY_MINIMUM_HOPS_PER_TURN, BUNNY_MAXIMUM_HOPS_PER_TURN)
		self.lifespan = random.randint(BUNNY_MINIMUM_NATURAL_LIFESPAN, BUNNY_MAXIMUM_NATURAL_LIFESPAN)
	def is_alive(self):
		return self.energy > 0
	def hunger(self):
		# it never stops.
		self.energy -= BUNNY_HUNGER
	def hop(self, meadow):
		# hop in a semi-random direction, generally toward greener patches
		options = []
		options.append(self.position)
		weights = []
		weights.append(int(meadow.get_patch(self.position).greens) ** 2 + 1)
		for d in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]:
			neighbor_position = meadow.get_neighbor_position(self.position, d)
			if neighbor_position:
				options.append(neighbor_position)
				weights.append(int(meadow.get_patch(neighbor_position).greens) ** 2 + 1)
		choice = random.choices(options, weights)[0]
		meadow.get_patch(self.position).move_out(self)
		self.position = choice
		meadow.get_patch(self.position).move_in(self)
	def eat(self, meadow):
		# eat some tasty greens, assuming any are here
		right_here = meadow.get_patch(self.position)
		self.energy += right_here.get_eaten(BUNNY_HUNGER)
	def mate(self, meadow, time_count):
		# make more bunnies, maybe
		right_here = meadow.get_patch(self.position)
		for b in right_here.bunnies:
			if b.is_alive() and self.sex is not b.sex and self.last_mate_time + BUNNY_MATING_MINIMUM_RECOVERY_TIME <= time_count and b.last_mate_time + BUNNY_MATING_MINIMUM_RECOVERY_TIME <= time_count:
				mating_chance = BUNNY_MATING_CHANCE
				if SCALE_MATING_CHANCE_WITH_ENERGY: mating_chance = mating_chance * self.energy / BUNNY_STARTING_ENERGY
				if random.random() < mating_chance:
					self.last_mate_time = time_count
					b.last_mate_time = time_count
					litter_size = random.randint(BUNNY_MINIMUM_LITTER_SIZE, BUNNY_MAXIMUM_LITTER_SIZE)
					for i in range(litter_size):
						e = self.energy
						if b.energy > e: e = b.energy
						right_here.bunnies.append(Bunny(time_count, self.position, energy=e))
					break
	def die(self):
		self.energy = 0

if __name__ == '__main__': main()
