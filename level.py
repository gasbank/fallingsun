import logging

TERRAIN_GRASS = 0
TERRAIN_WATER = 1

class TileLevel(object):
    
    TENT = 2
    TREE = 3
    TREASUREBOX = 4
    
    def __init__(self, width = 0, height = 0, useTestData=False):
        
        if useTestData:
            self.fillWithTestData()
        else:
            self.terrain = self.getZeroed2DArray(width, height)
            self.building = self.getZeroed2DArray(width, height)
            self.collision = self.getZeroed2DArray(width, height)
            
            self.updateLevelSize()
        
        #self.placeTree(11, 7)
        #self.placeTree(15, 8)
        
        #self.placeTent(10,13)
        #self.placeTent(16,17)
        #self.placeTent(16,17)
    
    def getCellDataPixelCoord(self, x, y):
        return self.getCellData(int(x//32), int(y//32))
    
    def getCellData(self, tx, ty):
        t = self.terrain[ty][tx] if 0<=tx<self.width and 0<=ty<self.height else TERRAIN_GRASS
        b = self.building[ty][tx] if 0<=tx<self.width and 0<=ty<self.height else 0
        c = self.collision[ty][tx] if 0<=tx<self.width and 0<=ty<self.height else 0
        
        return t, b, c
    
    def toTileIndex(self, location):
        return (int(location[0]//32), int(location[1]//32))
    
    def updateLevelSize(self):
        self.width = len(self.terrain[0])
        self.height = len(self.terrain)
        
        assert self.width == len(self.building[0])
        assert self.height == len(self.building)
        
        assert self.width == len(self.collision[0])
        assert self.height == len(self.collision)
        
        logging.info('Level size updated to (%d,%d).' % (self.width, self.height))        

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
    
    def placeTreasureBox(self, tx, ty, place=True):
                
        originOffset = (0, 0)
        collisionRect = (0, 0, 1, 1)
        
        self.placeBuilding(tx, ty, TileLevel.TREASUREBOX if place else 0, 
                           originOffset, collisionRect)        
    
    def fillWithTestData(self):
        
        self.terrain = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                        [0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0,0,0,0,0,0,0],
                        [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                        [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                        [0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0,0,0,0,0,0,0],
                        [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0,0,0,0,0,0,0],
                        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,0,0,0,0,0,0],
                        [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 2, 1,0,0,0,0,0,0],
                        [0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 2, 1,0,2,0,0,0,0],
                        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 1,0,2,0,0,0,0],
                        [0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 2, 2,2,2,0,0,0,0],
                        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,0,2,0,0,0,0],
                        [0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,0,2,0,0,0,0],
                        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0,0,2,0,0,0,0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 2,2,2,0,0,0,0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0,0,0,0,0,0,0],
                        [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 1, 2, 0,0,0,0,0,0,0],
                        [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0,0,0,2,0,0,0],
                        [0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 2, 1, 2, 2,2,2,2,0,0,0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,0,0,0,0,0,0], ]
        
        self.building = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0], ]
        
        self.collision = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0], ]
        
        EXPAND_SIZE = 4
        for x in range(len(self.terrain)):
            self.terrain[x].extend([0]*EXPAND_SIZE)
            self.building[x].extend([0]*EXPAND_SIZE)
            self.collision[x].extend([0]*EXPAND_SIZE)
        for x in range(EXPAND_SIZE):
            self.terrain.append([0]*len(self.terrain[0]))
            self.building.append([0]*len(self.building[0]))
            self.collision.append([0]*len(self.collision[0]))
        
        self.updateLevelSize()
        
    def getZeroed2DArray(self, width, height):
        
        r = []
        for _ in range(height):
            r.append([0]*width)
        
        return r
    
    def isMovablePixelCoord(self, x, y):
        return self.isMovable(int(x//32), int(y//32))
        
    def isMovable(self, tx, ty):
        t, _, c = self.getCellData(tx, ty)
        return t != 1 and c == 0
    
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
    
    def getNeighborSameString(self, tx, ty, c):
        
        r = []
        for nb in TileNeighborhood4(self.width, self.height, tx, ty,
                                    noCheck=True):
            t, _, _ = self.getCellData(*nb)
            r.append(int(t == c))
        
        return '%d%d%d%d' % tuple(r)

DEFAULT_TILE_NEIGHBORHOOD4_SEQ = ((0,-1),(0,1),(-1,0),(1,0))

class TileNeighborhood4(object):
    # Iteration sequence: Top -> Bottom -> Left -> Right
    
    def __init__(self, width, height, i, j, seq=DEFAULT_TILE_NEIGHBORHOOD4_SEQ,
                 noneOnInvalid=False, noCheck=False):
        self.width = width
        self.height = height
        self.i = i
        self.j = j
        self.c = -1 # Top -> Bottom -> Left -> Right if default seq used.
        self.seq = seq
        self.noneOnInvalid = noneOnInvalid
        self.noCheck = noCheck
        
    def __iter__(self):
        return self
    
    def next(self):
        
        self.c = self.c + 1
        
        if self.c >= len(self.seq):
            raise StopIteration()
        
        i = self.i + self.seq[self.c][0]
        j = self.j + self.seq[self.c][1]
        if self.noCheck or (0 <= i < self.width and 0 <= j < self.height):
            return (i, j)
        elif self.noneOnInvalid:
            return None
        else:
            return self.next()
        