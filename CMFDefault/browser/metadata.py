##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser views for metadata.

$Id$
"""

from Acquisition import aq_self

from Products.CMFDefault.exceptions import ResourceLockedError
from Products.CMFDefault.utils import Message as _

from utils import decode
from utils import FormViewBase
from utils import memoize


class MetadataMinimalEditView(FormViewBase):

    """Edit view for IMutableMinimalDublinCore.
    """

    _BUTTONS = ({'id': 'change',
                 'title': _(u'Change'),
                 'transform': ('edit_control',),
                 'redirect': ('portal_types', 'object/edit')},
                {'id': 'change_and_view',
                 'title': _(u'Change and View'),
                 'transform': ('edit_control',),
                 'redirect': ('portal_types', 'object/view')})

    # interface

    @memoize
    @decode
    def title(self):
        return self.request.form.get('title', self.context.Title())

    @memoize
    @decode
    def description(self):
        return self.request.form.get('description',
                                     self.context.Description())

    # controllers

    def edit_control(self, title, description, **kw):
        context = self.context
        if title!=context.Title() or description != context.Description():
            context.edit(title=title, description=description)
            return True, _(u'Metadata changed.')
        else:
            return False, _(u'Nothing to change.')


class MetadataEditView(MetadataMinimalEditView):

    """Edit view for IMutableDublinCore.
    """

    _BUTTONS = ({'id': 'change',
                 'title': _(u'Change'),
                 'transform': ('edit_control',),
                 'redirect': ('portal_types', 'object/metadata')},
                {'id': 'change_and_edit',
                 'title': _(u'Change and Edit'),
                 'transform': ('edit_control',),
                 'redirect': ('portal_types', 'object/edit')},
                {'id': 'change_and_view',
                 'title': _(u'Change and View'),
                 'transform': ('edit_control',),
                 'redirect': ('portal_types', 'object/view')})

    #helpers

    def _tuplify(self, value):
        if isinstance(value, basestring):
            value = (value,)
        return tuple([ i for i in value if i ])

    # interface

    @memoize
    @decode
    def allow_discussion(self):
        context = aq_self(self.context)
        allow_discussion = getattr(context, 'allow_discussion', None)
        if allow_discussion is not None:
            allow_discussion = bool(allow_discussion)
        return allow_discussion

    @memoize
    @decode
    def identifier(self):
        return self.context.Identifier()

    @memoize
    @decode
    def subject(self):
        subjects = self.request.form.get('subject', self.context.Subject())
        return tuple(subjects)

    @memoize
    @decode
    def allowed_subjects(self):
        mdtool = self._getTool('portal_metadata')
        subjects = mdtool.listAllowedSubjects(self.context)
        return tuple(subjects)

    @memoize
    @decode
    def extra_subjects(self):
        subjects = [ s for s
                     in self.subject() if not s in self.allowed_subjects() ]
        return tuple(subjects)

    @memoize
    @decode
    def format(self):
        return self.request.form.get('format', self.context.Format())

    @memoize
    @decode
    def contributors(self):
        return self.request.form.get('contributors',
                                     self.context.Contributors())

    @memoize
    @decode
    def language(self):
        return self.request.form.get('language', self.context.Language())

    @memoize
    @decode
    def rights(self):
        return self.request.form.get('rights', self.context.Rights())

    # controllers

    def edit_control(self, allow_discussion, title=None, subject=None,
                     description=None, contributors=None, effective_date=None,
                     expiration_date=None, format=None, language=None,
                     rights=None, **kw):
        context = self.context
        dtool = self._getTool('portal_discussion')

        if title is None:
            title = context.Title()

        if subject is None:
            subject = context.Subject()
        else:
            subject = self._tuplify(subject)

        if description is None:
            description = context.Description()

        if contributors is None:
            contributors = context.Contributors()
        else:
            contributors = self._tuplify(contributors)

        if effective_date is None:
            effective_date = context.EffectiveDate()

        if expiration_date is None:
            expiration_date = context.expires()

        if format is None:
            format = context.Format()

        if language is None:
            language = context.Language()

        if rights is None:
            rights = context.Rights()

        if allow_discussion == 'default':
            allow_discussion = None
        elif allow_discussion == 'off':
            allow_discussion = False
        elif allow_discussion == 'on':
            allow_discussion = True
        dtool.overrideDiscussionFor(context, allow_discussion)

        try:
            context.editMetadata( title=title
                                , description=description
                                , subject=subject
                                , contributors=contributors
                                , effective_date=effective_date
                                , expiration_date=expiration_date
                                , format=format
                                , language=language
                                , rights=rights
                                )
            return True, _(u'Metadata changed.')
        except ResourceLockedError, errmsg:
            return False, errmsg
