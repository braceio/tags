from pyparsing import *
import inspect


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------

class TagErrorArguments(Exception):
    def __init__(self, tagname, nargs, args):
        params = (tagname, nargs, " ".join(args))
        errstr = "malformed tag '{0}' should have {1} argument(s), got '{2}'"
        self.msg = errstr.format(*params)

    def __str__(self):
        return self.msg


class TagErrorBody(Exception):
    def __init__(self, tagname, req_body, has_body):
        req = '' if req_body else "n't"
        has = 'does' if has_body else "doesn't"
        params = (tagname, req, has)
        errstr = "malformed tag '{0}' should{1} have a body, but {2}"
        self.msg = errstr.format(*params)

    def __str__(self):
        return self.msg


class TagErrorException(ParseBaseException):
    def __init__(self, parsestr, loc, exc, dev=False):
        if dev:
            import traceback
            msg = traceback.print_exc()
        else:
            msg = str(exc)
        super(TagErrorException, self).__init__(parsestr, loc=loc, msg=msg)


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

def debug_action(name=''):
    def _wrapped(parsestr, loc, tokens):
        print(name, ": ", parsestr[0:loc], '*', parsestr[loc:], "-->", tokens)
    return _wrapped


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class TemplateLanguage(object):
    ''' A generic tag-based language supporting nested tags. 

    Each tag has a name, optional arguments, and an optional closing tag.

    Examples: 

    {% tagname arg1 arg2 %}

    {% tagname args %}
        tag body
    {% endtagname %}

    The action performed by each tag must be supplied in a tag definition,
    either passed to the __init__ method, or by using the add_tag 
    decorators.
    '''

    # decorators --------------------------------------------------------------

    def add_tag_with_name(self, name):
        ''' Adds a tag to the language. 

        The function for the decorator should 
        accept a list of positional args, the context keyword arg, and an
        optional body keyword arg.

        Example:

        @language.add_tag_with_name('mytag')
        def tagfn(arg1, arg2, body=u'', context={}):
            return "tag args: {0}, body: {1}".format([arg1, arg2], body])

        The positional args define the required arguments for the tag. 
        If the body keyword arg is present the tag must have a body and
        closing tag.

        Tag argument checking won't happen if the development flag is set.
        '''
        def _decorator(fn):
            posargs, varargs, varkwargs, defaults = inspect.getargspec(fn)
            req_body = "body" in posargs
            nargs = len(posargs)
            if "context" in posargs:
                nargs -= 1
            if req_body:
                nargs -= 1

            def _wrapper(*args, **kwargs):
                if not self._development:
                    if (varargs and len(args) < nargs) or len(args) != nargs:
                        raise TagErrorArguments(name, nargs, args)
                    has_body = 'body' in kwargs
                    if has_body != req_body:
                        raise TagErrorBody(name, req_body, has_body)
                return fn(*args, **kwargs)

            self._tags[name] = _wrapper

            return _wrapper
        return _decorator


    def add_tag(self, fn):
        ''' Shortcut for add_tag_with_name.

        Uses the function's name as the tag name.

        Example:

        @language.add_tag
        def mytag(body=u'', context={}):
            return "tag body: "+body
        '''
        return self.add_tag_with_name(fn.__name__)(fn)


    # language specification --------------------------------------------------

    def _mkopentag(self, name):
        tagname = CaselessKeyword(name)
        quote = quotedString.setParseAction(removeQuotes)
        arg = Optional(White()).suppress() + CharsNotIn(" \t\r\n")
        args = Group(ZeroOrMore(quote | arg))
        rawargs = SkipTo(self._tagclose)
        rawargs.setParseAction(lambda toks: args.parseString(toks[0]))
        return self._tagopen + tagname + rawargs + self._tagclose


    def _mkclosetag(self, name):
        tagname = CaselessKeyword("end"+name)
        return self._tagopen + tagname.suppress() + self._tagclose


    def _mktag(self, name, body):
        opentag = self._mkopentag(name)
        closetag = self._mkclosetag(name)
        tag = opentag + body + closetag | opentag
        return tag


    def _mkparser(self, tags):
        onechar = CharsNotIn('', exact=1)
        freetext = Combine(OneOrMore(~self._tagopen + ~self._tagclose + onechar))
        anytag = Forward()
        body = originalTextFor(ZeroOrMore(anytag | freetext))
        anytag << MatchFirst([self._mktag(key, body) for key in list(tags.keys())])
        return anytag


    def _mkparsefn(self, context):
        def _parsefn(parsestr, loc, tokens):
            name, parseresult = tokens[:2]
            args = parseresult.asList()
            try:
                fn = self._tags[name]
            except KeyError:
                # This should never be reached since the parser 
                # won't match a tag that's not in the list
                raise
            kwargs = {'context': context}
            if len(tokens) > 2:
                kwargs.update({'body': tokens[2]})
            try:
                processed = fn(*args, **kwargs)
            except ParseBaseException:
                raise
            except Exception as e:
                raise TagErrorException(parsestr, loc, e, self._development)
            return self.parse(processed, **context)
        return _parsefn


    # public methods ----------------------------------------------------------

    def __init__(self, tags=None, openseq='{%', closeseq='%}', development=False):
        ''' Creates a new template language instance.

        If the tag keyword argument isn't provided, tags should be created
        using the add_tag decorators. Otherwise, tags should be a dictionairy
        of name/function pairs.

        If the development flag is set, tag argument checking is disabled and
        errors will include a stack trace.
        '''
        self._tags = {}
        self._development = development
        self._openseq = openseq
        self._tagopen = Literal(openseq).suppress()
        self._tagclose = Literal(closeseq).suppress()

        if tags:
            for name, fn in tags.items():
                self.add_tag_with_name(name)(fn)
            self._parser = self._mkparser(self._tags)
        else:
            self._parser = None


    def parse(self, string, **context):
        ''' Parses a template string. 

        For each tag in the input string, calls the tag functions and replaces
        the tag with the function results. Keyword arguments provided to parse 
        will be added to the context passed to the tag functions.
        '''
        if self._openseq in string:
            if not self._parser:
                self._parser = self._mkparser(self._tags)
            parsefn = self._mkparsefn(context.copy())
            parser = self._parser.copy()
            parser.setParseAction(parsefn)
            return parser.transformString(string)
        else:
            return string

