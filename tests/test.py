from hcvote.counter import csv_to_position, Position


# Create a position from .csv file
test_pos1 = csv_to_position("test_votes1.csv", "Position1", 2)
test_pos1.count_vote()
print(test_pos1.get_elected())
