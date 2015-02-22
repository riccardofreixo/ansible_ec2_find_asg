#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import unittest
import uuid
from ec2_find_asg.ec2_find_asg import match, get_properties

try:
    import boto.ec2.autoscale
except ImportError:
    print "failed=True msg='boto required for this module'"
    sys.exit(1)


class TestEc2FindAsg(unittest.TestCase):

    def setUp(self):

        self.SEARCH_RANDOM_TAGS = [
                boto.ec2.autoscale.Tag(
                    key='Foo',
                    value=str(uuid.uuid4())
                    ),
                boto.ec2.autoscale.Tag(
                    key='Bar',
                    value=str(uuid.uuid4())
                    )
                ]

        self.SEARCH_RANDOM_TAGS_DICT = dict(
                (self.SEARCH_RANDOM_TAGS[i].key, self.SEARCH_RANDOM_TAGS[i].value) for i in range(0, len(self.SEARCH_RANDOM_TAGS), 1)
                )

        self.IGNORE_RANDOM_TAGS = [
                boto.ec2.autoscale.Tag(
                    key='IgnoreMe',
                    value=str(uuid.uuid4())
                    ),
                boto.ec2.autoscale.Tag(
                    key='DontFindThis',
                    value=str(uuid.uuid4())
                    )
                ]

        self.IGNORE_RANDOM_TAGS_DICT = dict(
                (self.IGNORE_RANDOM_TAGS[i].key, self.IGNORE_RANDOM_TAGS[i].value) for i in range(0, len(self.IGNORE_RANDOM_TAGS), 1)
                )

        self.SEARCH_ASG = boto.ec2.autoscale.AutoScalingGroup(
                name='MatchingAsg',
                launch_config='FakeLC',
                desired_capacity=1,
                min_size=1,
                max_size=1,
                tags=self.SEARCH_RANDOM_TAGS
                )

        self.IGNORE_ASG = boto.ec2.autoscale.AutoScalingGroup(
                name='UnmatchingAsg',
                launch_config='FakeLC',
                desired_capacity=1,
                min_size=1,
                max_size=1,
                tags=self.IGNORE_RANDOM_TAGS
                )

        self.AS_GROUPS = [
                self.SEARCH_ASG,
                self.IGNORE_ASG
                ]

    def test_match_one_as_group(self):
        matching_as_groups = match(
                self.AS_GROUPS,
                self.SEARCH_RANDOM_TAGS_DICT
                )
        self.assertEqual(
                len(matching_as_groups['as_groups']),
                1,
                msg='Assert only one ASG was matched'
                )

    def test_match_correct_as_group(self):
        matching_as_groups = match(
                self.AS_GROUPS,
                self.SEARCH_RANDOM_TAGS_DICT
                )
        self.assertEqual(
                matching_as_groups['as_groups'][0]['name'],
                self.SEARCH_ASG.name,
                msg='Assert correct ASG was matched'
                )

    def test_get_properties(self):
        properties = get_properties(self.SEARCH_ASG)
        self.assertDictEqual(
                properties['tags'],
                self.SEARCH_RANDOM_TAGS_DICT,
                msg='Assert get_properties returns correct random tags'
                )

if __name__ == '__main__':
    unittest.main()
