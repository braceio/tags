Brace Tags
==========

> The simplest static site generator

Tags is a command line static site generator focused on simplicity. There are only two tags: `include` and `is`. It's meant for building multi-page static sites with common navigation and footer code.

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
        <a href="/" {% is index.html %}class="active"{% endis %}>
      </li>
      <li>
        <a href="/about.html" {% is about.html %}class="active"{% endis %}>
      </li>
    </ul>        


That's basically all there is to Brace Tags. There's almost zero convention or syntax to learn. It doesn't currently support markdown, or provide fancy optimizations. It's just here to help you avoid duplicating HTML boilerplate on several web pages.


## Installing Brace Tags

Brace Tags is written in Python. Most computers today come with Python. You can install it with `easy_install` by opening up your terminal and typing in:

    sudo easy_install brace-tags

(The sudo part will ask you to log-in. It's required because Brace Tags needs to install the `tags` command line script.)

Alternatively, if you're familiar with Python, you can use pip to install it:

    pip install brace-tags

Brace has one external dependency, `watchdog` which is only required if you want to use Brace to monitor a folder for changes, and recompile your site on the fly. Before using the `--watch` option you'll need to install `watchdog`.

    easy_install watchdog


## Using Brace Tags

Tags has two commands, the `build` command and the `serve` command. Build is used to generate a site from a source folder. 

    tags build

By default, Brace Tags compiles all the .html files in your site. Tags places the generated site in the `_site` folder, and ignores those files during future builds. (In fact, it ignores all folders that start with an underscore.)

If you want to be specific about what files to compile, or where your site gets generated, you can specify that with the `--files` and `--out` options:

    tags build --files docs/*.html --out www/docs

As mentioned above, you can track the changes in your site folder and re-build automatically with the `--watch` option. However this requires that you first install `watchdog`.

    easy_install watchdog
    tags build --watch

The `serve` command will start a local webserver that you can use for testing. 

    tags serve

For more options and explanation, check out the help:

    tags --help


## Extending Brace Tags

Tags was built to be easily extended. You can add your own tags to implement custom functionality. 

In the `/tags/tags.py` file you'll find a function for each template tag. Adding your own tag requires three steps:

1.  Create a new function that will be called by the generator when it encounters your tag. It should look like this:

        def print3x_tag(args, context, body=u''):
            ''' A tag that appends 3 copies of its body '''
            return body + body + body

    The arguments that the function accepts should be: 
    - *args*: A list of arguments. These come from the opening tag, 
      for example `{% print3x bold italic %} HAHA! {% endprint3x %}` will 
      produce an args parameter of `['bold', 'italic']`.
    - *context*: A dictionary that contains contextual data that was passed 
      in by the generator. By default it includes only a `filename` key.
    - *body* (optional): If the tag has an opening tag and a closing tag, 
      the body is the content between the tags. It will be passed to your 
      function as the `body` keyword argument.

2. Add the function to the `keys` dictionary that's used to create the template language. For example:

        tags = {
            'include': include_tag,
            'is': is_tag,
            'print3x': print3x_tag  # <-- my new tag
        }
        lang = TemplateLanguage(tags)

3. Use your tag in your own html files:

        <p> pretty sweet site, don't you think? <p>
        {% print3x %}
          <h1> ROBOTS MADE IT FOR ME </h1>
        {% endprint3x %}

