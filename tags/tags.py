import os

from templatelang import TemplateLanguage
from utils import checktag


@checktag(num_args=1, is_block=False)
def include_tag(args, context):
    path = os.path.join(context.get('rootdir'), args[0])
    return open(path).read()


@checktag(num_args=1, is_block=True)
def is_tag(args, context, body=u''):
    return body if args[0] == context.get('filename') else u''


tags = {
    'include': include_tag,
    'is': is_tag
}
lang = TemplateLanguage(tags)


def render(content, filename=u'', rootdir=u'.'):
    return lang.parse(content, filename=filename, rootdir=rootdir)
