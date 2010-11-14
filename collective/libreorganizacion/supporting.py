from contentratings.browser.base_vocabs import titled_vocab
from contentratings.browser.basic import BasicUserRatingView

from collective.libreorganizacion import _


support_vocab = titled_vocab(
    ((1, _(u'Apoyar')),
    ))


class SupportView(BasicUserRatingView):
    """Vista para apoyar y retirar apoyos."""

    vocab_name = 'collective.libreorganizacion.support_vocab'
