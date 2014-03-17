import os

from templatelang import TemplateLanguage

lang = TemplateLanguage(openseq=u'{%', closeseq=u'%}')

@lang.add_tag
def include(path, context={}):
    '''
    Renders the content of a file. File paths should be relative
    to the site's root folder. Ex: {% include nav.html %}
    '''
    fullpath = os.path.join(context.get('rootdir'), path)
    return open(fullpath).read()


@lang.add_tag_with_name('is')
def _is(path, body=u'', context={}):
    '''
    Renders the tag body if the path matches the current file. File paths 
    should be relative to the site's root folder. 
    Ex: {% is index.html %}Home!{% endis %}
    '''
    return body if path == context.get('filename') else u''


# ---- Add your own tags here! -----


def render(content, filename=u'', rootdir=u'.'):
    return lang.parse(content, filename=filename, rootdir=rootdir)