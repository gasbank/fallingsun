import unittest
import random
import time
import math
import itertools

DIM = 2

class KdNode(object):
    def __init__(self, x):
        assert type(x) == tuple
        assert len(x) == DIM
        
        self.data = x
        self.left = None
        self.right = None
        
    def findMin(self, i, cd):
        if cd == i:
            if self.left is None:
                return self.data
            else:
                return self.left.findMin(i, (cd+1)%DIM)
        else:
            l = self.left.findMin(i, (cd+1)%DIM) if self.left else self.data
            r = self.right.findMin(i, (cd+1)%DIM) if self.right else self.data
            return min((self.data, l, r), key=lambda t: t[i])
        
        raise RuntimeError('This line should be unreachable.')
    
    def getAllPoints(self):
        points = [self.data]
        if self.left:
            points += self.left.getAllPoints()
        if self.right:
            points += self.right.getAllPoints()
        return points
    
    def getMaxDepth(self):
        return 1 + max(self.left.getMaxDepth() if self.left else 0,
                       self.right.getMaxDepth() if self.right else 0)
    
    def __len__(self):
        return sum((1, len(self.left or []), len(self.right or [])))
    
    def __nonzero__(self):
        return self is not None
    
    def __bool__(self):
        return self.__nonzero__()
        

class Rect(object):
    
    @property
    def x2(self): return self.x+self.w
    @property
    def y2(self): return self.y+self.h
    
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def distance(self, p):
        assert len(p) == 2
        
        px, py = p
        
        dx = max(abs(self.x+self.w/2.0 - px) - self.w/2.0, 0)
        dy = max(abs(self.y+self.h/2.0 - py) - self.h/2.0, 0)
        return distance((0,0),(dx,dy))
    
    def trimLeft(self, cd, p):
        
        assert len(p) == 2
        assert self.x <= p[0] <= self.x+self.w
        assert self.y <= p[1] <= self.y+self.h
        
        if cd == 0:
            return Rect(self.x, self.y, p[0]-self.x, self.h)
        elif cd == 1:
            return Rect(self.x, self.y, self.w, p[1]-self.y)
        else:
            raise RuntimeError('invalid cd value.')
    
    def trimRight(self, cd, p):
        
        assert len(p) == 2
        assert self.x <= p[0] <= self.x2
        assert self.y <= p[1] <= self.y2
        
        if cd == 0:
            return Rect(p[0], self.y, self.x2-p[0], self.h)
        elif cd == 1:
            return Rect(self.x, p[1], self.w, self.y2-p[1])
        else:
            raise RuntimeError('invalid cd value.')
    
    def isDisjointFromRect(self, r):
        return not self.isOverlapWithRect(r)
    
    def isOverlapWithRect(self, r):
        xOverlap = r.x <= self.x <= r.x2 or self.x <= r.x <= self.x2
        yOverlap = r.y <= self.y <= r.y2 or self.y <= r.y <= self.y2
        return xOverlap and yOverlap
        
    def containsRect(self, r):
        return self.containsPoint((r.x,r.y)) and self.containsPoint((r.x2,r.y2))
    
    def containsPoint(self, x):
        return self.x <= x[0] <= self.x2 and self.y <= x[1] <= self.y2
    
    def __str__(self):
        return 'Rect(%s, X:%s, Y:%s)' % (str([self.x,self.y,self.w,self.h]),
                                         str((self.x,self.x2)),
                                         str((self.y,self.y2))) 
    
class Range(Rect):
    pass

class Close(object):
    def __init__(self, point=None, dist=float('inf')):
        self.point = point
        self.dist = dist

def distancePointRect(q, r):
    pass

def distance(q, p):
    return abs(q[0]-p[0]) + abs(q[1]-p[1])    

class OutOfSearchSpaceError(Exception):
    def __init__(self, x, ss):
        Exception.__init__(self, 'A point %s is out of search space.'\
                           'Search space is %s.' % (str(x), str(ss)))

class KdTree(object):
    def __init__(self, x=None, points=None,
                 searchSpace=Rect(-10000,-10000,20000,20000)):
        
        self._root = None
        self._searchSpace = searchSpace
        
        if x is not None and points is None:
            self.insert(x)
        elif x is None and points is not None:
            
            self.insert(points[0])
             
            for x in points[1:]:
                self.insert(x)
        elif x and points:
            raise RuntimeError('Both x and points are not none.')

    def __len__(self):
        return len(self._root or [])
    
    def getAllPoints(self):
        if self._root:
            return self._root.getAllPoints()
        else:
            return []
        
    def insert(self, x):
        
        if not self._searchSpace.containsPoint(x):
            raise OutOfSearchSpaceError(x, self._searchSpace)
        
        self._root = self._insert(x, self._root, 0)
        
    def nearestNeighbor(self, q):
        closest = self._nearNeigh(q, self._root, 0, self._getRootRect(),
                                  Close())
        return closest.point, closest.dist
    
    def range(self, Q):
        c, _ = self._range(Q, self._root, 0, self._getRootRect(), False)
        return c
    
    def rangePoints(self, Q):
        _, points = self._range(Q, self._root, 0, self._getRootRect(), True)
        return points
    
    def deleteNode(self, x):
        self._root = self._deleteNode(x, self._root, 0)
        
    def getMaxDepth(self):
        if self._root: return self._root.getMaxDepth()
        else: return 0
        
    def _getRootRect(self):
        return self._searchSpace
    
    def _insert(self, x, t, cd):
        if t is None:
            t = KdNode(x)
        elif x is t.data:
            raise RuntimeError('Duplicated data')
        elif x[cd] < t.data[cd]:
            t.left = self._insert(x, t.left, (cd+1)%DIM)
        else:
            t.right = self._insert(x, t.right, (cd+1)%DIM)
        return t
    
    def _nearNeigh(self, q, t, cd, r, close):
        if t is None:
            return close
        
        if r.distance(q) >= close.dist:
            return close
        
        dist = distance(q, t.data)
        if dist < close.dist:
            close = Close(t.data, dist)
        
        if q[cd] < t.data[cd]:
            close = self._nearNeigh(q, t.left, (cd+1)%DIM,
                                    r.trimLeft(cd, t.data), close)
            close = self._nearNeigh(q, t.right, (cd+1)%DIM,
                                    r.trimRight(cd, t.data), close)
        else:
            close = self._nearNeigh(q, t.right, (cd+1)%DIM,
                                    r.trimRight(cd, t.data), close)
            close = self._nearNeigh(q, t.left, (cd+1)%DIM,
                                    r.trimLeft(cd, t.data), close)
        
        return close
    
    def _range(self, Q, t, cd, C, queryPoints):
        
        c = 0
        points = queryPoints and []
        
        if t is None:
            return c, points
        if Q.isDisjointFromRect(C):
            return c, points
        if Q.containsRect(C):
            return len(t), queryPoints and t.getAllPoints()
        
        if Q.containsPoint(t.data):
            c += 1
            if queryPoints:
                points.append(t.data)
        
        cl, pl = self._range(Q, t.left, (cd+1)%DIM, C.trimLeft(cd, t.data),
                             queryPoints)
        cr, pr = self._range(Q, t.right, (cd+1)%DIM, C.trimRight(cd, t.data),
                             queryPoints)
        
        c += cl + cr
        if queryPoints:
            assert type(pl) == list
            assert type(pr) == list
            points += pl + pr
        
        return c, points
            
    def _deleteNode(self, x, t, cd):
        if t is None:
            raise RuntimeError('Invalid node to delete.')
        elif x == t.data:
            if t.right:
                t.data = t.right.findMin(cd, (cd+1)%DIM)
                t.right = self._deleteNode(t.data, t.right, (cd+1)%DIM)
            elif t.left:
                t.data = t.left.findMin(cd, (cd+1)%DIM)
                t.right = self._deleteNode(t.data, t.left, (cd+1)%DIM)
                t.left = None
            else:
                t = None
        elif x[cd] < t.data[cd]:
            t.left = self._deleteNode(x, t.left, (cd+1)%DIM)
        else:
            t.right = self._deleteNode(x, t.right, (cd+1)%DIM)
        
        return t
        
class KdTreeTestCase(unittest.TestCase):
    
    def testEmpty(self):
        
        t = KdTree()
        self.assertEqual(0, len(t))
        self.assertEqual([], t.getAllPoints())
        self.assertEqual(0, t.getMaxDepth())
    
    def testInsertion(self):
        
        t = KdTree((10,20))
        self.assertEqual((10,20), t._root.data)
        self.assertEqual(1, len(t))
        self.assertEqual(1, t.getMaxDepth())
        
        t.insert((20,5))
        self.assertEqual((20,5), t._root.right.data)
        self.assertEqual(2, len(t))
        self.assertEqual(2, t.getMaxDepth())
        
        t.insert((5,10))
        self.assertEqual((5,10), t._root.left.data)
        self.assertEqual(3, len(t))
        self.assertEqual(2, t.getMaxDepth())
        
        t.insert((0,7))
        self.assertEqual((0,7), t._root.left.left.data)
        self.assertEqual(4, len(t))
        self.assertEqual(3, t.getMaxDepth())
        
        t.insert((5,1))
        self.assertEqual((5,1), t._root.left.left.right.data)
        self.assertEqual(5, len(t))
        self.assertEqual(4, t.getMaxDepth())
        
        t.insert((25,20))
        self.assertEqual((25,20), t._root.right.right.data)
        self.assertEqual(6, len(t))
        self.assertEqual(4, t.getMaxDepth())
        
        self.assertRaises(OutOfSearchSpaceError, t.insert, (-100000,0))
        self.assertRaises(OutOfSearchSpaceError, t.insert, (100000,0))
        self.assertRaises(OutOfSearchSpaceError, t.insert, (0,-100000))
        self.assertRaises(OutOfSearchSpaceError, t.insert, (999999,100000))
        
    def testFindMin(self):
        t = KdTree((10,20))
        t.insert((20,5))
        t.insert((5,10))
        t.insert((0,7))
        t.insert((5,1))
        t.insert((25,20))
        #t.insert((25,20))
        
        
        self.assertEqual((0,7), t._root.findMin(0, 0))
        self.assertEqual((5,1), t._root.findMin(1, 0))
        
        t.insert((-1,-2))
        t.insert((100,-5))
        
        self.assertEqual((-1,-2), t._root.findMin(0, 0))
        self.assertEqual((100,-5), t._root.findMin(1, 0))
        
    def testDistance(self):
        
        self.assertEqual(2, distance((0,0), (1,1)))
        self.assertEqual(2, distance((-3,-5), (-4,-6)))
        self.assertEqual(1, distance((10,20), (10,21)))
        self.assertEqual(0, distance((10,20), (10,20)))
        
        r = Rect(0,0,5,10)
        self.assertEqual(0, r.distance((0,0)))
        self.assertEqual(0, r.distance((4,2)))
        self.assertEqual(2, r.distance((-1,-1)))
        self.assertEqual(3, r.distance((2,-3)))
        self.assertEqual(2, r.distance((6,-1)))
        self.assertEqual(3, r.distance((8,5)))
        self.assertEqual(3, r.distance((6,12)))
        self.assertEqual(10, r.distance((4,20)))
        self.assertEqual(10, r.distance((-5,15)))
        self.assertEqual(1, r.distance((-1,5)))
        
    def testRectTrim(self):
        
        r = Rect(0,0,10,5)
        self.assertEqual(Rect(0,0,3,5), r.trimLeft(0, (3,2)))
        self.assertEqual(Rect(0,0,10,2), r.trimLeft(1, (3,2)))
        
        self.assertEqual(Rect(3,0,7,5), r.trimRight(0, (3,2)))
        self.assertEqual(Rect(0,2,10,3), r.trimRight(1, (3,2)))
        
    def testRectDisjoint(self):
        
        r1 = Rect(0,0,10,5)
        r2 = Rect(20,20,1,1)
        r3 = Rect(-10,-5,100,6)
        r4 = Rect(3,4,2,3)
        r5 = Rect(-1,-1,5,100)
        r6 = Rect(12,0,10,5)
        r7 = Rect(3,-2,5,20)
        
        self.assertEqual(True, r1.isDisjointFromRect(r2))
        self.assertEqual(False, r1.isDisjointFromRect(r3))
        self.assertEqual(False, r1.isDisjointFromRect(r4))
        self.assertEqual(False, r1.isDisjointFromRect(r5))
        self.assertEqual(True, r1.isDisjointFromRect(r6))
        self.assertEqual(True, r1.isDisjointFromRect(r6))
        self.assertEqual(False, r1.isDisjointFromRect(r7))
        
        
    def testFindNearestNeighborQuery(self):
        
        t = KdTree(points=[(10,20),(20,5),(5,10),(0,7),(5,1),(25,20)])
        
        x, dist = t.nearestNeighbor((26,21))
        self.assertEqual((25,20), x)
        self.assertEqual(2, dist)
        
        x, dist = t.nearestNeighbor((11,22))
        self.assertEqual((10,20), x)
        self.assertEqual(3, dist)
        
        x, dist = t.nearestNeighbor((-2,6))
        self.assertEqual((0,7), x)
        self.assertEqual(3, dist)
        
        x, dist = t.nearestNeighbor((0,0))
        self.assertEqual((5,1), x)
        self.assertEqual(6, dist)
        
        x, dist = t.nearestNeighbor((18,5))
        self.assertEqual((20,5), x)
        self.assertEqual(2, dist)
        
        x, dist = t.nearestNeighbor((12,5))
        self.assertEqual((20,5), x)
        self.assertEqual(8, dist)
        
        x, dist = t.nearestNeighbor((10,5))
        self.assertEqual((5,1), x)
        self.assertEqual(9, dist)
        
    def testFindNearestNighbor2Query(self):

        n = 1000 # point count
        nq = 100 # query count
        
        points = list(set((getRandomPoint() for _ in range(n))))
        t = KdTree(points=points)
        
        for _ in range(nq):
            q = getRandomPoint()
            nn, dist = t.nearestNeighbor(q)
            
            # Check our query result.
            sortf = lambda x: distance(x,q)
            # nnSol can contain two or more points.
            nnSol = list(next(itertools.groupby(sorted(points, key=sortf), key=sortf))[1])
            
            i = nnSol.index(nn)
            self.assertLessEqual(0, i)
            self.assertEqual(nnSol[i], nn)
            self.assertEqual(distance(nnSol[i],q), dist)
            self.assertEqual(distance(nnSol[i],q), distance(nn,q))
                
    def testRangeQuery(self):
        
        points = [(10,20),(20,5),(5,10),(0,7),(5,1),(25,20)]
        t = KdTree(points=points)
        
        self.assertEqual(set(points), set(t.getAllPoints()))
        
        self.assertEqual(6, len(t))
        self.assertEqual(2, t.range(Range(0,0,8,8)))
        self.assertEqual(3, t.range(Range(9,4,100,100)))
        self.assertEqual(0, t.range(Range(100,100,5,5)))
        self.assertEqual(1, t.range(Range(23,18,5,5)))
        self.assertEqual(2, t.range(Range(3,0,3,20)))
        self.assertEqual(0, t.range(Range(-3,-3,1,1)))
        self.assertEqual(1, t.range(Range(-1,0,2,8)))
        self.assertEqual(2, t.range(Range(0,15,30,5)))
        self.assertEqual(4, t.range(Range(0,0,50,18)))
        self.assertEqual(len(t), t.range(Range(-100,-100,200,200)))
        
        self.assertEqual(set([(0,7),(5,1)]),
                         set(t.rangePoints(Range(0,0,8,8))))
        self.assertEqual(set([(10,20),(20,5),(25,20)]),
                         set(t.rangePoints(Range(9,4,100,100))))
        self.assertEqual(set([]),
                         set(t.rangePoints(Range(100,100,5,5))))
        self.assertEqual(set(points),
                         set(t.rangePoints(Range(-100,-100,200,200))))
    
    def testRange2Query(self):

        n = 1000 # point count
        nq = 100 # query count
        
        points = list(set((getRandomPoint() for _ in range(n))))
        t = KdTree(points=points)
        
        for _ in range(nq):
            q0 = getRandomPoint()
            w = random.randrange(0,1000)
            h = random.randrange(0,1000)
            Q = Range(q0[0],q0[1],w,h)
            rangePoints = t.rangePoints(Q)
            
            # Check our query result.
            rangePointSet = set(rangePoints) 
            rangePointSetSol = set([pp for pp in points if Q.containsPoint(pp)])
            self.assertEqual(rangePointSetSol, rangePointSet)
                
    def testDeleteNode(self):
        points = [(10,20),(20,5),(5,10),(0,7),(5,1),(25,20)]
        t = KdTree(points=points)
        
        self.assertEqual(set(points), set(t.getAllPoints()))
        
        t.deleteNode((10,20))
        self.assertEqual(set(points)-set([(10,20)]),
                         set(t.getAllPoints()))
        
        t.deleteNode((0,7))
        self.assertEqual(set(points)-set([(10,20),(0,7)]),
                         set(t.getAllPoints()))
        
        t.deleteNode((5,1))
        self.assertEqual(set(points)-set([(10,20),(0,7),(5,1)]),
                         set(t.getAllPoints()))
        
        t.deleteNode((20,5))
        self.assertEqual(set(points)-set([(10,20),(0,7),(5,1),(20,5)]),
                         set(t.getAllPoints()))
        
        t.deleteNode((5,10))
        self.assertEqual(set(points)-set([(10,20),(0,7),(5,1),(20,5),(5,10)]),
                         set(t.getAllPoints()))
        
        t.deleteNode((25,20))
        self.assertEqual(set([]), set(t.getAllPoints()))
        
        t.insert((0,0))
        self.assertEqual(set([(0,0)]), set(t.getAllPoints()))
        
        t.insert((1,0))
        self.assertEqual(set([(0,0),(1,0)]), set(t.getAllPoints()))
        
        t.deleteNode((0,0))
        self.assertEqual(set([(1,0)]), set(t.getAllPoints()))
        
def getRandomPoint():
    SIZE = 9000
    return (random.randrange(-SIZE,SIZE), random.randrange(-SIZE,SIZE))       
    #return (random.randrange(0,SIZE), random.randrange(0,SIZE))

def runit(n=2000, nq=1000):
    t = KdTree(getRandomPoint())
    for _ in range(n):
        t.insert(getRandomPoint())
        
    for _ in range(nq):
        t.nearestNeighbor(getRandomPoint())
        
if __name__ == '__main__':
    
    random.seed(1)
    
    '''
    === Nearest neighbor search ===
    '''    
    points = list(set([getRandomPoint() for x in range(500)]))
    t = KdTree(points=points)
    print '# of points', len(points)
    
    t0 = time.clock()
    nq = 10 # query count
    for i in range(nq):
        q = getRandomPoint() #(9000,9000)
        r2, dist = t.nearestNeighbor(q)
        '''
        r1 = min(points, key=lambda x: distance(x,q))
        if r1 != r2 and distance(r1,q) != distance(r2,q):
            print 'ERROR! q=%s : r1=%s [%d], r2=%s [%d]' % (str(q),
                                                            str(r1),
                                                            distance(r1,q),
                                                            str(r2),
                                                            distance(r2,q))
        if i % 100 == 0:
            print 'Querying...', i
        '''
    elapsed = time.clock() - t0
    print 'kd-tree:', elapsed, 'seconds elapsed.', elapsed/nq, 'sec per query.'
    
    '''
    === Nearest neighbor (bruteforce) for the comparison ===
    '''
    t0 = time.clock()
    for i in range(nq):
        q = getRandomPoint() #(9000,9000)
        r1 = min(points, key=lambda x: distance(x,q))
    
    elapsed = time.clock() - t0
    print 'bruteforce:', elapsed, 'seconds elapsed.', elapsed/nq, 'sec per query.'
    
    '''
    === Range query ===
    '''
    t0 = time.clock()
    nq = 100 # query count
    for i in range(nq):
        q0 = getRandomPoint() #(9000,9000)
        w = random.randrange(0,1000)
        h = random.randrange(0,1000)
        Q = Range(q0[0],q0[1],w,h)
        
        rangePoints = t.rangePoints(Q)
        #print len(rangePoints)
        
        '''
        
        r1 = set(rangePoints) 
        r2 = set([pp for pp in points if Q.containsPoint(pp)])
        if r1 != r2:
            print "ERROR!"
            print '  Q=',str(Q)
            print "  r1=", r1
            print "  r2=", r2
            '''

    elapsed = time.clock() - t0
    print 'kd-tree rangePoints:', elapsed, 'seconds elapsed.', elapsed/nq, 'sec per query.'
    
    
    '''
    === Insertion/Deletion ===
    '''
    t0 = time.clock()
    n = 500
    points = list(set([getRandomPoint() for x in range(n)]))
    t = KdTree(points=points)
    print '# of points', len(points)
    print 'kd-tree construction:', elapsed, 'seconds elapsed.', elapsed/n, 'sec per element. Max depth=', t.getMaxDepth()

    t0 = time.time()
    nq = n*2 # insertion/deletion count
    elapsedList = []
    insCount = delCount = 0
    for i in range(nq):
        
        action = random.choice(['INS', 'DEL'])
        if action == 'INS':
            p = getRandomPoint()
            points.append(p)
            
            tt0 = time.time()
            t.insert(p)
            elapsedList.append(time.time() - tt0)
            
            insCount += 1
        else:
            p = random.choice(points)
            points.remove(p)
            
            tt0 = time.time()
            t.deleteNode(p)
            elapsedList.append(time.time() - tt0)
            
            delCount += 1

    mean = sum(elapsedList) / len(elapsedList)
    variance = sum((v**2 for v in elapsedList)) / len(elapsedList) - mean**2
    stddev = math.sqrt(variance)
            
    elapsed = time.time() - t0
    print 'kd-tree ins', insCount, 'del', delCount
    print 'kd-tree ins/del:', elapsed, 'seconds elapsed.', mean, 'sec per ins/del.', 'stddev=', stddev, 'Max depth=', t.getMaxDepth()
    
    