# Variables are triplets (a,v,t) agent A at vertex V at time T 
# Constraints - agent must be at its starting point at t 0
# Agent is at its goal location at time T
# Valid moves (a,v,t) -> (a,u,t+1) u and v must be neighbors
# Two agents cannot be at same vertex at same time 
# swap - two gents cannot swap places -> not((a,v,t) and (a,u,t+1) and (b,u,t) and (b,u,t+1))


from pysat.solvers import Glucose3
import itertools
import sys


#input file
#5 - grid_size
#
# start
# (x,y) starts for agents
#
#end
# (x,y)
def parse_input(input_str):
    lines = [l.strip() for l in input_str.strip().split('\n') if l.strip()]
    
    # 1. Grid Size
    grid_n = int(lines[0].split()[0])
    
    starts = []
    goals = []
    
    current_mode = None # 'start' or 'end'
    
    for line in lines[1:]:
        if line == 'start':
            current_mode = 'start'
            continue
        elif line == 'end':
            current_mode = 'end'
            continue
            
        # Parse coordinate line "(x,y)"
        clean_line = line.replace('(', '').replace(')', '')
        if ',' in clean_line:
            parts = clean_line.split(',')
            coord = (int(parts[0]), int(parts[1]))
            
            if current_mode == 'start':
                starts.append(coord)
            elif current_mode == 'end':
                goals.append(coord)
                
    # Pair them up: Agent 0 gets starts[0]->goals[0], etc.
    agents = {}
    for i in range(len(starts)):
        agents[i] = (starts[i], goals[i])
        
    return (grid_n, grid_n), agents



class SAT_MAPF:
    def __init__(self, grid_size, agents):
        self.grid_w, self.grid_h = grid_size
        self.agents = agents
        self.num_agents = len(agents)
        # Generate all valid walkable nodes
        self.nodes = [(x, y) for x in range(self.grid_w) for y in range(self.grid_h)]
        
    def get_neighbors(self, u):
        x, y = u
        moves = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)] # Wait, Up, Down, Right, Left
        neighbors = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_w and 0 <= ny < self.grid_h and (nx, ny):
                neighbors.append((nx, ny))
        return neighbors

    def solve(self, max_horizon=20):
        for T in range(1, max_horizon + 1):
            # print(f"Checking horizon T={T}...") # Uncomment for debug
            model = self.build_and_solve_sat(T)
            if model:
                return self.extract_solution(model, T)
        return None

    def build_and_solve_sat(self, T):
        """T is the time to find solution"""
        self.var_map = {}
        self.counter = 1
        solver = Glucose3()
        
        # Helper to get variable ID - created if state does not exist via counter, else returned from var_map
        def get_var(agent_idx, node, t):
            key = (agent_idx, node, t)
            if key not in self.var_map:
                self.var_map[key] = self.counter
                self.counter += 1
            return self.var_map[key]


        # --- CONSTRAINTS ---
        for i in range(self.num_agents):
            start, goal = self.agents[i]
            
            # 1. Initialize and Goal
            solver.add_clause([get_var(i, start, 0)])
            solver.add_clause([get_var(i, goal, T)])
            
            # 2. Transitions
            for t in range(T):
                for u in self.nodes:
                    # If at u at time t -> must be at neighbor at t+1
                    # either agent wasnt at u at time t, or it moved to valid neighbor in t+1 equivalent to agent in u implies it is in neighbor in next time step
                    u_var = get_var(i, u, t)
                    clause = [-u_var] 
                    for v in self.get_neighbors(u):
                        clause.append(get_var(i, v, t + 1))
                    solver.add_clause(clause)
            
            # robots arent cloned
            for t in range(T + 1):
                for u, v in itertools.combinations(self.nodes, 2):
                     solver.add_clause([-get_var(i, u, t), -get_var(i, v, t)])

        # 4. Vertex Conflict (No two agents in same cell)
        for t in range(T + 1):
            for u in self.nodes:
                for i, j in itertools.combinations(range(self.num_agents), 2):
                    solver.add_clause([-get_var(i, u, t), -get_var(j, u, t)])
        
        # 5. Edge Conflict (No swapping)
        for t in range(T):
            for u in self.nodes:
                for v in self.get_neighbors(u):
                    if u == v: continue
                    for i, j in itertools.combinations(range(self.num_agents), 2):
                        # u->v AND j: v->u
                        solver.add_clause([
                            -get_var(i, u, t), -get_var(i, v, t+1),
                            -get_var(j, v, t), -get_var(j, u, t+1)
                        ])
                        
        if solver.solve():
            return solver.get_model()
        return None

    def extract_solution(self, model, T):
        model_set = set(model)
        paths = {i: [] for i in range(self.num_agents)}
        
        for (agent_idx, node, t), var_id in self.var_map.items():
            if var_id in model_set:
                paths[agent_idx].append((t, node))
        
        for i in paths:
            paths[i].sort(key=lambda x: x[0])
            paths[i] = [x[1] for x in paths[i]]
        return paths

# --- PARSER ---
def parse_and_run(input_text):
    lines = [l.strip() for l in input_text.strip().split('\n') if l.strip()]
    
    # 1. Parse Grid Size
    try:
        grid_n = int(lines[0].split()[0])
    except ValueError:
        print("Error: First line must contain the grid size integer.")
        return

    starts = []
    goals = []
    mode = None

    # 2. Parse Coordinates
    for line in lines[1:]:
        if line.lower() == 'start':
            mode = 'start'
            continue
        elif line.lower() == 'end':
            mode = 'end'
            continue
            
        # Parse "(x,y)"
        clean = line.replace('(', '').replace(')', '')
        if ',' in clean:
            parts = clean.split(',')
            coord = (int(parts[0]), int(parts[1]))
            if mode == 'start':
                starts.append(coord)
            elif mode == 'end':
                goals.append(coord)

    # 3. Setup Agents
    agents = {}
    if len(starts) != len(goals):
        print("Error: Mismatch between number of start and end positions.")
        return

    for i in range(len(starts)):
        agents[i] = (starts[i], goals[i])
        print(f"Agent {i}: {starts[i]} -> {goals[i]}")

    # 4. Solve
    solver = SAT_MAPF((grid_n, grid_n),  agents)
    print(f"\nSolving for {grid_n}x{grid_n} grid...")
    paths = solver.solve(max_horizon=15)
    
    if paths:
        print("\nSolution Found:")
        # Print makespan (length of path - 1)
        print(f"Time Horizon: {len(paths[0]) - 1}")
        
        # Print table
        headers = [f"Agent {i}" for i in agents]
        print(f"{'Time':<6} | " + " | ".join(f"{h:<10}" for h in headers))
        print("-" * (8 + 13 * len(agents)))
        
        for t in range(len(paths[0])):
            row = [str(paths[i][t]) for i in agents]
            print(f"{t:<6} | " + " | ".join(f"{c:<10}" for c in row))
    else:
        print("No solution found within horizon limit.")

# --- MAIN ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mapf_sat.py <filename>")
    else:
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                parse_and_run(f.read())
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
    