from app import App
import json
import time

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import networkx as nx

# with open("lob_cab_col_gran_input.json") as json_file:
with open("canib_misio_input.json") as json_file:
    data = json.load(json_file)

app = App(data)

app.setAllPossibleStates()
app.setAllTransitions()
app.fillGraph()
app.setPaths()

app.draw()

mng = plt.get_current_fig_manager()
mng.window.maximize()

animation = FuncAnimation(
    plt.gcf(), app.animatePaths, frames=len(app.states), interval=2000
)

plt.tight_layout()
plt.show()

# app.createMachine()
# app.addTransitionsToMachine()
