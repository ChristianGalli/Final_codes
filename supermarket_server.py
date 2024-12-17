import logging
import asyncio
from asyncua import Server, ua

# standard lines to log and start a server

async def main():
    # Create and initialize OPC UA server
    server = Server()
    await server.init()

    # Configuration of the end point of a server (the address to which connects and identifies the server, basically is the server IP)
    server.set_endpoint("opc.tcp://0.0.0.0:3005/factory/server") # 0.0.0.0 is the local machine at port 3005 and then the folders
    server.set_server_name("MyFactory Server")
    
    # We have to set the security policies (log in)
    server.set_security_policy(
        [
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256Sha256_Sign
            ]
    )

    """
    async def PowerOn(powerStatus):
        await powerStatus.write_value("PowerOn")
        return "PowerOn"

    async def PowerOff(powerStatus):
        await powerStatus.write_value("PowerOff")
        return "PowerOff"    
    
    async def OpenDoor(doorStatus):
        await doorStatus.write_value("Open")
        return "Open"
    
    async def CloseDoor(doorStatus):
        await doorStatus.write_value("Closed")
        return "Closed"
    """

    # Name Spaces configuration
    uri = "http://examples.factory.github.io" # sub adress that we'll use as a place where to assign the 
    idx = await server.register_namespace(uri)

    # Create Object Type
    supermarket = await server.nodes.base_object_type.add_object_type(idx,"SupermarketType") # Object Type

    # Add Variables

    location = await supermarket.add_object_type(idx, "LocationType")

    fridges = await location.add_object_type(idx, "Fridges")   

    """
    
    # Door Status
    doorStatus = await fridges.add_variable(idx, "DoorStatus", val="DoorCLOSED", datatype=ua.NodeId(ua.ObjectIds.String))
    await doorStatus.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await doorStatus.set_writable()

    #Power Status
    powerStatus = await fridges.add_variable(idx, "powerStatus", val="On", datatype=ua.NodeId(ua.ObjectIds.String))
    await powerStatus.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await powerStatus.set_writable()

    """

    # Compressor Outlet Pressure Sensor
    compOutPres = await fridges.add_variable(idx, "compOutPres", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await compOutPres.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await compOutPres.set_writable()
    
    # Compressor Outlet Temperature Sensor
    compOutTemp = await fridges.add_variable(idx, "compOutTemp", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await compOutTemp.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await compOutTemp.set_writable()
    
    # Condenser Inlet Pressure Sensor
    condInPres = await fridges.add_variable(idx, "condInPres", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await condInPres.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await condInPres.set_writable()

    # Condenser Inlet Temperature Sensor
    condInTemp = await fridges.add_variable(idx, "condInTemp", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await condInTemp.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await condInTemp.set_writable()

    # Condenser Outlet Pressure Sensor
    condOutPres = await fridges.add_variable(idx, "condOutPres", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await condOutPres.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await condOutPres.set_writable()

    # Condenser Outlet Temperature Sensor
    condOutTemp = await fridges.add_variable(idx, "condOutTemp", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await condOutTemp.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await condOutTemp.set_writable()

    # Evaporator Inlet Pressure Sensor
    evapInPres = await fridges.add_variable(idx, "evapInPres", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await evapInPres.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await evapInPres.set_writable()

    # Compressor Inlet Temperature Sensor
    compInTemp = await fridges.add_variable(idx, "compInTemp", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await compInTemp.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await compInTemp.set_writable()

    # Evaporator Outlet Pressure Sensor
    evapOutPres = await fridges.add_variable(idx, "evapOutPres", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await evapOutPres.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await evapOutPres.set_writable()

    # Evaporator Outlet Temperature Sensor
    evapOutTemp = await fridges.add_variable(idx, "evapOutTemp", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await evapOutTemp.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await evapOutTemp.set_writable()

    # Temparaure chamber 1
    tempC1 = await fridges.add_variable(idx, "tempC1", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await tempC1.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await tempC1.set_writable()

    # Temparaure chamber 2
    tempC2 = await fridges.add_variable(idx, "tempC2", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await tempC2.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await tempC2.set_writable()

    # Temparaure chamber 3
    tempC3 = await fridges.add_variable(idx, "tempC3", val=0.0, datatype=ua.NodeId(ua.ObjectIds.Float))
    await tempC3.set_modelling_rule(True) # this allows us to add the variable as default to fridges
    await tempC3.set_writable()    

    """
    # Create Methods

    powerOnFunc = await fridges.add_method(idx, "PowerOn", PowerOn, None, [ua.VariantType.String]) # Different way to define the type (DON'T ASK Y)
    await powerOnFunc.set_modelling_rule(True)

    powerOffFunc = await fridges.add_method(idx, "PowerOff", PowerOff, None, [ua.VariantType.String])
    await powerOffFunc.set_modelling_rule(True) 

    closeDoorFunc = await fridges.add_method(idx, "Closed", CloseDoor, None, [ua.VariantType.String])
    await closeDoorFunc.set_modelling_rule(True)

    openDoorFunc = await fridges.add_method(idx, "open", OpenDoor, None, [ua.VariantType.String])
    await openDoorFunc.set_modelling_rule(True) 
    """

    # Instatiate supermarket 1
    supermarket1 = await server.nodes.objects.add_object(idx, "Supermarket1", supermarket)


    location1_1 = await supermarket1.add_object(idx, "Location1", location)

    fridge1_1 = await location1_1.add_object(idx, "Fridge1", fridges)

    fridge2_1 = await location1_1.add_object(idx, "Fridge2", fridges)


    location2_1 = await supermarket1.add_object(idx, "Location2", location)

    fridge1_2 = await location2_1.add_object(idx, "Fridge1", fridges)


    # Instatiate supermarket 2

    supermarket2 = await server.nodes.objects.add_object(idx, "Supermarket2", supermarket)

    location1_2 = await supermarket2.add_object(idx, "Location1", location)

    fridge1_1 = await location1_2.add_object(idx, "Fridge1", fridges)

    # Start the server (ALWAYS EQUAL)

    async with server:
        print("Server started")
        await asyncio.sleep(999999)

if __name__ == "__main__":    
    # Configuration of the logging (how much the server comunicates with us) option
    logging.basicConfig(level=logging.INFO)
    # Run the "main" part of the code in a asyncronous way
    asyncio.run(main()) # Execute the function "main" asyncronously, basically it allows us to go on with the rest of the code
                        # while waiting for an answare from the server for example. If it was syncronous it will wait for the answare

    

