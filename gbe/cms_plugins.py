from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext as _
from gbe.forms import ContactForm
from cms.models.pluginmodel import CMSPlugin
from django.urls import reverse


class ContactFormPlugin(CMSPluginBase):
    model = CMSPlugin
    module = _("GBE Plugins")
    name = _("Drop a Line")  # name of the plugin in the interface
    render_template = 'gbe/incl_contact_form.tmpl'

    def render(self, context, instance, placeholder):
        context.update({'contact_form': ContactForm()})
        return context


class SubscribeEmailPlugin(CMSPluginBase):
    model = CMSPlugin
    module = _("GBE Plugins")
    name = _("Subscribe to Email")  # name of the plugin in the interface
    render_template = 'gbe/email_subscribe.tmpl'


class GoFundMePlugin(CMSPluginBase):
    model = CMSPlugin
    module = _("GBE Plugins")
    name = _("Go Fund Me Widget")  # name of the plugin in the interface
    render_template = 'gbe/go_fund_me.tmpl'


class ShareOnFacebookPlugin(CMSPluginBase):
    model = CMSPlugin
    module = _("GBE Plugins")
    name = _("Share on Facebook")  # name of the plugin in the interface
    render_template = 'gbe/facebook_share.tmpl'


class FollowOnFacebookPlugin(CMSPluginBase):
    model = CMSPlugin
    module = _("GBE Plugins")
    name = _("Follow us on Facebook")  # name of the plugin in the interface
    render_template = 'gbe/facebook_follow.tmpl'

'''
class AdRotatorPlugin(CMSPluginBase):
    model = CMSPlugin
    module = _("GBE Plugins")
    name = _("Ad Rotator")
    render_template = 'gbe/ad-rotator.tmpl'
'''
# register the plugins
plugin_pool.register_plugin(ContactFormPlugin)
plugin_pool.register_plugin(SubscribeEmailPlugin)
plugin_pool.register_plugin(GoFundMePlugin)
plugin_pool.register_plugin(ShareOnFacebookPlugin)
plugin_pool.register_plugin(FollowOnFacebookPlugin)
# plugin_pool.register_plugin(AdRotatorPlugin)
