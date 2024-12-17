from fastapi import FastAPI, HTTPException
from asyncua import Client, Node
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import uvicorn
from pydantic import BaseModel
import logging
import re

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for the response
class OPCValue(BaseModel):
    node_id: str
    value: Any
    timestamp: datetime
    quality: str

class OPCNodeInfo(BaseModel):
    node_id: str
    browse_name: str
    description: Optional[str] = None

class OPCConnection:
    def __init__(self, url: str):
        self.url = url
        self.client = None

    async def connect(self):
        if not self.client:
            self.client = Client(url=self.url)
            await self.client.connect()
            logger.info(f"Connected to OPC UA server: {self.url}")

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()
            self.client = None
            logger.info("Disconnected from OPC UA server")

    async def get_node(self, node_id: str) -> Node:
        if not self.client:
            await self.connect()
        return self.client.get_node(node_id)

    async def get_objects_node(self):
        if not self.client:
            await self.connect()
        return await self.client.get_objects_node()

# Global connection instance
opc_connection = OPCConnection("opc.tcp://localhost:3005")

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await opc_connection.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await opc_connection.disconnect()

async def read_node_value(node: Node) -> Dict:
    """Reads the value of an OPC UA node"""
    try:
        value = await node.read_value()
        dv = await node.read_data_value()
        browse_name = await node.read_browse_name()
        
        return {
            "browse_name": browse_name.Name,
            "node_id": node.nodeid.to_string(),
            "value": value,
            "timestamp": dv.SourceTimestamp or datetime.now(),
            # "quality": str(dv.StatusCode)
        }
    except Exception as e:
        logger.error(f"Error reading node {node.nodeid}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get supermarkets, return a list of supermarket names
@app.get("/api/supermarkets")
async def get_supermarkets():
    try:
        # Log all'inizio della funzione per vedere se viene eseguita
        logger.info("Fetching supermarkets...")

        # Recupera il nodo "Objects"
        objects = await opc_connection.client.nodes.root.get_child("0:Objects")
        namespace = "http://examples.factory.github.io"
        nsidx = await opc_connection.client.get_namespace_index(namespace)

        # Ottieni i figli del nodo "Objects" (Supermercati)
        supermarkets = await objects.get_children()

        # Logga i nodi trovati
        logger.info(f"Found nodes: {supermarkets}")

        # Compila l'espressione regolare
        supermarket_pattern = re.compile(r"^Supermarket\d+$")
        identified_supermarkets = {}

        # Cicla attraverso i nodi trovati
        for supermarket in supermarkets:
            browse_name = await supermarket.read_browse_name()  # Ottieni il browse_name del nodo
            logger.info(f"Node ID: {supermarket.nodeid}, Browse Name: {browse_name}")

            # Confronta il browse_name con l'espressione regolare
            if supermarket_pattern.match(browse_name.Name):
                logger.info(f"Identified supermarket: {browse_name.Name}")
                identified_supermarkets[browse_name.Name] = browse_name.Name

        # Se non sono stati trovati supermercati, restituisci un messaggio vuoto
        if not identified_supermarkets:
            logger.warning("No supermarkets identified")

        # Restituisce i supermercati trovati
        return identified_supermarkets

    except Exception as e:
        logger.error(f"Error retrieving supermarkets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get locations for a specific supermarket
@app.get("/api/supermarkets/locations/{supermarket_id}")
async def get_supermarket_locations(supermarket_id: str):
    try:
        # Log all'inizio della funzione per vedere se viene eseguita
        logger.info("Fetching locations...")

        # Recupera il nodo "Objects"
        objects = await opc_connection.client.nodes.root.get_child("0:Objects")
        namespace = "http://examples.factory.github.io"
        nsidx = await opc_connection.client.get_namespace_index(namespace)
        supermarket = await objects.get_child(f"{nsidx}:{supermarket_id}")

        # Ottieni i figli del nodo "Objects" (Supermercati)
        locations = await supermarket.get_children()

        # Logga i nodi trovati
        logger.info(f"Found nodes: {locations}")

        # Compila l'espressione regolare
        location_pattern = re.compile(r"^Location\d+$")
        identified_locations = {}

        # Cicla attraverso i nodi trovati
        for location in locations:
            browse_name = await location.read_browse_name()  # Ottieni il browse_name del nodo
            logger.info(f"Node ID: {location.nodeid}, Browse Name: {browse_name}")

            # Confronta il browse_name con l'espressione regolare
            if location_pattern.match(browse_name.Name):
                logger.info(f"Identified location: {browse_name.Name}")
                identified_locations[browse_name.Name] = browse_name.Name

        # Se non sono stati trovati supermercati, restituisci un messaggio vuoto
        if not identified_locations:
            logger.warning("No locations identified")

        # Restituisce i supermercati trovati
        return identified_locations
    
    except Exception as e:
        logger.error(f"Error retrieving locations for {supermarket_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get fridges for a specific location within a supermarket
@app.get("/api/supermarkets/locations/{supermarket_id}/fridges/{location_id}")
async def get_supermarket_fridges(supermarket_id: str, location_id: str):
    try:
        # Log all'inizio della funzione per vedere se viene eseguita
        logger.info("Fetching locations...")

        # Recupera il nodo "Objects"
        objects = await opc_connection.client.nodes.root.get_child("0:Objects")
        namespace = "http://examples.factory.github.io"
        nsidx = await opc_connection.client.get_namespace_index(namespace)
        supermarket = await objects.get_child(f"{nsidx}:{supermarket_id}")
        location = await supermarket.get_child(f"{nsidx}:{location_id}")

        # Ottieni i figli del nodo "Objects" (Supermercati)
        fridges = await location.get_children()

        # Logga i nodi trovati
        logger.info(f"Found nodes: {fridges}")

        # Compila l'espressione regolare
        fridge_pattern = re.compile(r"^Fridge\d+$")
        identified_fridges = {}

        # Cicla attraverso i nodi trovati
        for fridge in fridges:
            browse_name = await fridge.read_browse_name()  # Ottieni il browse_name del nodo
            logger.info(f"Node ID: {fridge.nodeid}, Browse Name: {browse_name}")

            # Confronta il browse_name con l'espressione regolare
            if fridge_pattern.match(browse_name.Name):
                logger.info(f"Identified fridge: {browse_name.Name}")
                identified_fridges[browse_name.Name] = browse_name.Name

        # Se non sono stati trovati supermercati, restituisci un messaggio vuoto
        if not identified_fridges:
            logger.warning("No fridges identified")

        # Restituisce i supermercati trovati
        return identified_fridges
    
    except Exception as e:
        logger.error(f"Error retrieving fridges for {location_id} in {supermarket_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get data for a specific fridge
@app.get("/api/supermarkets/locations/{supermarket_id}/fridges/{location_id}/{fridge_id}")
async def get_fridge_data(supermarket_id: str, location_id: str, fridge_id: str):
    try:
        objects = await opc_connection.client.nodes.root.get_child("0:Objects")
        namespace = "http://examples.factory.github.io"
        nsidx = await opc_connection.client.get_namespace_index(namespace)

        # Fetch fridge node and its data
        supermarket = await objects.get_child(f"{nsidx}:{supermarket_id}")
        location = await supermarket.get_child(f"{nsidx}:{location_id}")
        fridge = await location.get_child(f"{nsidx}:{fridge_id}")
        variables = await fridge.get_children()

        data = {}

        for variable in variables:
            try:
                value_data = await read_node_value(variable)
                data[variable.nodeid.to_string()] = value_data
            except Exception as e:
                logger.error(f"Error reading node {variable.nodeid}: {e}")
                continue

        return data

    except Exception as e:
        logger.error(f"Error retrieving data for fridge {fridge_id} in {location_id}, {supermarket_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "middleware_chrome:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
