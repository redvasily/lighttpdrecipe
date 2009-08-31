import re
import os
import logging
import zc.buildout

import buildoutjinja

hostname_regexp = re.compile(r'^[-a-z\.0-9]*$', re.I)

def splitlit(t):
    return [s.strip() for s in t.splitlines()]


def normalize_bool(s):
    if s.lower() in ['yes', 'y', 'true']:
        return 'True'
    return ''

def is_regexp(s):
    return ((len(s.splitlines()) > 1) or (not hostname_regexp.match(s)))

class Lighttpd:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        self.logger = logging.getLogger(name)
        self.options = options

        if 'host' not in options:
            msg = "Required option 'host' is not specified."
            self.logger.error(msg)
            raise zc.buildout.UserError(msg)

        redirect_to = options['host'].splitlines()[0].strip()

        if ('redirect_to' not in options and is_regexp(redirect_to)):
            msg = ("Redirect location looks like a regexp. Please specify"
                " redirect destination with 'redirect_to' option")
            self.logger.error(msg)
            raise zc.buildout.UserError(msg)

        host_is_regexp = is_regexp(options['host'])
        redirect_is_regexp = is_regexp(options.get('redirect_to', ''))

        default_options = {
            'processes': '2',
            'extra': '',
            'media_url': '/media/',
            'priority': '11',
            'config_name': options.get('redirect_to', redirect_to),
            'socket': options.get('redirect_to', redirect_to),
            'bin_path': buildout['buildout']['bin-directory'] + '/django.fcgi',
            'document_root': buildout['buildout']['directory'],
            'host_is_regexp': str(host_is_regexp),
            'redirect_is_regexp': str(redirect_is_regexp),
            'redirect_to': redirect_to,
            'expiry_period': (options.get('far_future_expiry', False) and 
                '12 months' or '1 seconds'),
        }

        for key, value in default_options.iteritems():
            if key not in options:
                options[key] = value

        options['config_file'] = (options['priority'] + '-' +
            options['config_name'] + '.conf')

        options['host_is_regexp'] = normalize_bool(options['host_is_regexp'])
        options['redirect_is_regexp'] = normalize_bool(options['redirect_is_regexp'])

        def host_regexp(h):
            return ('|'.join('(%s)' % h for h in h.split()))

        template_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'default.conf.jinja')
        self.result = buildoutjinja.render_template(open(template_path).read(),
            buildout, options, 
            {
                'host_regexp': host_regexp,
            })

    def install(self):
        open(self.options['config_file'], 'w').write(self.result)
        self.options.created(self.options['config_file'])
        return self.options.created()

    def update(self):
        return self.install()
