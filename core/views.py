from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.conf import settings
import xml.etree.ElementTree as ET
import bpmn_python.bpmn_diagram_rep as diagram
from django.db.models import Sum,Q
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Organization,Process,Task,Activity,Log
from .forms import ProcessForm,TaskForm
from jalali_date import date2jalali,jdatetime
from .utils import get_elemet_atrs
# Create your views here.

@login_required
def home(request):
    activities = Activity.objects.filter(completed=False,returned=False,assigned_to=request.user)
    user = request.user
    
    refers = user.organizations.first()
    if(refers):
        refers = refers.members.all()
        refers = [ref for ref in refers if ref.id != user.id]
    else:
        refers = None
    context = {
        'title':_('Home'),
        'activities':activities,
        'viewing':True,
        'refers':refers,
    }
    return render(request, 'core/home.html',context)

@login_required
def processes(request):
    context = {
        'title':_('Processes'),
        'processes':Process.objects.filter(active=True),
        'viewing':True
    }    
    return render(request, 'core/processes.html',context)
@login_required
def add_process(request):
    form = ProcessForm(request.POST or None)
    organs = Organization.objects.filter(Q(is_department=True) | Q(is_deputy=True) | Q(is_manager=True))
    context = {
        'title':_('Add Process'),
        'organs':organs,
    }
    if form.is_valid():
        form.save()
        return redirect('processes')
    context['form'] = form
    context['modeling'] = True
    return render(request, 'core/add_process.html',context)

@login_required
def edit_process(request,id):
    process = Process.objects.get(id=id)
    form = ProcessForm(request.POST or None,instance=process)
    organs = Organization.objects.filter(Q(is_department=True) | Q(is_deputy=True) | Q(is_manager=True))
    context = {
        'title':_('Edit Process'),
        'organs':organs,
    }
    if form.is_valid():
        form.save()
        return redirect('processes')
    context['form'] = form
    context['modeling'] = True
    return render(request, 'core/edit_process.html',context)
@login_required
def tasks(request):
    tasks_all = Task.objects.select_related('process').all()
    context = {
        'title':_('Tasks'),
        'tasks':tasks_all,
        'viewing':True
    }
    return render(request, 'core/tasks.html',context)
@login_required
def add_task(request):
    form = TaskForm(request.POST or None)
    
    context = {
        'title':_('Add Task'),
    }
    if form.is_valid():
        task = form.save()
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.load_diagram_from_xml_file(f'{settings.BASE_DIR}/bpmn-files/{task.process.id}.xml')
        root = ET.fromstring(task.process.bpmn)
        first_node = bpmn_graph.get_nodes("startEvent")[0][1]
        outgoings = first_node['outgoing']
        for outgoing in outgoings:
            next_id = bpmn_graph.get_flow_by_id(outgoing)[1]
            next_node = bpmn_graph.get_node_by_id(next_id)
            node_type = next_node[1]['type']
            if node_type == 'task':
                atrs = get_elemet_atrs(root,node_type)
                group_id = atrs.get('group')
                org = Organization.objects.get(id=group_id)
                user = org.members.filter(is_staff=True).first()
                
                act = Activity.objects.create(
                    task=task,
                    name=atrs['name'],
                    activity_id=atrs['id'],
                    duration=float(atrs.get('duration',0)),
                    percent=float(atrs.get('percent',0)),
                    assigned_to = user,
                    organ=org
                )
                organ = user.organizations.first()
                Log.objects.create(
                    activity=act,
                    activity_name=act.name,
                    task=task,
                    task_name=task.name,
                    assigned_to=user,
                    assigned_from=request.user,
                    organ=organ,
                    organ_name=organ.name
                )
                
        return redirect('tasks')
    context['form'] = form
    context['modeling'] = True
    return render(request, 'core/add_task.html',context)

@login_required
def confirm_activity(request,id):
    next_activity = request.POST.get('next_activity')
    activity_id = request.POST.get('activity_id')
    group = request.POST.get('group',1)
    next_activity_type = request.POST.get('next_activity_type')
    duration = request.POST.get('duration',0)
    percent = request.POST.get('percent',0)
    activity_name = request.POST.get('activity_name')
    
    activity = Activity.objects.select_related('task','assigned_to').get(id=id)
    task = activity.task
    
    if activity.assigned_to == request.user:
        activity.completed = True
        activity.save()
    else:
        return redirect('home')
    if next_activity_type == "bpmn:Task":
        if group:
            org = Organization.objects.get(id=group)
            user = org.members.filter(is_staff=True).first()
        else:
            org = None
            user = None
        act = Activity.objects.create(task=task,
            name=activity_name,activity_id=next_activity,
            duration=duration,percent=percent,
            assigned_to=user,organ=org)
        Log.objects.create(activity=act,activity_name=activity_name,task=task,
        task_name=task.name,assigned_to=user,assigned_from=request.user,
        organ=org,organ_name=org.name)
    elif next_activity_type == "bpmn:EndEvent":
        task.completed = True
    elif next_activity_type == "bpmn:ParallelGateway":
        groups = group.split(":::")[1:]
        durations = duration.split(":::")[1:]
        percents = percent.split(":::")[1:]
        activity_names = activity_name.split(":::")[1:]
        activity_ids = next_activity.split(":::")[1:]
        incomings = zip(groups,durations,percents,activity_names,activity_ids)
        for group,duration,percent,activity_name,activity_id in incomings:
            org = Organization.objects.get(id=group)
            user = org.members.filter(is_staff=True).first()
            act = Activity.objects.create(task=task,
                name=activity_name,activity_id=activity_id,
                duration=float(duration),percent=float(percent),
                assigned_to=user,organ=org)
            Log.objects.create(activity=act,activity_name=activity_name,task=task,
            task_name=task.name,assigned_to=user,assigned_from=request.user,
            organ=org,organ_name=org.name)
        
        
        
    
    total = task.activities.aggregate(total=Sum('percent'))['total']
    task.percent_completed = total   
    task.save()
    return redirect('home')


@login_required
def refer_activity(request,id):
    id = request.POST.get('id')
    user = request.POST.get('refer')
    assinged = User.objects.get(id=user)
    activity = Activity.objects.select_related('task').get(id=id)
    activity.assigned_to = assinged
    activity.save()
    organ = assinged.organizations.first()
    Log.objects.create(
        activity=activity,
        activity_name=activity.name,
        task=activity.task,
        task_name=activity.task.name,
        assigned_to=assinged,
        assigned_from=request.user,
        organ=organ,
        organ_name=organ.name)    
    
    return redirect('home')
    

@login_required
def task_view2(request,id):
    task = Task.objects.get(id=id)
    activities = Activity.objects.filter(task=task,completed=True,returned=False)
    currnet_activities = Activity.objects.filter(task=task,completed=False)
    
    bpmn_graph = diagram.BpmnDiagramGraph()
    bpmn_graph.load_diagram_from_xml_file(f'{settings.BASE_DIR}/bpmn-files/{task.process.id}.xml')
    root = ET.fromstring(task.process.bpmn)
    first_node = bpmn_graph.get_nodes("startEvent")[0][1]
    outgoing = first_node['outgoing'][0]  # assuming after the start is one task not the other elemetns like if or parallel gate
    dates = []
    percentages = []
    # nodes = bpmn_graph.get_nodes()
    # nums = 0
    # graphs = {}
    # ifgates = []
    # for node in nodes:
    #     if node[1]['type'] == 'exclusiveGateway':
    #         if node[0] not in ifgates:
    #             ifgates.append(node[0])
    # if ifgates:
        
    
    # else:
    #     graphs = {
    #         'original':{
    #         'time':[],
    #         'percent':[]
    #         }
    #     }

    

    
    next_id = bpmn_graph.get_flow_by_id(outgoing)[1]
    next_node = bpmn_graph.get_node_by_id(next_id)
    node_type = next_node[1]['type']
    atrs = get_elemet_atrs(root,node_type)
    duration = float(atrs.get('duration',0))
    percent = float(atrs.get('percent',0))
    dates.append(task.created_at + timedelta(days=duration))
    percentages.append(sum(percentages)+percent)
    # next node
    outgoing = next_node[1]['outgoing'][0]
    next_id = bpmn_graph.get_flow_by_id(outgoing)[1]
    next_node = bpmn_graph.get_node_by_id(next_id)

    breakWhile = True
    while breakWhile:
        node_type = next_node[1]['type']
        if node_type == 'task':
            duration,percent,group,next_node = process_task_node(next_node,root,bpmn_graph)            
            dates.append(dates[-1] + timedelta(days=duration))
            percentages.append(percentages[-1]+percent)
        elif node_type == 'parallelGateway':
            next_node,pdates,ppercentages,times,deltas = process_parallel(next_node,root,bpmn_graph,dates,percentages)
            new_list = list(zip(times,deltas))
            new_list_sorted = sorted(new_list, key=lambda tup: tup[0])
            times,deltas = zip(*new_list_sorted)
            for i,time in enumerate(times):
                dates.append(dates[-1] + timedelta(days=deltas[i]))
                percentages.append(percentages[-1]+deltas[i])
        elif node_type == 'exclusiveGateway':
            breakWhile = False
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
                dates.append(dates[-1] + timedelta(days=time))
                percentages.append(percentages[-1]+deltas[i])
                
                
        # to do if event
        
        elif node_type == 'endEvent':
            breakWhile = False

    new_list = list(zip(dates,percentages))
    new_list_sorted = sorted(new_list, key=lambda tup: tup[0])
    dates,percentages = zip(*new_list_sorted)
    new_dates = [date2jalali(date).strftime('%Y-%m-%d') for date in dates]
    percentages = list(percentages)
    

    context = {
        'title':_('Task View'),
        'task':task,
        'activities':activities,
        'viewing':True,
        'currnet_activities':currnet_activities,
        'dates':new_dates,
        'percentages':percentages,
    }
    return render(request, 'core/task_view.html',context)


@login_required
def task_view(request,id):
    task = Task.objects.get(id=id)
    activities = Activity.objects.filter(task=task,completed=True,returned=False)
    currnet_activities = Activity.objects.filter(task=task,completed=False)
    
    context = {
        'title':_('Task View'),
        'task':task,
        'activities':activities,
        'viewing':True,
        'currnet_activities':currnet_activities,
    }
    return render(request, 'core/task_view.html',context)