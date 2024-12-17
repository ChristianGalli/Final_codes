# opc_udp_middleware.py
from asyncua import Client
import asyncio
import json
from datetime import datetime
import logging
from typing import Dict, Any, Optional
import socket

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OPCUDPBridge:
    def __init__(self, 
                 opc_url: str = "opc.tcp://localhost:3005",
                 unity_ip: str = "127.0.0.1", 
                 unity_port: int = 12345,
                 update_rate: float = 0.1):  # Time in seconds between updates
        self.opc_url = opc_url
        self.unity_ip = unity_ip
        self.unity_port = unity_port
        self.update_rate = update_rate
        self.client = None
        self.udp_socket = None
        self.running = False
        self.monitored_nodes = {}
        self.last_values = {}

    async def connect(self):
        """Connects to OPC UA server and initializes UDP socket"""
        try:
            # OPC UA connection
            self.client = Client(url=self.opc_url)
            await self.client.connect()
            logger.info(f"Connected to OPC UA server: {self.opc_url}")

            # UDP socket initialization
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            logger.info(f"UDP socket initialized for {self.unity_ip}:{self.unity_port}")

        except Exception as e:
            logger.error(f"Connection error: {e}")
            if self.client:
                await self.client.disconnect()
            if self.udp_socket:
                self.udp_socket.close()
            raise

    async def add_node(self, node_id: str, alias: Optional[str] = None):
        """Adds a node to monitor"""
        try:
            node = self.client.get_node(node_id)
            # Verify node exists by reading its name
            browse_name = await node.read_browse_name()
            self.monitored_nodes[node_id] = {
                'node': node,
                'alias': alias or node_id
            }
            logger.info(f"Added node: {node_id} with alias: {alias}")
        except Exception as e:
            logger.error(f"Error adding node {node_id}: {e}")
            raise

    async def read_node_value(self, node_id: str) -> Dict:
        """Reads the current value of a node"""
        try:
            node_info = self.monitored_nodes[node_id]
            node = node_info['node']
            value = await node.read_value()
            dv = await node.read_data_value()
            
            return {
                'alias': node_info['alias'],
                'value': value,
                'timestamp': dv.SourceTimestamp.isoformat() if dv.SourceTimestamp else datetime.now().isoformat(),
                'quality': str(dv.StatusCode)
            }
        except Exception as e:
            logger.error(f"Error reading node {node_id}: {e}")
            return None

    async def send_to_unity(self, data: Dict):
        """Sends data to Unity via UDP"""
        try:
            json_data = json.dumps(data)
            self.udp_socket.sendto(
                json_data.encode('utf-8'), 
                (self.unity_ip, self.unity_port)
            )
            logger.debug(f"Data sent to Unity: {json_data}")
        except Exception as e:
            logger.error(f"Error sending data to Unity: {e}")

    async def update_loop(self):
        """Main loop for updating and sending data"""
        while self.running:
            try:
                # Read all values
                current_values = {}
                for node_id in self.monitored_nodes:
                    value = await self.read_node_value(node_id)
                    if value:
                        current_values[str(node_id)] = value

                # Send only if there are changes
                if current_values != self.last_values:
                    json_object = {
                        'timestamp': datetime.now().isoformat(),
                        'values': current_values
                    }
                    print(json_object)
                    await self.send_to_unity(json_object)
                    self.last_values = current_values

                await asyncio.sleep(self.update_rate)

            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(1)  # Pause before retrying

    async def start(self):
        """Starts the bridge"""
        await self.connect()
        self.running = True
        logger.info("Bridge started")
        await self.update_loop()

    async def stop(self):
        """Stops the bridge"""
        self.running = False
        if self.client:
            await self.client.disconnect()
        if self.udp_socket:
            self.udp_socket.close()
        logger.info("Bridge stopped")

    async def receive_from_unity(self):
        """Receives data from Unity via UDP"""
        if self.udp_socket is None:
            logger.error("UDP socket is not initialized.")
            return None
        try:
            data, _ = self.udp_socket.recvfrom(1024)  # Buffer size is 1024 bytes
            json_data = json.loads(data.decode('utf-8'))
            return json_data
        except Exception as e:
            logger.error(f"Error receiving data from Unity: {e}")
            return None

async def main():
    # Bridge configuration
    bridge = OPCUDPBridge(
        opc_url="opc.tcp://localhost:3005",    # OPC UA server URL
        unity_ip="127.0.0.1",                  # Unity application IP
        unity_port=12345,                      # Unity application UDP port
        update_rate=0.1                        # Update every 100ms
    )

    """
    # Ricevi il valore di "Supermarket" da Unity
    unity_data = await bridge.receive_from_unity()
    if unity_data and "Supermarket" in unity_data:
        supermarket_name = unity_data["Supermarket"]
    else:
        supermarket_name = "Supermarket1"  # Valore di default o gestisci l'errore

    if unity_data and "Location" in unity_data:
        location_name = unity_data["Location"]
    else:
        location_name = "Location1"  # Valore di default o gestisci l'errore

    if unity_data and "Fridge" in unity_data:
        fridge_name = unity_data["Fridge"]
    else:
        fridge_name = "Fridge1"  # Valore di default o gestisci l'errore

    """


    try:
        # Add nodes to monitor
        await bridge.connect()

        objects = await bridge.client.nodes.root.get_child(f"0:Objects")

        # penso vada cambiato con le varibili di richiamo da unity (nomi e variabili)
        # dobbiamo implementare la parte in OPCUDPBridge tale che possa ricevere i dati da unity
        # praticamente i nomi del menù a tendina in mdo che il nodo sia cercato correttamente
        
        """
        supermarket = await objects.get_child(f"2:{supermarket_name}")  # Basta sostitutire il nome corretto del nodo
        location = await supermarket.get_child(f"2:{location_name}")  # Basta sostituire il nome corretto del nodo
        fridge = await location.get_child(f"2:{fridge_name}")  # Basta sostituire il nome corretto del nodo
        inTemp = await fridge.get_child("2:inTemp")
        inHumid = await fridge.get_child("2:inHumid")

        """
        # Supermarket 1

        supermarket1 = await objects.get_child("2:Supermarket1")  # Basta sostitutire il nome corretto del nodo
        
        # Location 1

        location1 = await supermarket1.get_child("2:Location1")  # Basta sostituire il nome corretto del nodo
        
        # Firidge 1

        fridge1 = await location1.get_child("2:Fridge1")  # Basta sostituire il nome corretto del nodo
        
        compOutPres_S1L1F1 = await fridge1.get_child("2:compOutPres")
        compOutTemp_S1L1F1 = await fridge1.get_child("2:compOutTemp")
        condInPres_S1L1F1 = await fridge1.get_child("2:condInPres")
        condInTemp_S1L1F1 = await fridge1.get_child("2:condInTemp")
        condOutPres_S1L1F1 = await fridge1.get_child("2:condOutPres")
        condOutTemp_S1L1F1 = await fridge1.get_child("2:condOutTemp")
        evapInPres_S1L1F1 = await fridge1.get_child("2:evapInPres")
        compInTemp_S1L1F1 = await fridge1.get_child("2:compInTemp")
        evapOutPres_S1L1F1 = await fridge1.get_child("2:evapOutPres")
        evapOutTemp_S1L1F1 = await fridge1.get_child("2:evapOutTemp")
        tempC1_S1L1F1 = await fridge1.get_child("2:tempC1")
        tempC2_S1L1F1 = await fridge1.get_child("2:tempC2")
        tempC3_S1L1F1 = await fridge1.get_child("2:tempC3")
        
        # Example of adding nodes with aliases
        await bridge.add_node(compOutPres_S1L1F1, "compOutPres_S1L1F1")
        await bridge.add_node(compOutTemp_S1L1F1, "compOutTemp_S1L1F1")
        await bridge.add_node(condInPres_S1L1F1, "condInPres_S1L1F1")
        await bridge.add_node(condInTemp_S1L1F1, "condInTemp_S1L1F1")
        await bridge.add_node(condOutPres_S1L1F1, "condOutPres_S1L1F1")
        await bridge.add_node(condOutTemp_S1L1F1, "condOutTemp_S1L1F1")
        await bridge.add_node(evapInPres_S1L1F1, "evapInPres_S1L1F1")
        await bridge.add_node(compInTemp_S1L1F1, "compInTemp_S1L1F1")
        await bridge.add_node(evapOutPres_S1L1F1, "evapOutPres_S1L1F1")
        await bridge.add_node(evapOutTemp_S1L1F1, "evapOutTemp_S1L1F1")
        await bridge.add_node(tempC1_S1L1F1, "tempC1_S1L1F1")
        await bridge.add_node(tempC2_S1L1F1, "tempC2_S1L1F1")
        await bridge.add_node(tempC3_S1L1F1, "tempC3_S1L1F1")

        # Firidge 1

        fridge2 = await location1.get_child("2:Fridge2")  # Basta sostituire il nome corretto del nodo
        
        compOutPres_S1L1F2 = await fridge2.get_child("2:compOutPres")
        compOutTemp_S1L1F2 = await fridge2.get_child("2:compOutTemp")
        condInPres_S1L1F2 = await fridge2.get_child("2:condInPres")
        condInTemp_S1L1F2 = await fridge2.get_child("2:condInTemp")
        condOutPres_S1L1F2 = await fridge2.get_child("2:condOutPres")
        condOutTemp_S1L1F2 = await fridge2.get_child("2:condOutTemp")
        evapInPres_S1L1F2 = await fridge2.get_child("2:evapInPres")
        compInTemp_S1L1F2 = await fridge2.get_child("2:compInTemp")
        evapOutPres_S1L1F2 = await fridge2.get_child("2:evapOutPres")
        evapOutTemp_S1L1F2 = await fridge2.get_child("2:evapOutTemp")
        tempC1_S1L1F2 = await fridge2.get_child("2:tempC1")
        tempC2_S1L1F2 = await fridge2.get_child("2:tempC2")
        tempC3_S1L1F2 = await fridge2.get_child("2:tempC3")
        
        # Example of adding nodes with aliases
        await bridge.add_node(compOutPres_S1L1F2, "compOutPres_S1L1F2")
        await bridge.add_node(compOutTemp_S1L1F2, "compOutTemp_S1L1F2")
        await bridge.add_node(condInPres_S1L1F2, "condInPres_S1L1F2")
        await bridge.add_node(condInTemp_S1L1F2, "condInTemp_S1L1F2")
        await bridge.add_node(condOutPres_S1L1F2, "condOutPres_S1L1F2")
        await bridge.add_node(condOutTemp_S1L1F2, "condOutTemp_S1L1F2")
        await bridge.add_node(evapInPres_S1L1F2, "evapInPres_S1L1F2")
        await bridge.add_node(compInTemp_S1L1F2, "compInTemp_S1L1F2")
        await bridge.add_node(evapOutPres_S1L1F2, "evapOutPres_S1L1F2")
        await bridge.add_node(evapOutTemp_S1L1F2, "evapOutTemp_S1L1F2")
        await bridge.add_node(tempC1_S1L1F2, "tempC1_S1L1F2")
        await bridge.add_node(tempC2_S1L1F2, "tempC2_S1L1F2")
        await bridge.add_node(tempC3_S1L1F2, "tempC3_S1L1F2")

        # Location 2

        location2 = await supermarket1.get_child("2:Location2")  # Basta sostituire il nome corretto del nodo
        
        # Firidge 1

        fridge1_2 = await location2.get_child("2:Fridge1")  # Basta sostituire il nome corretto del nodo
        
        compOutPres_S1L2F1 = await fridge1_2.get_child("2:compOutPres")
        compOutTemp_S1L2F1 = await fridge1_2.get_child("2:compOutTemp")
        condInPres_S1L2F1 = await fridge1_2.get_child("2:condInPres")
        condInTemp_S1L2F1 = await fridge1_2.get_child("2:condInTemp")
        condOutPres_S1L2F1 = await fridge1_2.get_child("2:condOutPres")
        condOutTemp_S1L2F1 = await fridge1_2.get_child("2:condOutTemp")
        evapInPres_S1L2F1 = await fridge1_2.get_child("2:evapInPres")
        compInTemp_S1L2F1 = await fridge1_2.get_child("2:compInTemp")
        evapOutPres_S1L2F1 = await fridge1_2.get_child("2:evapOutPres")
        evapOutTemp_S1L2F1 = await fridge1_2.get_child("2:evapOutTemp")
        tempC1_S1L2F1 = await fridge1_2.get_child("2:tempC1")
        tempC2_S1L2F1 = await fridge1_2.get_child("2:tempC2")
        tempC3_S1L2F1 = await fridge1_2.get_child("2:tempC3")
        
        # Example of adding nodes with aliases
        await bridge.add_node(compOutPres_S1L2F1, "compOutPres_S1L2F1")
        await bridge.add_node(compOutTemp_S1L2F1, "compOutTemp_S1L2F1")
        await bridge.add_node(condInPres_S1L2F1, "condInPres_S1L2F1")
        await bridge.add_node(condInTemp_S1L2F1, "condInTemp_S1L2F1")
        await bridge.add_node(condOutPres_S1L2F1, "condOutPres_S1L2F1")
        await bridge.add_node(condOutTemp_S1L2F1, "condOutTemp_S1L2F1")
        await bridge.add_node(evapInPres_S1L2F1, "evapInPres_S1L2F1")
        await bridge.add_node(compInTemp_S1L2F1, "compInTemp_S1L2F1")
        await bridge.add_node(evapOutPres_S1L2F1, "evapOutPres_S1L2F1")
        await bridge.add_node(evapOutTemp_S1L2F1, "evapOutTemp_S1L2F1")
        await bridge.add_node(tempC1_S1L2F1, "tempC1_S1L2F1")
        await bridge.add_node(tempC2_S1L2F1, "tempC2_S1L2F1")
        await bridge.add_node(tempC3_S1L2F1, "tempC3_S1L2F1")

        # Supermarket 2

        supermarket2 = await objects.get_child("2:Supermarket2")  # Basta sostitutire il nome corretto del nodo
        
        # Location 1

        location1_2 = await supermarket2.get_child("2:Location1")  # Basta sostituire il nome corretto del nodo
        
        # Firidge 1

        fridge1_22 = await location1_2.get_child("2:Fridge1")  # Basta sostituire il nome corretto del nodo
        
        compOutPres_S2L1F1 = await fridge1_22.get_child("2:compOutPres")
        compOutTemp_S2L1F1 = await fridge1_22.get_child("2:compOutTemp")
        condInPres_S2L1F1 = await fridge1_22.get_child("2:condInPres")
        condInTemp_S2L1F1 = await fridge1_22.get_child("2:condInTemp")
        condOutPres_S2L1F1 = await fridge1_22.get_child("2:condOutPres")
        condOutTemp_S2L1F1 = await fridge1_22.get_child("2:condOutTemp")
        evapInPres_S2L1F1 = await fridge1_22.get_child("2:evapInPres")
        compInTemp_S2L1F1 = await fridge1_22.get_child("2:compInTemp")
        evapOutPres_S2L1F1 = await fridge1_22.get_child("2:evapOutPres")
        evapOutTemp_S2L1F1 = await fridge1_22.get_child("2:evapOutTemp")
        tempC1_S2L1F1 = await fridge1_22.get_child("2:tempC1")
        tempC2_S2L1F1 = await fridge1_22.get_child("2:tempC2")
        tempC3_S2L1F1 = await fridge1_22.get_child("2:tempC3")
        
        # Example of adding nodes with aliases
        await bridge.add_node(compOutPres_S2L1F1, "compOutPres_S2L1F1")
        await bridge.add_node(compOutTemp_S2L1F1, "compOutTemp_S2L1F1")
        await bridge.add_node(condInPres_S2L1F1, "condInPres_S2L1F1")
        await bridge.add_node(condInTemp_S2L1F1, "condInTemp_S2L1F1")
        await bridge.add_node(condOutPres_S2L1F1, "condOutPres_S2L1F1")
        await bridge.add_node(condOutTemp_S2L1F1, "condOutTemp_S2L1F1")
        await bridge.add_node(evapInPres_S2L1F1, "evapInPres_S2L1F1")
        await bridge.add_node(compInTemp_S2L1F1, "compInTemp_S2L1F1")
        await bridge.add_node(evapOutPres_S2L1F1, "evapOutPres_S2L1F1")
        await bridge.add_node(evapOutTemp_S2L1F1, "evapOutTemp_S2L1F1")
        await bridge.add_node(tempC1_S2L1F1, "tempC1_S2L1F1")
        await bridge.add_node(tempC2_S2L1F1, "tempC2_S2L1F1")
        await bridge.add_node(tempC3_S2L1F1, "tempC3_S2L1F1")
        
        # Start the bridge
        await bridge.start()

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await bridge.stop()

if __name__ == "__main__":
    asyncio.run(main())