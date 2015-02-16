#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ansible module for finding AutoScalingGroups

Copyright (c) 2015 Riccardo Freixo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

DOCUMENTATION = '''
---
module: ec2_find_asg
short_description: Finds AutoScalingGroups based on ec2 tags
description:
     - Finds and retrieves properties about AutoScalingGroups based on ec2 tags.
options:
  tags:
    description:
      - dictonary of key value tags to search for.
      required: true
    default: null
    aliases: []
requirements: [ "boto" ]
author: Riccardo Freixo
'''

EXAMPLES = '''
# a playbook task line:
- ec2_find_asg:
    region: us-west-1
    tags:
      foo: true
      bar: true
'''

import sys
import time

from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

try:
    import boto.ec2.autoscale
    from boto.ec2.autoscale import AutoScaleConnection, AutoScalingGroup, Tag
    from boto.ec2.autoscale import LaunchConfiguration
    from boto.exception import BotoServerError
except ImportError:
    print "failed=True msg='boto required for this module'"
    sys.exit(1)

ASG_ATTRIBUTES = ('availability_zones', 'default_cooldown', 'desired_capacity',
    'health_check_period', 'health_check_type', 'launch_config_name',
    'load_balancers', 'max_size', 'min_size', 'name', 'placement_group',
    'termination_policies', 'vpc_zone_identifier')

def get_properties(autoscaling_group):
    properties = dict((attr, getattr(autoscaling_group, attr)) for attr in ASG_ATTRIBUTES)
    properties['healthy_instances'] = 0
    properties['in_service_instances'] = 0
    properties['unhealthy_instances'] = 0
    properties['pending_instances'] = 0
    properties['viable_instances'] = 0
    properties['terminating_instances'] = 0

    if autoscaling_group.instances:
        properties['instances'] = [i.instance_id for i in autoscaling_group.instances]
        instance_facts = {}
        for i in autoscaling_group.instances:
            instance_facts[i.instance_id] = {'health_status': i.health_status,
                                            'lifecycle_state': i.lifecycle_state,
                                            'launch_config_name': i.launch_config_name }
            if i.health_status == 'Healthy' and i.lifecycle_state == 'InService':
                properties['viable_instances'] += 1
            if i.health_status == 'Healthy':
                properties['healthy_instances'] += 1
            else:
                properties['unhealthy_instances'] += 1
            if i.lifecycle_state == 'InService':
                properties['in_service_instances'] += 1
            if i.lifecycle_state == 'Terminating':
                properties['terminating_instances'] += 1
            if i.lifecycle_state == 'Pending':
                properties['pending_instances'] += 1
        properties['instance_facts'] = instance_facts
    properties['load_balancers'] = autoscaling_group.load_balancers

    if getattr(autoscaling_group, "tags", None):
        properties['tags'] = dict((t.key, t.value) for t in autoscaling_group.tags)

    return properties

def find(connection, module):
    """Find and get properties of ASGs with specified tags"""
    search_tags = module.params.get('tags')

    matching_as_groups = {}
    matching_as_groups_list = []

    as_groups = connection.get_all_groups()
    for as_group in as_groups:
        as_group_tags = dict((t.key, t.value) for t in as_group.tags)
        tags_intersection = dict(set.intersection(*(set(d.iteritems()) for d in [as_group_tags, search_tags])))
        if tags_intersection == search_tags:
            matching_as_groups_list.append(get_properties(as_group))

    matching_as_groups.update(
        as_groups=matching_as_groups_list
    )

    return matching_as_groups

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            tags=dict(type='dict')
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    region, ec2_url, aws_connect_params = get_aws_connection_info(module)
    try:
        connection = connect_to_aws(boto.ec2.autoscale, region, **aws_connect_params)
        if not connection:
            module.fail_json(msg="failed to connect to AWS for the given region: %s" % str(region))
    except boto.exception.NoAuthHandlerFound, e:
        module.fail_json(msg=str(e))
    changed = create_changed = replace_changed = False

    module.exit_json( changed=False, **find(connection, module) )

main()
