def get_elemet_atrs(root,node_type,node_id=None):
    for elm in root.iter():
        elm_tag = elm.tag
        if node_id:
            if 'MODEL' in elm_tag and node_type in elm_tag and node_id == elm.attrib['id']:
                return elm.attrib
        else:
            if 'MODEL' in elm_tag and node_type in elm_tag:
                return elm.attrib
        
def process_task_node(node,root,bpmn_graph):
    node_type = node[1]['type']
    node_id = node[1]['id']
    atrs = get_elemet_atrs(root,node_type,node_id)
    duration = float(atrs.get('duration',0))
    percent = float(atrs.get('percent',0))
    group = int(atrs.get('group',0))
    out = node[1]['outgoing'][0]
    next_flow = bpmn_graph.get_flow_by_id(out)[1]
    next_node = bpmn_graph.get_node_by_id(next_flow)
    return duration,percent,group,next_node
def process_parallel(node,root,bpmn_graph,dates,percentages):
    last_date = dates[-1]
    incomings = node[1]['incoming']
    outgoings = node[1]['outgoing']
    new_dates = dates.copy()
    new_percentages = percentages.copy()
    times = []
    deltas = []
    if len(incomings) == 1:
        # node starts here
        branches = {}
        for branch in outgoings:
            branches[branch] = []
            d = 0
            next_flow = bpmn_graph.get_flow_by_id(branch)[1]
            next_node = bpmn_graph.get_node_by_id(next_flow)
            while 1:
                node_type = next_node[1]['type']
                if node_type == 'task':
                    duration,percent,group,next_node = process_task_node(next_node,root,bpmn_graph)
                    d += duration
                    times.append(d)
                    deltas.append(percent)
                    new_dates.append(last_date + timedelta(days=d))
                    new_percentages.append(new_percentages[-1] + percent)
                elif node_type == 'parallelGateway':
                    if len(next_node[1]['incoming']) == 1:
                        next_node,pdates,ppercentages,times,deltas = process_parallel(next_node,root,bpmn_graph,dates,percentages)
                        new_list = list(zip(times,deltas))
                        new_list_sorted = sorted(new_list, key=lambda tup: tup[0])
                        times,deltas = zip(*new_list_sorted)
                        for i,time in enumerate(times):
                            new_dates.append(new_dates[-1] + timedelta(days=deltas[i]))
                            new_percentages.append(new_percentages[-1]+deltas[i])
                elif node_type == 'exclusiveGateway':
                    next_node,outputs = process_exclusive(next_node,root,bpmn_graph)
                    name = ""
                    maximum = 0
                    for output in outputs:
                        times = outputs[output]['times']
                        deltas = outputs[output]['deltas']
                        if sum(times) > maximum:
                            maximum = sum(times)
                            name = output
                    times = outputs[name]['times']
                    deltas = outputs[name]['deltas']
                    for i,time in enumerate(times):
                        new_dates.append(new_dates[-1] + timedelta(days=time))
                        new_percentages.append(new_percentages[-1]+deltas[i])
                else :
                    break
        
        next_flow = bpmn_graph.get_flow_by_id(next_node[1]['outgoing'][0])[1]
        next_node = bpmn_graph.get_node_by_id(next_flow)
    return next_node,new_dates,new_percentages,times,deltas

def process_exclusive(node,root,bpmn_graph):
    outgoings = node[1]['outgoing']
    outputs = {}
    for outgoing in outgoings:
        outputs[outgoing] = {
            'times':[],
            'deltas' : [],
        }
        d = 0
        next_flow = bpmn_graph.get_flow_by_id(outgoing)[1]
        next_node = bpmn_graph.get_node_by_id(next_flow)
        while 1:
            node_type = next_node[1]['type']
            if node_type == 'task':
                duration,percent,group,next_node = process_task_node(next_node,root,bpmn_graph)
                d += duration
                outputs[outgoing]['times'].append(d)
                outputs[outgoing]['deltas'].append(percent)
            elif node_type == 'parallelGateway':
                next_node,pdates,ppercentages,times,deltas = process_parallel(next_node,root,bpmn_graph,[],[])
                new_list = list(zip(times,deltas))
                new_list_sorted = sorted(new_list, key=lambda tup: tup[0])
                times,deltas = zip(*new_list_sorted)
                for i,time in enumerate(times):
                    outputs[outgoing]['times'].append(time)
                    outputs[outgoing]['deltas'].append(deltas[i])
            else:
                next_node = next_node
                break
    return next_node,outputs
