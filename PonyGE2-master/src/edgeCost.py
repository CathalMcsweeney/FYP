
class edgeCost:
	def __init__(self,val):
		self.val = val
	
# def trafficLvl(edgeOccupancy,trafficBuildUp):
	
# 	# check the edge for congestion if traffic is heavy it increases the cost if 0 same cost based on length and junction
# 	# edgeOccupancy is the percentage of time the edge was occupied by a vehicle
# 	if edgeOccupancy > trafficBuildUp:
# 		trafficLevel = 1 + edgeOccupancy
# 	else:
# 		trafficLevel = 1
# 	return trafficLevel

def functionJunctionType(junction,one,two):
	# use the junction object to identify what type of junction is at the end of this edge
	test =  junction._type
	weight = 0.01
	#traffic lights
	if "light" in test:
		weight = 1
	#stop sign or roundabout
	if "right_before" in test:
		weight = one
	# assumes that the road has a right of way or connects to another edge instead of a node
	if "priority" in test:
		weight = two

	return weight