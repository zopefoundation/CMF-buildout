##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for DCWorkflow module.

$Id$
"""

from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope
Zope.startup()
from Interface.Verify import verifyClass

from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyTool
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.CMFCore.WorkflowTool import WorkflowTool
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition


class DCWorkflowDefinitionTests(TestCase):

    def setUp( self ):
        self.site = DummySite('site')
        self.site._setObject( 'portal_types', DummyTool() )
        self.site._setObject( 'portal_workflow', WorkflowTool() )
        addWorkflowFactory(DCWorkflowDefinition)

    def test_doActionFor(self):
        wftool = self.site.portal_workflow
        wftool.manage_addWorkflow('Workflow (DC Workflow Definition)', 'wf')
        wftool.setDefaultChain('wf')

        wf = wftool.wf
        wf.states.addState('private')
        sdef = wf.states['private']
        sdef.setProperties( transitions=('publish',) )
        wf.states.addState('published')
        wf.states.setInitialState('private')
        wf.transitions.addTransition('publish')
        tdef = wf.transitions['publish']
        tdef.setProperties(title='', new_state_id='published', actbox_name='')
        wf.variables.addVariable('comments')
        vdef = wf.variables['comments']
        vdef.setProperties(description='',
                 default_expr="python:state_change.kwargs.get('comment', '')",
                 for_status=1, update_always=1)

        dummy = self.site._setObject( 'dummy', DummyContent() )
        wftool.notifyCreated(dummy)
        self.assertEqual( wf._getStatusOf(dummy),
                          {'state': 'private', 'comments': ''} )
        wf.doActionFor(dummy, 'publish', comment='foo' )
        self.assertEqual( wf._getStatusOf(dummy),
                          {'state': 'published', 'comments': 'foo'} )

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_workflow \
                import WorkflowDefinition as IWorkflowDefinition

        verifyClass(IWorkflowDefinition, DCWorkflowDefinition)


def test_suite():
    return TestSuite((
        makeSuite(DCWorkflowDefinitionTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
