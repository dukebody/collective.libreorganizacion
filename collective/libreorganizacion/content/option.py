# -*- coding: utf-8 -*-

# CMF and Zope imports
from zope import schema
from zope.interface import Interface

from collective.libreorganizacion import _


class IOption(Interface):
    """An option to vote for or against inside a proposal.
    """

    title = schema.TextLine(
        title=_(u'Title'),
        )

    description = schema.Text(
        title=_(u'Description'),
        description=_(u'A concrete exposition about what this vote option is about.'),
        max_length=500,
        )
