from django.db.models import Model
from django.utils.translation import get_language

from content_editor import renderer as content_editor
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

    def admin_inlines(self, exclude=[]):
        """
        from . import content_plugins

        class YourAdmin(admin.ModelAdmin):
            inlines = content_plugins.renderer.admin_inlines()
        """
        plugins = [p for p in self.plugins() if p not in exclude]
        return [p.admin_inline() for p in plugins]


# Experimental implementation
class PluginRenderer(content_editor.PluginRenderer):
    def register(self, plugin, renderer=None):
        if not renderer:
            # Might raise an AttributeError
            renderer = getattr(plugin, 'render')
        self._renderers[plugin] = renderer

    def get_registered_plugins(self, exclude=[]):
        registered_plugins = list(self._renderers.keys())
        registered_plugins.remove(Model)
        return [p for p in registered_plugins if p not in exclude]

    def get_admin_inlines(self, exclude=[]):
        plugins = self.get_registered_plugins(exclude)
        return [p.admin_inline() for p in plugins]
