class TileLevel(object):
    
    TENT = 2
    TREE = 3
    
    def __init__(self, width = 0, height = 0, useTestData=False):
        self.width = width
        self.height = height
        self.terrain = self.get2DArray(width, height)
        self.building = self.get2DArray(width, height)
        self.collision = self.get2DArray(width, height)
        
        if useTestData: self.fillWithTestData()
        
        #self.placeTree(11, 7)
        #self.placeTree(15, 8)
        
        #self.placeTent(10,13)
        #self.placeTent(16,17)
        #self.placeTent(16,17)
    
    def toTileIndex(self, location):
        return (int(location[0]//32), int(location[1]//32))
    
    def updateLevelSize(self):
        self.width = len(self.terrain[0])
        self.height = len(self.terrain)
        
        assert self.width == len(self.building[0])
        assert self.height == len(self.building)
        
        assert self.width == len(self.collision[0])
        assert self.height == len(self.collision)
        

    def placeBuilding(self, tx, ty, building, originOffset, collisionRect):
        
        self.building[ty-originOffset[1]][tx-originOffset[0]] = building
        
        for j in range(ty-originOffset[1]+collisionRect[1], 
                       ty-originOffset[1]+collisionRect[1]+collisionRect[3]):
            for i in range(tx-originOffset[0]+collisionRect[0],
                           tx-originOffset[0]+collisionRect[0]+collisionRect[2]):
                self.collision[j][i] = 1 if building > 0 else 0
    
    
    def placeTree(self, tx, ty, place=True):
        
        originOffset = (1, 4)
        collisionRect = (1, 4, 2, 1)
        
        self.placeBuilding(tx, ty, TileLevel.TREE if place else 0, 
                           originOffset, collisionRect)
        
    def placeTent(self, tx, ty, place=True):
        
        originOffset = (2, 4)
        collisionRect = (0, 2, 5, 3)
        
        self.placeBuilding(tx, ty, TileLevel.TENT if place else 0, 
                           originOffset, collisionRect)
        
    
    def fillWithTestData(self):
        
        self.terrain = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                        [0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0,0,0,0,0,0],
                        [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0,0,0,0,0,0],
                        [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,0,0,0,0,0],
                        [0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0,0,0,0,0,0],
                        [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0,0,0,0,0,0],
                        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,0,0,0,0,0],
                        [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 2, 1,0,0,0,0,0],
                        [0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 2, 1,0,2,0,0,0],
                        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 1,0,2,0,0,0],
                        [0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 2, 2,2,2,0,0,0],
                        [0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,0,2,0,0,0],
                        [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,0,2,0,0,0],
                        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0,0,2,0,0,0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 2,2,2,0,0,0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0,0,0,0,0,0],
                        [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 1, 2, 0,0,0,0,0,0],
                        [0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 2, 1, 2, 0,0,0,2,0,0],
                        [0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 2, 2, 2, 2,2,2,2,0,0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0], ]
        
        self.building = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0], ]
        
        self.collision = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0], ]
        
        self.updateLevelSize()
        
    def get2DArray(self, width, height, newValue=0):
        return [[0]*width]*height
    
    def isMovable(self, i, j):
        return self.collision[j][i] == 0 and self.terrain[j][i] != 1
    
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
        
        pathCellCache = {}
        
        openCells = []
        startCell = self.createPathCell(fromI, fromJ)
        
        # Jammed!
        if not startCell.movable:
            return []
        
        # No need to move anyway.
        if fromI == toI and fromJ == toJ:
            return [(fromI, fromJ)]        
        
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
                    
                if (cell.movable or (ni,nj)==(toI,toJ)) and cell.expandedFrom is None:
                    
                    cell.expandedFrom = current
                    openCells.append(cell)
        
        pathCellCache = {k:x for k,x in pathCellCache.items() if x.expandedFrom}
        
        if not pathCellCache:
            return [(fromI, fromJ)]
        
        closestGoal = min(pathCellCache.items(),
                          key=lambda (k,x): abs(toI-x.i) + abs(toJ-x.j))[1]
                    
        path = []
        pc = pathCellCache.get((closestGoal.i, closestGoal.j), None)
        while pc is not None:
            if pc.movable:
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
        