#cellular automata in Pyglet
import pyglet
import numpy as np
import random
from pyglet.window import mouse, key

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 480
CELL_WIDTH = 8
CELL_HEIGHT = 8

window = pyglet.window.Window(width = WINDOW_WIDTH, height = WINDOW_HEIGHT)

class Cell:
    EMPTY = 0
    YOUNG = 1
    YOUNG_2 = 2
    MATURE = 3
    OLD = 4
    DEAD = 5
    LEAF = 6
    LEAF_2 = 7
    LEAF_3 = 8
    LEAF_4 = 9
    LEAF_5 = 10
    
    EXPANDED_NEIGHBORHOOD = [(y,x) for y in range(-2,3) for x in range(-2,3) if not (x==0 and y==0) and (abs(x) + abs(y) < 3)]
    EXPANDED_NEIGHBORHOOD_GROW = EXPANDED_NEIGHBORHOOD[5:]
    EXPANDED_NEIGHBORHOOD_GROW_VERTICAL_BIAS = EXPANDED_NEIGHBORHOOD[7:]
    
    MOORE_NEIGBHORHOOD = [ (x,y) for x in range(-1,2) for y in range(-1,2) if not (x==0 and y==0) ]
    MOORE_NEIGBHORHOOD_GROW = MOORE_NEIGBHORHOOD[3:] 
    MOORE_NEIGBHORHOOD_GROW_VERTICAL_BIAS = MOORE_NEIGBHORHOOD[5:] 
    
    COLORS = {LEAF_5: (0,255,96), LEAF_4: (16,255,64), LEAF_3: (0,255,32), LEAF_2: (0,240,32), LEAF: (0,240,0), YOUNG: (64,192,16), YOUNG_2: (64,192,16), MATURE: (128,128,32), OLD: (192,64,48), DEAD: (160,64,64)}
    
    
    
class CellGrid:
    def __init__(self, width = WINDOW_WIDTH//CELL_WIDTH, height = WINDOW_HEIGHT//CELL_HEIGHT ):
        '''
        Initializes a grid
        '''
        self.width, self.height = width, height
        self.grid = np.full((height,width), Cell.EMPTY )

    def limit_x_y(self,x,y,wraparound = False):
        _x, _y = x, y
        if not wraparound:
            _y = max( ( 0 , min( (y , self.height - 1 ) ) ) ) 
            _x = max( ( 0 , min( (x , self.width - 1 ) ) ) )             
        else:
            _y = (y + self.height) % self.height
            _x = (x + self.width) % self.width
            
        return (_x, _y)
        
    def get_cell(self, x, y):
        _x, _y= self.limit_x_y(x,y)
        return self.grid[_y][_x]
        
    def set_cell(self, x, y, new_state):
        _x, _y = self.limit_x_y(x,y)
        self.grid[_y][_x] = new_state
    
    def get_neighbors_number(self, x, y, neighborhood = Cell.EXPANDED_NEIGHBORHOOD, search_for = [Cell.YOUNG, Cell.YOUNG_2, Cell.MATURE, Cell.OLD]):
        '''
        get the number of neighboring cells that match the specified search criteria
        '''
        neighbors = [self.get_cell(x+dx,y+dy) for dy,dx in neighborhood]
        return sum([1 for neighbor in neighbors if neighbor in search_for])
    
    def get_coords_neighbors(self, x, y, neighborhood = Cell.EXPANDED_NEIGHBORHOOD):
        return [self.limit_x_y(x+dx, y+dy) for (dy,dx) in neighborhood]
    
    def get_valid_grow_cells(self, x, y, check_neighborhood = Cell.MOORE_NEIGBHORHOOD_GROW, neighbor_limit = [0,1]):
        return [(i,j) for (i,j) in self.get_coords_neighbors(x,y,check_neighborhood) if self.get_neighbors_number(i,j) in neighbor_limit and self.get_cell(i,j) in [Cell.EMPTY] ]
    
    
    def update(self):
        '''
        Update values in grid 
        '''
        new_grid = np.copy(self.grid)
        for y in range(self.height):
            for x in range(self.width):
            
                current_cell = self.grid[y][x]
                #growth of overall tree
                if current_cell in [Cell.YOUNG, Cell.YOUNG_2, Cell.MATURE]:
                    if self.get_neighbors_number(x,y) in [0,1,2]:
                        grow_neighborhood = Cell.MOORE_NEIGBHORHOOD_GROW
                        
                        if current_cell in [Cell.YOUNG, Cell.YOUNG_2]:
                            grow_neighborhood = Cell.MOORE_NEIGBHORHOOD_GROW_VERTICAL_BIAS
                            
                        #valid_grow_cells = [(i,j) for (i,j) in self.get_coords_neighbors(x,y,grow_neighborhood) if self.get_neighbors_number(i,j) in [0,1] and self.get_cell(i,j) in [Cell.EMPTY] ]
                        valid_grow_cells =  self.get_valid_grow_cells(x, y, check_neighborhood = grow_neighborhood, neighbor_limit = [0,1])
                        if valid_grow_cells:
                            random.shuffle(valid_grow_cells)
                            x_choose, y_choose = random.choice( valid_grow_cells )
                            new_grid[y_choose][x_choose] = random.choice((Cell.EMPTY, Cell.YOUNG))
                        
                    new_grid[y][x] = current_cell + 1
                        
                #leaf growth
                if current_cell in [Cell.OLD]:
                    if self.get_neighbors_number(x,y) in [0,1]:
                        #valid_grow_cells = [(i,j) for (i,j) in self.get_coords_neighbors(x,y,Cell.MOORE_NEIGBHORHOOD_GROW) if self.get_neighbors_number(i,j) in [0,1] and self.get_cell(i,j) in [Cell.EMPTY] ]
                        valid_grow_cells = self.get_valid_grow_cells(x, y, check_neighborhood = Cell.MOORE_NEIGBHORHOOD_GROW_VERTICAL_BIAS, neighbor_limit = [0,1])
                        if valid_grow_cells:
                            random.shuffle(valid_grow_cells)
                            x_choose, y_choose = random.choice(valid_grow_cells)
                            new_grid[y_choose][x_choose] = random.choice([Cell.LEAF_4, Cell.EMPTY])
                            
                    new_grid[y][x] = Cell.DEAD
                
                if current_cell in [Cell.LEAF_5, Cell.LEAF_4, Cell.LEAF_3, Cell.LEAF_2]:
                    if self.get_neighbors_number(x,y) in [0,1,2,3,4,5,6]:
                        #valid_grow_cells = [(i,j) for (i,j) in self.get_coords_neighbors(x,y,Cell.MOORE_NEIGBHORHOOD_GROW) if self.get_neighbors_number(i,j) in [0,1,2] and self.get_cell(i,j) in [Cell.EMPTY] ]
                        valid_grow_cells = self.get_valid_grow_cells(x, y, neighbor_limit = [0,1,2])
                        if valid_grow_cells:
                            random.shuffle(valid_grow_cells)
                            x_choose, y_choose = random.choice( valid_grow_cells )  
                            new_grid[y_choose][x_choose] = random.choice([current_cell - 1, Cell.EMPTY])
                    
                    new_grid[y][x] = current_cell - 1
            
            
        self.grid = new_grid
     
    def draw(self):
        '''
        Draw each cell in the grid
        '''
        for y in range(self.height):
            for x in range(self.width):
                current_cell = self.get_cell(x,y)
                
                if not current_cell == Cell.EMPTY:
                    draw_color = Cell.COLORS[current_cell]
                    X1,Y1 = x * CELL_WIDTH, y * CELL_HEIGHT,
                    X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
                    pyglet.graphics.draw(4 ,pyglet.gl.GL_POLYGON, ('v2i',[X1,Y1, X2,Y1, X2,Y2, X1,Y2] ), ('c3B', draw_color * 4 ) )
                    
                    
TEST = CellGrid()

@window.event
def on_draw():
    window.clear()
    TEST.draw()

@window.event        
def on_mouse_press(x, y, button, modifiers):
    _x, _y = x // CELL_WIDTH, y // CELL_HEIGHT
    if button == mouse.LEFT:
        TEST.set_cell(_x, _y, Cell.YOUNG)
    elif button == mouse.RIGHT:
        TEST.set_cell(_x,_y,Cell.EMPTY)
           
           
def update(t):
    TEST.update()

            
pyglet.clock.schedule_interval(update, 1/120)
pyglet.app.run()
