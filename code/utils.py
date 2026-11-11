###
### Globals (note: comments in doxygen)
###

LARGE_NUMBER = 999999 # Proxy for Infinity 

PLANT_GROUNDS = {
    Entities.Grass: [Grounds.Grassland, Grounds.Soil]
    , Entities.Tree: [Grounds.Grassland, Grounds.Soil]
    , Entities.Bush: [Grounds.Grassland, Grounds.Soil]
    , Entities.Carrot: [Grounds.Soil]
    , Entities.Pumpkin: [Grounds.Soil]
    , Entities.Sunflower: [Grounds.Soil]
    , Entities.Cactus: [Grounds.Soil]
    }

DIRECTION_TO_TUPLE = {
    North: (0,1)
    , South: (0,-1)
    , East: (1,0)
    , West: (-1,0)
}

###
### Misc
###

def harvest_safe(default_entity=Entities.Pumpkin):
    #"""! @brief Harvest if possible. Then replace the plant if possible.
    #@param default_entity What to plant if not sure. Biggest known case is if original entity was a dead pumpkin.
    #"""

    entity_type = get_entity_type()
    if not can_harvest():
        if entity_type == Entities.Dead_Pumpkin:
            plant(Entities.Pumpkin)
        elif entity_type == None:
            plant(default_entity)
    else:
        harvest()
        if get_entity_type() != entity_type:
            plant(entity_type)
    
def do_water(repeat=False):
    #"""! @brief Water the plants until <=1 saturation.
    #@param repeat If false then water at most once even if more water is needed.
    #"""
    if num_items(Items.Water) <= 0:
        return 0
    if get_water() > 0.75:
        return 0
    else:
        use_item(Items.Water)
        
        nwaters = 1
        if repeat:
            nwaters += do_water(repeat)
        
        return nwaters

def plant_this(entity_type, ground_type=None):
    #"""! @brief Plant entity in appropraite ground"""
    
    current_ground_type = get_ground_type()
    if ground_type == None:
        if current_ground_type in PLANT_GROUNDS[entity_type]:
            ground_type = current_ground_type
        else:
            ground_type = PLANT_GROUNDS[entity_type][0]
    
    if current_ground_type!= ground_type:
        till()
    
    if get_entity_type() != entity_type:
        plant(entity_type)

def tree_is_adjacent():
    #"""! @brief TRUE if there is a tree adjacent in a cardinal direction."""

    if get_entity_type(North) == Entities.Tree:
       return True
    elif get_entity_type(South) == Entities.Tree:
        return True
    elif get_entity_type(East) == Entities.Tree:
        return True
    elif get_entity_type(West) == Entities.Tree:
        return True

def wait_for_drone_completion(drones=None):
    #"""! @brief Wait until all spawned drones have finished thier tasks"""
    if drones != None:
        for idrone in drones:
            wait_for(idrone)
    else:
        while num_drones() > 1:
            pass

###
### Pumpkins
###


def plant_pumpkin_patch_once(x0, y0, width, past_problem_locations=None, harvest_if_done=True, do_fertalize=False):
    #"""! @brief Plant a width*width pumpkin patch with lower left corner at (x0,y0). If already planted, replants dead pumkins in area.
    #@param past_problem_locations A list of (x,y). Only plant on these locations (ignore other locations). None indicates all locations in square. Empty set [] incidates no locations.
    #@param harvest_if_done If all plants are ready to harvest, harvest them if TRUE.
    #@return Returns modified past_problem_locations, locations which are not ready to harvest.
    #"""
    
    def tmp_plant(kwargs):
        do_water()
        if get_entity_type() != Entities.Pumpkin:
            plant_this(Entities.Pumpkin, Grounds.Soil)
            if do_fertalize:
                use_item(Items.Fertilizer)
            return [[kwargs['x'],kwargs['y']]]
        elif not can_harvest():
            return [[kwargs['x'],kwargs['y']]]
        else:
            return []
    
    if past_problem_locations == None:
        problem_locations = loop_rectangle(x0, y0, x0+width, y0+width, tmp_plant, [])
    else:
        problem_locations = []
        for xy in past_problem_locations:
            move_to(xy[0], xy[1])
            problem_locations += tmp_plant({'x': xy[0], 'y': xy[1]})
    
    if harvest_if_done:  
        if len(problem_locations) == 0:
            move_to(x0,y0)
            harvest()
            problem_locations = None
    
    return problem_locations


###
### Sunflower
###


def plant_sunflowers(water=True):
    #"""! @brief Plant sunflowers everywhere.
    #@return List describing the location of sunflowers of different lengths. Each index indicates a petal length. Within each index is a list of (x,y) positions of sunflowers with that petal length.
    #@todo Limit this to a specified region rather than everywhere. A close grouping of 10 sunflowers is likely most efficient.
    #"""
    all_petal_lengths = []
    for i in range(16): # Max petals is 15
        all_petal_lengths.append([])
    
    for i in range(get_world_size()**2):
        plant_this(Entities.Sunflower, Grounds.Soil)
        if water:
            do_water()
        all_petal_lengths[measure()] += [[get_pos_x(), get_pos_y()]]
        move_increment()
    
    return  all_petal_lengths

def harvest_sunflowers(all_petal_lengths):
    #"""! @brief Harvest sunfowers in decreasing order of petal length.
    #@param See output of plant_sunflowers().
    #"""
    cur_petals = len(all_petal_lengths)-1
    while cur_petals > 0:
        while len(all_petal_lengths[cur_petals]) > 0:
            xy = all_petal_lengths[cur_petals].pop(0)
            move_to(xy[0], xy[1])
            if can_harvest():
                harvest()
            else:
                all_petal_lengths[cur_petals].append(xy)
        
        cur_petals += -1

###
### Companions
###

# companions_requested: Dict. Key: Tuple XY coordinates of a plant who wants a companion (a requester). Value: get_companion() of that plant at the location, indicating that plant's requested companion.
# companions_requester: Dict. Key: Tuple of XY coordinates (of a requested). Value: A list of XY coordinates of every plant (requester) who wants a companion in that cell.
# Note: Elements removed once the companion is planted or intended to be planted.

def companion_add(xy_requester, companions_requested, companions_requester):
    #"""! @brief Add a companion pair to companions_requested and companions_requester corresponding to the current location.
    #@param xy_requester optional. Tuple indicaitng current location of the drone.
    #"""
    if xy_requester == None:
        xy_requester = (get_pos_x(), get_pos_y())
    
    companions_requester[xy_requester] = get_companion()
    xy_requested = companions_requester[xy_requester][1]
    if xy_requested not in companions_requested:
        companions_requested[xy_requested] = []
    companions_requested[xy_requested].append(xy_requester)
        

def companion_remove(xy_requester, companions_requested, companions_requester):
    #"""! @brief Remove a companion pair to companions_requested and companions_requester.
    #@param xy_requester XY tuple of plant who wants a companion.
    #"""
    if xy_requester not in companions_requester:
        return
    xy_requested = companions_requester[xy_requester][1]
    if len(companions_requested[xy_requested]) > 1:
        for i in range(len(companions_requested[xy_requested])):
            if companions_requested[xy_requested][i] == xy_requester:
                companions_requested[xy_requested].pop(i)
    else:
        companions_requested.pop(xy_requested)
    
    companions_requester.pop(xy_requester)

def choose_entity(xy, companions_requested, companions_requester):
    #"""! @brief Decide the best plant to place in a location. Chooses companion if possible, otherwise randomly among companionable plants.
    #@param xy Tuple location of where we want to plant.
    #@return chosen_entity: What we want to plant. xy_requester: If this plant is a companion, the xy coordinates of the plant who wanted this companion.
    #@todo If there are multiple competing requesters, choose the most popular request.
    #"""
    
    possiblities = [Entities.Grass, Entities.Carrot, Entities.Tree]

    if xy == None:
        xy = (get_pos_x(), get_pos_y())
    
    chosen_entity = None
    xy_requester_fn = None
    tree_is_adjacent_cache = None
    
    # Choose based on companion
    if xy in companions_requested:
        for xy_requester in companions_requested[xy]:
            chosen_entity = companions_requester[xy_requester][0]
            if chosen_entity == Entities.Tree:
                tree_is_adjacent_cache = tree_is_adjacent()
                if tree_is_adjacent_cache:
                    chosen_entity = None
                    
            if chosen_entity != None:
                xy_requester_fn = xy_requester
                break
    
    # Choose randomly
    if chosen_entity == None:
        chosen_entity = possiblities[(random() * len(possiblities)) // 1]
    
    if chosen_entity == Entities.Tree:
        if tree_is_adjacent_cache == None:
            tree_is_adjacent_cache = tree_is_adjacent()
        if tree_is_adjacent_cache:
            possiblities.pop()
            chosen_entity = possiblities[(random() * len(possiblities)) // 1]
                
    return {'chosen_entity': chosen_entity, 'xy_requester': xy_requester_fn}

def plant_companions_chain(xy, possible_xy):
    #"""! @brief Plant once at a time. Each time we plant, next plant the corresponding companion if possible. Stop once we cannot plant companion
    #@param xy is tuple of current drone coordinates.
    #@param possible_xy Dictionary containing every location eligible for planting. Key: XY Tuple. Values are not used.
    #@todo Change break criteria `match_cnts[0] > 1`. If we can't do a tree with can continue the chain with the current plant. If there is no valid companion then we cannot continue.
    #@return Length two list. First element are how many plants were planted without companions. Second indicates how many plants were planted with companions
    #"""
    
    match_cnts = [0,0]
    
    if xy == None:
        xy = (get_pos_x(), get_pos_y())
    if xy not in possible_xy:
        return match_cnts
    
    def try_harvest():
        if can_harvest():
            harvest()
            return 1
        elif get_entity_type() == None:
            return 1
        else:
            return 0
    
    
    xy_new = xy
    companions_requester = {}
    companions_requested = {}
    while True:
        if not try_harvest():
            break
         
        # Plant
        chosen_entity = choose_entity(xy_new, companions_requested, companions_requester)
        plant_this(chosen_entity['chosen_entity'])
        do_water()
        
        # Increment variables
        # Always build companions from scratch due to multi-drone race conditions
        if chosen_entity['xy_requester'] != None:
            match_cnts[1] += 1
        else:
            match_cnts[0] += 1
        companions_requester = {}
        companions_requested = {}
        companion_add(xy_new, companions_requested, companions_requester)
        xy_new = companions_requester[xy_new][1]

        # Move to new location
        if xy_new not in possible_xy:
            break
        move_to(xy_new[0], xy_new[1])
        
    return match_cnts


def plantharvest_all_companions_grid(coords_list, companions_requested, companions_requester):
    #"""! @brief Go through each coordinate. Plant preferring companion if possible. Compared to plant_all_companions_chain(), this sacrifices companion efficiency for drone speed. Would not work well for multiple drones since globals are not shared.
    #@param coords_list A list of (x,y) tuples of every location we want to visit.
    #@return Length two list. First element are how many plants were planted without companions. Second indicates how many plants were planted with companions
    #"""
    
    match_cnts = [0,0]
    
    def tmp_plant(kwargs):
        if can_harvest():
            harvest()
            companion_remove((kwargs['x'],kwargs['y']), companions_requested, companions_requester)
        chosen_entity = choose_entity((kwargs['x'],kwargs['y']), companions_requested, companions_requester)
        plant_this(chosen_entity['chosen_entity'])
        do_water()
        companion_add((kwargs['x'],kwargs['y']), companions_requested, companions_requester)
        if chosen_entity['xy_requester'] != None:
            return(1)
        else:
            return(0)
        
    match_cnts = loop_coords(coords_list, tmp_plant, 0)
    match_cnts = [len(coords_list)-match_cnts,match_cnts]
        
    return match_cnts


###
### Maze
###

### Assumptions:
### * You do not wrap around the edges of the map in mazes.
### * Bottom left of maze is (0,0)
###

def make_maze(ndim=get_world_size()):
    #"""! @brief Make an ndim*ndim maze if possible"""

    if ndim > get_world_size():
        ndim = get_world_size()
    
    
    qty = ndim * 2**(num_unlocked(Unlocks.Mazes)-1)
    move_to(ndim//2,ndim//2)
    plant_this(Entities.Bush)
    use_item(Items.Weird_Substance, qty)

def solve_maze(maze_dim, check_entity=False, current_xy=None):
    #"""! @brief Solve a maze. Does so by preferring the least traveled route. Ties are broken in direction of treasure.
    #@param check_entity At each step validate the plant the drone is standing on. This slows the drone slightly. Important when multiple drones are solving to start/stop drones appropriately.
    #@return Number of steps needed to solve maze. None if maze was not solved by this drone.
    #"""

    if current_xy == None:
        current_xy = (get_pos_x(), get_pos_y())
    nvisits = {current_xy: 1}
    adjacency_dict = {}
    
    if check_entity:
        # Wait for maze to start
        while True:
            if get_entity_type() == Entities.Hedge:
                break
            elif get_entity_type() == Entities.Treasure:
                break
    
    treasure_xy = measure()
    nsteps = 0
    while current_xy != treasure_xy:
        nsteps += 1
        adjacency_current = get_all_adj(current_xy, treasure_xy, maze_dim, nvisits, adjacency_dict)
        current_xy = move_once(current_xy, adjacency_current, nvisits, adjacency_dict)
        current_xy = current_xy
        
        if check_entity:
            # Quit if a different drone finished the maze
            ientity = get_entity_type()
            if ientity == Entities.Treasure:
                break
            elif ientity != Entities.Hedge:
                # Can occur if a different drone solves the maze
                break
    
    success = False        
    if get_entity_type() == Entities.Treasure:
        harvest()
        success = True
        return nsteps
    
    return None

def get_adj_key(x,y):
    #"""! @brief Builds key for adjacency_dict. Does so by sorting a pair of coordinates to ensure bi-directinal support."""
    if array_ineq(x,y) == -1:
        return (x,y)
    else:
        return (y,x)

def get_all_adj(current_xy, treasure_xy, maze_dim, nvisits, adjacency_dict):
    #"""! @brief From the current location, get information on each cardinal direction.
    #@param current_xy Tuple of current drone location
    #@param treasure_xy Tuple of treasure location
    #@param maze_dim Width/length of maze.
    #@param nvisits Dictionary. Key: XY tuple. Value: Number of times this drone visited that position.
    #@param adjacency_dict Dictonary. Key: Pair of XY coordinates (see get_adj_key). Value: Is travel between these coordinates possible? Bi-directional.
    #@return A list of length 4 corresponding to each cardinal direction. Sorted from smallest nvisits loss to largest. Each element is a dictonary. 
    #
    #nvisits is the most important element of each dictionary. It is principally the number of times the corresponding location was visited, but it is modified in the following ways. 1) If a node should not be visited (e.g. impossible to visit) it's set to LARGE_NUMBER (~infinity). 2) For tiebreaking purposes we add two values. a) The distance from coordinate to treasure prefers coordinates towards the treasuree. b) A random value permits different drones to take different paths. Addends are combined in a way that we effectively sort on tuple (is LARGE_NUMBER, raw nvisits, distance, random).
    #"""

    all_adj = [
        {'direction': North, 'new_xy': tuple(array_add(current_xy, DIRECTION_TO_TUPLE[North]))}
        , {'direction': South, 'new_xy': tuple(array_add(current_xy, DIRECTION_TO_TUPLE[South]))}
        , {'direction': East, 'new_xy': tuple(array_add(current_xy, DIRECTION_TO_TUPLE[East]))}
        , {'direction': West, 'new_xy': tuple(array_add(current_xy, DIRECTION_TO_TUPLE[West]))}
        ]
    for i in range(len(all_adj)):
                
        if dict_get(adjacency_dict, get_adj_key(current_xy,all_adj[i]['new_xy']),-1) == 0:
            all_adj[i]['nvisits'] = LARGE_NUMBER
        elif all_adj[i]['new_xy'][0] < 0:
            all_adj[i]['nvisits'] = LARGE_NUMBER
        elif all_adj[i]['new_xy'][1] < 0:
            all_adj[i]['nvisits'] = LARGE_NUMBER
        elif all_adj[i]['new_xy'][0] >= maze_dim:
            all_adj[i]['nvisits'] = LARGE_NUMBER
        elif all_adj[i]['new_xy'][1] >= maze_dim:
            all_adj[i]['nvisits'] = LARGE_NUMBER
        else:
            all_adj[i]['nvisits'] = dict_get(nvisits, all_adj[i]['new_xy'],0)
            all_adj[i]['nvisits'] += dist_manhattan(all_adj[i]['new_xy'], treasure_xy) / (4*get_world_size())
            all_adj[i]['nvisits'] += random() / (8*get_world_size())
                
    
    def adj_less_than(x,y):
        return sign(x['nvisits']-y['nvisits'])
    list_sort(all_adj, adj_less_than)
    
    return all_adj


def move_once(current_xy, all_adj, nvisits, adjacency_dict):
    #"""! @brief Attempt to move in the most logical cardinal direction. If this fails, repeat in the next most appropriate direction. Updates nvisits, adjacency_dict appropriately.
    #@param all_adj List output from get_all_adj() describing each direction.
    #@return The new location of the drone.
    #@todo Can we identify loops which are dead ends or other complex dead ends (i.e. this path splits but goes nowhere useful)?
    #"""
    
    did_move = False
    while not did_move:
        min_val = all_adj.pop(0)
        min_val['adj_key'] = get_adj_key(current_xy, min_val['new_xy'])
         
        did_move = move(min_val['direction'])
        adjacency_dict[min_val['adj_key']] = did_move
    
    nvisits[min_val['new_xy']] = dict_get(nvisits, min_val['new_xy'], 0) + 1
    
    # Identity dead ends
    if min_val['nvisits'] >= 1:
        if len(all_adj) == 0:
            nvisits[current_xy] = LARGE_NUMBER
        elif all_adj[0]['nvisits'] >= LARGE_NUMBER:
            nvisits[current_xy] = LARGE_NUMBER

    return min_val['new_xy']

###
### Cacti
###  


def plant_cacti(x0, y0, x1, y1):
    #"""! @brief Plant catci from (x0,y0) to (x1,y1) inclusive."""

    def plant(kwargs):
        plant_this(Entities.Cactus)
    loop_rectangle(x0, y0, x1+1, y1+1, plant)

def cacti_sort(x0, y0, x1, y1):
    #"""! @brief When y0==y1, sorts cacti from (x0,y0) to (x1,y0). Identical operation if x0==x1 instead."""
    
    # Make ordered list of coordinates from (x0,y0) to (x1,y1)
    coordinates = []
    if x0==x1:
        directions = (South, North)
        for i in range(y1-y0+1):
            coordinates.append( (x0, y0+i) )
    elif y0==y1:
        directions = (West, East)
        for i in range(x1-x0+1):
            coordinates.append( (x0+i, y0) )
    else:
        return
    
    def compare_fun(x,i):
        if i==1:
            move_to(x[i][0], x[i][1])
        else:
            move(directions[1])
        val0 = measure(directions[0])
        val1 = measure()
        return sign(val0-val1)
        
    def swap_fun(x,i):
        swap(directions[0])
    
    bubble_sort(coordinates, compare_fun, swap_fun)

###
### Dinosaurs
###

def get_apple(xy, tail_length, snake_start):
    #"""! @brief Take a slow and roundabout path to retrieve an apple. This should usually avoid tripping over one's tail.
    #@param tail_length A list containing a single integer. Specified the tail length (number of apples picked up so far). Both an input and output argument, mutates.
    #@param snake_start A list containing a single integer. Starts [0]. Flip to [1] once we use snake_direction(). Both an input and output argument, mutates.
    #@todo 1) Terminates early if on the last loop of edge_cc_direction() it touches an extra apple on its return trip southward. Fix. 2) Improve speed by more direct pathing under smaller tail sizes.
    #@return The coordinates of the next apple. None on failure.
    #"""
    
    world_size_cache = get_world_size()
    
    path_fun = None
    if tail_length[0] < 4*world_size_cache-5-1: # Extra '-1' in case an extra apple is found going south.
        path_fun = edge_cc_direction
    else:
        path_fun = snake_direction
        if snake_start[0] != 1:
            snake_start[0] = 1
            
            # Circle fully CC before starting
            if (xy[1]>0) or ((xy[0] == 0) and (xy[1] == 0)):
                path_to((1,0), edge_cc_direction)
            path_to((0,0), edge_cc_direction)
    
    direction_info_zy = path_fun(xy)
    if direction_info_zy != None:
        # Move along path to XY
        if not path_to(xy, path_fun):
            return None
        tail_length[0] += 1
        return measure()
    else:
        # Assumed: (path_fun==edge_cc_direction) and (direction_info_zy==None)
        # Move West of XY and then cut over
        
        if not path_to((0,xy[1]), path_fun):
            return None
        if not move_n(East, xy[0]):
            return None
    
        new_apple_xy = measure()
        tail_length[0] += 1
        
        # Return to Southern border
        xy0 = [xy[0],xy[1]]
        while xy0[1]>0:
            if (xy0[0] == new_apple_xy[0]) and (xy0[1] == new_apple_xy[1]):
                new_apple_xy = measure()
                tail_length[0] += 1
            if not move(South):
                return None
            xy0[1] += -1
        
        return new_apple_xy
        
        

###
### General Looping
###

def loop_coords(coords_list, fun, out_init=None):
    #"""! @brief For each xy in coords_list, apply fun().
    #@param List of xy tuples.
    #@param fun Function that expects a single dictionary argument: {'x': , 'y': , 'out': current rolling value of out_init}. 
    #@param out_init If not None, each value of fun() will be added to this. May mutate.
    #@return The final value of out_init.
    #"""
    xy0 = None
    for xy1 in coords_list:
        move_to(xy1[0], xy1[1], xy0)
        xy0 = xy1
        fun_out = fun({'x': xy1[0],'y': xy1[1], 'out': out_init})
        if out_init != None:
            out_init += fun_out
     
    return out_init
        

def loop_rectangle(x0, y0, x1, y1, fun, out_init=None):
    #"""! @brief Apply fun to each coordinate in rectanglular range (x0,y0) to (x1-1, y1-1) inclusive.
    #@param host @copydoc loop_coords(fun)
    #"""
    for iy in range(y1-y0):
        move_to(x0, y0+iy)
        for ix in range(x1-x0):
            fun_out = fun({'x': x0+ix,'y': y0+iy, 'out': out_init})
            if out_init != None:
                out_init += fun_out
            move(East)
    
    return out_init


###
### Movement
###
    

def move_increment():
    #"""! @brief Moves drone once. Repeated use moves a drone first East (circumnavigating) and then North (eventually circumnavigating).
    #@return Returns 1 if drone has now returned to (0,0).
    #"""
    if get_pos_x() == get_world_size()-1:
        move(North)
        move(East)
    else:
        move(East)
    
    if (get_pos_x() == 0) and (get_pos_y() == 0):
        return 1
    else:
        return 0  

def move_to(x,y, xy0=None, check=False):
    #"""! @brief Moves a drone to (x,y) following shortest path.
    #@param xy0 Optional xy tuple of the drone's current location.
    #"""
    dirs_x = {-1: West, 1: East, 0: East}
    dirs_y = {-1: South, 1: North, 0: North}
    
    if xy0 == None:
        xy0 = (get_pos_x(), get_pos_y())
        
    
    distance = shortest_distance(xy0[0], x)
    dir = dirs_x[sign(distance)]
    for i in range(abs(distance)):
        move(dir)
    
    distance = shortest_distance(xy0[1], y)
    dir = dirs_y[sign(distance)]
    for i in range(abs(distance)):
        move(dir)
    
    if check:
        if get_pos_x() != x:
            print("Error X.")
        if get_pos_y() != y:
            print("Error Y.")

def shortest_distance(x_from, x_to):
    #"""! @brief Along the x-axis, find the shortest distance from x_from to x_to. (symmetric for Y)
    #@return +3 Incidates that x_to is 3 spaces East. -2 indicates x_to is two spaces West.
    #"""
    if x_from == x_to:
        return 0
    elif x_from > x_to:
        return -shortest_distance(x_to, x_from)
    
    dist_forward = x_to - x_from
    dist_backward = x_from + get_world_size() - x_to
    
    if dist_forward <= dist_backward:
        return dist_forward
    else:
        return -dist_backward

def edge_cc_direction(xy):
    #"""! @brief If tuple xy is on the edge of the map, return the counter-clockwise direction."""
    
    if (xy[0] == 0) and (xy[1] == 0):
        return East
    elif xy[0] == 0:
        return South
    elif xy[1] == get_world_size()-1:
        return West
    elif xy[0] == get_world_size()-1:
        return North
    elif xy[1] == 0:
        return East
    else:
        return None

def snake_direction(xy):
    #"""! @brief Direction to loop entire map without crossing self or circumnavigating. Approach: Southern border goes east. Above snakes north/south. Assumes dimensions are even."""
    
    world_size_cache = get_world_size()
    
    if (xy[0]==world_size_cache-1) and (xy[1]==0):
        return North
    elif (xy[0]==world_size_cache-1) and (xy[1]==1):
        return North
    elif (xy[0]==0) and (xy[1]==1):
        return South
    elif (xy[1] == 0):
        return East
    elif (world_size_cache-xy[0]) % 2 == 1:
        if xy[1] == world_size_cache-1:
            return West
        else:
            return North
    else: # world_size_cache-xy[0] % 2 == 0:
        if xy[1] == 1:
            return West
        else:
            return South

def move_n(direction, n):
    #"""! @brief Move this drone n places is the stated direction"""
    success = 1
    for i in range(n):
        if not move(direction):
            success=0
    return success

def path_to(xy, path_fun, xy0=None):
    #"""! @brief Follow path_fun until we reach xy.
    #@param Takes an xy tuple and gives a direction to move.
    #@return 1 if successful. 0 otherwise.
    #"""
    
    if xy0 == None:
        xy0 = (get_pos_x(), get_pos_y())
    
    if xy0 == xy:
        return 1
    
    while xy0 != xy:
        direction = path_fun(xy0)
        if direction == None:
            return 0
        elif not move(direction):
            return 0
        xy0 = array_add(xy0, DIRECTION_TO_TUPLE[direction])
    
    return 1

###
### Arrays
###


def which_min(x):
    #"""! @brief Find the index of the minimum value of X."""
    min_ind = 0
    min_val = x[min_ind]
    for ind in range(x):
        if x[ind] < min_val:
            min_ind = ind
            min_val = x[min_ind]
    
    return {'index': min_ind, 'value': min_val}

def list_move(x, ind0, ind1):
    #"""! @brief From an element in x from ind0 to ind1."""
    val = x.pop(ind0)
    if ind0 < ind1:
        ind1 += -1
    x.insert(ind1, val)

def list_sort(x, compare_fun=less_than):
    #"""! @brief Bubble sort x inplace.
    #@param compare_fun Inequality function(y,z) -> {-1,0,1}.  Something of form sign(y-z) gives ascending order.
    #"""
    
    def compare_fun2(x,i):
        return compare_fun(x[i-1], x[i])
    def swap_fun(x,i):
        list_move(x, i, i-1)
    
    bubble_sort(x, compare_fun2, swap_fun)

def bubble_sort(x, compare_fun, swap_fun):
    #"""! @brief Bubble sort x inplace.
    #@param compare_fun function(x,i). Returns 1 if x[i-1]>x[i] for ascending.
    #@param swap_fun function(x,i). Swaps elements x[i-1] and x[i] inplace.
    #"""
    
    while True:
        any_changes = False
        for i in range(len(x)):
            if i>0:
              if compare_fun(x,i) == 1:
                  swap_fun(x, i)
                  any_changes = True
         
        if not any_changes:
            break 
                
        any_changes = True
            
    return None

def array_ineq(x,y):
    #"""! @brief Inequality between two vectors."""
    ineq = 0
    for i in range(len(x)):
        if x[i] < y[i]:
            ineq -1
            break
        elif x[i] > y[i]:
            ineq = 1
            break
    
    return ineq

def array_add(x,y):
    #"""! @brief Add two vectors"""
    def add(x,y):
        return [x+y]
    return arrays_apply(x, y, add, [])
    
def dist_manhattan(x,y):
    #"""! @brief Manhattan (L1) distance between two vectors"""
    def dist(x,y):
        return abs(x-y)
    return arrays_apply(x, y, dist, 0)

def arrays_apply(x, y, fun, init):
    #"""! @brief Return $init + sum_i fun(x[i], y[i])$"""
    for i in range(len(x)):
        init += fun(x[i], y[i])
    return(init)
    

###
### Dictionary
###

def dict_get(x, key, default):
    #"""! @brief Same as dictionary.get() method in Python. Safely extracts a value from a dictionary."""
    if key in x:
        return x[key]
    else:
        return default

def dict_first_key(x):
    #"""! @brief Get a single key element from a dictionary."""
    key = None
    for key in x:
        break
    return key

def dict_copy(x):
    #"""! @brief Same as dictionary.copy() method in Python. Makes a shallow copy."""
    y = {}
    for key in x:
        y[key] = x[key]
    return y
    
###
### Proper Utils
###

def range_list(n):
    #"""! @brief Make a list from 0 to n-1 inclusive"""
    
    x = []
    for i in range(n):
        x.append(i)
    return x

def tuple(x):
    #"""! @brief Cast x to tuple. Apparently no better way in this game..."""
    
    if len(x) == 0:
        return ()
    elif len(x) == 1:
        return (x[0])
    elif len(x) == 2:
        return (x[0], x[1])
    elif len(x) == 3:
        return (x[0], x[1], x[2])
    else:
        return x

def less_than(x,y):
    return sign(x-y)
    
def sign(x):
    #"""! @brief Is x positive or negative?"""
    if x==0:
        return 0
    elif x>0:
        return 1
    elif x<0:
        return -1
    else:
        return None