
class A:
    def __init__(self, x):
        self.x = x
class B:
    def __init__(self, x):
        self.x = x
grid = [[None, None], [None, None]]
print(grid)
grid[0][0] = A(2)
grid[0][1] = B(2)
print(grid)

def count_gird(grid):
    n = 0
    for list in grid:
        n += list.count(None)
    print(n)

print(type(grid[0][0]))
print(isinstance(grid[0][0], B))
print(isinstance(grid[0][1], B))
count_gird(grid)
grid[1][1] = B(2)
count_gird(grid)
 
patterns = [[[0, 0], [0, 1], [0, 2]], [[1, 0], [1, 1], [1, 2]], [[2, 0], [2, 1], [2, 2]]]
for a in range(3):
    print(a)