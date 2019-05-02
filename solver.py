import networkx as nx
import random
import math
# Put your solution here.

# client.time: An integer value; the amount of time elapsed thus far.

# client.cant_scout: A list of sets, 1 - indexed by student number.
# Each set stores the vertices that the student cannot scout.

# client.bot_count: A list of integers, 1 - indexed by vertex number.
# Each entry represents the number of known bots at that vertex.

# client.bot_locations: A list of integers representing the vertices that the known bots are on.
# Contains one value for each known bot.

def solve(client):
    client.end()
    client.start()

    all_students = list(range(1, client.students + 1))
    non_home = list(range(1, client.home)) + list(range(client.home + 1, client.v + 1))
    stu_opinion = [client.scout(ele, non_home) for ele in all_students]
    Yes_count = {}

    # store all vertices that contain a bot
    Yes_label = []
    # store all vertices that don't contain a bot
    No_label = []

    for ver in non_home:
        counter = 0
        for stu in all_students:
            counter += stu_opinion[stu[ver]]
        Yes_count[ver] = counter
    sorted_count = sorted((key, value) for (key, value) in Yes_count.items())
    # find the vertex which has most "YES"s

    for tuple in sorted_count:
        if tuple[0] not in Yes_label and tuple[0] not in No_label:
            ver_num = tuple[0]
            # generate a list sorted by neighbouring edge weights
            # pop up the shortest weight
            # if this edge is connected with a node that is very likely to contain a bot, (probability >= ?)
            # choose the second shortest edge
            neighbour_edges = {}
            for nbr in client.G[ver_num]:
                if nbr not in Yes_label and nbr not in No_label:
                    neighbour_edges[ver_num] = client.G[ver_num][nbr]['weight']
            sorted_edges = sorted((key, value) for (key, value) in neighbour_edges.items())
            nearest_neighbour = sorted_edges[0][0]
            known_bot = client.remote(ver_num, nearest_neighbour)
            if known_bot == 0:
                No_label.append(ver_num)
            else:
                No_label.append(ver_num)
                Yes_label.append(nearest_neighbour)
        if len(Yes_count) == client.bots:
            break
    








    # Step1: locate all bots by labeling the graph
    # We can create 2 arrays Y_loc and N_loc (empty initially)
    # Step2: Once we precisely locate all bots on the graph, we can remote them in a fashion that has the minimum cost





    client.scout(random.choice(non_home), all_students)

    for _ in range(100):
        u, v = random.choice(list(client.G.edges()))
        client.remote(u, v)

    client.end()
    pass
