import networkx as nx
from base_analys.word_manager import is_continue_word


def add_to_graph(sintax, graph):
    """
    :param sintax:
    Струтура синтаксиса:
    0 - Номер слова
    1 - Слово
    2 - Нормализованное слово
    3 -
    5 - язык
    6 - Ссылка на слово-родитель
    :param graph:
    :return:
    """
    sintax_dict = dict()  # Номер: слово, ссылка
    sintax = sintax.split("\n")
    for word in sintax:  # Добавляем вершины
        if len(word) == 0 or word[0] == "#":
            continue
        word = word.replace("	", " ").split()
        if word[5] == "Foreign=Yes":  # текст не на русском
            return
        if word[2] in graph.nodes.keys():
            graph.nodes[word[2]]["size"] += 1
        else:
            graph.add_node(word[2], size=1)

        sintax_dict[word[0]] = word[2], word[6]

    for word in sintax:  # Добавляем ребра
        if len(word) > 0 and word[0] != "#":
            word = word.replace("	", " ").split()
            num_neib = word[6]  # Ссылка в лоб
            if num_neib == "0":  # Не ссылкается
                continue
            if is_continue_word(word[2]):  # Если текущее слово - проходное, пропустим
                continue

            if is_continue_word(sintax_dict[num_neib][0]):  # Если текущее слово ссылается на проходное, возьмем через одно
                num_neib = sintax_dict[num_neib][1]
                if num_neib == "0":
                    continue
            graph.add_edge(sintax_dict[num_neib][0], word[2], context=word[6], story_time=len(graph.edges))


def replace_edge(node1, node2, new_node, graph):  # node1 ссылалась на node2 теперь будет на new_node
    hystory = nx.get_edge_attributes(graph, "story_time")
    story_time = None
    for i in range(10000):
        if (node1, node2, i) in hystory.keys():
            story_time = hystory[(node1, node2, i)]
        if (node2, node1, i) in hystory.keys():
            story_time = hystory[(node2, node1, i)]
    graph.remove_edge(node1, node2)
    if story_time is None:
        return
    graph.add_edge(node1, new_node, story_time=story_time)


def copy_edge(node1, node2, new_node, graph):  # node1 ссылалась на node2 теперь будет на new_node
    hystory = nx.get_edge_attributes(graph, "story_time")
    story_time = None
    for i in range(10000):
        if (node1, node2, i) in hystory.keys():
            story_time = hystory[(node1, node2, i)]
        if (node2, node1, i) in hystory.keys():
            story_time = hystory[(node2, node1, i)]
    if story_time is None:
        return
    graph.add_edge(node1, new_node, story_time=story_time)


def combine_nodes(node1, node2, new_name, graph):
    sum_size = graph.nodes[node1]["size"] + graph.nodes[node2]["size"]
    graph.add_node(new_name, size=sum_size)
    if new_name != node1:
        graph.add_edges_from([x for x in zip([new_name] * len(graph[node1]), graph[node1])])
        graph.remove_node(node1)
    if new_name != node2:
        graph.add_edges_from([x for x in zip([new_name] * len(graph[node2]), graph[node2])])
        graph.remove_node(node2)


def merge_nodes(to_node, from_node, graph):
    if to_node == from_node:
        return {"res": False, "err": "Входные вершины совпадают"}
    if to_node not in graph.nodes or from_node not in graph.nodes:
        return {"res": False, "err": "одной из вершин нет в графе"}
    graph.nodes[to_node]["size"] += graph.nodes[from_node]["size"]
    graph.add_edges_from([x for x in zip([to_node] * len(graph[from_node]), graph[from_node])])
    graph.remove_node(from_node)
    return {"res": True, "err": None}

