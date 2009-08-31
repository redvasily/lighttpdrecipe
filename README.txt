==========================================
Lighttpd config file creation for Buildout
==========================================

This recipe is intended for generation of lighttpd configuration files.


Status
======

This recipe is an alpha state, so don't expect any stability. It can be used
but better hardcode the requirement for particular version that works for you.


Usage
=====

Example buildout.cfg::

    [buildout]
    develop = lighttpdrecipe buildoutjinja
    parts = lighty-conf

    [django]
    project=lighttpdrecipetest

    [lighty-conf]
    recipe = lighttpdrecipe
    host = (a|b).example.com
    redirect_from = www.example.com
    redirect_to = a.example.com


This recipe will generate a following config file::

    $HTTP["host"] =~ "((a|b).example.com)" {

        server.document-root = "/home/vasily/projects/lighttpd_recipe/src"
        server.follow-symlink = "enable"
        dir-listing.activate = "enable"

        fastcgi.server = (
            "/fcgi" => (
                (
                    "bin-path" => "/home/vasily/projects/lighttpd_recipe/src/bin/django.fcgi",
                    "socket" => "/tmp/a.example.com.socket",
                    "check-local" => "disable",
                    "max-procs" => 2,
                    "min-procs" => 2,
                )
            )
        )

        url.rewrite-once = (
            "^(/media/.*)$" => "/$1",
            "^(/.*)$" => "/fcgi$1",
        )

        $HTTP["url"] =~ "^/media/" {
            expire.url = ( "" => "access 1 seconds" )
        }
    }



    $HTTP["host"] == "www.example.com" {

        url.redirect = ( "^(/.*)" => "http://a.example.com$1" )
    }
