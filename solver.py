import networkx as nx
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
    # dictionary to store the students as values, who predict yes on some vertex
    Yes_found = {}
    # student's count(weight), decrease when they make wrong predictions
    Stu_weight = [1.00 for _ in range(client.students)]

    for ver in non_home:
        mydict = client.scout(ver, all_students)
        Yes_found[ver] = [stu for (stu, pred) in mydict.items() if pred]
        Yes_count[ver] = sum([Stu_weight[stu - 1] for stu in Yes_found.get(ver)])
        assert Yes_count.get(ver) <= client.students
    sorted_count = sorted(Yes_count.items(), key=operator.itemgetter(1), reverse=True)
    # print(sorted_count)
    ranking = [place for (place, votes) in sorted_count]

    # find the vertex which has the largest number of "YES"
    while len(Yes_label) + len(No_label) < 99:
        # print(len(Yes_label))
        # print(len(No_label))
        myiter = iter(sorted_count)
        next_tuple = next(myiter)
        while next_tuple and next_tuple[0] in Yes_label or next_tuple[0] in No_label:
            next_tuple = next(myiter)

        if next_tuple[0] not in Yes_label and next_tuple[0] not in No_label:
            ver_num = next_tuple[0]
            # generate a list sorted by neighbouring edge weights
            # pop up the shortest weight
            # if this edge is connected with a node that is very likely to contain a bot, (probability >= ?)
            # choose the second shortest edge
            neighbour_edges = {}
            for nbr in client.G[ver_num]:
                if len(Yes_label) + len(No_label) == 99 or (nbr not in Yes_label and nbr not in No_label):
                    assert nbr != ver_num
                    # only consider neighbours with low prob of containing a bot
                    # print(Yes_count.get(nbr))
                    # avoid remoting to a node with high ranking
                    if nbr != client.h and ranking.index(nbr) < client.students/1.8:
                        continue
                    neighbour_edges[nbr] = client.G[ver_num][nbr]['weight']
            sorted_edges = sorted(neighbour_edges.items(), key=operator.itemgetter(1))
            # print(sorted_edges)
            nearest_neighbour = sorted_edges[0][0]
            assert ver_num != nearest_neighbour
            known_bot = client.remote(ver_num, nearest_neighbour)
            No_label.append(ver_num)
            if known_bot != 0:
                if nearest_neighbour not in Yes_label:
                    Yes_label.append(nearest_neighbour)
                if nearest_neighbour in No_label:
                    No_label.remove(nearest_neighbour)
                # find students who predict "NO" on ver_num
                penalty = [x for x in all_students if x not in Yes_found.get(ver_num)]
            else:
                # find students who predict "YES" on ver_num
                penalty = [x for x in all_students if x in Yes_found.get(ver_num)]
            # penalize bad students by decreasing their weights
            for bad_stu in penalty:
                # Stu_weight is indexed from 1
                Stu_weight[bad_stu - 1] = Stu_weight[bad_stu - 1] * 0.9
            for ver in non_home:
                Yes_count[ver] = sum([Stu_weight[stu - 1] for stu in Yes_found.get(ver)])
            sorted_count = sorted(Yes_count.items(), key=operator.itemgetter(1), reverse=True)
            ranking = [place for (place, votes) in sorted_count]
            print(sorted_count)

        if len(Yes_label) == client.bots or (len(Yes_label) + len(No_label) == 100):
            break
    # sanity check：the length of Yes_label should be less equal than 5 instead of 5
    # because bots may occur in the same vertex when we do locating
    if client.home not in Yes_label:
        No_label.append(client.home)
    assert len(Yes_label) == 5 or (len(Yes_label) + len(No_label) == 100)
    print(len(Yes_label), len(No_label))

    Tree_endpoint = [ele for ele in Yes_label]
    print(Tree_endpoint)
    print(client.home)
    if client.home not in Tree_endpoint:
        Tree_endpoint.append(client.home)
    print(Tree_endpoint)

    # Step1: locate all bots by labeling the graph (done)
    # Step2: Once we precisely locate all bots on the graph, we can remote them in a fashion that has the minimum cost

    # First, generate 5(or less) shortest paths and store them as values in the dictionary
    # The key is the name of vertex(an integer)

    appro_tree = nx.algorithms.approximation.steinertree.steiner_tree(client.G, Tree_endpoint, weight='weight')
    assert appro_tree.has_node(client.home)
    print(appro_tree.nodes())
    print(appro_tree.edges())
    for ele in Tree_endpoint:
        assert appro_tree.has_node(ele)
    print(list(nx.edge_dfs(appro_tree, client.home)))
    post_order_edges = list(nx.edge_dfs(appro_tree, client.home))
    post_order_edges.reverse()
    post_order_edges = [(b, a) for (a, b) in post_order_edges]
    print(post_order_edges)
    cost = 0
    for (start, end) in post_order_edges:
        shortest_path = nx.shortest_path(client.G, start, end, weight='weight')
        i = 0
        while i < len(shortest_path) - 1:
            client.remote(shortest_path[i], shortest_path[i + 1])
            cost += client.G[start][end]['weight']
            i = i + 1
    assert cost == sum([client.G[u][v]['weight'] for (u, v) in appro_tree.edges()])
    client.end()
    pass
