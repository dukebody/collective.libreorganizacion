"""Voting for polls
Based on optilux.cinemacontent. Thanks, Martin!
"""

from BTrees.OOBTree import OOSet

from zope.interface import implements, Interface
from zope import schema
from zope.component import adapts

from zope.annotation.interfaces import IAnnotations

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
        
        # We assume IPoll is annotatable, in which case we can adapt to
        # IAnnotations and get a mapping-like object back. We use a dictionary
        # for all votes and keep a list of the people who voted.

        annotations = IAnnotations(context)
        annotations.setdefault(VOTES_KEY, {})
        annotations.setdefault(ELECTORS_KEY, OOSet())

        self.electors = annotations[ELECTORS_KEY]
        self.votes = annotations[VOTES_KEY]

        # initialize each option to 0 votes
        for option in context.keys():
            self.votes.setdefault(option, 0)

    @property
    def results(self):
        return self.votes
        
    def available(self, user_token):
        return not self.electors.has_key(user_token)
                    
    def vote(self, user_token, option_no):
        if not self.available(user_token):
            raise KeyError("Voting not available for %s" % user_token)

        self.electors.insert(user_token)
        self.votes[option_no] += 1
