import networkx as nx
import random
import math
import operator
import networkx.algorithms.approximation
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
    # dictionary to store the total number of "YES" for each vertex
    Yes_count = {}
    # store all vertices that contain a bot
    Yes_label = []
    # store all vertices that don't contain a bot
    No_label = []

    for ver in non_home:
        Yes_count[ver] = sum(client.scout(ver, all_students).values())

    sorted_count = sorted(Yes_count.items(), key=operator.itemgetter(1), reverse=True)

    # find the vertex which has the largest number of "YES"
    for tuple in sorted_count:
        if tuple[0] not in Yes_label and tuple[0] not in No_label:
            ver_num = tuple[0]
            # generate a list sorted by neighbouring edge weights
            # pop up the shortest weight
            # if this edge is connected with a node that is very likely to contain a bot, (probability >= ?)
            # choose the second shortest edge
            neighbour_edges = {}
            for nbr in client.G[ver_num]:
                if len(Yes_label) + len(No_label) == 99 or (nbr not in Yes_label and nbr not in No_label):
                    assert nbr != ver_num
                    neighbour_edges[nbr] = client.G[ver_num][nbr]['weight']
            sorted_edges = sorted(neighbour_edges.items(), key=operator.itemgetter(1))
            nearest_neighbour = sorted_edges[0][0]
            assert ver_num != nearest_neighbour
            known_bot = client.remote(ver_num, nearest_neighbour)
            No_label.append(ver_num)
            if known_bot != 0:
                if nearest_neighbour not in Yes_label:
                    Yes_label.append(nearest_neighbour)
                if nearest_neighbour in No_label:
                    No_label.remove(nearest_neighbour)

        if len(Yes_label) == client.bots or (len(Yes_label) + len(No_label) == 100):
            break
    # sanity check：the length of Yes_label should be less equal than 5 instead of 5
    # because bots may occur in the same vertex when we do locating
    if client.home not in Yes_label:
        No_label.append(client.home)
    assert len(Yes_label) == 5 or (len(Yes_label) + len(No_label) == 100)

    Tree_endpoint = [ele for ele in Yes_label]
    if client.home not in Tree_endpoint:
        Tree_endpoint.append(client.home)

    # Step1: locate all bots by labeling the graph (done)
    # Step2: Once we precisely locate all bots on the graph, we can remote them in a fashion that has the minimum cost

    # First, generate 5(or less) shortest paths and store them as values in the dictionary
    # The key is the name of vertex(an integer)

    appro_tree = nx.algorithms.approximation.steinertree.steiner_tree(client.G, Tree_endpoint, weight='weight')
    assert appro_tree.has_node(client.home)
    print(appro_tree.nodes())
    print(appro_tree.edges())
    assert appro_tree.__len__() == len(Tree_endpoint)
    assert appro_tree.size() == len(Tree_endpoint) - 1
    for ele in Tree_endpoint:
        assert appro_tree.has_node(ele)
    print(list(nx.edge_dfs(appro_tree, client.home)))
    post_order_edges = list(nx.edge_dfs(appro_tree, client.home))
    post_order_edges.reverse()
    post_order_edges = [(b, a) for (a, b) in post_order_edges]
    print(post_order_edges)
    for (start, end) in post_order_edges:
        shortest_path = nx.shortest_path(client.G, start, end, weight='weight')
        i = 0
        while i < len(shortest_path) - 1:
            client.remote(shortest_path[i], shortest_path[i + 1])
            i = i + 1




    M = nx.algorithms.approximation.steinertree.metric_closure(client.G)
    H = M.subgraph(Tree_endpoint)
    #print(H.nodes())
    #print(H.edges())
    mst = nx.minimum_spanning_tree(H, weight='distance')
    #print(mst.nodes())
    #print(mst.edges())
    #T = client.G.edge_subgraph(mst_edges)

    #print(T.nodes())
    #print(T.edges())










    #client.scout(random.choice(non_home), all_students)

    #for _ in range(100):
    #    u, v = random.choice(list(client.G.edges()))
    #    client.remote(u, v)

    client.end()
    pass
