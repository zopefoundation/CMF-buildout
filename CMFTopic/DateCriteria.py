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
""" Various date criteria

$Id$
"""

from AccessControl import ClassSecurityInfo
from DateTime.DateTime import DateTime
from Globals import InitializeClass

from permissions import View
from permissions import ChangeTopics
from AbstractCriterion import AbstractCriterion
from interfaces import Criterion
from Topic import Topic


class FriendlyDateCriterion( AbstractCriterion ):
    """
        Put a friendly interface on date range searches, like
        'where effective date is less than 5 days old'.
    """
    __implements__ = ( Criterion, )

    meta_type = 'Friendly Date Criterion'

    security = ClassSecurityInfo()

    _editableAttributes = ( 'value', 'operation', 'daterange' )

    _defaultDateOptions = ( (     0, 'Now'      )
                          , (     1, '1 Day'    )
                          , (     2, '2 Days'   )
                          , (     5, '5 Days'   )
                          , (     7, '1 Week'   )
                          , (    14, '2 Weeks'  )
                          , (    31, '1 Month'  )
                          , (  31*3, '3 Months' )
                          , (  31*6, '6 Months' )
                          , (   365, '1 Year'   )
                          , ( 365*2, '2 years'  )
                          )

    def __init__( self, id, field ):

        self.id = id
        self.field = field
        self.value = None
        self.operation = 'min'
        self.daterange = 'old'

    security.declarePublic( 'defaultDateOptions' )
    def defaultDateOptions( self ):
        """
            Return a list of default values and labels for date options.
        """
        return self._defaultDateOptions

    security.declareProtected( ChangeTopics, 'getEditForm' )
    def getEditForm( self ):
        """
            Return the name of the skin method used by Topic to edit
            criteria of this type.
        """
        return 'friendlydatec_editform'

    security.declareProtected( ChangeTopics, 'edit' )
    def edit( self
            , value=None
            , operation='min'
            , daterange='old'
            ):
        """
            Update the values to match against.
        """
        if value in ( None, '' ):
            self.value = None
        else:
            try:
                self.value = int( value )
            except:
                raise ValueError, 'Supplied value should be an int'

        if operation in ( 'min', 'max', 'within_day' ):
            self.operation = operation
        else:
            raise ValueError, 'Operation type not in set {min,max,within_day}'

        if daterange in ( 'old', 'ahead' ):
            self.daterange = daterange
        else:
            raise ValueError, 'Date range not in set {old,ahead}'

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems( self ):
        """
            Return a sequence of items to be used to build the catalog query.
        """
        if self.value is not None:
            field = self.Field()
            value = self.value

            # Negate the value for 'old' days
            if self.daterange == 'old':
                value = -value

            date = DateTime() + value

            operation = self.operation
            if operation == 'within_day':
                range = ( date.earliestTime(), date.latestTime() )
                return ( ( field, {'query': range, 'range': 'min:max'} ), )
            else:
                return ( ( field, {'query': date, 'range': operation} ), )
        else:
            return ()

InitializeClass(FriendlyDateCriterion)


# Register as a criteria type with the Topic class
Topic._criteriaTypes.append( FriendlyDateCriterion )
