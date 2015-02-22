# ansible-find-asg

[![Build Status](https://travis-ci.org/riccardofreixo/ansible-find-asg.svg?branch=master)](https://travis-ci.org/riccardofreixo/ansible-find-asg.svg)

Simple module to find and retrive properties about EC2 AutoScalingGroups based on tags.

###Usage

To use this module, you can either:

* Place it in your ANSBILE_LIBRARY path.
* Use the --module-path command line option.
* Place it in the directory ./library alongside your top level playbooks.

For more information check out the official [Ansible documentation](docs.ansible.com/developing_modules.html "Developing Modules").

###Example

```
# a playbook task line:
- ec2_find_asg:
    region: us-west-1
    tags:
      foo: true
      bar: true
```
