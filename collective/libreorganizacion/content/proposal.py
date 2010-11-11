# -*- coding: utf-8 -*-

# CMF and Zope imports
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import Interface

from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage

from collective.libreorganizacion import _


# Vocabularies
TOPICS = SimpleVocabulary([
    SimpleTerm(value='derechoshumanos', title=_(u'Derechos Humanos')),
    SimpleTerm(value='derechosanimales', title=_(u'Derechos de los animales')),
    SimpleTerm(value='ecologia', title=_(u'Ecología y desarrollo sostenible')),
    ])

SCOPES = SimpleVocabulary([
    SimpleTerm(value='global', title=_(u'Global')),
    SimpleTerm(value='international', title=_(u'Internacional')),
    SimpleTerm(value='national', title=_(u'Nacional')),
    SimpleTerm(value='regional', title=_(u'Regional')),
    SimpleTerm(value='provincial', title=_(u'Provincial')),
    SimpleTerm(value='local', title=_(u'Local')),
    ])


class IProposal(Interface):
    """An entry (proposal) in a LibreOrganizacion directory
    """

    title = schema.TextLine(
        title=_(u'Slogan'),
        )

    image = NamedImage(
        title=_(u'Imagen'),
        )

    text = RichText(
        title=_(u'Texto'),
        )

    topics = schema.Choice(
        title=_(u'Temas'),
        description=_(u'Temas de la propuesta'),
        vocabulary=TOPICS,
        )

    scope = schema.Choice(
        title=_(u'Ámbito'),
        description=_(u'Ámbito territorial de la propuesta'),
        vocabulary=SCOPES,
        )

    #TODO: hacer Choice con vocabulario de países
    country = schema.TextLine(
        title=_(u'País'),
        )
