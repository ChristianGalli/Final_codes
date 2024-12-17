from asyncua import Client
import pandas as pd
import logging
import asyncio

_logger = logging.getLogger(__name__)

# define a function to loop the value list

async def thread_function(values, var_server):
    while True:  # It loops infinitely
        try: # With try we can use a single code for any kind of node value
            value = float(values.pop(0)) # pop allow us to extract the element of the list in position 0 (in our case)
        except:
            value = str(values.pop(0))

        await var_server.write_value(value)
        _logger.info(f"Value {var_server}: {value}")
        values.append(value) # place the value at the end



# define function to extract from excel file

def excel_to_list(Controller, start_row=0):
    filename = "./Dataset.csv"  # ./ indica che il file è nella stessa directory del codice
    try:
        workbook = pd.read_excel(filename)
    except:
        workbook = pd.read_csv(filename)

    # Estrai i valori a partire dalla riga indicata
    compOutPres = workbook.iloc[start_row:, 0].values.tolist()
    compOutTemp = workbook.iloc[start_row:, 1].values.tolist()
    condInPres = workbook.iloc[start_row:, 2].values.tolist()
    condInTemp = workbook.iloc[start_row:, 3].values.tolist()
    condOutPres = workbook.iloc[start_row:, 4].values.tolist()
    condOutTemp = workbook.iloc[start_row:, 5].values.tolist()
    evapInPres = workbook.iloc[start_row:, 6].values.tolist()
    compInTemp = workbook.iloc[start_row:, 7].values.tolist()
    evapOutPres = workbook.iloc[start_row:, 8].values.tolist()
    evapOutTemp = workbook.iloc[start_row:, 9].values.tolist()
    tempC1 = workbook.iloc[start_row:, 10].values.tolist()
    tempC2 = workbook.iloc[start_row:, 11].values.tolist()
    tempC3 = workbook.iloc[start_row:, 12].values.tolist()

    # Crea e restituisci l'oggetto Controller
    controller = Controller(
        compOutPres, compOutTemp, condInPres, condInTemp,
        condOutPres, condOutTemp, evapInPres, compInTemp,
        evapOutPres, evapOutTemp, tempC1, tempC2, tempC3
    )

    return controller
 

url="opc.tcp://localhost:3005/"
namespace="http://examples.factory.github.io"

async def main():
    print(f"Connecting to {url} ...")
    async with Client(url=url) as client: #instantiation of client class 
        nsidx = await client.get_namespace_index(namespace) # we want to find the namespace index
        print(f"Namespace Index for '{namespace}': {nsidx}")
        print(await client.nodes.root.get_children()) # It prints outr the nodes inside the server

        # Classe Controller
        class Controller:
            def __init__(self, compOutPres, compOutTemp, condInPres, condInTemp,
                         condOutPres, condOutTemp, evapInPres, compInTemp,
                         evapOutPres, evapOutTemp, tempC1, tempC2, tempC3):
                self.compOutPres = compOutPres
                self.compOutTemp = compOutTemp
                self.condInPres = condInPres
                self.condInTemp = condInTemp
                self.condOutPres = condOutPres
                self.condOutTemp = condOutTemp
                self.evapInPres = evapInPres
                self.compInTemp = compInTemp
                self.evapOutPres = evapOutPres
                self.evapOutTemp = evapOutTemp
                self.tempC1 = tempC1
                self.tempC2 = tempC2
                self.tempC3 = tempC3

        # Controller per il primo frigorifero (riga iniziale 0)
        controller_S1L1F1 = excel_to_list(Controller, start_row=0)
        # Controller per il secondo frigorifero (riga iniziale 100)
        controller_S1L1F2 = excel_to_list(Controller, start_row=100)

        controller_S1L2F1 = excel_to_list(Controller, start_row=200)

        controller_S2L1F1 = excel_to_list(Controller, start_row=300)

        # Nodi del primo frigorifero
        object = await client.nodes.root.get_child("0:Objects")

        # Supermarket 1

        supermarket1 = await object.get_child(f"{nsidx}:Supermarket1")

        # Location 1

        location1 = await supermarket1.get_child(f"{nsidx}:Location1")
        
        #Nodi fridge 1

        fridge1 = await location1.get_child(f"{nsidx}:Fridge1")

        compOutPres_S1L1F1 = await fridge1.get_child(f"{nsidx}:compOutPres")
        compOutTemp_S1L1F1 = await fridge1.get_child(f"{nsidx}:compOutTemp")
        condInPres_S1L1F1 = await fridge1.get_child(f"{nsidx}:condInPres")
        condInTemp_S1L1F1 = await fridge1.get_child(f"{nsidx}:condInTemp")
        condOutPres_S1L1F1 = await fridge1.get_child(f"{nsidx}:condOutPres")
        condOutTemp_S1L1F1 = await fridge1.get_child(f"{nsidx}:condOutTemp")
        evapInPres_S1L1F1 = await fridge1.get_child(f"{nsidx}:evapInPres")
        compInTemp_S1L1F1 = await fridge1.get_child(f"{nsidx}:compInTemp")
        evapOutPres_S1L1F1 = await fridge1.get_child(f"{nsidx}:evapOutPres")
        evapOutTemp_S1L1F1 = await fridge1.get_child(f"{nsidx}:evapOutTemp")
        tempC1_S1L1F1 = await fridge1.get_child(f"{nsidx}:tempC1")
        tempC2_S1L1F1 = await fridge1.get_child(f"{nsidx}:tempC2")
        tempC3_S1L1F1 = await fridge1.get_child(f"{nsidx}:tempC3")

        #Nodi fridge 2 

        fridge2 = await location1.get_child(f"{nsidx}:Fridge2")

        compOutPres_S1L1F2 = await fridge2.get_child(f"{nsidx}:compOutPres")
        compOutTemp_S1L1F2 = await fridge2.get_child(f"{nsidx}:compOutTemp")
        condInPres_S1L1F2 = await fridge2.get_child(f"{nsidx}:condInPres")
        condInTemp_S1L1F2 = await fridge2.get_child(f"{nsidx}:condInTemp")
        condOutPres_S1L1F2 = await fridge2.get_child(f"{nsidx}:condOutPres")
        condOutTemp_S1L1F2 = await fridge2.get_child(f"{nsidx}:condOutTemp")
        evapInPres_S1L1F2 = await fridge2.get_child(f"{nsidx}:evapInPres")
        compInTemp_S1L1F2 = await fridge2.get_child(f"{nsidx}:compInTemp")
        evapOutPres_S1L1F2 = await fridge2.get_child(f"{nsidx}:evapOutPres")
        evapOutTemp_S1L1F2 = await fridge2.get_child(f"{nsidx}:evapOutTemp")
        tempC1_S1L1F2 = await fridge2.get_child(f"{nsidx}:tempC1")
        tempC2_S1L1F2 = await fridge2.get_child(f"{nsidx}:tempC2")
        tempC3_S1L1F2 = await fridge2.get_child(f"{nsidx}:tempC3")

        # Location 2

        location2 = await supermarket1.get_child(f"{nsidx}:Location2")
        
        #Nodi fridge 1

        fridge1_2 = await location2.get_child(f"{nsidx}:Fridge1")

        compOutPres_S1L2F1 = await fridge1_2.get_child(f"{nsidx}:compOutPres")
        compOutTemp_S1L2F1 = await fridge1_2.get_child(f"{nsidx}:compOutTemp")
        condInPres_S1L2F1 = await fridge1_2.get_child(f"{nsidx}:condInPres")
        condInTemp_S1L2F1 = await fridge1_2.get_child(f"{nsidx}:condInTemp")
        condOutPres_S1L2F1 = await fridge1_2.get_child(f"{nsidx}:condOutPres")
        condOutTemp_S1L2F1 = await fridge1_2.get_child(f"{nsidx}:condOutTemp")
        evapInPres_S1L2F1 = await fridge1_2.get_child(f"{nsidx}:evapInPres")
        compInTemp_S1L2F1 = await fridge1_2.get_child(f"{nsidx}:compInTemp")
        evapOutPres_S1L2F1 = await fridge1_2.get_child(f"{nsidx}:evapOutPres")
        evapOutTemp_S1L2F1 = await fridge1_2.get_child(f"{nsidx}:evapOutTemp")
        tempC1_S1L2F1 = await fridge1_2.get_child(f"{nsidx}:tempC1")
        tempC2_S1L2F1 = await fridge1_2.get_child(f"{nsidx}:tempC2")
        tempC3_S1L2F1 = await fridge1_2.get_child(f"{nsidx}:tempC3")

        # Supermarket 2

        supermarket2 = await object.get_child(f"{nsidx}:Supermarket2")

        # Location 1

        location1_2 = await supermarket2.get_child(f"{nsidx}:Location1")
        
        #Nodi fridge 1

        fridge1_22 = await location1_2.get_child(f"{nsidx}:Fridge1")

        compOutPres_S2L1F1 = await fridge1_22.get_child(f"{nsidx}:compOutPres")
        compOutTemp_S2L1F1 = await fridge1_22.get_child(f"{nsidx}:compOutTemp")
        condInPres_S2L1F1 = await fridge1_22.get_child(f"{nsidx}:condInPres")
        condInTemp_S2L1F1 = await fridge1_22.get_child(f"{nsidx}:condInTemp")
        condOutPres_S2L1F1 = await fridge1_22.get_child(f"{nsidx}:condOutPres")
        condOutTemp_S2L1F1 = await fridge1_22.get_child(f"{nsidx}:condOutTemp")
        evapInPres_S2L1F1 = await fridge1_22.get_child(f"{nsidx}:evapInPres")
        compInTemp_S2L1F1 = await fridge1_22.get_child(f"{nsidx}:compInTemp")
        evapOutPres_S2L1F1 = await fridge1_22.get_child(f"{nsidx}:evapOutPres")
        evapOutTemp_S2L1F1 = await fridge1_22.get_child(f"{nsidx}:evapOutTemp")
        tempC1_S2L1F1 = await fridge1_22.get_child(f"{nsidx}:tempC1")
        tempC2_S2L1F1 = await fridge1_22.get_child(f"{nsidx}:tempC2")
        tempC3_S2L1F1 = await fridge1_22.get_child(f"{nsidx}:tempC3")

        # Task per il primo frigorifero
        tasks = [
            asyncio.ensure_future(thread_function(controller_S1L1F1.compOutPres,compOutPres_S1L1F1)),
            asyncio.ensure_future(thread_function(controller_S1L1F1.compOutTemp,compOutTemp_S1L1F1)),
            asyncio.ensure_future(thread_function(controller_S1L1F1.condInPres,condInPres_S1L1F1)),
            asyncio.ensure_future(thread_function(controller_S1L1F1.condInTemp,condInTemp_S1L1F1)),
            asyncio.ensure_future(thread_function(controller_S1L1F1.condOutPres,condOutPres_S1L1F1)),
            asyncio.ensure_future(thread_function(controller_S1L1F1.condOutTemp,condOutTemp_S1L1F1)),
            asyncio.ensure_future(thread_function(controller_S1L1F1.evapInPres,evapInPres_S1L1F1)),
            asyncio.ensure_future(thread_function(controller_S1L1F1.compInTemp,compInTemp_S1L1F1)),
            asyncio.ensure_future(thread_function(controller_S1L1F1.evapOutPres,evapOutPres_S1L1F1)),
            asyncio.ensure_future(thread_function(controller_S1L1F1.evapOutTemp,evapOutTemp_S1L1F1)), 
            asyncio.ensure_future(thread_function(controller_S1L1F1.tempC1,tempC1_S1L1F1)),
            asyncio.ensure_future(thread_function(controller_S1L1F1.tempC2,tempC2_S1L1F1)),
            asyncio.ensure_future(thread_function(controller_S1L1F1.tempC3,tempC3_S1L1F1)),
        ]
             
        # Task per il secondo frigorifero
        tasks += [
            asyncio.ensure_future(thread_function(controller_S1L1F2.compOutPres,compOutPres_S1L1F2)),
            asyncio.ensure_future(thread_function(controller_S1L1F2.compOutTemp,compOutTemp_S1L1F2)),
            asyncio.ensure_future(thread_function(controller_S1L1F2.condInPres,condInPres_S1L1F2)),
            asyncio.ensure_future(thread_function(controller_S1L1F2.condInTemp,condInTemp_S1L1F2)),
            asyncio.ensure_future(thread_function(controller_S1L1F2.condOutPres,condOutPres_S1L1F2)),
            asyncio.ensure_future(thread_function(controller_S1L1F2.condOutTemp,condOutTemp_S1L1F2)),
            asyncio.ensure_future(thread_function(controller_S1L1F2.evapInPres,evapInPres_S1L1F2)),
            asyncio.ensure_future(thread_function(controller_S1L1F2.compInTemp,compInTemp_S1L1F2)),
            asyncio.ensure_future(thread_function(controller_S1L1F2.evapOutPres,evapOutPres_S1L1F2)),
            asyncio.ensure_future(thread_function(controller_S1L1F2.evapOutTemp,evapOutTemp_S1L1F2)), 
            asyncio.ensure_future(thread_function(controller_S1L1F2.tempC1,tempC1_S1L1F2)),
            asyncio.ensure_future(thread_function(controller_S1L1F2.tempC2,tempC2_S1L1F2)),
            asyncio.ensure_future(thread_function(controller_S1L1F2.tempC3,tempC3_S1L1F2)),
        ]

        tasks += [
            asyncio.ensure_future(thread_function(controller_S1L2F1.compOutPres,compOutPres_S1L2F1)),
            asyncio.ensure_future(thread_function(controller_S1L2F1.compOutTemp,compOutTemp_S1L2F1)),
            asyncio.ensure_future(thread_function(controller_S1L2F1.condInPres,condInPres_S1L2F1)),
            asyncio.ensure_future(thread_function(controller_S1L2F1.condInTemp,condInTemp_S1L2F1)),
            asyncio.ensure_future(thread_function(controller_S1L2F1.condOutPres,condOutPres_S1L2F1)),
            asyncio.ensure_future(thread_function(controller_S1L2F1.condOutTemp,condOutTemp_S1L2F1)),
            asyncio.ensure_future(thread_function(controller_S1L2F1.evapInPres,evapInPres_S1L2F1)),
            asyncio.ensure_future(thread_function(controller_S1L2F1.compInTemp,compInTemp_S1L2F1)),
            asyncio.ensure_future(thread_function(controller_S1L2F1.evapOutPres,evapOutPres_S1L2F1)),
            asyncio.ensure_future(thread_function(controller_S1L2F1.evapOutTemp,evapOutTemp_S1L2F1)), 
            asyncio.ensure_future(thread_function(controller_S1L2F1.tempC1,tempC1_S1L2F1)),
            asyncio.ensure_future(thread_function(controller_S1L2F1.tempC2,tempC2_S1L2F1)),
            asyncio.ensure_future(thread_function(controller_S1L2F1.tempC3,tempC3_S1L2F1)),
        ]

        tasks += [
            asyncio.ensure_future(thread_function(controller_S2L1F1.compOutPres,compOutPres_S2L1F1)),
            asyncio.ensure_future(thread_function(controller_S2L1F1.compOutTemp,compOutTemp_S2L1F1)),
            asyncio.ensure_future(thread_function(controller_S2L1F1.condInPres,condInPres_S2L1F1)),
            asyncio.ensure_future(thread_function(controller_S2L1F1.condInTemp,condInTemp_S2L1F1)),
            asyncio.ensure_future(thread_function(controller_S2L1F1.condOutPres,condOutPres_S2L1F1)),
            asyncio.ensure_future(thread_function(controller_S2L1F1.condOutTemp,condOutTemp_S2L1F1)),
            asyncio.ensure_future(thread_function(controller_S2L1F1.evapInPres,evapInPres_S2L1F1)),
            asyncio.ensure_future(thread_function(controller_S2L1F1.compInTemp,compInTemp_S2L1F1)),
            asyncio.ensure_future(thread_function(controller_S2L1F1.evapOutPres,evapOutPres_S2L1F1)),
            asyncio.ensure_future(thread_function(controller_S2L1F1.evapOutTemp,evapOutTemp_S2L1F1)), 
            asyncio.ensure_future(thread_function(controller_S2L1F1.tempC1,tempC1_S2L1F1)),
            asyncio.ensure_future(thread_function(controller_S2L1F1.tempC2,tempC2_S2L1F1)),
            asyncio.ensure_future(thread_function(controller_S2L1F1.tempC3,tempC3_S2L1F1)),
        ]
        

        # Esecuzione parallela dei task
        await asyncio.gather(*tasks)

# Esecuzione del codice
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())


