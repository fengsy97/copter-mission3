import vrep
import ctypes
import numpy as np
import time
import math
import gearControl
import util
import controller
import _thread
from PlaneController import PlaneCotroller
PI = 3.1415926


class MainController:
    def __init__(self, *args, **kwargs):
        print ('Program started')
        vrep.simxFinish(-1) # just in case, close all opened connections
        self.clientId=vrep.simxStart('127.0.0.1',19997,True,True,5000,5) # Connect to V-REP, set a very large time-out for blocking commands
    
    def pdThread(self):
        while(True):
            self.pdController.control_step()
    #=============================================================#
    #                 don't change this function                  #
    #=============================================================#
    def startSimulation(self):
        if self.clientId!=-1:
            #+++++++++++++++++++++++++++++++++++++++++++++
            step = 0.005
            vrep.simxSetFloatingParameter(self.clientId, vrep.sim_floatparam_simulation_time_step, step, vrep.simx_opmode_oneshot)
            vrep.simxSynchronous(self.clientId, True)
            vrep.simxStartSimulation(self.clientId,vrep.simx_opmode_oneshot)
            #init the controller
            planeController = PlaneCotroller(self.clientId)
            planeController.take_off()
            self.pdController = controller.PID(cid=self.clientId,ori_mode=True)

            #create a thread to controll the move of quadcopter
            _thread.start_new_thread(self.pdThread,())
            print("thread created")
            #to be stable
            planeController.loose_jacohand()
            # planeController.move_to(planeController.get_object_pos(planeController.copter),True)
            # planeController.plane_pos = planeController.get_object_pos(planeController.copter)
            # time.sleep(10)
            self.run_simulation(planeController)
        else:
            print ('Failed connecting to remote API server')
        print ('Simulation ended')
        vrep.simxStopSimulation(self.clientId,vrep.simx_opmode_oneshot)
    
    #=============================================================#
    #                 simulation runs here                        #
    #=============================================================#
    def run_simulation(self,planeController):
        # while(True):
        #     None
        print("run simulation")
        # planeController.move_with_v(1,0.0)
        # while True:
        #     continue

        # planeController.initial_pos()
        target = planeController.locate_target()
        print("target = " + str(target))
        planeController.follow_target(target)
        planeController.landing()



mainController = MainController()
mainController.startSimulation()