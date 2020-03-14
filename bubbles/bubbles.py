from collections import namedtuple
from itertools import chain
from typing import Tuple, List


class Bubble(str):
    pass


# colors
yellow = Bubble('yellow')
orange = Bubble('orange')
red = Bubble('red')
blue = Bubble('blue')
lightblue = Bubble('lightblue')
green = Bubble('green')
pink = Bubble('pink')
lightgreen = Bubble('lightgreen')
gray = Bubble('gray')
brown = Bubble('brown')
purple = Bubble('purple')
sea = Bubble('sea')


class Bottle:
    size = 4

    def __init__(self, *bubbles: Bubble):
        """first is upper, last is lower"""
        self.bubbles = list(bubbles)

    def __repr__(self):
        return f"<Bottle: {self.bubbles.__repr__()}>"

    def __len__(self):
        return len(self.bubbles)

    def __getitem__(self, item):
        if len(self) > item:
            return self.bubbles[item]
        return None

    def pop(self):
        if not len(self):
            raise ValueError("Empty")
        return self.bubbles.pop(0)

    @property
    def full(self):
        return len(self) >= self.size

    @property
    def empty(self):
        return not len(self)

    def insertFrom(self, bottle: 'Bottle'):
        if self.full:
            raise ValueError("Full")
        if not self.empty and self[0] != bottle[0]:
            raise ValueError("Wrong color")
        self.bubbles.insert(0, bottle.pop())


class PathPart:
    def __init__(self, from_, to_, bubble):
        self.from_ = from_
        self.to_ = to_
        self.what = bubble

    def __repr__(self):
        return f"<PathPart: {self.from_}->{self.to_} {self.what}>"

    def __eq__(self, other):
        if isinstance(other, PathPart):
            return self.from_ == other.from_ and self.to_ == other.to_ and self.what == other.what
        raise ValueError('Cannot compare')


Step = namedtuple("Step", ("from_", "to_"))
MAX_CYCLES_LENGTH = 1000
MAX_RECURSIVE_LEVEL = 500


def getPathCycleLastElems(path):
    cycle = None
    for cycleLen in range(2, MAX_CYCLES_LENGTH):
        if len(path) >= cycleLen * 2:
            if path[-cycleLen:] == path[-2 * cycleLen:-cycleLen]:
                cycle = path[-cycleLen:]
    return cycle


class Game:
    GENERATED_GAMES = set()

    def __init__(self, *bottles: Bottle, passedPath: List[PathPart] = ()):
        """ Use applyPath to recreate part of Game"""
        self.bottles: Tuple[Bottle] = tuple(Bottle(*bottle.bubbles) for bottle in bottles)
        self.path: List[PathPart] = [ppart for ppart in passedPath]
        self.foolcheck()

    def foolcheck(self):
        allBubbles = list(chain(*(bottle.bubbles for bottle in self.bottles)))
        for bubble in set(allBubbles):
            if allBubbles.count(bubble) != Bottle.size:
                raise ValueError(f"Bubble '{bubble}' count is '{allBubbles.count(bubble)}'.")

    def applyPath(self, path: List[PathPart]):
        for pathPart in path:
            self.move(pathPart.from_, pathPart.to_)
        return self

    def move(self, from_, to_):
        bottleFrom = self.bottles[from_]
        bottleTo = self.bottles[to_]

        bubble = bottleFrom[0]
        bottleTo.insertFrom(bottleFrom)

        self.path.append(PathPart(from_, to_, bubble=bubble))

    @property
    def superBottles(self):
        idxs = [(idx, bottle) for idx, bottle in enumerate(self.bottles) if len(set(bottle.bubbles)) == 1]
        idxs = sorted(idxs, key=lambda idxBottle: len(idxBottle[1]), reverse=True)
        idxs = [idx[0] for idx in idxs]
        return idxs

    def genSteps(self):
        # fill up super bottles
        for idxTo in self.superBottles:
            targetBubble = self.bottles[idxTo][0]
            for idxFrom, bottleFrom in enumerate(self.bottles):
                if idxTo == idxFrom:
                    continue
                if targetBubble == bottleFrom[0]:
                    yield Step(idxFrom, idxTo)

        # generate all steps
        for idxFrom, bottleFrom in enumerate(self.bottles):
            if bottleFrom.empty:
                continue
            if idxFrom in self.superBottles:
                # dont move from super-bottles
                continue
            for idxTo, bottleTo in enumerate(self.bottles):
                if idxFrom == idxTo:
                    continue
                if bottleTo.full:
                    continue

                # custom stupid case check:
                #
                # 1 - => - 1
                # 1 1    1 1
                # 2 1    2 1
                # 3 5    3 5
                if not bottleTo.empty:
                    emptyCount = bottleTo.size - len(bottleTo)
                    upperColorCount = 1
                    for idx, bubble in enumerate(bottleFrom):
                        if bubble == bottleFrom[0]:
                            upperColorCount = idx + 1
                        else:
                            break
                    if upperColorCount > emptyCount:
                        continue

                # checks passed
                if bottleTo.empty or bottleFrom.bubbles[0] == bottleTo.bubbles[0]:
                    # criteria passed
                    yield Step(idxFrom, idxTo)

    @property
    def solved(self) -> bool:
        return len(self.superBottles) == len(self.bottles)

    def solve(self):
        if self.solved:
            return True

        if len(self.path) > MAX_RECURSIVE_LEVEL:
            return False

        for step in self.genSteps():
            newPathPart = PathPart(*step, self.bottles[step.from_][0])
            # checks
            cycle = getPathCycleLastElems(self.path + [newPathPart])
            if cycle:
                continue

            # recursive game attempts
            steppedGame = Game(*self.bottles, passedPath=self.path).applyPath([newPathPart])
            if steppedGame.isDuplicate:
                continue
            else:
                steppedGame.save()
            steppedGame.solve()

            if steppedGame.solved:
                self.applyPath(steppedGame.path[len(self.path):])
                assert self.solved
                return

    def show(self):
        print(f'Solved: {self.solved}')
        print(f'Bottles:')
        for idx in range(Bottle.size):
            for bottle in self.bottles:
                print(f"{bottle[idx]}".center(12, ' '), end='')
            print()
        print(f'Path ({len(self.path)}):')
        for move in self.path:
            print("Move", move.from_ + 1, "->", move.to_ + 1, move.what)

    def hash(self):
        return tuple(chain(*(bottle.bubbles for bottle in self.bottles)))

    def save(self):
        self.GENERATED_GAMES.add(self.hash())

    @property
    def isDuplicate(self):
        return self.hash() in self.GENERATED_GAMES


def main():
    assert getPathCycleLastElems([1, 0, 1, 0]) == getPathCycleLastElems([3, 2, 1, 0, 1, 0]) == [1, 0]
    assert getPathCycleLastElems([1, 0, 2, 1, 0, 2]) == [1, 0, 2]
