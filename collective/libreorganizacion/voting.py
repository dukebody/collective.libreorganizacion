"""Voting for polls
Based on optilux.cinemacontent. Thanks, Martin!
"""

from BTrees.OOBTree import OOSet
from Acquisition import aq_inner
from AccessControl import Unauthorized

from zope.interface import implements, Interface
from zope import schema
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewlet

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from zope.annotation.interfaces import IAnnotations

from pyvotecore.plurality import Plurality

from collective.libreorganizacion.content.poll import IPoll

from collective.libreorganizacion import _

VOTES_KEY = 'collective.libreorganizacion.voting'
ELECTORS_KEY = 'collective.libreorganizacion.electors'


class IVoting(Interface):
    """A poll that can be voted on.
    """
    
    results = schema.Container(title=_(u"A dict with all options and the sum of votes for each one"),
                            readonly=True)
         
    def available(user_token):
        """Whether or not rating is available for the given user.
        """
                       
    def vote(user_token, option_no):
        """Vote for the option number option_no.
        """

class Voting(object):
    """Vote in a poll
    
    The user_token is a username or IP address or other string identifying
    users. We use this to try to avoid people voting more than once.
    
    Here is how it works. First, we create a dummy film. We need to make sure 
    it's annotatable. The standard Film content type is attribute annotatable 
    because all content in Plone is.
        
        >>> from zope.interface import implements
        >>> from zope.annotation.interfaces import IAttributeAnnotatable
        
        >>> from collective.libreorganizacion.content.poll import IPoll
        
        >>> class DummyPoll(object):
        ...     implements(IPoll, IAttributeAnnotatable)
        ...     film_code = u""
        ...     title = u""
        ...     summary = u""
        ...     teaser = u""
        ...     shown_from = None
        ...     shown_until = None
        
    We need to make sure the rating adapter is configured. Normally, this 
    would happen during ZCML processing. We also need the standard annotation
    adapter.
    
        >>> from zope.component import provideAdapter
        >>> from zope.annotation.attribute import AttributeAnnotations
        >>> provideAdapter(AttributeAnnotations)
    
        >>> from optilux.cinemacontent.ratings import FilmRatings
        >>> provideAdapter(FilmRatings)
    
    Now we can adapt a film to a IRatings and rate it.
    
        >>> test_film = DummyFilm()
        >>> ratings = IRatings(test_film)
        
        >>> ratings.score is None
        True
        
    Let's rate as different users. The score is calculated as the percentage
    of positive votes, returned as an integer. Once a user has voted once, he 
    cannot vote again.
        
        >>> ratings.available('user1')
        True
        
        >>> ratings.rate('user1', True)
        >>> ratings.available('user1')
        False
        >>> ratings.score
        100
        
        >>> ratings.rate('user1', True) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        KeyError: 'Ratings not available for user1'
        
        >>> ratings.rate('user2', False)
        >>> ratings.score
        50
        
        >>> ratings.rate('user3', True)
        >>> ratings.score
        66
    """
    implements(IVoting)
    adapts(IPoll)
    
    def __init__(self, context):
        self.context = context
        self.wt = getToolByName(self.context, "portal_workflow")
        
        # We assume IPoll is annotatable, in which case we can adapt to
        # IAnnotations and get a mapping-like object back. We use a dictionary
        # for all votes and keep a list of the people who voted.

        annotations = IAnnotations(context)
        annotations.setdefault(VOTES_KEY, {})
        annotations.setdefault(ELECTORS_KEY, OOSet())

        self.electors = annotations[ELECTORS_KEY]
        self.votes = annotations[VOTES_KEY]

        # initialize each option to 0 votes
        for option in self.options:
            self.votes.setdefault(option, 0)

    @property
    def options(self):
        return self.context.keys()

    @property
    def results(self):
        # no results if the poll is not closed yet
        wf_state = self.wt.getInfoFor(aq_inner(self.context), 'review_state', None)

        if wf_state != 'closed':
            # XXX: This should be managed by a permission.
            return None
        
        input = [{'ballot':option, 'count':count} for option, count in self.votes.items()]
        return Plurality(input).as_dict()
        
    def available(self, user_token):
        wf_state = self.wt.getInfoFor(aq_inner(self.context), 'review_state', None)

        return not self.electors.has_key(user_token) and wf_state == 'voting'
                    
    def vote(self, user_token, option):
        if not self.available(user_token):
            raise KeyError("Voting not available for %s" % user_token)

        wf_state = self.wt.getInfoFor(aq_inner(self.context), 'review_state', None)

        if wf_state != 'voting':
            # XXX: This should be managed by a permission.
            raise Unauthorized("The poll is not open for voting")
        self.electors.insert(user_token)
        self.votes[option] += 1



class VotingViewlet(BrowserView):
    """Viewlet for allowing users to vote in election polls.
    """
    implements(IViewlet)

    render = ViewPageTemplateFile('voting.pt')

    def __init__(self, context, request, view, manager):
        super(VotingViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.view = view
        self.manager = manager
        self.voting = IVoting(self.context)
        self.portal_state = getMultiAdapter((context, self.request), name=u"plone_portal_state")

    def update(self):
        option = self.request.get('collective.libreorganizacion.voting_option')
            
        if option is None or self.portal_state.anonymous():
            return

        user_token = self.portal_state.member().getId()    
        if user_token is not None and self.voting.available(user_token):
            self.voting.vote(user_token, option)
    
    def has_winner(self):
        return self.voting.results is not None

    def available(self):
        if self.portal_state.anonymous():
            return False
        return self.voting.available(self.portal_state.member().getId())

    @property
    def winner(self):
        if self.has_winner():
            return self.voting.results['winner']
        return None
