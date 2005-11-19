##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Caching policy manager node adapters.

$Id: cachingpolicymgr.py 40087 2005-11-13 19:55:09Z yuppie $
"""

from Products.GenericSetup.interfaces import INodeExporter
from Products.GenericSetup.interfaces import INodeImporter
from Products.GenericSetup.interfaces import PURGE
from Products.GenericSetup.utils import NodeAdapterBase

from Products.CMFCore.interfaces import ICachingPolicy
from Products.CMFCore.interfaces import ICachingPolicyManager


class CachingPolicyNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for CachingPolicy.
    """

    __used_for__ = ICachingPolicy

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        obj = self.context
        node = self._doc.createElement('caching-policy')
        node.setAttribute('name', obj.getPolicyId())
        node.setAttribute('predicate', obj.getPredicate())
        node.setAttribute('mtime_func', obj.getMTimeFunc())
        node.setAttribute('max_age_secs', str(obj.getMaxAgeSecs()))
        node.setAttribute('no_cache', str(bool(obj.getNoCache())))
        node.setAttribute('no_store', str(bool(obj.getNoStore())))
        node.setAttribute('must_revalidate',
                          str(bool(obj.getMustRevalidate())))
        node.setAttribute('vary', obj.getVary())
        node.setAttribute('etag_func', obj.getETagFunc())
        s_max_age_secs = obj.getSMaxAgeSecs()
        if s_max_age_secs is not None:
            node.setAttribute('s_max_age_secs', str(s_max_age_secs))
        node.setAttribute('proxy_revalidate',
                          str(bool(obj.getProxyRevalidate())))
        node.setAttribute('public', str(bool(obj.getPublic())))
        node.setAttribute('private', str(bool(obj.getPrivate())))
        node.setAttribute('no_transform', str(bool(obj.getNoTransform())))
        node.setAttribute('enable_304s', str(bool(obj.getEnable304s())))
        node.setAttribute('last_modified', str(bool(obj.getLastModified())))
        pre_check = obj.getPreCheck()
        if pre_check is not None:
            node.setAttribute('pre_check', str(pre_check))
        post_check = obj.getPostCheck()
        if post_check is not None:
            node.setAttribute('post_check', str(post_check))
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        info = {}
        policy_id = node.getAttribute('name')
        if not policy_id:
            # BBB: for CMF 1.5 profiles
            policy_id = node.getAttribute('policy_id')
        info['policy_id'] = str(policy_id)
        info['predicate'] = str(node.getAttribute('predicate'))
        info['mtime_func'] = str(node.getAttribute('mtime_func'))
        info['max_age_secs'] = int(node.getAttribute('max_age_secs'))
        no_cache = node.getAttribute('no_cache')
        info['no_cache'] = self._convertToBoolean(no_cache)
        no_store = node.getAttribute('no_store')
        info['no_store'] = self._convertToBoolean(no_store)
        must_revalidate = node.getAttribute('must_revalidate')
        info['must_revalidate'] = self._convertToBoolean(must_revalidate)
        info['vary'] = str(node.getAttribute('vary'))
        info['etag_func'] = str(node.getAttribute('etag_func'))
        s_max_age_secs = node.getAttribute('s_max_age_secs')
        if s_max_age_secs != '':
            info['s_max_age_secs'] = int(s_max_age_secs)
        proxy_revalidate = node.getAttribute('proxy_revalidate')
        info['proxy_revalidate'] = self._convertToBoolean(proxy_revalidate)
        info['public'] = self._convertToBoolean(node.getAttribute('public'))
        info['private'] = self._convertToBoolean(node.getAttribute('private'))
        no_transform = node.getAttribute('no_transform')
        info['no_transform'] = self._convertToBoolean(no_transform)
        enable_304s = node.getAttribute('enable_304s')
        info['enable_304s'] = self._convertToBoolean(enable_304s)
        last_modified = node.getAttribute('last_modified')
        info['last_modified'] = self._convertToBoolean(last_modified)
        pre_check = node.getAttribute('pre_check')
        if pre_check != '':
            info['pre_check'] = int(pre_check)
        post_check = node.getAttribute('post_check')
        if post_check != '':
            info['post_check'] = int(post_check)
        self.context.__init__(**info)


class CachingPolicyManagerNodeAdapter(NodeAdapterBase):

    """Node im- and exporter for CachingPolicyManager.
    """

    __used_for__ = ICachingPolicyManager

    def exportNode(self, doc):
        """Export the object as a DOM node.
        """
        self._doc = doc
        node = self._getObjectNode('object')
        node.appendChild(self._extractCachingPolicies())
        return node

    def importNode(self, node, mode=PURGE):
        """Import the object from the DOM node.
        """
        if mode == PURGE:
            self._purgeCachingPolicies()

        self._initCachingPolicies(node, mode)

    def _extractCachingPolicies(self):
        fragment = self._doc.createDocumentFragment()
        for policy_id, policy in self.context.listPolicies():
            exporter = INodeExporter(policy, None)
            if exporter is None:
                continue
            fragment.appendChild(exporter.exportNode(self._doc))
        return fragment

    def _purgeCachingPolicies(self):
        self.context.__init__()

    def _initCachingPolicies(self, node, mode):
        for child in node.childNodes:
            if child.nodeName != 'caching-policy':
                continue
            parent = self.context

            policy_id = str(child.getAttribute('name'))
            if policy_id not in parent._policy_ids:
                parent.addPolicy(policy_id, 'python:1', 'object/modified',
                                 0, 0, 0, 0, '', '')

            policy = self.context._policies[policy_id]
            INodeImporter(policy).importNode(child, mode)