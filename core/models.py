from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone,timesince
import xml.etree.ElementTree as ET
import bpmn_python.bpmn_diagram_rep as diagram
from .utils import get_elemet_atrs
# Create your models here.

class Organization(MPTTModel):
    name = models.CharField(_('organization name'),max_length=300, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',verbose_name=_('parent organization'))
    members = models.ManyToManyField(User,related_name='organizations',verbose_name=_('organization memebers'), null=True, blank=True)
    is_department = models.BooleanField(_('is department'),default=False)
    is_deputy = models.BooleanField(_('is deputy'),default=False)
    is_manager = models.BooleanField(_('is management'),default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    class MPTTMeta:
        order_insertion_by = ['name']
    def __str__(self) -> str:
        return self.name
class Process(models.Model):
    name = models.CharField(_('process name'),max_length=300)
    description = models.TextField(_('process description'),null=True, blank=True)
    bpmn = models.TextField(_('bpmn process'),null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    active = models.BooleanField(_('active'),default=True)
    
    def __str__(self) -> str:
        return self.name
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        file_name = f'{self.id}.xml'
        with open(f'{settings.BASE_DIR}/bpmn-files/{file_name}', 'w') as f:
            f.write(self.bpmn)


class Task(models.Model):
    name = models.CharField(_('task name'),max_length=300)
    description = models.TextField(_('task description'),null=True, blank=True)
    process = models.ForeignKey(Process,on_delete=models.CASCADE,verbose_name=_('process name'),related_name='tasks')
    completed = models.BooleanField(default=False)
    percent_completed = models.FloatField(default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    def __str__(self) -> str:
        return self.name
    def get_done_activities(self):
        return Activity.objects.filter(task=self,completed=True,returned=False)

class Activity(models.Model):
    task = models.ForeignKey(Task,on_delete=models.CASCADE,related_name='activities')
    name = models.CharField(_('activity name'),max_length=300)
    activity_id =models.CharField(_('activity id'),max_length=300)
    completed = models.BooleanField(default=False)
    returned = models.BooleanField(default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    duration = models.FloatField(default=0)
    percent = models.FloatField(default=0)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    assigned_to = models.ForeignKey(User,on_delete=models.CASCADE,related_name='activities',null=True, blank=True)
    organ = models.ForeignKey(Organization,on_delete=models.CASCADE,related_name='activities',null=True, blank=True)
    
    
    def get_curent_task_dones(self):
        acts = Activity.objects.filter(task=self.task,completed=True,returned=False)
        acts = [act.activity_id for act in acts]
        return acts
    
    
    def __str__(self) -> str:
        return f'{self.name} : {self.activity_id}'
    
    def get_duration(self):
        if self.completed:
            days = self.updated_at - self.created_at
            days = days.days
            return days + 1
        else:
            now = timezone.now()
            days = now - self.created_at
            days = days.days
            return days + 1
    def what_is_next(self):
        process = self.task.process
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.load_diagram_from_xml_file(f'{settings.BASE_DIR}/bpmn-files/{process.id}.xml')
        root = ET.fromstring(process.bpmn)
        node = bpmn_graph.get_node_by_id(self.activity_id)
        outgoing = node[1]['outgoing'][0]
        next_id = bpmn_graph.get_flow_by_id(outgoing)[1]
        next_node = bpmn_graph.get_node_by_id(next_id)
        node_type = next_node[1]['type']
        
        if node_type == 'task':
            return 'task',next_node[0],None,None # next_node, next_node_id, Questions?
        elif node_type == 'parallelGateway':
            return 'parallelGateway',next_node[0],None,None
        elif node_type == 'exclusiveGateway':
            outgoings = next_node[1]['outgoing']
            questions = []
            for i,out in enumerate(outgoings):
                flow = bpmn_graph.get_flow_by_id(out)
                for elm in root.iter():
                    elm_tag = elm.tag
                    if 'MODEL' in elm_tag and elm.attrib and  out == elm.attrib['id']:
                        questions.append([i+1,elm.attrib.get('condition',"")])
                        break                            
            return 'exclusiveGateway',next_node[0],questions,outgoings


class Log(models.Model):
    activity = models.ForeignKey(Activity,on_delete=models.CASCADE)
    activity_name = models.CharField(_('activity name'),max_length=300)
    task = models.ForeignKey(Task,on_delete=models.CASCADE)
    task_name = models.CharField(_('task name'),max_length=300)
    assigned_to = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True,related_name="logs_to")
    assigned_from = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True,related_name="logs_from")
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    organ = models.ForeignKey(Organization,related_name='logs',on_delete=models.CASCADE,null=True,blank=True)
    organ_name = models.CharField(_('organ name'),max_length=300)
    
    def __str__(self) -> str:
        return f'{self.task_name} : {self.activity_name}'
    