import logging

from ..settings import SIMPLE_SOCIALAUTH_PROVIDERS

logger = logging.getLogger(__name__)


def import_class(item):
    try:
        module_name, klass_name = item.rsplit('.', 1)
        mod = __import__(module_name, fromlist=module_name)
        return getattr(mod, klass_name)
    except:
        pass


class ProviderRegistry(object):
    providers = {}
    TYPE_CHOICES = []

    def __init__(self):
        for provider_ in SIMPLE_SOCIALAUTH_PROVIDERS:
            provider_class = import_class(provider_)
            if provider_class:
                logger.debug('{0} social provider loaded successfully.'.format(provider_class.type))
                provider_type = provider_class.type
                self.providers[provider_type] = provider_class

                setattr(self, 'TYPE_{0}'.format(provider_type.upper()), provider_type)
                self.TYPE_CHOICES.append((provider_type, provider_class.display_name()))
            else:
                logger.debug('Social provider class not found/imported: {0}'.format(provider_))

        self.TYPE_CHOICES = sorted(self.TYPE_CHOICES)

    def get(self, provider_type, **kwargs):
        provider_class = self.providers.get(provider_type)
        if provider_class:
            return provider_class(**kwargs)


registry = ProviderRegistry()
