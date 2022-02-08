# Main script with pygame loop.
import pygame
from library import cursor, database, scheduler
from components import tilesets, animations
from wins import apptitle, realm, inventory, skillbook, context, target, hotbar, pools, charstats, overlay, dialogue, demos, options


def launch(pygame_settings, resources, log=False):
	# creating tilesets components
	tile_sets = tilesets.Tilesets()
	# creating animations
	anims = animations.Animations()
	# connecting to the database
	db = database.DB('res/data/tables.db')
	# creating mouse pointer object
	mouse_pointer = cursor.Cursor(pygame_settings, resources)
	# creating scheduler
	schedule_man = scheduler.Scheduler(5, 4, 9999999)
	# declaring wins
	wins_dict = {
		'app_title': apptitle.AppTitle(pygame_settings, resources, tile_sets, anims, db, mouse_pointer, schedule_man),
		'realm': realm.Realm(pygame_settings, resources, tile_sets, anims, db, mouse_pointer, schedule_man),
		'inventory': inventory.Inventory(pygame_settings, resources, tile_sets, anims, db, mouse_pointer, schedule_man),
		'target': target.Target(pygame_settings, resources, tile_sets, anims, db, mouse_pointer, schedule_man),
		'context': context.Context(pygame_settings, resources, tile_sets, anims, db, mouse_pointer, schedule_man),
		'skillbook': skillbook.SkillBook(pygame_settings, resources, tile_sets, anims, db, mouse_pointer, schedule_man),
		'hotbar': hotbar.Hotbar(pygame_settings, resources, tile_sets, anims, db, mouse_pointer, schedule_man),
		'pools': pools.Pools(pygame_settings, resources, tile_sets, anims, db, mouse_pointer, schedule_man),
		'charstats': charstats.CharStats(pygame_settings, resources, tile_sets, anims, db, mouse_pointer, schedule_man),
		'overlay': overlay.Overlay(pygame_settings, resources, tile_sets, anims, db, mouse_pointer, schedule_man),
		'dialogue': dialogue.Dialogue(pygame_settings, resources, tile_sets, anims, db, mouse_pointer, schedule_man),
		'demos': demos.Demos(pygame_settings, resources, tile_sets, anims, db, mouse_pointer, schedule_man),
		'options': options.Options(pygame_settings, resources, tile_sets, anims, db, mouse_pointer, schedule_man),
	}
	bigloop(pygame_settings, resources, wins_dict, mouse_pointer, schedule_man)


def bigloop(pygame_settings, resources, wins_dict, mouse_pointer, schedule_man, log=True):
	# adding the first unit to active wins
	active_wins = [wins_dict['app_title']]
	title_win = wins_dict['app_title']

	run = True

	while run:
		# Checking controls
		events(pygame_settings, resources, wins_dict, active_wins, mouse_pointer)

		schedule_man.tick()
		for win in active_wins:
			win.tick(pygame_settings, wins_dict, active_wins, mouse_pointer)

		if mouse_pointer.still_timer < mouse_pointer.still_max:
			mouse_pointer.still_timer += 1

		# RENDERING COOLDOWNS
		if title_win.pc is not None and len(title_win.pc.hot_cooling_set) > 0:
			for socket, skill in title_win.pc.hot_cooling_set:
				if socket.win in active_wins:
					socket.win.win_rendered.blit(socket.rendered_panel,
												 socket.rendered_rect.topleft)
					socket.win.win_rendered.fill((1, 1, 1),
							 (socket.rendered_rect.left, socket.rendered_rect.top,
							  socket.size[0], socket.size[1] * skill.cooldown_timer // skill.props['cooldown']))


		# DRAWING
		pygame_settings.screen.fill((10,10,10))
		# drawing active windows
		for win in reversed(active_wins):
			win.draw(pygame_settings.screen)

		if mouse_pointer.visible:
			mouse_pointer.draw(pygame_settings.screen)
		# Final rendering for a current frame
		pygame_settings.clock.tick_busy_loop(pygame_settings.fps)
		pygame.display.flip()


def events(pygame_settings, resources, wins_dict, active_wins, mouse_pointer, log=True):
	for event in pygame.event.get():
		# Checking for keys pressed globally.
		if event.type == pygame.KEYDOWN:
			# Exit the app when Esc is pressed.
			if event.key == pygame.K_q:
				exit()

		# checking for mouse move
		if event.type == pygame.MOUSEMOTION:
			mouse_pointer.xy = pygame.mouse.get_pos()
			mouse_pointer.still_timer = 0
			mouse_pointer.move()

		# Checking for window resize
		if event.type == pygame.VIDEORESIZE:
			if wins_dict['realm'].maze is not None:
				wins_dict['realm'].view_resize(wins_dict, event.w, event.h)
			wins_dict['app_title'].align(event.w, event.h)
			pygame_settings.set_display(event.w, event.h)

		# checking wins for events
		wins_num = len(active_wins)
		for win in active_wins:
			# blocking interaction from other windows if one was interacted
			if win.event_check(event, pygame_settings, resources, wins_dict, active_wins, log=True):
				break
			if len(active_wins) != wins_num:
				break

		"""if event.type == pygame.MOUSEBUTTONUP:
			for win in active_wins:
				if win == wins_dict['realm']:
					continue
				for inter in win.win_ui.interactives:
					inter.release(event.buttnon)"""