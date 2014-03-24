import os
import sys
import time
import posixpath
import threading

if sys.version > '3':
    import urllib.parse
    from http.server import HTTPServer
    from http.server import SimpleHTTPRequestHandler
else:
    import urllib
    from BaseHTTPServer import HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler

from . import tags
from . import utils
from . import templatelang

def build_file(filename, outfilename, root='.', create_dir=True):
    filepath = os.path.join(root, filename)
    with utils.open_file(filepath) as infile:
        try:
            if sys.version > '3':
                content = str(infile.read(), 'utf-8')
            else:
                content = unicode(infile.read(), 'utf-8')
            output = tags.render(content, filename=filename, rootdir=root)
        except templatelang.ParseBaseException as e:
            utils.print_parse_exception(e, filename)
            return

    with utils.open_file(outfilename, "w", create_dir=create_dir) as outfile:
        if sys.version > '3':
            outfile.write(output)
        else:
            outfile.write(output.encode('utf-8'))

            
def build_files(root='.', dest='_site', pattern='**/*.html', 
                exclude='_*/**', watch=False, force=False):
    try:
        os.stat(os.path.join(root, 'index.html'))
    except OSError:
        if not force:
            msg = "Oops, we can't find an index.html in the source folder.\n"+\
                  "If you want to build this folder anyway, use the --force\n"+\
                  "option."
            print(msg)
            sys.exit(1)

    print("Building site from '{0}' into '{1}'".format(root, dest))

    exclude = exclude or os.path.join(dest, '**')
    for filename in utils.walk_folder(root or '.'):
        included = utils.matches_pattern(pattern, filename)
        excluded = utils.matches_pattern(exclude, filename)
        destfile = os.path.join(dest, filename)
        if included and not excluded: 
            build_file(filename, destfile, root=root)
        elif not excluded:
            filepath = os.path.join(root, filename)
            destpath = os.path.join(dest, filename)
            utils.copy_file(filepath, destpath)

    if watch:
        observer = _watch(root=root,
                          dest=dest,
                          pattern=pattern,
                          exclude=exclude)
        if not observer:
            return
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


def _watch(root='.', dest='_site', pattern='**/*.html', exclude='_*/**'):

    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        msg = "The build --watch feature requires watchdog. \n"\
            + "Please install it with 'easy_install watchdog'."
        print(msg)
        return None

    class handler(FileSystemEventHandler):
        def on_any_event(self, event):
            exclude_path = os.path.join(os.getcwd(), exclude)
            if not utils.matches_pattern(exclude_path, event.src_path):
                build_files(root=root,
                            dest=dest,
                            pattern=pattern,
                            exclude=exclude)

    observer = Observer()
    observer.schedule(handler(), root, recursive=True)
    observer.start()

    print("Watching '{0}' ...".format(root))

    return observer


def serve_files(root='.', dest='_site', pattern='**/*.html', 
                exclude='_*/**', watch=False, port=8000, force=False):

    # setup server

    class RequestHandler(SimpleHTTPRequestHandler):
        
        def translate_path(self, path):
            root = os.path.join(os.getcwd(), dest)

            # normalize path and prepend root directory
            path = path.split('?',1)[0]
            path = path.split('#',1)[0]
            if sys.version > '3':
                path = posixpath.normpath(urllib.parse.unquote(path))
            else:
                path = posixpath.normpath(urllib.unquote(path))
            words = path.split('/')
            words = [_f for _f in words if _f]
            
            path = root
            for word in words:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir):
                    continue
                path = os.path.join(path, word)

            return path

    class StoppableHTTPServer(HTTPServer):

        def serve_until_shutdown(self):
            self._stopped = False
            while not self._stopped:
                try:
                    httpd.handle_request()
                except:
                    self._stopped=True
                    self.server_close()


        def shutdown(self):
            self._stopped = True            
            self.server_close()

    server_address = ('', port)
    httpd = StoppableHTTPServer(server_address, RequestHandler)
    server_thread = threading.Thread(
        target=httpd.serve_until_shutdown)
    server_thread.daemon = True
    server_thread.start()

    print("HTTP server started on port {0}".format(server_address[1]))

    # build files

    build_files(root=root,
                dest=dest,
                pattern=pattern,
                exclude=exclude,
                force=force)

    # watch files while server running

    if watch:
        observer = _watch(root=root,
                          dest=dest,
                          pattern=pattern,
                          exclude=exclude)
        if not observer:
            return
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            httpd.shutdown()
        observer.join()

    else:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            httpd.shutdown()



NEW_INDEX_STR = """<!DOCTYPE html>
<html>
{% include _partials/header.html %}
<body>
  {% include _partials/nav.html %}
  <h1>Welcome!</h1>
</body>
</html>"""

NEW_ABOUT_STR = """<!DOCTYPE html>
<html>
{% include _partials/header.html %}
<body>
  {% include _partials/nav.html %}
  <h1>About!</h1>
</body>
</html>"""

NEW_HEADER_STR = """
<head>
  <title>My new site</title>
  <link rel="stylesheet" href="/css/style.css" />
</head>"""

NEW_NAV_STR = """
  <ul>
    <li>
      <a href="/"{% is index.html %} class="active"{% endis %}>
        home
      </a>
    </li>
    <li>
      <a href="/about.html"{% is about.html %} class="active"{% endis %}>
        about
      </a>
    </li>
  </ul>"""

NEW_STYLE_STR = """.active {font-weight:bold;}"""

NEW_SITE = {
    'index.html': NEW_INDEX_STR,
    'about.html': NEW_ABOUT_STR,
    '_partials/header.html': NEW_HEADER_STR,
    '_partials/nav.html': NEW_NAV_STR,
    'css/style.css': NEW_STYLE_STR
}

def new_site(root='.', force=False):
    try:
        os.stat(os.path.join(root, 'index.html'))
        if not force:
            msg = "Oops, there's already an index.html file in the source \n"+\
                  "folder. If you want to overwrite this folder with a new \n"+\
                  "site, use the --force option."
            print(msg)
            sys.exit(1)
    except OSError:
        pass

    print("Creating new site in '{0}'.".format(root))

    for fname, text in list(NEW_SITE.items()):
        fpath = os.path.join(root, fname)
        with utils.open_file(fpath, "w", create_dir=True) as afile:
            afile.write(text)
