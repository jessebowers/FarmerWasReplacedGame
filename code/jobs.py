import utils


def job_sunflowers(nitr=100, word_size=7):
    #"""! @brief Plant and harvest entire field with sunflowers"""
    set_world_size(word_size)
    clear()
    for i in range(nitr):
        all_petal_lengths=utils.plant_sunflowers()
        utils.harvest_sunflowers(all_petal_lengths)

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

def do_maze_v2(nitr=1, maze_dim=None, ndrones=None, max_steps=utils.LARGE_NUMBER):
    #"""! @brief Generate and solve a maze. Works with as many drones as possible."""
    clear()
    if maze_dim == None:
         maze_dim = get_world_size()
    
    if ndrones == None:
        ndrones = max_drones()
    
    drone_pos = utils.dispersed_locations(ndrones, maze_dim)
    
    def drone_fun_master():
        change_hat(Hats.Wizard_Hat)
        utils.move_to(0,0)
        utils.make_maze(maze_dim)   
        utils.move_to(drone_pos[0][0], drone_pos[0][1])
        nsteps = utils.solve_maze(maze_dim, 2, max_steps)
        if nsteps != None:
            quick_print(nsteps)        
    
    def drone_fun_follower(xy):
        utils.move_to(xy[0],xy[1])
        nsteps = utils.solve_maze(maze_dim, 1, max_steps)
        if nsteps != None:
            quick_print(nsteps)   
    
    for itr in range(nitr):
        clear()
        if ndrones == 1:
            drone_fun_master()
        else:
            for i in range(len(drone_pos)-1):
                spawn_drone(drone_fun_follower, drone_pos[i+1])
            drone_fun_master()

def job_catcti():
    #"""! @brief Plant catci across whole map and sort."""
    clear()
    
    def plant_east(y0):
        utils.plant_cacti(0, y0, get_world_size()-1, y0)
    
    def sort_east(y0):
        utils.cacti_sort(0, y0, get_world_size()-1, y0)
    
    def sort_north(x0):
        utils.cacti_sort(x0, 0, x0, get_world_size()-1)
    
    for ifun in [plant_east, sort_east, sort_north]:
    
        all_drones = []
        vals = utils.range_list(get_world_size())
        while len(vals)>1:
            idrone=spawn_drone(ifun, vals[0])
            if idrone != None:
                all_drones.append(idrone)
                vals.pop(0)
        
        # Run original 'dispatcher' drone on final value
        ifun(vals[0])
        
        utils.wait_for_drone_completion(all_drones) # Redundant safeguard
    
    utils.move_to(get_world_size()//2,get_world_size()//2)
    harvest()

def job_dinosaurs(nitr=1):
    #"""! @brief Collect apples for our dinosaurs in a roundabout fashion. Takes one full loop of area per apple."""
    for i in range(nitr):
        clear()
        tail_length = [1]
        snake_start = [0]
        change_hat(Hats.Dinosaur_Hat)
        new_apple_xy = measure()
        while True:
            new_apple_xy = utils.get_apple(new_apple_xy, tail_length, snake_start)
            if new_apple_xy == None:
                break

        move(East) # In case last position is apple, try to capture it
        change_hat(Hats.Brown_Hat) # Cash in

def mixed_crop_v5(do_fertalize=False):
    #"""! @brief Plant and harvest a field of [Grass, Carrot, Tree, Pumpkin]. Each time we plant, we try to next sow that plant's companion."""
    
    # coords_list_master = []
    coords_dict_master = {}
    for x in range(get_world_size()):
        for y in range(get_world_size()):
            if (x<6) and (y<6):
                pass # Pumpkin patch here
            else:
                # coords_list_master.append((x,y))
                coords_dict_master[(x,y)] = 1

    def pumpkin_fun():
        pumpkin_problems = None
        while True:
            pumpkin_problems = utils.plant_pumpkin_patch_once(0, 0, 6, pumpkin_problems, True, do_fertalize)
    def mixed_fun(possible_xy):
        
        utils.move_to((random()*get_world_size())//1, (random()*get_world_size())//1)
        
        while True:
            match_cnts = utils.plant_companions_chain(None, possible_xy)
            utils.move_increment()
          
            # Sometimes drones hit an error due to race conditions when two drones plant the same place. Try making a new drone just in case.
            if num_drones() < max_drones():
                spawn_drone(mixed_fun, possible_xy)
    
    
    clear()
    idrone = 'DUMMY'
    while idrone != None:
        idrone=spawn_drone(mixed_fun, coords_dict_master)
    
    pumpkin_fun()

def maze_sun():
    power_last = num_items(Items.Power)
    weird_last = num_items(Items.Weird_Substance)

    while True:
        set_world_size(32)
        do_maze_v2(50)
        
        while (num_items(Items.Power) < power_last):
            job_sunflowers(1)
        power_last = num_items(Items.Power)
        
        pumpkin_problems = None
        while (num_items(Items.Weird_Substance) < weird_last):
            pumpkin_problems = utils.plant_pumpkin_patch_once(0, 0, 6, pumpkin_problems, True, True)
        weird_last = num_items(Items.Weird_Substance)
