import re
import os
from os.path import join, dirname, abspath
import logging
import zc.buildout

import buildoutjinja

hostname_regexp = re.compile(r'^[-a-z\.0-9]*$', re.I)

def is_simple_host(s):
    return not ((len(s.splitlines()) > 1) or (not hostname_regexp.match(s)))

def is_true(s):
    if s.lower() in set(['yes', 'y', 'true', 'enable', 'enabled']):
        return True
    return False

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

        if ('redirect_to' not in options and 'redirect_from' in options and
            not is_simple_host(redirect_to)):

            msg = ("Redirect location looks like a regexp. Please specify"
                " redirect destination with 'redirect_to' option")
            self.logger.error(msg)
            raise zc.buildout.UserError(msg)

        default_options = {
           'priority': '11',
           'config_name': options.get('redirect_to', redirect_to),
           'redirect_to': redirect_to,
        }

        for key, value in default_options.iteritems():
           if key not in options:
               options[key] = value

        options['config_file'] = (options['priority'] + '-' +
            options['config_name'] + '.conf')

        def host_regexp(h):
            return ('|'.join('(%s)' % h for h in h.split()))

        template_name = options.get('template', 'djangorecipe_fcgi.jinja')
        template_search_paths = [
            dirname(abspath(__file__)),
            buildout['buildout']['directory'],
        ]
        self.result = buildoutjinja.render_template(
            template_search_paths,
            template_name,
            buildout,
            options, 
            tests={
                'simple_host': is_simple_host,
                'true': is_true,
            },
        )

    def install(self):
        open(self.options['config_file'], 'w').write(self.result)
        self.options.created(self.options['config_file'])
        return self.options.created()

    def update(self):
        return self.install()
