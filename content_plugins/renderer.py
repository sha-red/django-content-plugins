from django.utils.translation import get_language

from feincms3.renderer import Regions, TemplatePluginRenderer


class MultilingualRegions(Regions):
    def cache_key(self, region):
        return '%s-%s' % (get_language(), super().cache_key(region))


class ContentPluginRenderer(TemplatePluginRenderer):
    def register(self):
        """
        Used as decorator

        Usage:
            @renderer.register()
            class TextPlugin(ModelPlugin):
                pass

        """
        def _renderer_wrapper(plugin_class):
            plugin_class.register_with_renderer(self)
            return plugin_class
        return _renderer_wrapper

    def regions(self, item, inherit_from=None, regions=MultilingualRegions):
        return super().regions(item, inherit_from=inherit_from, regions=regions)
