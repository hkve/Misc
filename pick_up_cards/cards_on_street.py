import numpy as np
import random
import matplotlib.pyplot as plt


def collect_deck(deck_size):
	"""
	Slow function that will always work. 
	"""
	deck = set()
	draws = 0

	while len(deck) < deck_size:
		new_card = random.randint(1, deck_size)
		deck.add(new_card)
		draws += 1

	return draws


def collect_deck_buffered(deck_size, buffer_size=1500):
	"""
	For large n, this is quite a lot faster than "collect_deck", NumPy is very nice.
	A buffer size of 1500 has worked perfectly for a deck size of 52, but if you increase this, 
	increasing the buffer might be need. 
	"""
	deck = set()
	draws = 0

	buffer_size = 1500
	draw_buffer = np.random.uniform(1, deck_size+1, buffer_size).astype(int)

	while len(deck) < deck_size:
		new_card = draw_buffer[draws]
		deck.add(new_card)
		draws += 1

	return draws


def collect_deck_with_draws(deck_size):
	deck = set()
	draws = 0

	deck_size_per_draw = []

	while len(deck) < deck_size:
		new_card = random.randint(1,deck_size)
		deck.add(new_card)
		deck_size_per_draw.append(len(deck))
		draws += 1

	return np.array(deck_size_per_draw), np.arange(0, draws)


def collect_decks(n, deck_size, buffered=False, buffered_size=1500):
	draws = np.zeros(n, dtype=int)

	if buffered:
		args = (deck_size, buffered_size,)
		cd = collect_deck_buffered
	else:
		args = (deck_size,)
		cd = collect_deck

	for i in range(n):
		draws[i] = cd(*args)

	return draws


def draws_hist(n=int(1e4), deck_size=52, plot=True, buffered=False, buffer_size=1500):
	"""
	Makes a histogram of P(# of cards). n is the number of deck collections (trials) in the 
	Monte Carlo. For large n, using buffered=True is recommended, however increasing buffer size
	is needed if you want to increase the deck_size.
	"""
	n, deck_size = int(n), int(deck_size)

	draws = collect_decks(n, deck_size, buffered, buffer_size)

	mean, std, std_m = np.mean(draws), np.std(draws), np.std(draws)/np.sqrt(n)
	print(f"mean = {np.mean(draws):.2f}, std = {np.std(draws):.2f}")

	if plot:
		fig, ax = plt.subplots()
		weights = np.ones_like(draws)/n
		x, bins, bar_containers = ax.hist(draws, bins=100, weights=weights, label=f"mean={mean:.2f}\nstd={std:.2f}\nstd_m={std_m:.2f}")
		assert abs(np.sum(x) - 1) < 1e-5, "Upsi something wrong in hist normalization"
		
		ax.set(xlabel="# of draws", ylabel="P(# of draws)")
		ax.legend()
		plt.show()


def example_paths(cases=5, deck_size=52):
	"""
	Makes line plots showing examples of paths taken when collecting cards. That is, how many
	cards you have collected as a function of how many cards you have found.
	"""
	cases = 5
	fig, ax = plt.subplots()

	for i in range(cases):
		deck_size_per_draw, draws = collect_deck_with_draws(deck_size)

		ax.plot(draws, deck_size_per_draw, label=f"Tot {draws[-1]} draws")
	
	ax.set(xlabel="# of draws", ylabel="deck size")
	ax.legend()
	plt.show()

if __name__ == "__main__":
	draws_hist(n=int(1e6), plot=True, buffered=True)
	example_paths()