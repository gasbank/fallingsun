class TileLevel(object):
    def __init__(self, width = 0, height = 0):
        self.width = width
        self.height = height
        self.terrain = self.get2DArray(width, height)
        self.building = self.get2DArray(width, height)
        self.collision = self.get2DArray(width, height)
        
        self.fillWithTestData()
    
    def updateLevelSize(self):
        self.width = len(self.terrain[0])
        self.height = len(self.terrain)
        
        assert self.width == len(self.building[0])
        assert self.height == len(self.building)
        
        assert self.width == len(self.collision[0])
        assert self.height == len(self.collision)
    
    def fillWithTestData(self):
        
        self.terrain = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0],
                        [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
                        [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                        [0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                        [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
                        [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0],
                        [0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0],
                        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], ]
        
        self.building = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], ]
        
        self.collision = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], ]
        
        self.updateLevelSize()
        
    def get2DArray(self, width, height, newValue=0):
        return [[0]*width]*height
    
    def isMovable(self, i, j):
        return self.collision[j][i] == 0 and self.terrain[j][i] == 0
    
    def createPathCell(self, i, j):
        class PathCell(object): pass
        cell = PathCell()
        cell.i = i
        cell.j = j
        cell.movable = self.isMovable(i, j)
        cell.expandedFrom = None
        return cell
    
    def findPath(self, fromI, fromJ, toI, toJ):
        
        if not (0 <= fromI < self.width):
            raise IndexError('Invalid fromI value')
        
        if not (0 <= fromJ < self.height):
            raise IndexError('Invalid fromJ value')
        
        if not (0 <= toI < self.width):
            raise IndexError('Invalid toI value')
        
        if not (0 <= toJ < self.height):
            raise IndexError('Invalid toJ value')
        
        if fromI == toI and fromJ == toJ:
            return [(fromI, fromJ)]        
        
        pathCellCache = {}
        
        openCells = []
        startCell = self.createPathCell(fromI, fromJ)
        openCells.append(startCell)
        
        while openCells:
            current = openCells.pop()
            
            for ni, nj in TileNeighborhood4(self.width, self.height,
                                            current.i, current.j):
                
                if not pathCellCache.has_key((ni, nj)):
                    cell = self.createPathCell(ni, nj)
                    pathCellCache[(ni, nj)] = cell
                else:
                    cell = pathCellCache[(ni, nj)] 
                
                if cell.movable and cell.expandedFrom is None:
                    
                    cell.expandedFrom = current
                    openCells.append(cell)
                    
        path = []
        if pathCellCache.has_key((toI,toJ)):
            pc = pathCellCache[(toI,toJ)]
            while pc is not None:
                path.insert(0, (pc.i, pc.j))
                pc = pc.expandedFrom
        
        return path

class TileNeighborhood4(object):
    # Iteration sequence: Top -> Bottom -> Left -> Right
    seq = ((0,-1),(0,1),(-1,0),(1,0))
    
    def __init__(self, width, height, i, j):
        self.width = width
        self.height = height
        self.i = i
        self.j = j
        self.c = -1 # Top -> Bottom -> Left -> Right
        
    def __iter__(self):
        return self
    
    def next(self):
        
        self.c = self.c + 1
        
        if self.c >= len(TileNeighborhood4.seq):
            raise StopIteration()
        
        i = self.i + TileNeighborhood4.seq[self.c][0]
        j = self.j + TileNeighborhood4.seq[self.c][1]
        if 0 <= i < self.width and 0 <= j < self.height:
            return (i, j)
        else:
            return self.next()
        