# ansible-find-asg

[![Build Status](https://travis-ci.org/riccardofreixo/ansible-find-asg.svg?branch=master)](https://travis-ci.org/riccardofreixo/ansible-find-asg.svg)

Simple module to find and retrive properties about EC2 AutoScalingGroups based on tags.

###Example

```
# a playbook task line:
- ec2_find_asg:
    region: us-west-1
    tags:
      foo: true
      bar: true
```
