#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor


class Options(object):
    '''
    这是一个公共的类,因为ad-hoc和playbook都需要一个options参数
    并且所需要拥有不同的属性,但是大部分属性都可以返回None或False
    因此用这样的一个类来省去初始化大一堆的空值的属性
    '''
    def __init__(self):
        self.connection = "ssh" 
        self.forks = 10
        self.check = False
   
    def __getattr__(self, name):
        return None


def run_playbook(tomcat_hosts_file,ansible_playbook_file):
    options = Options()
    loader = DataLoader()
    variable_manager = VariableManager() 
    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=tomcat_hosts_file)
    variable_manager.set_inventory(inventory) 
    playbooks=[ansible_playbook_file]
    pb = PlaybookExecutor(playbooks=playbooks, inventory=inventory, variable_manager=variable_manager, loader=loader, options=options, passwords=None)
    result = pb.run()
    return result

#if __name__ == '__main__':
#    run_playbook("/data/django_deploy_directory/roles/tomcathosts",'/data/django_deploy_directory/roles/tomcat.yml')
