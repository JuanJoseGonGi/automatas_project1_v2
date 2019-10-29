from transitions_gui import WebMachine as Machine
import networkx as nx
import itertools
import time


class App:
    def __init__(self, data):
        self.characters = data["characters"]
        self.initial_state = "".join(sorted(data["initial_state"]))
        self.boat = data["boat"]
        self.boat["position"] = "left"
        self.restricted_states = data["restricted_states"]

        for index, restricted_state in enumerate(self.restricted_states):
            self.restricted_states[index] = "".join(sorted(restricted_state))

        self.states = []
        self.transitions = []
        self.goal_state = "|" + "".join(sorted(self.characters))
        self.graph = nx.MultiDiGraph()
        self.paths = []

    def isBoatLeft(self):
        return self.boat["position"] == "left"

    def isBoatRight(self):
        return self.boat["position"] == "right"

    def changeBoatPosition(self):
        if self.boat["position"] == "left":
            self.boat["position"] = "right"
            return

        self.boat["position"] = "left"

    def setAllPossibleStates(self):
        for index in range(len(self.characters) + 1):
            combinations = itertools.combinations(self.characters, index)
            for combination in combinations:
                right = "".join(sorted(combination))
                left = self.characters.copy()

                for character in right:
                    left.remove(character)

                left = "".join(sorted(left))

                if left in self.restricted_states or right in self.restricted_states:
                    continue

                self.states.append(left + "|" + right)

    def setAllTransitions(self):
        for i in range(self.boat["capacity"]):
            for state in self.states:
                left, right = state.split("|")

                toRightTravelers = itertools.combinations(left, i + 1)
                for traveler in toRightTravelers:
                    drivers = set(traveler).intersection(self.boat["drivers"])

                    if len(drivers) == 0:
                        continue

                    travelerStr = "".join(traveler)

                    if travelerStr in self.boat["restricted_boat_states"]:
                        continue

                    transitionLeft = list(left)
                    transitionRight = "".join(sorted(right + travelerStr))

                    for character in travelerStr:
                        transitionLeft.remove(character)

                    transitionLeft = "".join(sorted(transitionLeft))

                    if (
                        transitionLeft in self.restricted_states
                        or transitionRight in self.restricted_states
                    ):
                        continue

                    if len(transitionLeft + transitionRight) != len(self.characters):
                        print(state, transitionLeft, transitionRight, travelerStr, "L")
                        exit(0)

                    newTransition = ",".join(
                        [state, "isBoatLeft", transitionLeft + "|" + transitionRight]
                    )

                    if newTransition not in self.transitions:
                        self.transitions.append(newTransition)

                toLeftTravelers = itertools.combinations(right, i + 1)
                for traveler in toLeftTravelers:
                    drivers = set(traveler).intersection(self.boat["drivers"])

                    if len(drivers) == 0:
                        continue

                    travelerStr = "".join(traveler)

                    if travelerStr in self.boat["restricted_boat_states"]:
                        continue

                    transitionLeft = "".join(sorted(left + travelerStr))
                    transitionRight = list(right)

                    for character in travelerStr:
                        transitionRight.remove(character)

                    transitionRight = "".join(sorted(transitionRight))

                    if (
                        transitionLeft in self.restricted_states
                        or transitionRight in self.restricted_states
                    ):
                        continue

                    if len(transitionLeft + transitionRight) != len(self.characters):
                        print(state, transitionLeft, transitionRight)
                        exit(0)

                    newTransition = ",".join(
                        [state, "isBoatRight", transitionLeft + "|" + transitionRight]
                    )

                    if newTransition not in self.transitions:
                        self.transitions.append(newTransition)

    def addTransitionsToMachine(self):
        for transition in self.transitions:
            source, condition, dest = transition.split(",", 2)

            self.machine.add_transition(
                trigger=source + "to" + dest,
                source=source,
                dest=dest,
                conditions=condition,
                after="changeBoatPosition",
            )

    def createMachine(self):
        self.machine = Machine(
            model=self,
            states=self.states,
            initial=self.initial_state,
            name="River crossing",
            ignore_invalid_triggers=True,
        )

    def setPaths(self):
        paths = list(
            nx.algorithms.all_simple_paths(
                self.graph, self.initial_state, self.goal_state
            )
        )

        pathsToDelete = []

        for path in paths:
            boatCondition = "isBoatLeft"
            isToDelete = False

            for index, state in enumerate(path):
                if index + 2 >= len(path):
                    break

                for transition in self.transitions:
                    source, condition, dest = transition.split(",")

                    if (
                        source == state
                        and dest == path[index + 1]
                        and boatCondition == condition
                    ):
                        self.paths.append(path)

                    if boatCondition == "isBoatLeft":
                        boatCondition = "isBoatRight"
                    else:
                        boatCondition = "isBoatLeft"

    def drawStatesLabels(self):
        for state in self.states:
            nx.draw_networkx_labels(self.graph, self.pos, {state: state})

    def drawLabels(self):
        self.drawStatesLabels()

    def drawTransitions(self):
        for transition in self.transitions:
            source, condition, dest = transition.split(",")

            nx.draw_networkx_edges(self.graph, self.pos, [(source, dest)])

    def drawStates(self):
        for state in self.states:
            if state == self.initial_state:
                nx.draw_networkx_nodes(
                    self.graph, self.pos, [state], node_color="g", label=state
                )
                continue

            if state == self.goal_state:
                nx.draw_networkx_nodes(
                    self.graph,
                    self.pos,
                    [state],
                    node_color="w",
                    edgecolors="b",
                    label=state,
                )
                continue

            nx.draw_networkx_nodes(self.graph, self.pos, [state], label=state)

    def fillGraph(self):
        for transition in self.transitions:
            source, condition, dest = transition.split(",")
            self.graph.add_edges_from([(source, dest)], label=source + " to " + dest)

    def draw(self):
        self.pos = nx.spring_layout(self.graph)

        self.drawTransitions()
        self.drawStates()
        self.drawLabels()

    def animatePaths(self, frame):
        for path in self.paths:
            for state in path:
                # self.drawStates()
                nx.draw_networkx_nodes(self.graph, self.pos, [state], node_color="w")

