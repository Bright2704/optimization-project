import numpy as np



n_variables = 2
n_agents = 40
maxiter = 50
std_dev = 0.1

min_bound = np.array([ 0, 0 ])
max_bound = np.array([ 1, 1 ])

def my_function(x):
    return x[0]**2 - x[0] + x[1]**2 - 0.5*x[1]

fitness = my_function

agents = np.random.uniform( low=min_bound, high=max_bound, size=(n_agents, n_variables) )

for k in range( maxiter ):
    for i in range( n_agents ):
        # step 1: generate a random change in the location
        loc_change = np.random.normal(loc=0.0, scale=std_dev, size= (n_variables))
        # step 2: update the position
        old_pos = agents[i]
        new_pos = old_pos + loc_change
        # step 3: clip the position to the bounds
        new_pos = np.clip( new_pos, min_bound , max_bound )

        if (fitness(new_pos) <= fitness( old_pos ) ):
            agents[i] = new_pos

# Termination
values = np.zeros( n_agents )
for i in range( n_agents ):
    values[i] = fitness( agents[i] )
best_idx = np.argmin( values )
best_pos = agents[best_idx]
best_value = values[best_idx]

print(maxiter , 'iterations')
print('min value at', best_pos , '; min value equals:', f"{best_value:,.8f}" )