""" Class representing a single position with an aribtrary number of 

"""
class Position:
	
	def __init__(self, name, no_vac, candidate, opt_pref = False):

		self.name = name
		self.__opt_pref = opt_pref

		# Create a dictionary storing first preference vote for each candidate
		self.__cand_index = {i : c for i, c in enumerate(candidates)}
		self.__votes = []
		self.__first_prefs = {i : 0 for i in range(len(candidates))}

		self.__no_vac = no_vac
		self.__no_cand = len(candidates)

		self.__elected = []
		self.__elect_open = True




	def add_vote(self, prefs):
		# If vote is incorrect, 
		# TODO: Check that vote is valid

		self.__votes.append(prefs)


	def count_vote(self):
		if not self.__elect_open:
			print("Election has already been counted")
			return

		# Vote backup in case count fails
		self.__vote_bku = self.__votes.copy()

		# Number of first preference votes for each candidate
		first_prefs = [0]*self.__no_cand

		# Calculate the quote
		quota = (len(self.__votes) + 1)/(self.__no_vac + 1)


		while self.__no_cand < self.__no_vac:
			# Count first preference votes
			for v in self.__votes:
				first_prefs[v[0]] += 1

			# Check for election
			for c in range(len(self.__no_cand)):
				if first_prefs[c] >= quota:
					self.__elected.append(c)
					self.__no_vac -= 1
					self.__no_cand -= 1

			if no_vac < 0:
				raise ValueError()
			elif no_vac == 0:
				# Election complete
				break
			else:

				# Calculate transfer values
				no_exclude = False
				transfer =[0]*self.__no_cand

				for e in self.__elected:
					surplus = first_prefs[e] - quota
					if surplus > 0:
						no_exclude = True
						transfer[e] = surplus/first_prefs[e]

					# Remove from consideration
					first_prefs.remove(e)

				# Transfer surplus votes
				if no_exclude:
					for v in votes:
						try:
							first_prefs[v[1]] += transfer[v[0]]
							if v[0] in self.__elected:
								v.remove[0]
						
						except IndexError:
							# Second preference is already elected candidate
							pass


				else:
					exclude = first_prefs.index(min(first_prefs))  # GET INDEX OF MIN
					for v in votes:
						v.remove(exclude)


		# Check for remaining vacancies
		if self.__no_vac <= self.__no_cand:
			# Elect remaining candidates
			self.__elected
		else:
			raise ValueError("Error in counting")



	def is_opt_pref(self):
		return self.__opt_pref


	def set_opt_pref(self, n_val):
		if not isinstance(n_val, bool):
			raise TypeError

		self.__opt_pref = n_val



	def get_elected(self):
		if self.__elect_open:
			raise AttributeError('The vote has not been counted for this position yet. Call the count_vote method to do so.')

		# Generator of elected candidiates
		for i in self.__elected yield self.__cand_index[i]




def csv_to_position(filename):
	pass
