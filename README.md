# Hare-Clark-VoteCounter
Python implementation of the [Hare-Clark electoral system](http://www.abc.net.au/elections/tas/2006/guide/hareclark.htm) for electing individuals to an arbitrary number of positions. Written for use by the Adelaide University Mathematics Society in their annual committee election. The implementation is designed to automatically read votes collected via a Google Form (example form [here]()), but the `hcvote` module can be used for any collection of preference votes stored in a `pandas` DataFrame.

## Requirements
Coming soon

## General Use
Coming soon

## With Google Forms
Coming soon

## Counting Process
The following outlines the Hare-Clark counting process. Suppose we have some elected position with ```no_vac``` vacancies (e.g. a general committee) and ```no_cand``` candidates for that position. Assume that ```no_vac < no_cand```, otherwise the election is trivial. Each vote orders the candidates in the voter's preferred order, i.e. a preferential vote. Assume that there are ```no_votes``` valid votes.

1. Calulate the quota, which the minimum number of votes required for a candidate to be elected, as 
```
quota = (no_votes + 1)/(no_vac + 1)
```

2. For each candidate, count the number of votes with that candidate as first preference. From hereon, the phrases "number of votes" or "count" for a candidate refer to this number of first preference votes. This number can increase as the counting process continues. 

3. Any candidate with a number of votes equal to or greater than the quota are declared elected.
	* If all vacancies have been filled, the election is complete and no further action is required.
	* If vacancies still remain, and
		* at least one candidate has more votes than the quota, **go to step 4**?
		* otherwise, **go to step 5**

4. For each elected candidate with surplus votes 

5. If unelected candidates and vacancies 



### Psuedocode
The counting process is impelemented in this module according to the following psuedocode
```
# Calculate the quota
quota = (no_votes + 1)/(no_vac + 1)

# Count the number of first preference votes for each candidate
first_prefs = zeros(no_cand)
for v in votes:
	first_prefs[v[0]]++

for c in 0 to no_cand:
	if first_prefs[c] >= quota:
		elected.append[c]
		no_vac--
		

```