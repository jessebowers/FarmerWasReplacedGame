import utils


def job_sunflowers(word_size=6):
    #"""! @brief Plant and harvest entire field with sunflowers"""
    set_world_size(word_size)
    clear()
    while True:
        all_petal_lengths=utils.plant_sunflowers()
        utils.harvest_sunflowers(all_petal_lengths)

def mixed_crop_v2():
    #"""! @brief Plant and harvest a field of [Grass, Carrot, Tree, Pumpkin]. Operates with a single drone which after planting, always tries to sow that plant's companion next."""
    
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
    #"""! @brief Plant and harvest a field of [Grass, Carrot, Tree, Pumpkin]. Operates with a single drone which loops through a grid preferring compansions where possible."""
    
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
   
def mixed_crop_v4():
    #"""! @brief Plant and harvest a field of [Grass, Carrot, Tree, Pumpkin]. Operates with exactly two drones which work in a grid pattern."""
    
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
    #"""! @brief Generate and solve a maze. Works with as many drones as possible."""
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
                       , ((1/2*maze_dim)//1, (1/4*maze_dim)//1), ((1/4*maze_dim)//1, (1/2*maze_dim)//1), ((1/2*maze_dim)//1, (3/4*maze_dim)//1), ((3/4*maze_dim)//1, (1/2*maze_dim)//1)
                       , ((1/5*maze_dim)//1, (1/5*maze_dim)//1), ((4/5*maze_dim)//1, (1/5*maze_dim)//1), ((1/5*maze_dim)//1, (4/5*maze_dim)//1), ((4/5*maze_dim)//1, (4/5*maze_dim)//1)
                       , ((1/2*maze_dim)//1, 0), (0, (1/2*maze_dim)//1), ((1/2*maze_dim)//1, maze_dim-1), (maze_dim-1, (1/2*maze_dim)//1)
                       ]
            for i in range(min(ndrones-1, len(drone_pos))):
                spawn_drone(drone_fun_follower, drone_pos[i])
            drone_fun_master()

