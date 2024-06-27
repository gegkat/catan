import hexagon

def hexagon_layout(num_rings: int) -> list[hexagon.Hexagon]:
    '''Configures a hexagonal tiling.'''
    N = num_rings
    num_hexagons = 1 + 3*(N-1)*N
    resources = hexagon.get_resources(num_hexagons)
    hexagons = []
    for i in range(-N+1, N):
        for j in range(-N+1, N):
            if abs(i + j) >= N:
                continue
            hexagons.append(hexagon.Hexagon(i, j, resources.pop()))
    assert(len(resources) == 0)
    return hexagons

def diamond_layout(num_rings: int) -> list[hexagon.Hexagon]:
    '''Configures a diagonal tiling. '''
    N = num_rings
    num_hexagons = (2*N-1)**2
    resources = hexagon.get_resources(num_hexagons)
    hexagons = []
    for i in range(-N+1, N):
        for j in range(-N+1, N):
            hexagons.append(hexagon.Hexagon(i, j, resources.pop()))
    assert(len(resources) == 0)
    return hexagons