function sysCall_init() 
    -- Make sure we have version 2.4.13 or above (the particles are not supported otherwise)
    v=sim.getInt32Parameter(sim.intparam_program_version)
    if (v<20413) then
        sim.displayDialog('Warning','The propeller model is only fully supported from V-REP version 2.4.13 and above.&&nThis simulation will not run as expected!',sim.dlgstyle_ok,false,'',nil,{0.8,0,0,0,0,0})
    end

    -- Detatch the manipulation sphere:
    targetObj=sim.getObjectHandle('Quadricopter_target')
    sim.setObjectParent(targetObj,-1,true)

    -- This control algo was quickly written and is dirty and not optimal. It just serves as a SIMPLE example

    d=sim.getObjectHandle('Quadricopter_base')
    hand_handle=sim.getObjectHandle('JacoHand')
    quadricopter=sim.getObjectHandle('Quadricopter')
    quadricopter_prop_respondable1=sim.getObjectHandle('Quadricopter_propeller_respondable1')

    particlesAreVisible=sim.getScriptSimulationParameter(sim.handle_self,'particlesAreVisible')
    sim.setScriptSimulationParameter(sim.handle_tree,'particlesAreVisible',tostring(particlesAreVisible))
    simulateParticles=sim.getScriptSimulationParameter(sim.handle_self,'simulateParticles')
    sim.setScriptSimulationParameter(sim.handle_tree,'simulateParticles',tostring(simulateParticles))

    propellerScripts={-1,-1,-1,-1}
    for i=1,4,1 do
        propellerScripts[i]=sim.getScriptHandle('Quadricopter_propeller_respondable'..i)
    end
    heli=sim.getObjectAssociatedWithScript(sim.handle_self)
    hand_script_handle = sim.getScriptHandle('JacoHand')
    --print('hand_script_handle', hand_script_handle)

    particlesTargetVelocities={0,0,0,0}

    pParam=6
    iParam=0.04
    dParam=0.08
    vParam=-2

    cumul=0
    lastE=0
    pAlphaE=0
    pBetaE=0
    alphaCumul=0
    betaCumul=0
    rotCorrCumul=0
    psp2=0
    psp1=0
    spCumul=0

    prevEuler=0


    fakeShadow=sim.getScriptSimulationParameter(sim.handle_self,'fakeShadow')
    if (fakeShadow) then
        shadowCont=sim.addDrawingObject(sim.drawing_discpoints+sim.drawing_cyclic+sim.drawing_25percenttransparency+sim.drawing_50percenttransparency+sim.drawing_itemsizes,0.2,0,-1,1)
    end

    -- Prepare 2 floating views with the zed camera views:
    zed_vision0 = sim.getObjectHandle('zed_vision0')
    zed_vision1 = sim.getObjectHandle('zed_vision1')

    zed_v0_View=sim.floatingViewAdd(0.9,0.9,0.2,0.2,0)
    zed_v1_View=sim.floatingViewAdd(0.7,0.9,0.2,0.2,0)
    sim.adjustView(zed_v0_View,zed_vision0,64)
    sim.adjustView(zed_v1_View,zed_vision1,64)

    end_vector = {0,0,0.14}
    t_sim_start = sim.getSimulationTime()
    grapped = false
    speed = -1 -- m/s
    hold_time = 0.5 -- s
    distance_hold = 0.11
    start_position = sim.getObjectPosition(targetObj, -1)
    ----- the commented part is the decision logic to grap a 'Sphere'
    --hold_target_handle = sim.getObjectHandle('Sphere')
    --hold_target_position = sim.getObjectPosition(hold_target_handle, -1)
end

function sysCall_cleanup() 
    sim.removeDrawingObject(shadowCont)
    sim.floatingViewRemove(zed_v0_View)
    sim.floatingViewRemove(zed_v1_View)
end 

local power = 0

function sysCall_actuation() 
    s=sim.getObjectSizeFactor(d)
    
    pos=sim.getObjectPosition(d,-1)
    
    if (fakeShadow) then
        itemData={pos[1],pos[2],0.002,0,0,1,0.2*s}
        sim.addDrawingObjectItem(shadowCont,itemData)

        -- Draw shadow for target
        targetPos=sim.getObjectPosition(targetObj,-1)
        itemData={targetPos[1],targetPos[2],0.002,0,0,1,0.1*s}
        --sim.addDrawingObjectItem(shadowContTarget,itemData)
    end

    -- Send the desired motor velocities to the 4 rotors:
    data=sim.getStringSignal("rotorPower")

    if (data ~= nil) then
        vector=sim.unpackFloatTable(data)
        if (vector[1] ~= nil) then
            power = vector[1]
        end
    end

    data=sim.getStringSignal("rotorTargetVelocities")


    -- which external forcing functions to use
    -- 0 will use no forcing functions
    forcefunc=sim.getIntegerSignal("ForceFunction")
    if (power ~= 0) then
        for i=1,4,1 do
            sim.setScriptSimulationParameter(propellerScripts[i],'particleVelocity',9 + power)
        end
    elseif(data ~= nil) then
        vector=sim.unpackFloatTable(data)
        if (vector[1] ~= nil) then
            for i=1,4,1 do
                sim.setScriptSimulationParameter(propellerScripts[i],'particleVelocity',vector[i] + power)
            end
        end
    end

    -- Retrive signals from vrep_gui.py
    --mass=sim.getIntegerSignal("mass")
    --print(mass)
    --sim.setShapeMassAndInertia(sim.handle_self, mass)

end 
