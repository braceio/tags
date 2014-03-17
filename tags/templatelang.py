from pyparsing import *

class TagErrorException(ParseBaseException):
    def __init__(self, parsestr, loc, exc):
        msg = unicode(exc)
        super(TagErrorException, self).__init__(parsestr, loc=loc, msg=msg)


def debug_action(name=''):
    def _wrapped(parsestr, loc, tokens):
        print name, ": ", parsestr[0:loc], '*', parsestr[loc:], "-->", tokens
    return _wrapped


class TemplateLanguage(object):

    def _mkopentag(self, name):
        tagname = CaselessKeyword(name)
        quote = quotedString.setParseAction(removeQuotes)
        arg = Optional(White()).suppress() + CharsNotIn(u" \t\r\n")
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
        onechar = CharsNotIn(u'', exact=1)
        freetext = Combine(OneOrMore(~self._tagopen + ~self._tagclose + onechar))
        anytag = Forward()
        body = originalTextFor(ZeroOrMore(anytag | freetext))
        anytag << MatchFirst([self._mktag(key, body) for key in tags.keys()])
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
            kwargs = {'body': tokens[2]} if len(tokens) > 2 else {}
            try:
                processed = fn(args, context, **kwargs)
            except ParseBaseException:
                raise
            except Exception as e:
                raise TagErrorException(parsestr, loc, e)
            return self.parse(processed, **context)
        return _parsefn


    def __init__(self, tags, openseq=u'{%', closeseq=u'%}'):
        self._tags = tags
        self._openseq = openseq
        self._tagopen = Literal(openseq).suppress()
        self._tagclose = Literal(closeseq).suppress()
        self._parser = self._mkparser(tags)


    def parse(self, string, **context):
        if self._openseq in string:
            parsefn = self._mkparsefn(context.copy())
            parser = self._parser.copy()
            parser.setParseAction(parsefn)
            return parser.transformString(string)
        else:
            return string

