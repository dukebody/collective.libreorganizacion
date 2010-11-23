# -*- coding: utf-8 -*-

from Products.DCWorkflow.interfaces import IAfterTransitionEvent
from Products.CMFPlone.utils import getToolByName


def proposal_transition_dispatch(proposal, event):
    """Handles actions that should be made when a proposal does transitions.
    """

    # create a skeleton poll when the proposal hits the plenary
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


    # start the poll when the voting on the proposal starts
    if IAfterTransitionEvent.providedBy(event) and\
        event.old_state.id == 'plenary' and event.new_state.id == 'voting':
        wft = getToolByName(proposal, 'portal_workflow')

        poll = proposal.poll

        # start poll voting
        status = wft.getStatusOf('collective.libreorganizacion.poll_workflow', poll)
        if status['review_state'] == 'draft':
            wft.doActionFor(poll, 'start')


    # stop the poll when the voting on the proposal ends
    if IAfterTransitionEvent.providedBy(event) and\
        event.old_state.id == 'voting' and event.new_state.id == 'archived':
        wft = getToolByName(proposal, 'portal_workflow')

        poll = proposal.poll

        # close poll voting
        status = wft.getStatusOf('collective.libreorganizacion.poll_workflow', poll)
        if status['review_state'] == 'voting':
            wft.doActionFor(poll, 'close')


def poll_transition_dispatch(poll, event):
    """Handles actions that should be made when a poll does transitions.
    """

    # enable poll after voting starts
    if IAfterTransitionEvent.providedBy(event) and\
        event.old_state.id == 'draft' and event.new_state.id == 'voting':

        poll.setEnabled(True)
        poll.update()


    # disable poll after voting ends
    if IAfterTransitionEvent.providedBy(event) and\
        event.old_state.id == 'voting' and event.new_state.id == 'closed':

        poll.setEnabled(False)
        poll.update()
