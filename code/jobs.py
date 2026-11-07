import utils


def mixed_crop_v1():
    clear()
    
    for itr in range(utils.NUM_SQUARES):
        if itr < 3*get_world_size():
            entity_type = Entities.Pumpkin
        elif itr % utils.NUM_SQUARES <= 0.8*utils.NUM_SQUARES:
            if utils.tree_is_adjacent():
                entity_type = Entities.Grass
            else:
                entity_type = Entities.Tree
        else:
            entity_type = Entities.Carrot
        
        utils.plant_this(entity_type)
        if entity_type != Entities.Grass:
            utils.do_water()
        utils.move_increment()
    
    while True:
        utils.harvest_safe()
        utils.move_increment()

def job_sunflowers():
    clear()
    while True:
        all_petal_lengths=utils.plant_sunflowers()
        utils.harvest_sunflowers(all_petal_lengths)

def plant_harvest_pumpkin_patch(x0, y0, width):
    
    problem_locations = None
    while True:
        problem_locations = plant_pumpkin_patch_once(x0, y0, width, problem_locations)
        if len(problem_locations) == 0:
            break
    
    move_to(x0, y0)
    harvest()

def mixed_crop_v2():
    # Set Up Variables
    coords_list_master = []
    coords_dict_master = {}
    for x in range(get_world_size()):
        for y in range(get_world_size()):
            if (x<6) and (y<6):
                pass # Pumpkin patch here
            else:
                coords_list_master.append((x,y))
                coords_dict_master[(x,y)] = 0
    
    def tmp_harvest(kwargs):
            if can_harvest():
                harvest()
                return []
            else:
                return [(kwargs['x'], kwargs['y'])]
    
    pumpkin_problems = None
    
    clear()
    while True:
    
        pumpkin_problems = utils.plant_pumpkin_patch_once(0, 0, 6, pumpkin_problems)
        
        companions_requester = {}
        companions_requested = {}
        match_cnts = utils.plant_all_companions_chain(utils.dict_copy(coords_dict_master), companions_requested, companions_requester)
        quick_print(match_cnts)
        
        pumpkin_problems = utils.plant_pumpkin_patch_once(0, 0, 6, pumpkin_problems)
        missing_harvest = coords_list_master
        while len(missing_harvest) > 0:
            missing_harvest = utils.loop_coords(missing_harvest, tmp_harvest, [])


def mixed_crop_v3():
    # Set Up Variables
    coords_list_master = []
    coords_dict_master = {}
    for x in range(get_world_size()):
        for y in range(get_world_size()):
            if (x<6) and (y<6):
                pass # Pumpkin patch here
            else:
                coords_list_master.append((x,y))
                coords_dict_master[(x,y)] = 0
    
    pumpkin_problems = None
    
    clear()
    while True:
    
        pumpkin_problems = utils.plant_pumpkin_patch_once(0, 0, 6, pumpkin_problems)
        
        companions_requester = {}
        companions_requested = {}
        match_cnts = utils.plantharvest_all_companions_grid(coords_list_master, companions_requested, companions_requester)
        quick_print(match_cnts)
        
def get_weird_substance():
    clear()
    do_fertalize = True
    while True:
        utils.harvest_safe()
        if do_fertalize:
            fertalize_this()
        if utils.move_increment()==1:
            do_fertalize = not do_fertalize
   
def do_maze_v1(nitr=1, maze_dim=None):
    if maze_dim == None:
         maze_dim = get_world_size()
    for itr in range(nitr):
        utils.make_maze(maze_dim)    
        nsteps = utils.solve_maze(maze_dim, (get_pos_x(), get_pos_y()))
        quick_print(nsteps)
  
        
def mixed_crop_v4():
    
    def pumpkin_fun():
        pumpkin_problems = None
        while True:
            pumpkin_problems = utils.plant_pumpkin_patch_once(0, 0, 6, pumpkin_problems)
    def mixed_fun():
        # Set Up Variables
        coords_list_master = []
        coords_dict_master = {}
        for x in range(get_world_size()):
            for y in range(get_world_size()):
                if (x<6) and (y<6):
                    pass # Pumpkin patch here
                else:
                    coords_list_master.append((x,y))
                    coords_dict_master[(x,y)] = 0
        
        while True:
           companions_requester = {}
           companions_requested = {}
           match_cnts = utils.plantharvest_all_companions_grid(coords_list_master, companions_requested, companions_requester)
           quick_print(match_cnts)
        
    clear()
    spawn_drone(pumpkin_fun)
    mixed_fun()

def do_maze_v2(nitr=1, maze_dim=None, ndrones=None):
    if maze_dim == None:
         maze_dim = get_world_size()
    
    if ndrones == None:
        ndrones = max_drones()
    
    def drone_fun_master():
        change_hat(Hats.Wizard_Hat)
        utils.move_to(0,0)
        utils.make_maze(maze_dim)    
        nsteps = utils.solve_maze(maze_dim, True)
        if nsteps != None:
            quick_print(nsteps)        
    
    def drone_fun_follower(xy):
        utils.move_to(xy[0],xy[1])
        nsteps = utils.solve_maze(maze_dim, True)
        if nsteps != None:
            quick_print(nsteps)   
    
    for itr in range(nitr):
        clear()
        if ndrones == 1:
            drone_fun_master()
        else:
            drone_pos = [(0,0), (maze_dim-1, maze_dim-1), (0, maze_dim-1), (maze_dim-1, 0)
                       , (maze_dim//2, maze_dim//6), (maze_dim//2, (5/6*maze_dim)//1), (maze_dim//6, maze_dim//2), ((5/6*maze_dim)//1, maze_dim//2)]
            for i in range(min(ndrones-1, len(drone_pos))):
                spawn_drone(drone_fun_follower, drone_pos[i])
            drone_fun_master()

