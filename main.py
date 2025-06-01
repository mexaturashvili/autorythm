print("importing libraries...")
import librosa
import sounddevice
import pygame
import time
import random
import threading
import numpy as np
import os
import utils
pygame.init()
screen = pygame.display.set_mode((500, 500))

os.makedirs("src", exist_ok=True)
os.makedirs("beatmaps", exist_ok=True)




background_color_decrease = 10
helper_line_color_decrease = 10

WIDTH = screen.get_width()
HEIGHT = screen.get_height()
NOTE_HEIGHT = 100
NOTE_WIDTH = 50


target_helper_line_color = (0, 0, 0)
target_background_color = (255, 255, 255)


background_emoticon_font_size = 36
background_emoticon_scale = 0
helper_line_color = target_helper_line_color
background_color = target_background_color








fn = input("enter beatmap (.mp3) name: ")

if not fn.endswith(".mp3"):
	print("invalid .mp3 file")
	exit()


if not os.path.isfile(fn):
	newfn = "src/" + fn
	if not os.path.isfile(newfn):
		print(f"{fn} not found")
		exit()
	else:
		fn = newfn

print("importing song...")
y, sr = librosa.load(fn, sr=None, mono=False)

beatmap_name = os.path.splitext(os.path.basename(fn))[0]
beatmap_path = f"beatmaps/{beatmap_name}"


if os.path.isdir(beatmap_path) and os.path.isfile(f"{beatmap_path}/beatmap.json"):
	print("loading beatmap...")
	beatmap = utils.load_beatmap(f"{beatmap_path}/beatmap.json")

else:
	print("beatmap not found, creating new one...")
	os.makedirs(beatmap_path, exist_ok=True)


	beatmap = utils.create_beatmap(y, sr)
	utils.save_beatmap(beatmap, beatmap_path)




	

# sr *= 1.5 # for speeding up the song
# S = np.abs(librosa.stft(mono_y)) # for stereogram





print(beatmap["tempo"])
print(beatmap["harmonic_amp"])




BASE_BPM = 120
BASE_FALL_TIME = 0.5
NOTE_FALL_TIME = BASE_FALL_TIME * (BASE_BPM / float(beatmap["tempo"][0]))
NOTE_SPEED = (HEIGHT - NOTE_HEIGHT) / NOTE_FALL_TIME




pygame.display.set_caption("autorythm")

notes = []


class Rectangle(pygame.Surface):
	def __init__(self, parent, xpos, ypos, width, height, color):
		super(Rectangle, self).__init__((width, height), pygame.SRCALPHA)
		self.xpos = xpos
		self.ypos = ypos
		self.color = color
		self.width = width
		self.height = height
		self.fill(self.color)
		self.rect = pygame.Rect(xpos, ypos, width, height)


	def update(self):
		self.rect.topleft = (self.xpos, self.ypos)
		self.rect.width, self.rect.height = self.width, self.height

		pygame.draw.rect(screen, self.color, self.rect)





def spawn_note(coords: tuple, size: tuple, color: tuple):
	notes.append(Rectangle(screen, coords[0], coords[1], size[0], size[1], color))




def background_emoticon():
	# looks ugly so i commented it out
	# uncomment to use it

	# global background_emoticon_scale
	# start_time = time.time()

	# beat_times = beatmap["beat_times_percussive"]
	# harmonic_amplitudes = beatmap["harmonic_amp"]

	# for i, beat_time in enumerate(beat_times):
	# 	time_to_wait = beat_time - (time.time() - start_time)
	# 	if time_to_wait > 0:
	# 		time.sleep(time_to_wait)
		
	# 	background_emoticon_scale = harmonic_amplitudes[i] * 1000 * 0.5

	pass


def percussive_note_spawner():
	start_time = time.time()
	for beat_time in beatmap["beat_times_percussive"]:
		time_to_wait = beat_time - (time.time() - start_time)
		if time_to_wait > 0:
			time.sleep(time_to_wait)
		spawn_note((WIDTH//2 - NOTE_WIDTH, 0), (NOTE_WIDTH, NOTE_HEIGHT), (255, 0, 0))

def harmonic_note_spawner():
	start_time = time.time()
	for beat_time in beatmap["beat_times_harmonic"]:
		
		time_to_wait = beat_time - (time.time() - start_time)
		if time_to_wait > 0:
			time.sleep(time_to_wait)
		spawn_note((WIDTH//2, 0), (NOTE_WIDTH, NOTE_HEIGHT), (0, 255, 0))
		


threading.Thread(target=background_emoticon).start()
threading.Thread(target=percussive_note_spawner).start()
threading.Thread(target=harmonic_note_spawner).start()


def start_song(y, sample_rate):
	time.sleep(NOTE_FALL_TIME)
	print("playing song")
	sounddevice.play(y.T, sample_rate)


threading.Thread(target=start_song, args=(y, sr)).start()





dt = 0

running = True
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", background_emoticon_font_size)
text = font.render(f":3", True, (255, 255, 255))

pad1_rect = pygame.Rect(WIDTH//2 - NOTE_WIDTH, HEIGHT - NOTE_HEIGHT // 2 - 5/2, NOTE_WIDTH, 5)
pad2_rect = pygame.Rect(WIDTH//2, HEIGHT - NOTE_HEIGHT // 2 - 5/2, NOTE_WIDTH, 5)
helper_line_rect = pygame.Rect(0, HEIGHT - NOTE_HEIGHT // 2 - 5/2, WIDTH, 5)

pad1_active = False
pad2_active = False


while running:
	screen.fill(background_color)
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			spawn_note((mouse_x - 200 / 2, mouse_y), (200, 50), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False

			if event.key == pygame.K_f:
				for note in notes:
					if pad1_rect.colliderect(note.rect):
						notes.remove(note)

				pad1_active = True



			if event.key == pygame.K_j:
				for note in notes:
					if pad2_rect.colliderect(note.rect):
						notes.remove(note)
				pad2_active = True

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_f:
				pad1_active = False

			if event.key == pygame.K_j:
				pad2_active = False
	
	new_text_surface = pygame.transform.smoothscale(text,(int(text.get_width() * background_emoticon_scale / 50), int(text.get_height() * background_emoticon_scale / 50)))
	screen.blit(new_text_surface, (WIDTH//2 - new_text_surface.get_width()//2, HEIGHT//2 - new_text_surface.get_height()//2))
	for note in notes:
		note.ypos += NOTE_SPEED * (dt / 1000)
		note.update()
	

	keys = pygame.key.get_pressed()




	if any(helper_line_rect.colliderect(note.rect) for note in notes):
		helper_line_color = target_helper_line_color
		background_color = target_background_color

	
	pygame.draw.rect(screen, helper_line_color, rect=helper_line_rect)
	helper_line_color = (utils.clamp(helper_line_color[0] + helper_line_color_decrease, target_helper_line_color[0], 255), utils.clamp(helper_line_color[1] + helper_line_color_decrease, target_helper_line_color[1], 255), utils.clamp(helper_line_color[2] + helper_line_color_decrease, target_helper_line_color[2], 255))
	background_color = (utils.clamp(background_color[0] - background_color_decrease, 0, target_background_color[0]), utils.clamp(background_color[1] - background_color_decrease, 0, target_background_color[1]), utils.clamp(background_color[2] - background_color_decrease, 0, target_background_color[2]))


	if pad1_active:
		pygame.draw.rect(screen, (255, 0, 0), rect=pad1_rect)
	
	if pad2_active:
		pygame.draw.rect(screen, (0, 255, 0), rect=pad2_rect)




	notes = [note for note in notes if note.ypos < HEIGHT + NOTE_HEIGHT]
	pygame.display.flip()
	dt = clock.tick(120)

pygame.quit()