#from __future__ import print_function

import pysmac


import sklearn.ensemble
import sklearn.datasets
import sklearn.cross_validation



# First, let us generate some random classification problem. Note that, due to the
# way pySMAC implements parallelism, the data is either a global variable, or
# the function loads it itself. Please refere to the python manual about the 
# multiprocessing module for limitations. In the future, we might include additional
# parameters to the function, but for now that is not possible.
X,Y = sklearn.datasets.make_classification(1000, 20, random_state=23)		# seed yields a mediocre initial accuracy on my machine, 
X_train, X_test, Y_train, Y_test = sklearn.cross_validation.train_test_split(X,Y, test_size=0.33)




# The function to be minimezed for this example is the mean accuracy of a random
# forest on the test data set. Note: because SMAC minimizes the objective, we return
# the negative accuracy in order to maximize it.
def random_forest(n_estimators,criterion, max_features, max_depth):
	
	predictor = sklearn.ensemble.RandomForestClassifier(n_estimators, criterion, max_features, max_depth)
	predictor.fit(X_train, Y_train)
	
	return -predictor.score(X_test, Y_test)


parameter_definition=dict(\
		max_depth = ( [1,10], 4, 'int'),
		max_features=( [1, 20],  10, 'int'),				
		n_estimators=( [1, 100],  10, 'int', 'log'),			
		criterion =( {'gini', 'entropy'}, 'entropy'),
		)

# a litle bit of explanation: the first two lines define integer parameters
# ranging from 1 to 10/20 with some default values. The third line also defines
# a integer parameter, but the additional 'log' string tells SMAC to vary it
# uniformly on a logarithmic scale. Here it means, that 1<=n_estimators<=10 is 
# as likely as 10<n_estimators<=100.
# The last line defines a categorical parameter. For now ,the values are always
# treated as strings. This means you would have to cast that inside your function
# when this is not appropriate, e.g., when discretizing an interval.


# Now we create the optimizer object again. This time with some parameters
opt = pysmac.SMAC_optimizer( working_directory = '/tmp/pysmac_test/',# the folder where SMAC generates output
							 persistent_files=True,					 # whether the output will persist beyond the python objects lifetime
							 debug = False							 # if something goes wrong, enable this for diagnostic output
							)


# first we try the sklearn default, so we can see if SMAC can improve the performance
predictor = sklearn.ensemble.RandomForestClassifier()
predictor.fit(X_train, Y_train)
print('The default accuracy is %f'%predictor.score(X_test, Y_test))




# The minimize method also has optional arguments
value, parameters = opt.minimize(random_forest,
					1000 , parameter_definition,
					num_runs = 4,					# number of independent SMAC runs
					seed = 42,						# the random seed used. can be an int or a list of ints of length num_runs
					num_procs = 4,					# pySMAC can harness multicore architecture. Specify the number of processes to use here.
					mem_limit_function_mb=1000,		# There are a build-in mechanisms to limit the resources available to each function call:
					t_limit_function_s = 20			# 	You can limit the memory available and the wallclock time for each function call
					)
	
print('The highest accuracy found: %f'%(-value))
print('Parameter setting %s'%parameters)