Brace Tags
==========

> The simplest static site generator

Tags is a command line static site generator focused on simplicity. There are
only two tags: `include` and `is`. It's meant for building multi-page static
sites with common navigation and footer code.

Here's an example site using Tags:

index.html:

    <html>
      <body>
        {% include nav.html %}
        Welcome to Brace Tags!
      </body>
    </html>


about.html:

    <html>
      <body>
        {% include nav.html %}
        Tags is very simple!
      </body>
    </html>


nav.html:

    <ul>
      <li>
        <a href="/" {% is index.html %}class="active"{% endis %}>home</a>
      </li>
      <li>
        <a href="/about.html" {% is about.html %}class="active"{% endis %}>about</a>
      </li>
    </ul>        


That's basically all there is to Brace Tags. There's almost zero convention or
syntax to learn. It doesn't currently support markdown, or provide fancy
optimizations. It's just here to help you avoid duplicating HTML boilerplate on
several web pages.


## Installing Brace Tags

Brace Tags is written in Python. Most computers today come with Python. You can
install it with `easy_install` by opening up your terminal and typing in:

    sudo easy_install brace-tags

(The sudo part will ask you to log-in. It's required because Brace Tags needs to
install the `tags` command line script.)

Alternatively, if you're familiar with Python, you can use pip to install it:

    pip install brace-tags

Brace has one external dependency, `watchdog` which is only required if you want
to use Brace to monitor a folder for changes, and recompile your site on the
fly. Before using the `--watch` option you'll need to install `watchdog`.

    easy_install watchdog


## Using Brace Tags

Tags has two commands, the `build` command and the `serve` command. Build is
used to generate a site from a source folder.

    tags build

By default, Brace Tags compiles all the .html files in your site. Tags places
the generated site in the `_site` folder, and ignores those files during future
builds. (In fact, it ignores all folders that start with an underscore.)

If you want to be specific about what files to compile, or where your site gets
generated, you can specify that with the `--files` and `--out` options:

    tags build --files docs/*.html --out www/docs

As mentioned above, you can track the changes in your site folder and re-build
automatically with the `--watch` option. However this requires that you first
install `watchdog`.

    easy_install watchdog
    tags build --watch

The `serve` command will start a local webserver that you can use for testing. 

    tags serve

For more options and explanation, check out the help:

    tags --help


## Extending Brace Tags

Brace Tags was built to be easily extended. You can add your own tags to
implement custom functionality.

A custom tag should look like this:

    {% mytag argument1 argument2 %}

Optionally, a tag can have a body, like this:

    {% mytag %}
      Tag Body
    {% endmytag %}

When Tags generates a file, each time it encounters a tag in the input, it
checks for a corresponding tag function. If the function exists, it is called
and returns a string that's substituted in the output.

In the `/tags/tags.py` file you'll find a function for each template tag. Add
your custom tag functions here. They should look something like this:

    @lang.add_tag
    def print3x(style, body=u'', context={}):
        ''' A tag that appends 3 copies of its body '''
        result = body + body + body
        if style == "bold":
            result = u'<b>' + result + u'</b>'
        return result

The above function defines a print3x tag that would be called like this:

    {% print3x bold %}
      <h1> ROBOTS, MAKE MY HTML! </h1>
    {% endprint3x %}
    
When adding a new tag function, here are some things you should know:

- The `add_tag` decorator adds the tag function to the template language.

- The tag's name is taken from the function's name. For example, the function
above creates a `print3x` tag. Optionally you can use the `add_tag_with_name`
decorator to supply a tag name.

- The positional arguments of the function define the tag's required arguments.
In this case the tag requires one argument, `style`.

- If you specify a `body` keyword argument, then the tag will require a body.
The body is the content between the opening tag and an end tag.

- All tag functions must accept a `context` keyword argument. This is a
dictionary containing contextual data passed in by the generator. By default,
context includes a `filename` key whose value is the file currently being
generated.


You can also define tags that accept a variable argument list like so:

    @lang.add_tag
    def whatever(*args, **kwargs):
        return str(len(args))


When called, the `*args` parameter will contain the variable argument list, and
the `body` and `context` keyword args will be in the `**kwargs` dictionary.
