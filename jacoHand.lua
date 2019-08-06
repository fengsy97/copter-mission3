function sysCall_init() 
    modelHandle=sim.getObjectAssociatedWithScript(sim.handle_self)
    j0=sim.getObjectHandle("JacoHand_fingers12_motor1")
    j1=sim.getObjectHandle("JacoHand_fingers12_motor2")
    j2=sim.getObjectHandle("JacoHand_finger3_motor1")
    j3=sim.getObjectHandle("JacoHand_finger3_motor2")
    ui=simGetUIHandle('JacoHand')
    shape = sim.getObjectHandle('Target')
    sim.setObjectInt32Parameter(shape,sim.shapeintparam_static,0)
    simSetUIButtonLabel(ui,0,sim.getObjectName(modelHandle))
    closingVel=-0.04
end
-- See the end of the script for instructions on how to do efficient grasping

local attachedShape = -1

function sysCall_cleanup() 

end 

function sysCall_actuation() 
    closing=sim.boolAnd32(simGetUIButtonProperty(ui,20),sim.buttonproperty_isdown)~=0
    close_hand=sim.getScriptSimulationParameter(sim.handle_self,'close_hand')
    data=sim.getStringSignal("jacohand")

    if (data ~= nil) then
        vector=sim.unpackFloatTable(data)
        if(vector[1] == -1) then
            sim.setJointTargetVelocity(j0,-closingVel)
            sim.setJointTargetVelocity(j1,-closingVel)
            sim.setJointTargetVelocity(j2,-closingVel)
            sim.setJointTargetVelocity(j3,-closingVel)
             -- c) And just before opening the gripper again, detach the previously attached shape:
    --
            if attachedShape ~= -1 then
                sim.setObjectParent(attachedShape,-1,true)
            end
            attachedShape = -1
        else
            print('there')
            sim.setJointTargetVelocity(j0,closingVel)
            sim.setJointTargetVelocity(j1,closingVel)
            sim.setJointTargetVelocity(j2,closingVel)
            sim.setJointTargetVelocity(j3,closingVel)

            -- You have basically 2 alternatives to grasp an object:
    --
    -- 1. You try to grasp it in a realistic way. This is quite delicate and sometimes requires
    --    to carefully adjust several parameters (e.g. motor forces/torques/velocities, friction
    --    coefficients, object masses and inertias)
    --
    -- 2. You fake the grasping by attaching the object to the gripper via a connector. This is
    --    much easier and offers very stable results.
    --
    -- Alternative 2 is explained hereafter:
    --
    --
    -- a) In the initialization phase, retrieve some handles:
    -- 
    connector=sim.getObjectHandle('JacoHand_attachPoint')
    objectSensor=sim.getObjectHandle('JacoHand_attachProxSensor')
    
    -- b) Before closing the gripper, check which dynamically non-static and respondable object is
    --    in-between the fingers. Then attach the object to the gripper:
    --
     index=0
     while true do
         if attachedShape ~= -1 then
            break
         end
         shape=sim.getObjects(index,sim.object_shape_type)
         if (shape==-1) then
             break
         end
         err,isstatic = sim.getObjectInt32Parameter(shape,sim.shapeintparam_static)
         err,isRespeondable = sim.getObjectInt32Parameter(shape,sim.shapeintparam_respondable)
         res,a,b = sim.checkProximitySensor(objectSensor,shape)
         if (isstatic==0) and (isRespeondable~=0) and (res==1) then
             -- Ok, we found a non-static respondable shape that was detected
            attachedShape=shape
            print('connect')
             -- Do the connection:
             sim.setObjectParent(attachedShape,connector,true)
             break
         end
         index=index+1
    end
        end
    end

    
    
    -- c) And just before opening the gripper again, detach the previously attached shape:
    --
    -- sim.setObjectParent(attachedShape,-1,true)
end 
