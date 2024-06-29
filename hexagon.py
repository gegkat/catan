from dataclasses import dataclass
import random
from enum import Enum
from math import pi, sqrt
from typing import Any


VERTEX_RADIUS = 12
START_X = 400
START_Y = 200
HEXAGON_SIZE = 45
LINE_WIDTH = 8

class Resource(Enum):
    DESERT = (0, '#F4A460') # (Sandy Brown)
    ORE = (1, '#7D7D7D') # (Dark Gray)
    SHEEP = (2, '#9ACD32') # (Yellow Green)
    WOOD = (3, '#228B22') # (Forest Green)
    BRICK = (4, '#B22222') # (Firebrick)
    WHEAT = (5, '#FFD700') # (Gold)

    def __init__(self, key: int, color: str) -> None:
        self.key = key
        self.color = color

    def next(self) -> 'Resource':
        members = list(self.__class__)
        index = (members.index(self) + 1) % len(members)
        return members[index]

def get_resources(num_resources: int) -> list[Resource]:
    ''' Generates a shuffled list of resources. Will include exactly 
    one desert and approximately equal amounts of the others.
    '''
    # Ensure we have exactly one desert
    resources = [Resource.DESERT]
    numbers = [7]

    # Fill out list of resources in priority order.
    resource_priority = (Resource.SHEEP, Resource.WOOD, Resource.WHEAT, 
             Resource.BRICK, Resource.ORE)
    number_priority = (6, 8, 5, 9, 4, 10, 3, 11, 2, 12)
    for i in range(num_resources-1):
        resources.append(resource_priority[i % len(resource_priority)])
        numbers.append(number_priority[i % len(number_priority)])

    random.shuffle(resources)
    random.shuffle(numbers)
    return resources, numbers

def deg2rad(x: float) -> float:
    return pi / 180 * x

@dataclass(frozen=True, eq=True)
class Pixel: 
    x: float
    y: float

    def distance(self, other: 'Pixel') -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return sqrt(dx*dx + dy*dy)
    
def cross_product(p0: 'Pixel', p1: 'Pixel', p2: 'Pixel') -> float:
    return (p0.x - p1.x) * (p2.y - p1.y) - (p0.y - p1.y) * (p2.x - p1.x)

@dataclass(frozen=True, eq=True)
class Coordinate:
    q: int
    r: int
    s: int

    def to_pixel(self) -> Pixel:
        ''' We use cube coordinates here. 
        q points toward 2 on a clock.
        r points toward 6 on a clock.
        s points toward 10 on a clock.
        https://www.redblobgames.com/grids/hexagons/#coordinates-cube

        Since X points to 3 and Y points to 6, the x-y components of 
        each vector are:
        q: (cos(30), -sin(30))
        r: (0, 1)
        s: (-cos(30), -sin(30))
        '''
        dx = (self.q - self.s) * sqrt(3) / 2
        dy = self.r - (self.q + self.s) / 2
        x = START_X + HEXAGON_SIZE * dx
        y = START_Y + HEXAGON_SIZE * dy
        return Pixel(x, y)
    
    def add(self, dq: int, dr: int, ds: int) -> 'Coordinate':
        return Coordinate(self.q + dq, self.r + dr, self.s + ds)
    
    def greater(self, other: 'Coordinate') -> bool:
        if self.q == other.q:
            if self.r == other.r:
                return self.s > other.s
            return self.r > other.r
        return self.q > other.q

class Hexagon: 
    def __init__(self, q: int, r: int, resource: Resource, number: int) -> None:
        self.coordinate = Coordinate(q, r, -q - r)
        self.resource = resource
        self.number = number

    def get_pixel(self) -> Pixel:
        return self.coordinate.to_pixel()

    def get_vertices_coordinates(self) -> tuple[Coordinate, Coordinate, Coordinate, Coordinate, Coordinate, Coordinate]:
        # clockwise starting with +q
        return (
            self.coordinate.add( 1,  0,  0),
            self.coordinate.add( 0,  0, -1),
            self.coordinate.add( 0,  1,  0),
            self.coordinate.add(-1,  0,  0),
            self.coordinate.add( 0,  0,  1),
            self.coordinate.add( 0, -1,  0),
        )
    
    # This is approximate. This checks if we are inside the inner circle.
    def inside(self, pixel: Pixel) -> bool:
        return pixel.distance(self.get_pixel()) < HEXAGON_SIZE * sqrt(3) / 2

    def toggle_color(self) -> None:
        self.resource = self.resource.next()

    def color(self) -> str:
        return self.resource.color
    
    def to_dict(self) -> dict:
        pixels = [c.to_pixel() for c in self.get_vertices_coordinates()]
        center = self.coordinate.to_pixel()
        return {'vertices':[(p.x, p.y) for p in pixels], 
                'center': (center.x, center.y),
                'number': self.number,
                'color': self.color()}

    
class Vertex: 
    def __init__(self, coordinate: Coordinate) -> None:
        self.coordinate = coordinate
        self.color = 'rgba(255, 255, 255, 0)'

    def get_pixel(self) -> Pixel:
        return self.coordinate.to_pixel()
    
    def inside(self, pixel: Pixel) -> bool:
        return pixel.distance(self.get_pixel()) < VERTEX_RADIUS

    def toggle_color(self, color) -> None:
        if self.color == color:
            self.color = 'rgba(255, 255, 255, 0)'
        else:
            self.color = color
    
    def to_dict(self) -> dict[str, Any]:
        pixel = self.get_pixel()
        return {'x': pixel.x, 'y': pixel.y, 'radius': VERTEX_RADIUS, 'color': self.color}
    
class Line:
    def __init__(self, start: Coordinate, end: Coordinate) -> None:
        self.start = start.to_pixel()
        self.end = end.to_pixel()
        self.color = 'rgba(255, 255, 255, 0)'
        self.width = LINE_WIDTH

    # def inside(self, pixel: Pixel) -> bool:
    #     pixel1 = self.start.to_pixel()
    #     pixel2 = self.end.to_pixel()
    #     midpoint = Pixel((pixel1.x + pixel2.x) / 2, 
    #                      (pixel1.y + pixel2.y) / 2)
    #     return pixel.distance(midpoint) < VERTEX_RADIUS
    
    def unit_direction(self) -> Pixel:
        length = self.length()
        return Pixel((self.end.x - self.start.x) / length, 
                     (self.end.y - self.start.y) / length)
    
    def length(self) -> float:
        return self.start.distance(self.end)

    def get_corners(self) -> tuple[Pixel, Pixel, Pixel, Pixel]:

        # Calculate direction vector
        direction = self.unit_direction()

        # Calculate perpendicular vector and normalize to half the width
        offsetX = (-direction.y * self.width) / 2
        offsetY = (direction.x * self.width) / 2

        # Calculate rectangle corners
        A = Pixel(self.start.x + offsetX, self.start.y + offsetY)
        B = Pixel(self.start.x - offsetX, self.start.y - offsetY)
        C = Pixel(self.end.x + offsetX, self.end.y + offsetY)
        D = Pixel(self.end.x - offsetX, self.end.y - offsetY)
        return (A, B, C, D)

    def inside(self, pixel: Pixel):
        A, B, C, D = self.get_corners()
        # Check if the point is inside the rectangle using cross products
        if (cross_product(A, B, pixel) <= 0 and cross_product(B, D, pixel) <= 0 and
            cross_product(D, C, pixel) <= 0 and cross_product(C, A, pixel) <= 0):
            return True
        return False

    def toggle_color(self, color) -> None:
        if self.color == color:
            self.color = 'rgba(255, 255, 255, 0)'
        else:
            self.color = color

    def to_dict(self) -> dict[str, Any]:
        A, B, C, D = self.get_corners()
        return {'x1': A.x, 'y1': A.y, 
                'x2': B.x, 'y2': B.y, 
                'x3': D.x, 'y3': D.y, 
                'x4': C.x, 'y4': C.y, 
                'width': self.width, 'color': self.color}