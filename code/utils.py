###
### Globals
###

LARGE_NUMBER = 999999
NUM_SQUARES = get_world_size() * get_world_size()

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
    # Plant entity in appropraite ground
    
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
    if get_entity_type(North) == Entities.Tree:
       return True
    elif get_entity_type(South) == Entities.Tree:
        return True
    elif get_entity_type(East) == Entities.Tree:
        return True
    elif get_entity_type(West) == Entities.Tree:
        return True



###
### Pumpkins
###


def plant_pumpkin_patch_once(x0, y0, width, past_problem_locations=None, harvest_if_done=True, do_fertalize=False):
    
    def tmp_plant(kwargs):
        do_water()
        if get_entity_type() != Entities.Pumpkin:
            plant_this(Entities.Pumpkin, Grounds.Soil)
            use_item(Items.Fertilizer)
            return [[kwargs['x'],kwargs['y']]]
        elif not can_harvest():
            return [[kwargs['x'],kwargs['y']]]
        else:
            return []
    
    if past_problem_locations == None:
        problem_locations = loop_pumpkin_patch(x0, y0, width, tmp_plant, [])
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

def loop_pumpkin_patch(x0, y0, width, fun, out_init=None):
    return loop_rectangle(x0, y0, x0+width, y0+width, fun, out_init)

###
### Sunflower
###

def plant_sunflowers(water=False):
    all_petal_lengths = []
    for i in range(16): # Max petals is 15
        all_petal_lengths.append([])
    
    for i in range(NUM_SQUARES):
        plant_this(Entities.Sunflower, Grounds.Soil)
        if water:
            do_water()
        all_petal_lengths[measure()] += [[get_pos_x(), get_pos_y()]]
        move_increment()
     
    return  all_petal_lengths

def harvest_sunflowers(all_petal_lengths):
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

# companions_requested: Dict. Takes the tuple XY coordinates of a plant. Gives get_companion() of that plant's companion
# companions_requester: Dict. Takes a tuple of XY coordinates. Gives a list of XY coordinates whose companion is in that cell.
# Note: Elements removed once the companion is planted or intended to be planted.

def companion_add(xy_requester, companions_requested, companions_requester):
    if xy_requester == None:
        xy_requester = (get_pos_x(), get_pos_y())
    
    companions_requester[xy_requester] = get_companion()
    xy_requested = companions_requester[xy_requester][1]
    if xy_requested not in companions_requested:
        companions_requested[xy_requested] = []
    companions_requested[xy_requested].append(xy_requester)
        

def companion_remove(xy_requester, companions_requested, companions_requester):
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
        possiblities = [Entities.Grass, Entities.Carrot, Entities.Tree]
        chosen_entity = possiblities[(random() * len(possiblities)) // 1]
    
    if chosen_entity == Entities.Tree:
        if tree_is_adjacent_cache == None:
            tree_is_adjacent_cache = tree_is_adjacent()
        if tree_is_adjacent_cache:
            possiblities.pop()
            hosen_entity = possiblities[(random() * len(possiblities)) // 1]
                
    return {'chosen_entity': chosen_entity, 'xy_requester': xy_requester_fn}

def plant_all_companions_chain(is_not_planted, companions_requested, companions_requester):
    # Each time we plant, next plant the corresponding companion if possible
    match_cnts = [0,0]
    
    xy_requester_last = None
    while len(is_not_planted) > 0:
        xy = None
        if xy_requester_last != None:
            if companions_requester[xy_requester_last][1] in is_not_planted:
                xy = companions_requester[xy_requester_last][1]
        if xy == None:
            if xy_requester_last == None:
                possible_xy = [dict_first_key(is_not_planted)]
            else:
                possible_xy = [
                        ( (xy_requester_last[0]+1) % get_world_size(), (xy_requester_last[1]) )
                        , ( (xy_requester_last[0]), (xy_requester_last[1]+1) % get_world_size() )
                        , ( (xy_requester_last[0]-1) % get_world_size(), (xy_requester_last[1]) )
                        , ( (xy_requester_last[0]), (xy_requester_last[1]-1) % get_world_size() )
                        , dict_first_key(is_not_planted)
                    ]
            
            for ixy in possible_xy:
                if ixy in is_not_planted:
                    xy = ixy
        
        move_to(xy[0], xy[1])
        chosen_entity = choose_entity(xy, companions_requested, companions_requester)
        if chosen_entity['xy_requester'] != None:
            match_cnts[1] += 1
        else:
            match_cnts[0] += 1
                
        plant_this(chosen_entity['chosen_entity'])
        do_water()
        xy_requester_last = xy
        companion_add(xy, companions_requested, companions_requester)
        is_not_planted.pop(xy)
        
    return match_cnts

def plantharvest_all_companions_grid(coords_list, companions_requested, companions_requester):
    # Go through each coordinate preferring companion if possible. Faster movement, worse companion matching vs chain
    # Harvests if possible too
    
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
### * You do not wrap around the edges of the map here.
### * Bottom left of maze is (0,0)
###

def make_maze(ndim=get_world_size()):
    if ndim > get_world_size():
        ndim = get_world_size()
    
    
    qty = ndim * 2**(num_unlocked(Unlocks.Mazes)-1)
    move_to(ndim//2,ndim//2)
    plant_this(Entities.Bush)
    use_item(Items.Weird_Substance, qty)

def solve_maze(maze_dim, check_entity=False, current_xy=None):
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
    if array_ineq(x,y) == -1:
        return (x,y)
    else:
        return (y,x)

def get_all_adj(current_xy, treasure_xy, maze_dim, nvisits, adjacency_dict):
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
    sort(all_adj, adj_less_than)
    
    return all_adj


def move_once(current_xy, all_adj, nvisits, adjacency_dict):
    
    did_move = False
    while not did_move:
        min_val = all_adj.pop(0)
        min_val['adj_key'] = get_adj_key(current_xy, min_val['new_xy'])
         
        did_move = move(min_val['direction'])
        adjacency_dict[min_val['adj_key']] = did_move
    
    nvisits[min_val['new_xy']] = dict_get(nvisits, min_val['new_xy'], 0) + 1
    if min_val['nvisits'] >= 1:
        # Dead End
        nvisits[current_xy] = LARGE_NUMBER
        

    return min_val['new_xy']
    

###
### General Looping
###

def loop_coords(coords_list, fun, out_init=None):
    xy0 = None
    for xy1 in coords_list:
        move_to(xy1[0], xy1[1], xy0)
        xy0 = xy1
        fun_out = fun({'x': xy1[0],'y': xy1[1], 'out': out_init})
        if out_init != None:
            out_init += fun_out
     
    return out_init
        

def loop_rectangle(x0, y0, x1, y1, fun, out_init=None):
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
    # Move drone once.
    # Returns 1 if looped map
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

###
### Arrays
###


def which_min(x):
    min_ind = 0
    min_val = x[min_ind]
    for ind in range(x):
        if x[ind] < min_val:
            min_ind = ind
            min_val = x[min_ind]
    
    return {'index': min_ind, 'value': min_val}

def list_move(x, ind0, ind1):
    val = x.pop(ind0)
    if ind0 < ind1:
        ind1 += -1
    x.insert(ind1, val)

def sort(x, compare_fun=less_than):
    # Bubble sort of values
    
    while True:
        any_changes = False
        for i in range(len(x)):
            if i>0:
              if compare_fun(x[i-1], x[i]) == 1:
                  list_move(x, i, i-1)
                  any_changes = True
         
        if not any_changes:
            break 
                
        any_changes = True
            
    return None

def array_ineq(x,y):
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
    def add(x,y):
        return [x+y]
    return arrays_apply(x, y, add, [])
    
def dist_manhattan(x,y):
    def dist(x,y):
        return abs(x-y)
    return arrays_apply(x, y, dist, 0)

def arrays_apply(x, y, fun, init):
    for i in range(len(x)):
        init += fun(x[i], y[i])
    return(init)
    

###
### Dictionary
###

def dict_get(x, key, default):
    if key in x:
        return x[key]
    else:
        return default

def dict_first_key(x):
    key = None
    for key in x:
        break
    return key

def dict_copy(x):
    # Shallow copy
    y = {}
    for key in x:
        y[key] = x[key]
    return y
    

###
### Proper Utils
###

def tuple(x):
    # No better way to cast...
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
    if x==0:
        return 0
    elif x>0:
        return 1
    elif x<0:
        return -1
    else:
        return None