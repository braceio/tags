import os
import sys

from .templatelang import TemplateLanguage

lang = TemplateLanguage(openseq='{%', closeseq='%}')

@lang.add_tag
def include(path, context={}):
    '''
    Renders the content of a file. File paths should be relative
    to the site's root folder. Ex: {% include nav.html %}
    '''
    fullpath = os.path.join(context.get('rootdir'), path)
    if sys.version > '3':
        stuff = str(open(fullpath).read(), 'utf-8')
    else:
        stuff = unicode(open(fullpath).read(), 'utf-8')
    return stuff


@lang.add_tag_with_name('is')
def _is(path, body='', context={}):
    '''
    Renders the tag body if the path matches the current file. File paths 
    should be relative to the site's root folder. 
    Ex: {% is index.html %}Home!{% endis %}
    '''
    return body if path == context.get('filename') else ''


# ---- Add your custom tags here! -----

# Example:

# @lang.add_tag
# def print3x(style, body=u'', context={}):
#     ''' A tag that appends 3 copies of its body '''
#     result = body + body + body
#     if style == "bold":
#         result = u'<b>' + result + u'</b>'
#     return result

# Notes:

# - positional arguments define the tag's required arguments.
# - If you specify a `body` keyword argument, then the tag will require a body.
# - All tag functions must accept a `context` keyword argument. 

# You can also define tags that accept a variable argument list like so:

# @lang.add_tag
# def whatever(*args, **kwargs):
#     return str(len(args))


def render(content, filename='', rootdir='.'):
    ''' 
    Renders a content string containing template code into an output string. 
    Uses the tags specified above. Filename and rootdir are added to the 
    context passed to the tag functions.
    '''
    return lang.parse(content, filename=filename, rootdir=rootdir)
