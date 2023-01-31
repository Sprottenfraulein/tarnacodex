# Import pygame setup script and main game script.
import cProfile
import resman
import pginit
import unf


def run():
	# Creating resource manager object.
	res = resman.ResMan()
	# Run pygame setup and receive setup object.
	pygame_settings = pginit.PG(res)
	# Launch main game loop and pass setup object.
	unf.launch(pygame_settings, res, log=True)


# Run the scripts if we are 'main'.
if __name__ == '__main__':
	# cProfile.run('run()')
	run()
