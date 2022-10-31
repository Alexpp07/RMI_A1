
def find_path(self,xInitial,yInitial,xEnd,yEnd):
        print("FINDING PATH")
        node_initial = Node(None,(yInitial,xInitial),0,0,0)
        end_node = Node(None,(yEnd,xEnd),0,0,0)

        open_list=[]
        closed_list = []

        open_list.append(node_initial)

        while len(open_list) > 0:
            print("On while")
            current_node = open_list[0]
            print(current_node,"inicio")
            print(end_node,"fim")
            current_index = 0
            for index,item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            open_list.pop(current_index)
            closed_list.append(current_node)

            if current_node.position == end_node.position:
                print("getting path")
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]

            children = []
            for new_position in [(0,-1),(0,1),(-1,0),(1,0)]:
                node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
                if node_position[0] > (len(self.beacon_maze) - 1) or node_position[0] < 0 or node_position[1] > (len(self.beacon_maze[len(self.beacon_maze)-1]) -1) or node_position[1] < 0:
                    continue
                if self.beacon_maze[node_position[0]][node_position[1]] == '0':
                    continue
                new_node = Node(current_node, node_position)
                children.append(new_node)

            for child in children:
                for closed_child in closed_list:
                    if child == closed_child:
                        continue
                child.g = current_node.g + 1
                child.h = ((child.position[0] - end_node.position[0])**2) + ((child.position[1] - end_node.position[1])**2)
                child.f = child.g + child.h
                for open_node in open_list:
                    if child == open_node and child.g > open_node.g:
                        continue
                open_list.append(child)

def found_all_beacons(self,initialX,initialY):
    #self.beacon_maze is the maze with 0's and 1's
    #self.beacon_coords is the list of (y,x) coordinates of the beacons
    final_path=[]
    if len(self.beacon_coords)!=0:
        for i in self.beacon_coords:
            coordY,coordX = self.find_next_destiny(initialX,initialY)
            path = self.find_path(initialX,initialY,coordY,coordX)
            if final_path==[]:
                final_path = path
            elif final_path[-1] == path[0]:
                final_path = final_path + path[1:]
            else:
                final_path = final_path + path
    print("PATH FINAL: ",final_path)

def find_next_destiny(self,initialX,initialY):
    src = Pair(initialX, initialY)
    shortest_path = 0
    index = 0
    for i in range(self.beacon_cords):
        if i==0:
            shortest_path = findShortestPathLength(self.beacon_maze, src, Pair(self.beacon_cords[i][0], self.beacon_cords[i][1]))
            if (shortest_path != -1):
                print("Shortest Path is", dist)
            
            else:
                print("Shortest Path doesn't exist")
                return None

            index = 0
        else:
            temp_path = findShortestPathLength(self.beacon_maze, src, Pair(self.beacon_cords[i][0], self.beacon_cords[i][1]))
            if (temp_path != -1):
                print("Shortest Path is", dist)
            
            else:
                print("Shortest Path doesn't exist")
                return None

            if temp_path < shortest_path:
                shortest_path = temp_path
                index = i
    return self.beacon_cords.pop(index)

def isSafe(mat, visited, x, y):
    return (x >= 0 and x < len(mat) and y >= 0 and y < len(mat[0]) and mat[x][y] == 1 and (not visited[x][y]))

def findShortestPath(mat, visited, i, j, x, y, min_dist, dist):

    if (i == x and j == y):
        min_dist = min(dist, min_dist)
        return min_dist

    # set (i, j) cell as visited
    visited[i][j] = True
    
    # go to the bottom cell
    if (isSafe(mat, visited, i + 1, j)):
        min_dist = findShortestPath(
            mat, visited, i + 1, j, x, y, min_dist, dist + 1)

    # go to the right cell
    if (isSafe(mat, visited, i, j + 1)):
        min_dist = findShortestPath(
            mat, visited, i, j + 1, x, y, min_dist, dist + 1)

    # go to the top cell
    if (isSafe(mat, visited, i - 1, j)):
        min_dist = findShortestPath(
            mat, visited, i - 1, j, x, y, min_dist, dist + 1)

    # go to the left cell
    if (isSafe(mat, visited, i, j - 1)):
        min_dist = findShortestPath(
            mat, visited, i, j - 1, x, y, min_dist, dist + 1)

    # backtrack: remove (i, j) from the visited matrix
    visited[i][j] = False
    return min_dist

# Wrapper over findShortestPath() function
def findShortestPathLength(mat, src, dest):
    if (len(mat) == 0 or mat[src.first][src.second] == 0
            or mat[dest.first][dest.second] == 0):
        return -1

    row = len(mat)
    col = len(mat[0])

    # construct an `M × N` matrix to keep track of visited
    # cells
    visited = []
    for i in range(row):
        visited.append([None for _ in range(col)])

    dist = sys.maxsize
    dist = findShortestPath(mat, visited, src.first,
                            src.second, dest.first, dest.second, dist, 0)
    print(visited)

    if (dist != sys.maxsize):
        return dist
    return -1



class Node():
    def __init__(self,parent=None,position=None,g=0,h=0,f=0):
        self.parent = parent
        self.position = position
        self.g = g
        self.h = h
        self.f = f

    def __str__(self) -> str:
        return str(self.position)

# User defined Pair class
class Pair:
    def __init__(self, x, y):
        self.first = x
        self.second = y
    
    
if __name__ == '__main__':
    print("Hello")
    # Generate a random maze with 0's and 1's with 1's being the path and with a height of 21 and width of 49

    #Number of beacons ('3' in the maze)
    numBeacons = 3
    #List with indexes of those beacons
    beaconIndexes = [(6,24),(11,20),(14,12)]
    path = Path()
    print(path.find_path(0,0,12,14))