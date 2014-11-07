Setting Up
==========

Database
--------
Setting up the database should be done as described in the global README. This
is a necessary prerequisite for getting the visualizations to work.

Apache HTTPD
------------
Apache HTTPD needs to be set up with the wsgi plugin. This process varies
greatly from OS to OS, and greatly from version to version. Only requirements
are that the mod_wsgi supports python 2.7 (I honestly don't even know if
mod_wsgi with python 3.x is a thing, but that is inconsequential, as this is
*not* what you want to do).

Web Directory
-------------
Personally, I linked `/srv/http` to `<BASE_DIR>/web` (i.e. this directory),
but one could do this differently if they have more apps running and know more
httpd configuration-fu than I do. This may be different on your OS-- many put it
in `/var/web/http`.

Configuration
-------------
This is going to be a little different for everyone, again based on OS/httpd
version.
```
DocumentRoot "/srv/http"

#
# Each directory to which Apache has access can be configured with respect
# to which services and features are allowed and/or disabled in that
# directory (and its subdirectories). 
#
# First, we configure the "default" to be a very restrictive set of 
# features.  
#
<Directory />
    Options FollowSymLinks
    AllowOverride None
</Directory>

#
# Note that from this point forward you must specifically allow
# particular features to be enabled - so if something's not working as
# you might expect, make sure that you have specifically enabled it
# below.
#

Alias /pico/ /srv/http/wsgi-scripts/pico.wsgi/pico/

<Directory /srv/http/wsgi-scripts>
Options ExecCGI FollowSymLinks

SetHandler wsgi-script
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ /pico/$1 [QSA,PT,L]

</Directory>

#
# This should be changed to whatever you set DocumentRoot to.
#
<Directory "/srv/http">
    #
    # Possible values for the Options directive are "None", "All",
    # or any combination of:
    #   Indexes Includes FollowSymLinks SymLinksifOwnerMatch ExecCGI MultiViews
    #
    # Note that "MultiViews" must be named *explicitly* --- "Options All"
    # doesn't give it to you.
    #
    # The Options directive is both complicated and important.  Please see
    # http://httpd.apache.org/docs/2.2/mod/core.html#options
    # for more information.
    #
    Options Indexes FollowSymLinks

    #
    # AllowOverride controls what directives may be placed in .htaccess files.
    # It can be "All", "None", or any combination of the keywords:
    #   Options FileInfo AuthConfig Limit
    #
    AllowOverride None

    #
    # Controls who can get stuff from this server.
    #
</Directory>
```

Once you get this all set up, then you should be able to hit http://localhost/LA
and see the webpage.
