# -*- coding: utf-8 -*-

from Products.DCWorkflow.interfaces import IAfterTransitionEvent
from Products.CMFPlone.utils import getToolByName


def proposal_transition_dispatch(obj, event):
    """Handles actions that should be made when a proposal does transitions.
    """

    proposal = obj

    if IAfterTransitionEvent.providedBy(event) and\
        event.old_state.id == 'pending' and event.new_state.id == 'plenary':
        proposal.invokeFactory('PlonePopoll', 'poll')

        poll = proposal.poll
        poll.setTitle('Votación')
        poll.setDescription('¡Participa!')
        poll.setQuestion('Si no hubiera una opción de voto que le satisfaga, añada la suya.')
        poll.setChoices('Voto en blanco')
        poll.setNumber_of_choices(1)
        poll.setVisible(False)
        poll.setShowCurrentResults(False)
        poll.setEnabled(False)
        poll.update()


    if IAfterTransitionEvent.providedBy(event) and\
        event.old_state.id == 'plenary' and event.new_state.id == 'voting':
        wft = getToolByName(obj, 'portal_workflow')

        poll = proposal.poll

        # publish draft proposal
        status = wft.getStatusOf('collective.libreorganizacion.poll_workflow', poll)
        if status['review_state'] == 'draft':
            wft.doActionFor(poll, 'publish')
