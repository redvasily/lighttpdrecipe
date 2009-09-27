==========================================
Lighttpd config file creation for Buildout
==========================================

This recipe for buildout generates Lighttpd configuration files. It's
especially well suited for using with Django (djangorecipe) in FastCGI mode.

Config file is generated from Jinja2 template. Recipe provides some custom
Jinja tests, specifically tailored for Lighttpd configuration files.

Very little logic is hard coded in the python code, most of the work happens in
the template, so you can extend default template or even use your own.


Basic usage
===========

Basic buildout.cfg::

    [buildout]
    parts = django lighty-conf

    [django]
    recipe = djangorecipe
    project=lighttpdrecipetest
    version = 1.1
    fcgi = true
    settings = settings
    extra-paths = ${buildout:directory}/${django:project}
    unzip = true
    download-cache = dlcache

    [lighty-conf]
    recipe = lighttpdrecipe
    host = example.com
    redirect_from = www.example.com
    media =
        /favicon.ico => ${buildout:directory}/media/favicon.ico

This recipe will generate a following config file::

    $HTTP["host"] == "example.com" {
        server.document-root = "/var/sites/lighttpdrecipetest"
        server.follow-symlink = "enable"
        dir-listing.activate = "enable"

        fastcgi.server = (
            "/fcgi" => (
                (
                    "bin-path" => "/var/sites/lighttpdrecipetest/bin/django.fcgi",
                    "socket" => "/tmp/example.com.socket",
                    "check-local" => "disable",
                    "max-procs" => 4,
                    "min-procs" => 4,
                )
            )
        )

        alias.url = (
            "/favicon.ico" => "/var/sites/lighttpdrecipetest/media/favicon.ico",
            "/admin_media" => "/var/sites/lighttpdrecipetest/parts/django/django/contrib/admin/media/",
            "/media" => "/var/sites/lighttpdrecipetest/media/",
        )

        url.rewrite-once = (
            "^(/favicon.ico.*)$" => "/$1",
            "^(/admin_media.*)$" => "/$1",
            "^(/media/.*)$" => "/$1",
            "^(/.*)$" => "/fcgi$1",
        )

        $HTTP["url"] =~ "^/media/" {
            expire.url = ( "" => "access 1 seconds" )
        }
    }

    $HTTP["host"] == "www.example.com" {
        url.redirect = ( "^(/.*)" => "http://example.com$1" )
    }

Now you just need to symlink this config to /etc/lighttpd/conf-available/ (or
what your distribution uses) and you actually have a pretty high chance that it will work
on the very first attempt.

So just by writing several lines for lighttpdrecipe we configured Lighttpd to
use 4 fastcgi worker processes, set up rewrites and aliases for media files,
Django admin media files and favicon.ico. Also we set up a redirect from
www.example.com to example.com

That's exactly what I need most of the time, so perhaps that's what you need as well.


Recipe options
==============

host (required)
    List of host names or regular expressions of the server we are setting up,
    each on the separate line. At least one is required.

    Recipe will try to guess if you provide simple host name or a regular expression
    and depending on that will use corresponding match operator.

template (optional, default value is "djangorecipe_fcgi.jinja")
    Template to use for config generation. Lighttpdrecipe sets up Jinja with
    filesystem template loader. It searches for templates in the lighttpdrecipe
    installation directory and in ${buildout:directory}, so you can provide
    your own template and extend the default template

redirect_from (optional)
    List of hostnames (or regular expressions) to redirect from to our main
    host. Use it if you want to redirect all your users to www or non-www
    version of your site.

redirect_to (optional, default value is the first line of the "hosts" option)
    Primary domain where all users will be redirected to if they try to visit a
    site listed in the redirect_from.
    If "redirect_from" is specified and "redirect_to" is not specified and the 
    first "hosts" line looks like a regexp, then an exception will be thrown.

priority (optional, default value is 11)
    Generated config file will be named [priority]-[config_name].conf

config_name (optional, default value is [redirect_to])
    That's the second part of the generated config name. In the case of simple
    hostname without explict redirect_to specified, config will be named like
    11-example.com.conf

processes (optional, default value is 4)
    Number of fastcgi worker processes

media_url (optional, default value is "/media")
    Url to serve media files.

media_root (optional, default value is ${buildout:directory} + "/media")
    Media files location

dir_listing (optional, default value is "enable")
    Enable directory listing?

socket (optional, default value is [redirect_to] or ${django:project})
    Config will use /tmp/{{ socket }}/socket for communications with lighttpd

bin_path (optional, default value is ${buildout:bin-directory}/django.fcgi)
    Script to start fast cgi processes. Default value works with Django recipe fcgi file

document_root (optional, default value is ${buildout:directory})
    Site document root

far_future_expiry (optional, default value is "no")
    Set expiry of media files to the far future

rewrite_admin_media (optional, default value is "yes")
    Configure rewrite rule and alias for serving Django admin media files

admin_media_url (optional, default value is "/admin_media")
    URL to serve Django admin media files. Default value matched Django default

admin_media_path (optional, default value is ${django:location}/django/contrib/admin/media/")
    Location of Django admin media files. Matches the location if Django admin
    media files if djangorecipe is used

media (optional, default value is "")
    Pairs of /media_url => /path/to/my/media/on/the/server each on the separate line
    Each line will create a rewrite rule and alias.url in the config

expiry_period (optional, default value depends on "far_future_expiry" option)
    If "far_future_expiry" is set then expiry_period is set to "12 months", if
    not set - "1 seconds".
    If you provide explict "expiry_period" then your value is used.

extra (optional)
    Value of "extra" option (if given) in inserted verbatim near the end of
    $HTTP["host"] match section


Customizing template
====================

Lighttpdrecipe uses Jinja2 template for config generation. Template context
includes all options specified for the recipe and additionally "options" and
"buildout" variables. So you can access any variable from the buildout.cfg like
this {{ buildout.buildout.directory }} or {{ buildout.buildout['bin-directory'] }}.

Jinja environment is configured to use filesystem loader that looks for
templates in the lighttpdrecipe installation directory and in the 
{{ buildout:directory }}, e.g. the main buildout directory. This allows you to
use your own template, overriding default values for variables or even
whole template blocks.


Custom tests
------------

Two additional tests are provided for the Jinja environment:

true
    this test for "affirmative" string, e.g.  one of the following (case
    insensitive): 'yes', 'y', 'true', 'enable', 'enabled'.

    Example usage::

        {% if dir_listing is true %}
            Dir_listing is enabled
        {% endif %}

simple_host
    Tests if the argument is a "simple host name", e.g. single line string
    which consists of alphanumeric characters, hyphens and dots.

    For example::

        "www.example.com"

    will pass the test, but::

        ".*\.example.com" 

    or::

        """
        a.example.com
        b.example.com
        """"

    will not.

    Example usage::

        {% if host is simple_host %}
            Output simple host condition
        {% endif %}


Specifying different default option values
------------------------------------------

You can easily specify different default option values by extending default template.

Here's the example::

    {%- extends "djangorecipe_fcgi.jinja" -%}

    {%- set processes = processes or '2' -%}

This template will work just as the standard one but default value for "processes" will be '2'.


Use the source
--------------

You can do many other things by extending the template. To get the idea what's
going on in the template look at the template source_.

.. _source: http://github.com/redvasily/lighttpdrecipe/blob/master/lighttpdrecipe/djangorecipe_fcgi.jinja


Bugs
====

If you find a bug please use the github tracker_.

.. _tracker: http://github.com/redvasily/lighttpdrecipe/issues 


Custom templates
================

I don't expect my template to work for everyone, so if you find general
infrastructure of lighttpdrecipe and create another template which you can
think can be useful for someone else, please contact me at redvasily at
gmail.com and I'll include your template in the lighttpdrecipe
