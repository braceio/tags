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


## Extending Brace Tags

Tags was built to be easily extended. You can easily add your own tags to implement custom functionality. 

In the `/tags/tags.py` file you'll find a function for each template tag. Add your own tag requires two steps:

1. Create a new function that will be called by the generator when it encounters your tag. It should look like this:

         def print3x_tag(args, context, body=u''):
             ''' A function that appends 3 copies of the body '''
             return body + body + body

   The arguments that the function accepts should be:

   - *args*: A list of arguments. These will show up in the opening tag, 
     for example `{% print3x bold %} HAHA! {% endprint3x %}`.
   - *context*: A dictionary that contains contextual data that was passed 
     in by the generator. By default it includes only a `filename` key.
   - *body* (optional): If the tag has a body, contained within an open tag, 
     and an end tag, it will be passed in as the `body` keyword argument.

2. Add the function to the `keys` dictionary that's used to create the template language. For example:

         tags = {
             'include': include_tag,
             'is': is_tag,
             'print3x': print3x_tag  # <-- my new tag
         }
         lang = TemplateLanguage(tags)

That's it!

