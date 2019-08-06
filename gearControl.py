import vrep
import math
import time

RAD = 180/math.pi
step = 0.005

def send_gear_commands(clientID ,target_degree1, target_degree2, gearHandle1, gearHandle2):
	RAD = 180/math.pi
	lastCmdTime = vrep.simxGetLastCmdTime(clientID)
	vrep.simxSynchronousTrigger(clientID)
	count = 0
	while vrep.simxGetConnectionId(clientID) != -1:
		count += 1
		if count > 20:
			break
		currCmdTime = vrep.simxGetLastCmdTime(clientID)
		dt = currCmdTime - lastCmdTime

		ret, gear_pos1 = vrep.simxGetJointPosition(clientID, gearHandle1, vrep.simx_opmode_buffer)
		ret, gear_pos2 = vrep.simxGetJointPosition(clientID, gearHandle2, vrep.simx_opmode_buffer)
		degree1 = round(gear_pos1*RAD, 2)
		degree2 = round(gear_pos2*RAD, 2)
		print(degree1, degree2)
		if abs(degree1-target_degree1)<0.5 and abs(degree2-target_degree2)<0.5:
			break
		vrep.simxPauseCommunication(clientID, True)
		vrep.simxSetJointTargetPosition(clientID, gearHandle1, target_degree1/RAD, vrep.simx_opmode_oneshot)
		vrep.simxSetJointTargetPosition(clientID, gearHandle2, target_degree2/RAD, vrep.simx_opmode_oneshot)
		vrep.simxPauseCommunication(clientID, False)

		lastCmdTime = currCmdTime
		vrep.simxSynchronousTrigger(clientID)
		# vrep.simxGetPingTime(clientID)


# Demo
'''vrep.simxFinish(-1)
clientID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
if clientID != -1:
	vrep.simxSetFloatingParameter(clientID, vrep.sim_floatparam_simulation_time_step, step, vrep.simx_opmode_oneshot)
	vrep.simxSynchronous(clientID, True)
	vrep.simxStartSimulation(clientID, vrep.simx_opmode_oneshot)

	# get handles
	ret, gearHandle1 = vrep.simxGetObjectHandle(clientID, 'Gear_joint1',
										vrep.simx_opmode_oneshot_wait)
	ret, gearHandle2 = vrep.simxGetObjectHandle(clientID, 'Gear_joint2',
										vrep.simx_opmode_oneshot_wait)
	print(ret, gearHandle1, gearHandle2)

	# get the position of joint1
	ret, gear_pos1 = vrep.simxGetJointPosition(clientID, gearHandle1, vrep.simx_opmode_streaming)
	ret, gear_pos2 = vrep.simxGetJointPosition(clientID, gearHandle2, vrep.simx_opmode_streaming)
	print(ret, gear_pos1, gear_pos2)
	
	lastCmdTime = vrep.simxGetLastCmdTime(clientID)
	vrep.simxSynchronousTrigger(clientID)
	
	target_degree1 = -60.0
	target_degree2 = +60.0
	send_gear_commands(clientID, target_degree1, target_degree2, gearHandle1, gearHandle2)
	# time.sleep(2)
	print('cnm')
	target_degree1 = 0.0
	target_degree2 = 0.0
	send_gear_commands(clientID, target_degree1, target_degree2, gearHandle1, gearHandle2)

	# vrep.simxSetJointPosition(clientID, jointHandle, 90, vrep.simx_opmode_oneshot)
	# vrep.simxSetJointTargetPosition(clientID, joint, 10, vrep.simx_opmode_oneshot)
	# vrep.simxSetJointTargetVelocity(clientID, jointHandle, 1, vrep.simx_opmode_oneshot)
	# time.sleep(1)
else:
	print('Failed connecting to remote API server')'''