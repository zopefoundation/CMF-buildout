##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
""" Web-configurable workflow.

$Id$
"""

# Python library
from string import join

# Zope
from ZODB import Persistent
from AccessControl import getSecurityManager, ClassSecurityInfo
from OFS.Folder import Folder
from OFS.ObjectManager import bad_id
from OFS.Traversable import Traversable
from Globals import DTMLFile, PersistentMapping
import Acquisition
from Acquisition import aq_inner, aq_parent
import Globals
import App
from DocumentTemplate.DT_Util import TemplateDict

# CMFCore
from Products.CMFCore.WorkflowCore import WorkflowException, \
     ObjectDeleted, ObjectMoved
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.utils import getToolByName

# DCWorkflow
from utils import _dtmldir, modifyRolesForPermission
from WorkflowUIMixin import WorkflowUIMixin
from Transitions import TRIGGER_AUTOMATIC, TRIGGER_USER_ACTION, \
     TRIGGER_WORKFLOW_METHOD
from Expression import StateChangeInfo, createExprContext

Unauthorized = 'Unauthorized'

def checkId(id):
    res = bad_id(id)
    if res != -1 and res is not None:
        raise ValueError, 'Illegal ID'
    return 1


class DCWorkflowDefinition (WorkflowUIMixin, Folder):
    '''
    This class is the workflow engine and the container for the
    workflow definition.
    UI methods are in WorkflowUIMixin.
    '''
    meta_type = 'Workflow'
    title = 'DC Workflow Definition'
    _isAWorkflow = 1

    state_var = 'state'
    initial_state = None

    states = None
    transitions = None
    variables = None
    worklists = None
    scripts = None

    permissions = ()

    manage_options = (
        {'label': 'Properties', 'action': 'manage_properties'},
        {'label': 'States', 'action': 'states/manage_main'},
        {'label': 'Transitions', 'action': 'transitions/manage_main'},
        {'label': 'Variables', 'action': 'variables/manage_main'},
        {'label': 'Worklists', 'action': 'worklists/manage_main'},
        {'label': 'Scripts', 'action': 'scripts/manage_main'},
        {'label': 'Permissions', 'action': 'manage_permissions'},
        ) + App.Undo.UndoSupport.manage_options

    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

    def __init__(self, id):
        self.id = id
        from States import States
        self._addObject(States('states'))
        from Transitions import Transitions
        self._addObject(Transitions('transitions'))
        from Variables import Variables
        self._addObject(Variables('variables'))
        from Worklists import Worklists
        self._addObject(Worklists('worklists'))
        from Scripts import Scripts
        self._addObject(Scripts('scripts'))

    def _addObject(self, ob):
        id = ob.getId()
        setattr(self, id, ob)
        self._objects = self._objects + (
            {'id': id, 'meta_type': ob.meta_type},)

    #
    # Workflow engine.
    #

    def _getStatusOf(self, ob):
        tool = aq_parent(aq_inner(self))
        status = tool.getStatusOf(self.id, ob)
        if status is None:
            return {}
        else:
            return status

    def _getWorkflowStateOf(self, ob, id_only=0):
        tool = aq_parent(aq_inner(self))
        status = tool.getStatusOf(self.id, ob)
        if status is None:
            state = self.initial_state
        else:
            state = status.get(self.state_var, None)
            if state is None:
                state = self.initial_state
        if id_only:
            return state
        else:
            return self.states.get(state, None)

    def _getPortalRoot(self):
        return aq_parent(aq_inner(aq_parent(aq_inner(self))))

    security.declarePrivate('getCatalogVariablesFor')
    def getCatalogVariablesFor(self, ob):
        '''
        Allows this workflow to make workflow-specific variables
        available to the catalog, making it possible to implement
        worklists in a simple way.
        Returns a mapping containing the catalog variables
        that apply to ob.
        '''
        res = {}
        status = self._getStatusOf(ob)
        for id, vdef in self.variables.items():
            if vdef.for_catalog:
                if status.has_key(id):
                    value = status[id]

                # Not set yet.  Use a default.
                elif vdef.default_expr is not None:
                    ec = createExprContext(StateChangeInfo(ob, self, status))
                    value = vdef.default_expr(ec)
                else:
                    value = vdef.default_value

                res[id] = value
        # Always provide the state variable.
        state_var = self.state_var
        res[state_var] = status.get(state_var, self.initial_state)
        return res

    security.declarePrivate('listObjectActions')
    def listObjectActions(self, info):
        '''
        Allows this workflow to
        include actions to be displayed in the actions box.
        Called only when this workflow is applicable to
        info.content.
        Returns the actions to be displayed to the user.
        '''
        ob = info.content
        sdef = self._getWorkflowStateOf(ob)
        if sdef is None:
            return None
        res = []
        for tid in sdef.transitions:
            tdef = self.transitions.get(tid, None)
            if tdef is not None and tdef.trigger_type == TRIGGER_USER_ACTION:
                if tdef.actbox_name:
                    if self._checkTransitionGuard(tdef, ob):
                        res.append((tid, {
                            'id': tid,
                            'name': tdef.actbox_name % info,
                            'url': tdef.actbox_url % info,
                            'permissions': (),  # Predetermined.
                            'category': tdef.actbox_category,
                            'transition': tdef}))
        res.sort()
        return map((lambda (id, val): val), res)

    security.declarePrivate('listGlobalActions')
    def listGlobalActions(self, info):
        '''
        Allows this workflow to
        include actions to be displayed in the actions box.
        Called on every request.
        Returns the actions to be displayed to the user.
        '''
        if not self.worklists:
            return None  # Optimization
        sm = getSecurityManager()
        portal = self._getPortalRoot()
        res = []
        fmt_data = None
        for id, qdef in self.worklists.items():
            if qdef.actbox_name:
                guard = qdef.guard
                if guard is None or guard.check(sm, self, portal):
                    searchres = None
                    var_match_keys = qdef.getVarMatchKeys()
                    if var_match_keys:
                        # Check the catalog for items in the worklist.
                        catalog = getToolByName(self, 'portal_catalog')
                        dict = {}
                        for k in var_match_keys:
                            v = qdef.getVarMatch(k)
                            v_fmt = map(lambda x, info=info: x%info, v)
                            dict[k] = v_fmt
                        searchres = apply(catalog.searchResults, (), dict)
                        if not searchres:
                            continue
                    if fmt_data is None:
                        fmt_data = TemplateDict()
                        fmt_data._push(info)
                    searchres_len = lambda searchres=searchres: len(searchres)
                    fmt_data._push({'count': searchres_len})
                    res.append((id, {'name': qdef.actbox_name % fmt_data,
                                     'url': qdef.actbox_url % fmt_data,
                                     'permissions': (),  # Predetermined.
                                     'category': qdef.actbox_category}))
                    fmt_data._pop()
        res.sort()
        return map((lambda (id, val): val), res)

    security.declarePrivate('isActionSupported')
    def isActionSupported(self, ob, action):
        '''
        Returns a true value if the given action name
        is possible in the current state.
        '''
        sdef = self._getWorkflowStateOf(ob)
        if sdef is None:
            return 0
        if action in sdef.transitions:
            tdef = self.transitions.get(action, None)
            if (tdef is not None and
                tdef.trigger_type == TRIGGER_USER_ACTION and
                self._checkTransitionGuard(tdef, ob)):
                return 1
        return 0

    security.declarePrivate('doActionFor')
    def doActionFor(self, ob, action, **kw):
        '''
        Allows the user to request a workflow action.  This method
        must perform its own security checks.
        '''
        sdef = self._getWorkflowStateOf(ob)
        if sdef is None:
            raise WorkflowException, 'Object is in an undefined state'
        if action not in sdef.transitions:
            raise Unauthorized
        tdef = self.transitions.get(action, None)
        if tdef is None or tdef.trigger_type != TRIGGER_USER_ACTION:
            raise WorkflowException, (
                'Transition %s is not triggered by a user action' % action)
        if not self._checkTransitionGuard(tdef, ob):
            raise Unauthorized
        self._changeStateOf(ob, tdef, kw)

    security.declarePrivate('isWorkflowMethodSupported')
    def isWorkflowMethodSupported(self, ob, method_id):
        '''
        Returns a true value if the given workflow method
        is supported in the current state.
        '''
        sdef = self._getWorkflowStateOf(ob)
        if sdef is None:
            return 0
        if method_id in sdef.transitions:
            tdef = self.transitions.get(method_id, None)
            if (tdef is not None and
                tdef.trigger_type == TRIGGER_WORKFLOW_METHOD and
                self._checkTransitionGuard(tdef, ob)):
                return 1
        return 0

    security.declarePrivate('wrapWorkflowMethod')
    def wrapWorkflowMethod(self, ob, method_id, func, args, kw):
        '''
        Allows the user to request a workflow action.  This method
        must perform its own security checks.
        '''
        sdef = self._getWorkflowStateOf(ob)
        if sdef is None:
            raise WorkflowException, 'Object is in an undefined state'
        if method_id not in sdef.transitions:
            raise Unauthorized
        tdef = self.transitions.get(method_id, None)
        if tdef is None or tdef.trigger_type != TRIGGER_WORKFLOW_METHOD:
            raise WorkflowException, (
                'Transition %s is not triggered by a workflow method'
                % method_id)
        if not self._checkTransitionGuard(tdef, ob):
            raise Unauthorized
        res = apply(func, args, kw)
        try:
            self._changeStateOf(ob, tdef)
        except ObjectDeleted:
            # Re-raise with a different result.
            raise ObjectDeleted(res)
        except ObjectMoved, ex:
            # Re-raise with a different result.
            raise ObjectMoved(ex.getNewObject(), res)
        return res

    security.declarePrivate('isInfoSupported')
    def isInfoSupported(self, ob, name):
        '''
        Returns a true value if the given info name is supported.
        '''
        if name == self.state_var:
            return 1
        vdef = self.variables.get(name, None)
        if vdef is None:
            return 0
        return 1

    security.declarePrivate('getInfoFor')
    def getInfoFor(self, ob, name, default):
        '''
        Allows the user to request information provided by the
        workflow.  This method must perform its own security checks.
        '''
        if name == self.state_var:
            return self._getWorkflowStateOf(ob, 1)
        vdef = self.variables[name]
        if vdef.info_guard is not None and not vdef.info_guard.check(
            getSecurityManager(), self, ob):
            return default
        status = self._getStatusOf(ob)
        if status is not None and status.has_key(name):
            value = status[name]

        # Not set yet.  Use a default.
        elif vdef.default_expr is not None:
            ec = createExprContext(StateChangeInfo(ob, self, status))
            value = vdef.default_expr(ec)
        else:
            value = vdef.default_value

        return value

    security.declarePrivate('notifyCreated')
    def notifyCreated(self, ob):
        '''
        Notifies this workflow after an object has been created
        and put in its new place.
        '''
        try:
            self._changeStateOf(ob, None)
        except ( ObjectDeleted, ObjectMoved ):
            # Swallow.
            pass

    security.declarePrivate('notifyBefore')
    def notifyBefore(self, ob, action):
        '''
        Notifies this workflow of an action before it happens,
        allowing veto by exception.  Unless an exception is thrown, either
        a notifySuccess() or notifyException() can be expected later on.
        The action usually corresponds to a method name.
        '''
        pass

    security.declarePrivate('notifySuccess')
    def notifySuccess(self, ob, action, result):
        '''
        Notifies this workflow that an action has taken place.
        '''
        pass

    security.declarePrivate('notifyException')
    def notifyException(self, ob, action, exc):
        '''
        Notifies this workflow that an action failed.
        '''
        pass

    security.declarePrivate('updateRoleMappingsFor')
    def updateRoleMappingsFor(self, ob):
        '''
        Changes the object permissions according to the current
        state.
        '''
        changed = 0
        sdef = self._getWorkflowStateOf(ob)
        if sdef is not None and self.permissions:
            for p in self.permissions:
                roles = []
                if sdef.permission_roles is not None:
                    roles = sdef.permission_roles.get(p, roles)
                if modifyRolesForPermission(ob, p, roles):
                    changed = 1
        return changed

    def _checkTransitionGuard(self, t, ob):
        guard = t.guard
        if guard is None:
            return 1
        if guard.check(getSecurityManager(), self, ob):
            return 1
        return 0

    def _findAutomaticTransition(self, ob, sdef):
        tdef = None
        for tid in sdef.transitions:
            t = self.transitions.get(tid, None)
            if t is not None and t.trigger_type == TRIGGER_AUTOMATIC:
                if self._checkTransitionGuard(t, ob):
                    tdef = t
                    break
        return tdef
        
    def _changeStateOf(self, ob, tdef=None, kwargs=None):
        '''
        Changes state.  Can execute multiple transitions if there are
        automatic transitions.  tdef set to None means the object
        was just created.
        '''
        moved_exc = None
        while 1:
            try:
                sdef = self._executeTransition(ob, tdef, kwargs)
            except ObjectMoved, moved_exc:
                ob = moved_exc.getNewObject()
                sdef = self._getWorkflowStateOf(ob)
                # Re-raise after all transitions.
            if sdef is None:
                break
            tdef = self._findAutomaticTransition(ob, sdef)
            if tdef is None:
                # No more automatic transitions.
                break
            # Else continue.
        if moved_exc is not None:
            # Re-raise.
            raise moved_exc

    def _executeTransition(self, ob, tdef=None, kwargs=None):
        '''
        Private method.
        Puts object in a new state.
        '''
        sci = None
        econtext = None
        moved_exc = None

        # Figure out the old and new states.
        old_sdef = self._getWorkflowStateOf(ob)
        old_state = old_sdef.getId()
        if tdef is None:
            new_state = self.initial_state
            former_status = {}
        else:
            new_state = tdef.new_state_id
            if not new_state:
                # Stay in same state.
                new_state = old_state
            former_status = self._getStatusOf(ob)
        new_sdef = self.states.get(new_state, None)
        if new_sdef is None:
            raise WorkflowException, (
                'Destination state undefined: ' + new_state)

        # Execute the "before" script.
        if tdef is not None and tdef.script_name:
            script = self.scripts[tdef.script_name]
            # Pass lots of info to the script in a single parameter.
            sci = StateChangeInfo(
                ob, self, former_status, tdef, old_sdef, new_sdef, kwargs)
            try:
                script(sci)  # May throw an exception.
            except ObjectMoved, moved_exc:
                ob = moved_exc.getNewObject()
                # Re-raise after transition

        # Update variables.
        state_values = new_sdef.var_values
        if state_values is None: state_values = {}
        tdef_exprs = None
        if tdef is not None: tdef_exprs = tdef.var_exprs
        if tdef_exprs is None: tdef_exprs = {}
        status = {}
        for id, vdef in self.variables.items():
            if not vdef.for_status:
                continue
            expr = None
            if state_values.has_key(id):
                value = state_values[id]
            elif tdef_exprs.has_key(id):
                expr = tdef_exprs[id]
            elif not vdef.update_always and former_status.has_key(id):
                # Preserve former value
                value = former_status[id]
            else:
                if vdef.default_expr is not None:
                    expr = vdef.default_expr
                else:
                    value = vdef.default_value
            if expr is not None:
                # Evaluate an expression.
                if econtext is None:
                    # Lazily create the expression context.
                    if sci is None:
                        sci = StateChangeInfo(
                            ob, self, former_status, tdef,
                            old_sdef, new_sdef, kwargs)
                    econtext = createExprContext(sci)
                value = expr(econtext)
            status[id] = value

        # Update state.
        status[self.state_var] = new_state
        tool = aq_parent(aq_inner(self))
        tool.setStatusOf(self.id, ob, status)

        # Update role to permission assignments.
        self.updateRoleMappingsFor(ob)

        # Execute the "after" script.
        if tdef is not None and tdef.after_script_name:
            script = self.scripts[tdef.after_script_name]
            # Pass lots of info to the script in a single parameter.
            sci = StateChangeInfo(
                ob, self, status, tdef, old_sdef, new_sdef, kwargs)
            script(sci)  # May throw an exception.

        # Return the new state object.
        if moved_exc is not None:
            # Propagate the notification that the object has moved.
            raise moved_exc
        else:
            return new_sdef


Globals.InitializeClass(DCWorkflowDefinition)

addWorkflowFactory(DCWorkflowDefinition, id='dc_workflow',
                   title='Web-configurable workflow')
