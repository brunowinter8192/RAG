<!-- source: https://docs.searxng.org//dev/reST.html -->

# reST primer
[KISS](https://en.wikipedia.org/wiki/KISS_principle) and [readability](https://docs.python-guide.org/writing/style/)
Instead of defining more and more roles, we at SearXNG encourage our contributors to follow principles like [KISS](https://en.wikipedia.org/wiki/KISS_principle) and [readability](https://docs.python-guide.org/writing/style/).
We at SearXNG are using reStructuredText (aka [reST](https://docutils.sourceforge.io/rst.html)) markup for all kind of documentation. With the builders from the [Sphinx](https://www.sphinx-doc.org) project a HTML output is generated and deployed at [docs.searxng.org](https://docs.searxng.org/). For build prerequisites read [Build docs](https://docs.searxng.org/admin/buildhosts.html#docs-build).
The source files of SearXNG’s documentation are located at [git://docs](https://github.com/searxng/searxng/blob/master/docs). Sphinx assumes source files to be encoded in UTF-8 by default. Run [make docs.live](https://docs.searxng.org/dev/contribution_guide.html#make-docs-live) to build HTML while editing.
Further reading
  * [Sphinx-Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
  * [Sphinx markup constructs](https://www.sphinx-doc.org/en/stable/markup/index.html)
  * [reST](https://docutils.sourceforge.io/rst.html), [docutils](http://docutils.sourceforge.net/docs/index.html), [docutils FAQ](http://docutils.sourceforge.net/FAQ.html)
  * [Sphinx](https://www.sphinx-doc.org), [sphinx-doc FAQ](https://www.sphinx-doc.org/en/stable/faq.html)
  * [sphinx config](https://www.sphinx-doc.org/en/stable/config.html), [doctree](https://www.sphinx-doc.org/en/master/extdev/tutorial.html?highlight=doctree#build-phases)
  * [sphinx cross references](https://www.sphinx-doc.org/en/stable/markup/inline.html#cross-referencing-arbitrary-locations)
  * [linuxdoc](https://return42.github.io/linuxdoc)
  * [intersphinx](https://www.sphinx-doc.org/en/stable/ext/intersphinx.html)
  * [sphinx-jinja](https://github.com/tardyp/sphinx-jinja)
  * [Sphinx’s autodoc](https://www.sphinx-doc.org/en/stable/ext/autodoc.html)
  * [Sphinx’s Python domain](https://www.sphinx-doc.org/en/stable/domains.html#the-python-domain), [Sphinx’s C domain](https://www.sphinx-doc.org/en/stable/domains.html#cross-referencing-c-constructs)
  * [SVG](https://www.w3.org/TR/SVG11/expanded-toc.html), [ImageMagick](https://www.imagemagick.org)
  * [DOT](https://graphviz.gitlab.io/_pages/doc/info/lang.html), [Graphviz’s dot](https://graphviz.gitlab.io/_pages/pdf/dotguide.pdf), [Graphviz](https://graphviz.gitlab.io)

[Sphinx](https://www.sphinx-doc.org) and [reST](https://docutils.sourceforge.io/rst.html) have their place in the python ecosystem. Over that reST is used in popular projects, e.g the Linux kernel documentation [[kernel doc]](https://www.kernel.org/doc/html/latest/doc-guide/sphinx.html).
Content matters
The [readability](https://docs.python-guide.org/writing/style/) of the reST sources has its value, therefore we recommend to make sparse usage of reST markup / .. content matters!
**reST** is a plaintext markup language, its markup is _mostly_ intuitive and you will not need to learn much to produce well formed articles with. I use the word _mostly_ : like everything in live, reST has its advantages and disadvantages, some markups feel a bit grumpy (especially if you are used to other plaintext markups).
## Soft skills
Before going any deeper into the markup let’s face on some **soft skills** a trained author brings with, to reach a well feedback from readers:
  * Documentation is dedicated to an audience and answers questions from the audience point of view.
  * Don’t detail things which are general knowledge from the audience point of view.
  * Limit the subject, use cross links for any further reading.

To be more concrete what a _point of view_ means. In the ([git://docs](https://github.com/searxng/searxng/blob/master/docs)) folder we have three sections (and the _blog_ folder), each dedicate to a different group of audience. 

User’s POV: [git://docs/user](https://github.com/searxng/searxng/blob/master/docs/user) 
    
A typical user knows about search engines and might have heard about meta crawlers and privacy. 

Admin’s POV: [git://docs/admin](https://github.com/searxng/searxng/blob/master/docs/admin) 
    
A typical Admin knows about setting up services on a linux system, but he does not know all the pros and cons of a SearXNG setup. 

Developer’s POV: [git://docs/dev](https://github.com/searxng/searxng/blob/master/docs/dev) 
    
Depending on the [readability](https://docs.python-guide.org/writing/style/) of code, a typical developer is able to read and understand source code. Describe what a item aims to do (e.g. a function). If the chronological order matters, describe it. Name the _out-of-limits conditions_ and all the side effects a external developer will not know.
## Basic inline markup
Inline markup
Basic inline markup is done with asterisks and backquotes. If asterisks or backquotes appear in running text and could be confused with inline markup delimiters, they have to be escaped with a backslash (`\*pointer`).
Table 9 basic inline markup description | rendered | markup  
---|---|---  
one asterisk for emphasis | _italics_ | `*italics*`  
two asterisks for strong emphasis | **boldface** | `**boldface**`  
backquotes for code samples and literals | `foo()` | ```foo()```  
quote asterisks or backquotes | *foo is a pointer | `\*foo is a pointer`  
## Basic article structure
The basic structure of an article makes use of heading adornments to markup chapter, sections and subsections.
### reST template
reST template for an simple article:
```
.. _doc refname:

==============
Document title
==============

Lorem ipsum dolor sit amet, consectetur adipisici elit ..  Further read
:ref:`chapter refname`.

.. _chapter refname:

Chapter
=======

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
aliquid ex ea commodi consequat ...

.. _section refname:

Section
-------

lorem ..

.. _subsection refname:

Subsection
~~~~~~~~~~

lorem ..

```

### Headings
  1. title - with overline for document title:

> ```
==============
Document title
==============

```

  1. chapter - with anchor named `anchor name`:
```
.. _anchor name:

Chapter
=======

```

  2. section
```
Section
-------

```

  3. subsection
```
Subsection
~~~~~~~~~~

```

## Anchors & Links
### Anchors
To refer a point in the documentation a anchor is needed. The [reST template](https://docs.searxng.org//dev/reST.html#rest-template) shows an example where a chapter titled _“Chapters”_ gets an anchor named `chapter title`. Another example from _this_ document, where the anchor named `reST anchor`:
```
.. _reST anchor:

Anchors
-------

To refer a point in the documentation a anchor is needed ...

```

To refer anchors use the [ref role](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-ref) markup:
```
Visit chapter :ref:`reST anchor`.  Or set hyperlink text manually :ref:`foo
bar <reST anchor>`.

```

`:ref:` role
Visit chapter [Anchors](https://docs.searxng.org//dev/reST.html#rest-anchor). Or set hyperlink text manually [foo bar](https://docs.searxng.org//dev/reST.html#rest-anchor).
### Link ordinary URL
If you need to reference external URLs use _named_ hyperlinks to maintain readability of reST sources. Here is a example taken from _this_ article:
```
.. _Sphinx Field Lists:
   https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html

With the *named* hyperlink `Sphinx Field Lists`_, the raw text is much more
readable.

And this shows the alternative (less readable) hyperlink markup `Sphinx Field
Lists
<https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html>`__.

```

Named hyperlink
With the _named_ hyperlink [Sphinx Field Lists](https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html), the raw text is much more readable.
And this shows the alternative (less readable) hyperlink markup [Sphinx Field Lists](https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html).
### Smart refs
With the power of [sphinx.ext.extlinks](https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html) and [intersphinx](https://www.sphinx-doc.org/en/stable/ext/intersphinx.html) referencing external content becomes smart.
Table 10 smart refs with [sphinx.ext.extlinks](https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html) and [intersphinx](https://www.sphinx-doc.org/en/stable/ext/intersphinx.html) refer … | rendered example | markup  
---|---|---  
[`rfc`](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-rfc "\(in Sphinx v9.1.0\)") | [**RFC 822**](https://datatracker.ietf.org/doc/html/rfc822.html) | `:rfc:`822``  
[`pep`](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-pep "\(in Sphinx v9.1.0\)") | [**PEP 8**](https://peps.python.org/pep-0008/) | `:pep:`8``  
[sphinx.ext.extlinks](https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html)  
project’s wiki article | [ Offline-engines](https://github.com/searxng/searxng/wiki/Offline-engines) | `:wiki:`Offline-engines``  
to docs public URL | [docs: dev/reST.html](https://docs.searxng.org//dev/reST.html) | `:docs:`dev/reST.html``  
files & folders origin | [git://docs/dev/reST.rst](https://github.com/searxng/searxng/blob/master/docs/dev/reST.rst) | `:origin:`docs/dev/reST.rst``  
pull request | [PR 4](https://github.com/searxng/searxng/pull/4) | `:pull:`4``  
patch | [#af2cae6](https://github.com/searxng/searxng/commit/af2cae6) | `:patch:`af2cae6``  
PyPi package | [PyPi: httpx](https://pypi.org/project/httpx) | `:pypi:`httpx``  
manual page man | [bash](https://manpages.debian.org/jump?q=bash) | `:man:`bash``  
[intersphinx](https://www.sphinx-doc.org/en/stable/ext/intersphinx.html)  
external anchor | [Boolean operations](https://docs.python.org/3/reference/expressions.html#and "\(in Python v3.14\)") | `:ref:`python:and``  
external doc anchor | [Template Designer Documentation](https://jinja.palletsprojects.com/en/stable/templates/ "\(in Jinja v3.1.x\)") | `:doc:`jinja:templates``  
python code object | [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime "\(in Python v3.14\)") | `:py:obj:`datetime.datetime``  
flask code object | [`flask.Flask`](https://flask.palletsprojects.com/en/stable/api/#flask.Flask "\(in Flask v3.1.x\)") | `:py:obj:`flask.Flask``  
Intersphinx is configured in [git://docs/conf.py](https://github.com/searxng/searxng/blob/master/docs/conf.py):
```
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "flask": ("https://flask.palletsprojects.com/", None),
    "jinja": ("https://jinja.palletsprojects.com/", None),
    "linuxdoc" : ("https://return42.github.io/linuxdoc/", None),
    "sphinx" : ("https://www.sphinx-doc.org/en/master/", None),
}

```

To list all anchors of the inventory (e.g. `python`) use:
```
$ python -m sphinx.ext.intersphinx https://docs.python.org/3/objects.inv
...
$ python -m sphinx.ext.intersphinx https://docs.searxng.org/objects.inv
...

```

## Literal blocks
The simplest form of [literal-blocks](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#literal-blocks) is a indented block introduced by two colons (`::`). For highlighting use [highlight](https://docutils.sourceforge.io/docs/ref/rst/directives.html#highlight) or [code-block](https://docs.searxng.org//dev/reST.html#rest-code) directive. To include literals from external files use [`literalinclude`](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-literalinclude "\(in Sphinx v9.1.0\)") or [kernel-include](https://return42.github.io/linuxdoc/linuxdoc-howto/kernel-include-directive.html#kernel-include-directive "\(in LinuxDoc v20240924.dev1\)") directive (latter one expands environment variables in the path name).
### `::`
```
::

  Literal block

Lorem ipsum dolor::

  Literal block

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy
eirmod tempor invidunt ut labore ::

  Literal block

```

Literal block
```
Literal block

```

Lorem ipsum dolor:
```
Literal block

```

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore
```
Literal block

```

### `code-block`
Syntax highlighting
is handled by [pygments](https://pygments.org/languages/).
The [`code-block`](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code-block "\(in Sphinx v9.1.0\)") directive is a variant of the [code](https://docutils.sourceforge.io/docs/ref/rst/directives.html#code) directive with additional options. To learn more about code literals visit [Showing code examples](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#code-examples "\(in Sphinx v9.1.0\)").
```
The URL ``/stats`` handle is shown in :ref:`stats-handle`

.. code-block:: Python
   :caption: python code block
   :name: stats-handle

   @app.route('/stats', methods=['GET'])
   def stats():
       """Render engine statistics page."""
       stats = get_engines_stats()
       return render(
           'stats.html'
           , stats = stats )

```

```

```

Code block
The URL `/stats` handle is shown in [python code block](https://docs.searxng.org//dev/reST.html#stats-handle)
Listing 1 python code block
```
@app.route('/stats', methods=['GET'])
def stats():
    """Render engine statistics page."""
    stats = get_engines_stats()
    return render(
        'stats.html'
        , stats = stats )

```

## Unicode substitution
The [unicode directive](https://docutils.sourceforge.io/docs/ref/rst/directives.html#unicode-character-codes) converts Unicode character codes (numerical values) to characters. This directive can only be used within a substitution definition.
```
.. |copy| unicode:: 0xA9 .. copyright sign
.. |(TM)| unicode:: U+2122

Trademark |(TM)| and copyright |copy| glyphs.

```

Unicode
Trademark ™ and copyright © glyphs.
## Roles
Further reading
  * [Sphinx Roles](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html)
  * [MOVED: Domains](https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html "\(in Sphinx v9.1.0\)")

A _custom interpreted text role_ ([ref](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#roles)) is an inline piece of explicit markup. It signifies that that the enclosed text should be interpreted in a specific way.
The general markup is one of:
```
:rolename:`ref-name`
:rolename:`ref text <ref-name>`

```

Table 11 smart refs with [sphinx.ext.extlinks](https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html) and [intersphinx](https://www.sphinx-doc.org/en/stable/ext/intersphinx.html) role | rendered example | markup  
---|---|---  
[`guilabel`](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-guilabel "\(in Sphinx v9.1.0\)") | Cancel | `:guilabel:`&Cancel``  
[`kbd`](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-kbd "\(in Sphinx v9.1.0\)") | `C`-`x` `C`-`f` | `:kbd:`C-x C-f``  
[`menuselection`](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-menuselection "\(in Sphinx v9.1.0\)") | Open ‣ File | `:menuselection:`Open --> File``  
[`download`](https://www.sphinx-doc.org/en/master/usage/referencing.html#role-download "\(in Sphinx v9.1.0\)") | [`this file`](https://docs.searxng.org/_downloads/ad0ebe55d6b53b1559e0ca8dee6f30b9/reST.rst) | `:download:`this file <reST.rst>``  
[math](https://docs.searxng.org//dev/reST.html#math) | a^2 + b^2 = c^2 | `:math:`a^2 + b^2 = c^2``  
[`ref`](https://www.sphinx-doc.org/en/master/usage/referencing.html#role-ref "\(in Sphinx v9.1.0\)") | [Simple SVG image.](https://docs.searxng.org//dev/reST.html#svg-image-example) | `:ref:`svg image example``  
[`command`](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-command "\(in Sphinx v9.1.0\)") | **ls -la** | `:command:`ls -la``  
[emphasis](https://docutils.sourceforge.io/docs/ref/rst/roles.html#emphasis) | _italic_ | `:emphasis:`italic``  
[strong](https://docutils.sourceforge.io/docs/ref/rst/roles.html#strong) | **bold** | `:strong:`bold``  
[literal](https://docutils.sourceforge.io/docs/ref/rst/roles.html#literal) | `foo()` | `:literal:`foo()``  
[subscript](https://docutils.sourceforge.io/docs/ref/rst/roles.html#subscript) | H2O | `H\ :sub:`2`\ O`  
[superscript](https://docutils.sourceforge.io/docs/ref/rst/roles.html#superscript) | E = mc2 | `E = mc\ :sup:`2``  
[title-reference](https://docutils.sourceforge.io/docs/ref/rst/roles.html#title-reference) | Time | `:title:`Time``  
## Figures & Images
Image processing
With the directives from [linuxdoc](https://return42.github.io/linuxdoc/linuxdoc-howto/kfigure.html#kfigure "\(in LinuxDoc v20240924.dev1\)") the build process is flexible. To get best results in the generated output format, install [ImageMagick](https://www.imagemagick.org) and [Graphviz](https://graphviz.gitlab.io).
SearXNG’s sphinx setup includes: [Scalable figure and image handling](https://return42.github.io/linuxdoc/linuxdoc-howto/kfigure.html#kfigure "\(in LinuxDoc v20240924.dev1\)"). Scalable here means; scalable in sense of the build process. Normally in absence of a converter tool, the build process will break. From the authors POV it’s annoying to care about the build process when handling with images, especially since he has no access to the build process. With [Scalable figure and image handling](https://return42.github.io/linuxdoc/linuxdoc-howto/kfigure.html#kfigure "\(in LinuxDoc v20240924.dev1\)") the build process continues and scales output quality in dependence of installed image processors.
If you want to add an image, you should use the `kernel-figure` (inheritance of [figure](https://docutils.sourceforge.io/docs/ref/rst/directives.html#figure)) and `kernel-image` (inheritance of [image](https://docutils.sourceforge.io/docs/ref/rst/directives.html#image)) directives. E.g. to insert a figure with a scalable image format use SVG ([Simple SVG image.](https://docs.searxng.org//dev/reST.html#svg-image-example)):
```
.. _svg image example:

.. kernel-figure:: svg_image.svg
   :alt: SVG image example

   Simple SVG image

 To refer the figure, a caption block is needed: :ref:`svg image example`.

```

![SVG image example](https://docs.searxng.org/_images/svg_image.svg)
Fig. 4 Simple SVG image.
To refer the figure, a caption block is needed: [Simple SVG image.](https://docs.searxng.org//dev/reST.html#svg-image-example).
### DOT files (aka Graphviz)
With [kernel-figure & kernel-image](https://return42.github.io/linuxdoc/linuxdoc-howto/kfigure.html#kernel-figure "\(in LinuxDoc v20240924.dev1\)") reST support for **DOT** formatted files is given.
  * [Graphviz’s dot](https://graphviz.gitlab.io/_pages/pdf/dotguide.pdf)
  * [DOT](https://graphviz.gitlab.io/_pages/doc/info/lang.html)
  * [Graphviz](https://graphviz.gitlab.io)

A simple example is shown in [DOT’s hello world example](https://docs.searxng.org//dev/reST.html#dot-file-example):
```
.. _dot file example:

.. kernel-figure:: hello.dot
   :alt: hello world

   DOT's hello world example

```

hello.dot
```
graph G {
      Hello -- World
}

```

Fig. 5 DOT’s hello world example
### `kernel-render` DOT
Embed _render_ markups (or languages) like Graphviz’s **DOT** is provided by the [kernel-render](https://return42.github.io/linuxdoc/linuxdoc-howto/kfigure.html#kernel-render "\(in LinuxDoc v20240924.dev1\)") directive. A simple example of embedded [DOT](https://graphviz.gitlab.io/_pages/doc/info/lang.html) is shown in figure [Embedded DOT (Graphviz) code](https://docs.searxng.org//dev/reST.html#dot-render-example):
```
.. _dot render example:

.. kernel-render:: DOT
   :alt: digraph
   :caption: Embedded  DOT (Graphviz) code

   digraph foo {
     "bar" -> "baz";
   }

Attribute ``caption`` is needed, if you want to refer the figure: :ref:`dot
render example`.

```

Please note [build tools](https://return42.github.io/linuxdoc/linuxdoc-howto/kfigure.html#kfigure-build-tools "\(in LinuxDoc v20240924.dev1\)"). If [Graphviz](https://graphviz.gitlab.io) is installed, you will see an vector image. If not, the raw markup is inserted as _literal-block_.
kernel-render DOT
```
digraph foo {
  "bar" -> "baz";
}

```

Fig. 6 Embedded DOT (Graphviz) code
Attribute `caption` is needed, if you want to refer the figure: [Embedded DOT (Graphviz) code](https://docs.searxng.org//dev/reST.html#dot-render-example).
### `kernel-render` SVG
A simple example of embedded [SVG](https://www.w3.org/TR/SVG11/expanded-toc.html) is shown in figure [Embedded SVG markup](https://docs.searxng.org//dev/reST.html#svg-render-example):
```
.. _svg render example:

.. kernel-render:: SVG
   :caption: Embedded **SVG** markup
   :alt: so-nw-arrow

```

> ```
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1"
     baseProfile="full" width="70px" height="40px"
     viewBox="0 0 700 400"
     >
  <line x1="180" y1="370"
        x2="500" y2="50"
        stroke="black" stroke-width="15px"
        />
  <polygon points="585 0 525 25 585 50"
           transform="rotate(135 525 25)"
           />
</svg>

```

kernel-render SVG
![so-nw-arrow](https://docs.searxng.org/_images/SVG-1fb7029fa2cc454a267bae271cccb2c591387416.svg)
Fig. 7 Embedded **SVG** markup
## List markups
### Bullet list
List markup ([ref](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#bullet-lists)) is simple:
```
- This is a bulleted list.

  1. Nested lists are possible, but be aware that they must be separated from
     the parent list items by blank line
  2. Second item of nested list

- It has two items, the second
  item uses two lines.

#. This is a numbered list.
#. It has two items too.

```

bullet list
  * This is a bulleted list.
    1. Nested lists are possible, but be aware that they must be separated from the parent list items by blank line
    2. Second item of nested list
  * It has two items, the second item uses two lines.

  1. This is a numbered list.
  2. It has two items too.

### Horizontal list
The [`.. hlist::`](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-hlist "\(in Sphinx v9.1.0\)") transforms a bullet list into a more compact list.
```
.. hlist::

   - first list item
   - second list item
   - third list item
   ...

```

hlist
  * first list item
  * second list item
  * third list item
  * next list item

| 
  * next list item xxxx
  * next list item yyyy
  * next list item zzzz

  
---|---  
### Definition list
Note ..
  * the term cannot have more than one line of text
  * there is **no blank line between term and definition block** // this distinguishes definition lists ([ref](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#definition-lists)) from block quotes ([ref](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#block-quotes)).

Each definition list ([ref](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#definition-lists)) item contains a term, optional classifiers and a definition. A term is a simple one-line word or phrase. Optional classifiers may follow the term on the same line, each after an inline ‘ : ‘ (**space, colon, space**). A definition is a block indented relative to the term, and may contain multiple paragraphs and other body elements. There may be no blank line between a term line and a definition block (_this distinguishes definition lists from block quotes_). Blank lines are required before the first and after the last definition list item, but are optional in-between.
Definition lists are created as follows:
```
term 1 (up to a line of text)
    Definition 1.

See the typo : this line is not a term!

  And this is not term's definition.  **There is a blank line** in between
  the line above and this paragraph.  That's why this paragraph is taken as
  **block quote** (:duref:`ref <block-quotes>`) and not as term's definition!

term 2
    Definition 2, paragraph 1.

    Definition 2, paragraph 2.

term 3 : classifier
    Definition 3.

term 4 : classifier one : classifier two
    Definition 4.

```

definition list 

term 1 (up to a line of text)
    
Definition 1.
See the typo : this line is not a term!
> And this is not term’s definition. **There is a blank line** in between the line above and this paragraph. That’s why this paragraph is taken as **block quote** ([ref](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#block-quotes)) and not as term’s definition! 

term 2
    
Definition 2, paragraph 1.
Definition 2, paragraph 2. 

term 3classifier 
    
Definition 3.
term 4 : classifier one : classifier two
### Quoted paragraphs
Quoted paragraphs ([ref](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#block-quotes)) are created by just indenting them more than the surrounding paragraphs. Line blocks ([ref](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#line-blocks)) are a way of preserving line breaks:
```
normal paragraph ...
lorem ipsum.

   Quoted paragraph ...
   lorem ipsum.

| These lines are
| broken exactly like in
| the source file.

```

Quoted paragraph and line block
normal paragraph … lorem ipsum.
> Quoted paragraph … lorem ipsum.
These lines are
broken exactly like in
the source file.
### Field Lists
bibliographic fields
First lines fields are bibliographic fields, see [Sphinx Field Lists](https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html).
Field lists are used as part of an extension syntax, such as options for directives, or database-like records meant for further processing. Field lists are mappings from field names to field bodies. They marked up like this:
```
:fieldname: Field content
:foo:       first paragraph in field foo

            second paragraph in field foo

:bar:       Field content

```

Field List 

fieldname: 
    
Field content 

foo: 
    
first paragraph in field foo
second paragraph in field foo 

bar: 
    
Field content
They are commonly used in Python documentation:
```
def my_function(my_arg, my_other_arg):
    """A function just for me.

    :param my_arg: The first of my arguments.
    :param my_other_arg: The second of my arguments.

    :returns: A message (just for me, of course).
    """

```

### Further list blocks
  * field lists ([ref](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#field-lists), with caveats noted in [Field Lists](https://docs.searxng.org//dev/reST.html#rest-field-list))
  * option lists ([ref](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#option-lists))
  * quoted literal blocks ([ref](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#quoted-literal-blocks))
  * doctest blocks ([ref](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#doctest-blocks))

## Admonitions
### Sidebar
Sidebar is an eye catcher, often used for admonitions pointing further stuff or site effects. Here is the source of the sidebar [on top of this page](https://docs.searxng.org//dev/reST.html#rest-primer).
```
.. sidebar:: KISS_ and readability_

   Instead of defining more and more roles, we at SearXNG encourage our
   contributors to follow principles like KISS_ and readability_.

```

### Generic admonition
The generic [admonition](https://docutils.sourceforge.io/docs/ref/rst/directives.html#admonitions) needs a title:
```
.. admonition:: generic admonition title

   lorem ipsum ..

```

generic admonition title
lorem ipsum ..
### Specific admonitions
Specific admonitions: [hint](https://docutils.sourceforge.io/docs/ref/rst/directives.html#hint), [note](https://docutils.sourceforge.io/docs/ref/rst/directives.html#note), [tip](https://docutils.sourceforge.io/docs/ref/rst/directives.html#tip) [attention](https://docutils.sourceforge.io/docs/ref/rst/directives.html#attention), [caution](https://docutils.sourceforge.io/docs/ref/rst/directives.html#caution), [danger](https://docutils.sourceforge.io/docs/ref/rst/directives.html#danger), [error](https://docutils.sourceforge.io/docs/ref/rst/directives.html#error), , [important](https://docutils.sourceforge.io/docs/ref/rst/directives.html#important), and [warning](https://docutils.sourceforge.io/docs/ref/rst/directives.html#warning) .
```
.. hint::

   lorem ipsum ..

.. note::

   lorem ipsum ..

.. warning::

   lorem ipsum ..

```

Hint
lorem ipsum ..
Note
lorem ipsum ..
Tip
lorem ipsum ..
Attention
lorem ipsum ..
Caution
lorem ipsum ..
Danger
lorem ipsum ..
Important
lorem ipsum ..
Error
lorem ipsum ..
Warning
lorem ipsum ..
## Tables
Nested tables
Nested tables are ugly! Not all builder support nested tables, don’t use them!
ASCII-art tables like [Simple tables](https://docs.searxng.org//dev/reST.html#rest-simple-table) and [Grid tables](https://docs.searxng.org//dev/reST.html#rest-grid-table) might be comfortable for readers of the text-files, but they have huge disadvantages in the creation and modifying. First, they are hard to edit. Think about adding a row or a column to a ASCII-art table or adding a paragraph in a cell, it is a nightmare on big tables.
List tables
For meaningful patch and diff use [flat-table](https://docs.searxng.org//dev/reST.html#rest-flat-table).
Second the diff of modifying ASCII-art tables is not meaningful, e.g. widening a cell generates a diff in which also changes are included, which are only ascribable to the ASCII-art. Anyway, if you prefer ASCII-art for any reason, here are some helpers:
  * [Emacs Table Mode](https://www.emacswiki.org/emacs/TableMode)
  * [Online Tables Generator](https://www.tablesgenerator.com/text_tables)

### Simple tables
[Simple tables](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#simple-tables) allow _colspan_ but not _rowspan_. If your table need some metadata (e.g. a title) you need to add the `.. table:: directive` [(ref)](https://docutils.sourceforge.io/docs/ref/rst/directives.html#table) in front and place the table in its body:
```
.. table:: foo gate truth table
   :widths: grid
   :align: left

   ====== ====== ======
       Inputs    Output
   ------------- ------
   A      B      A or B
   ====== ====== ======
   False
   --------------------
   True
   --------------------
   True   False  True
          (foo)
   ------ ------ ------
   False  True
          (foo)
   ====== =============

```

Simple ASCII table
Table 12 foo gate truth table Inputs | Output  
---|---  
A | B | A or B  
False  
True  
True | False (foo) | True  
False | True (foo)  
### Grid tables
[Grid tables](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#grid-tables) allow colspan _colspan_ and _rowspan_ :
```
.. table:: grid table example
   :widths: 1 1 5

   +------------+------------+-----------+
   | Header 1   | Header 2   | Header 3  |
   +============+============+===========+
   | body row 1 | column 2   | column 3  |
   +------------+------------+-----------+
   | body row 2 | Cells may span columns.|
   +------------+------------+-----------+
   | body row 3 | Cells may  | - Cells   |
   +------------+ span rows. | - contain |
   | body row 4 |            | - blocks. |
   +------------+------------+-----------+

```

ASCII grid table
Table 13 grid table example Header 1 | Header 2 | Header 3  
---|---|---  
body row 1 | column 2 | column 3  
body row 2 | Cells may span columns.  
body row 3 | Cells may span rows. | 
  * Cells
  * contain
  * blocks.

  
body row 4  
### flat-table
The `flat-table` is a further developed variant of the [list tables](https://return42.github.io/linuxdoc/linuxdoc-howto/table-markup.html#list-table-directives "\(in LinuxDoc v20240924.dev1\)"). It is a double-stage list similar to the [list-table](https://docutils.sourceforge.io/docs/ref/rst/directives.html#list-table) with some additional features: 

column-span: `cspan` 
    
with the role `cspan` a cell can be extended through additional columns 

row-span: `rspan` 
    
with the role `rspan` a cell can be extended through additional rows 

auto-span:
    
spans rightmost cell of a table row over the missing cells on the right side of that table-row. With Option `:fill-cells:` this behavior can changed from _auto span_ to _auto fill_ , which automatically inserts (empty) cells instead of spanning the last cell. 

options:
     

header-rows: 
    
[int] count of header rows 

stub-columns: 
    
[int] count of stub columns 

widths: 
    
[[int] [int] … ] widths of columns 

fill-cells: 
    
instead of auto-span missing cells, insert missing cells 

roles:
     

cspan: 
    
[int] additional columns (_morecols_) 

rspan: 
    
[int] additional rows (_morerows_)
The example below shows how to use this markup. The first level of the staged list is the _table-row_. In the _table-row_ there is only one markup allowed, the list of the cells in this _table-row_. Exception are _comments_ ( `..` ) and _targets_ (e.g. a ref to [row 2 of table’s body](https://docs.searxng.org//dev/reST.html#row-body-2)).
```
.. flat-table:: ``flat-table`` example
   :header-rows: 2
   :stub-columns: 1
   :widths: 1 1 1 1 2

   * - :rspan:`1` head / stub
     - :cspan:`3` head 1.1-4

   * - head 2.1
     - head 2.2
     - head 2.3
     - head 2.4

   * .. row body 1 / this is a comment

     - row 1
     - :rspan:`2` cell 1-3.1
     - cell 1.2
     - cell 1.3
     - cell 1.4

   * .. Comments and targets are allowed on *table-row* stage.
     .. _`row body 2`:

     - row 2
     - cell 2.2
     - :rspan:`1` :cspan:`1`
       cell 2.3 with a span over

       * col 3-4 &
       * row 2-3

   * - row 3
     - cell 3.2

   * - row 4
     - cell 4.1
     - cell 4.2
     - cell 4.3
     - cell 4.4

   * - row 5
     - cell 5.1 with automatic span to right end

   * - row 6
     - cell 6.1
     - ..

```

List table
Table 14 `flat-table` example head / stub |  head 1.1-4  
---|---  
head 2.1 | head 2.2 | head 2.3 | head 2.4  
row 1 |  cell 1-3.1 | cell 1.2 | cell 1.3 | cell 1.4  
row 2 |  cell 2.2 |  cell 2.3 with a span over
  * col 3-4 &
  * row 2-3

  
row 3 | cell 3.2  
row 4 | cell 4.1 | cell 4.2 | cell 4.3 | cell 4.4  
row 5 | cell 5.1 with automatic span to right end  
row 6 | cell 6.1 |   
### CSV table
CSV table might be the choice if you want to include CSV-data from a outstanding (build) process into your documentation.
```
.. csv-table:: CSV table example
   :header: .. , Column 1, Column 2
   :widths: 2 5 5
   :stub-columns: 1
   :file: csv_table.txt

```

Content of file `csv_table.txt`:
```
stub col row 1, column, "loremLorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy
eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam
voluptua."
stub col row 1, "At vero eos et accusam et justo duo dolores et ea rebum. Stet clita
kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.", column
stub col row 1, column, column

```

CSV table
Table 15 CSV table example | Column 1 | Column 2  
---|---|---  
stub col row 1 | column | loremLorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.  
stub col row 1 | At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. | column  
stub col row 1 | column | column  
## Templating
Build environment
All _generic-doc_ tasks are running in the [Python environment (make install)](https://docs.searxng.org/dev/makefile.html#make-install).
Templating is suitable for documentation which is created generic at the build time. The [sphinx-jinja](https://github.com/tardyp/sphinx-jinja) extension evaluates [jinja](https://jinja.palletsprojects.com/) templates in the [Python environment (make install)](https://docs.searxng.org/dev/makefile.html#make-install) (with SearXNG modules installed). We use this e.g. to build chapter: [Configured Engines](https://docs.searxng.org/user/configured_engines.html#configured-engines). Below the jinja directive from the [git://docs/admin/engines.rst](https://github.com/searxng/searxng/blob/master/docs/admin/engines.rst) is shown:
```
==================
Configured Engines
==================

.. sidebar:: Further reading ..

   - :ref:`settings categories_as_tabs`
   - :ref:`engines-dev`
   - :ref:`settings engines`
   - :ref:`general engine configuration`

.. jinja:: searx

   SearXNG supports {{engines | length}} search engines of which
   {{enabled_engine_count}} are enabled by default.

   Engines can be assigned to multiple :ref:`categories <engine categories>`.
   The UI displays the tabs that are configured in :ref:`categories_as_tabs
   <settings categories_as_tabs>`.  In addition to these UI categories (also
   called *tabs*), engines can be queried by their name or the categories they
   belong to, by using a :ref:`\!bing syntax <search-syntax>`.

.. contents::
   :depth: 2
   :local:
   :backlinks: entry

.. jinja:: searx

   {% for category, engines in categories_as_tabs.items() %}

   tab ``!{{category.replace(' ', '_')}}``
   ---------------------------------------

   {% for group, group_bang, engines in engines | group_engines_in_tab %}

   {% if loop.length > 1 %}
   {% if group_bang %}group ``{{group_bang}}``{% else %}{{group}}{% endif %}
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   {% endif %}

   .. flat-table::
      :header-rows: 2
      :stub-columns: 1
      :widths: 10 1 10 1 1 1 1 1 1 1

      * - :cspan:`5` Engines configured by default (in :ref:`settings.yml <engine settings>`)
        - :cspan:`3` :ref:`Supported features <engine file>`

      * - Name
        - !bang
        - Module
        - Disabled
        - Timeout
        - Weight
        - Paging
        - Locale
        - Safe search
        - Time range

      {% for mod in engines %}

      * - `{{mod.name}} <{{mod.about and mod.about.website}}>`_
          {%- if mod.about and  mod.about.language %}
          ({{mod.about.language | upper}})
          {%- endif %}
        - ``!{{mod.shortcut}}``
        - {%- if 'searx.engines.' + mod.__name__ in documented_modules %}
          :py:mod:`~searx.engines.{{mod.__name__}}`
          {%- else %}
          :origin:`{{mod.__name__}} <searx/engines/{{mod.__name__}}.py>`
          {%- endif %}
        - {{(mod.disabled and "y") or ""}}
        - {{mod.timeout}}
        - {{mod.weight or 1 }}
        {% if mod.engine_type == 'online' %}
        - {{(mod.paging and "y") or ""}}
        - {{(mod.language_support and "y") or ""}}
        - {{(mod.safesearch and "y") or ""}}
        - {{(mod.time_range_support and "y") or ""}}
        {% else %}
        - :cspan:`3` not applicable ({{mod.engine_type}})
        {% endif %}

     {% endfor %}
     {% endfor %}
     {% endfor %}

```

The context for the template is selected in the line `.. jinja:: searx`. In sphinx’s build configuration ([git://docs/conf.py](https://github.com/searxng/searxng/blob/master/docs/conf.py)) the `searx` context contains the `engines` and `plugins`.
```
import searx.search
import searx.engines
import searx.plugins
searx.search.initialize()
jinja_contexts = {
   'searx': {
      'engines': searx.engines.engines,
      'plugins': searx.plugins.plugins
   },
}

```

## Tabbed views
With [sphinx-tabs](https://github.com/djungelorm/sphinx-tabs) extension we have _tabbed views_. To provide installation instructions with one tab per distribution we use the [group-tabs](https://github.com/djungelorm/sphinx-tabs#group-tabs) directive, others are [basic-tabs](https://github.com/djungelorm/sphinx-tabs#basic-tabs) and [code-tabs](https://github.com/djungelorm/sphinx-tabs#code-tabs). Below a _group-tab_ example from [Build docs](https://docs.searxng.org/admin/buildhosts.html#docs-build) is shown:
```
.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code-block:: sh

         $ sudo apt install shellcheck

   .. group-tab:: Arch Linux

      .. code-block:: sh

         $ sudo pacman -S shellcheck

   .. group-tab::  Fedora / RHEL

      .. code-block:: sh

         $ sudo dnf install ShellCheck

```

## Math equations
About LaTeX
  * [amsmath user guide](http://vesta.informatik.rwth-aachen.de/ftp/pub/mirror/ctan/macros/latex/required/amsmath/amsldoc.pdf)
  * [Mathematics](https://en.wikibooks.org/wiki/LaTeX/Mathematics)
  * [Build docs](https://docs.searxng.org/admin/buildhosts.html#docs-build)

The input language for mathematics is LaTeX markup using the [CTAN: amsmath](https://ctan.org/pkg/amsmath) package.
To embed LaTeX markup in reST documents, use role [`:math:`](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-math "\(in Sphinx v9.1.0\)") for inline and directive [`.. math::`](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-math "\(in Sphinx v9.1.0\)") for block markup.
```
In :math:numref:`schroedinger general` the time-dependent Schrödinger equation
is shown.

.. math::
   :label: schroedinger general

    \mathrm{i}\hbar\dfrac{\partial}{\partial t} |\,\psi (t) \rangle =
          \hat{H} |\,\psi (t) \rangle.

```

LaTeX math equation
In [(1)](https://docs.searxng.org//dev/reST.html#equation-schroedinger-general) the time-dependent Schrödinger equation is shown.
(1)\mathrm{i}\hbar\dfrac{\partial}{\partial t} |\,\psi (t) \rangle = \hat{H} |\,\psi (t) \rangle.
The next example shows the difference of `\tfrac` (_textstyle_) and `\dfrac` (_displaystyle_) used in a inline markup or another fraction.
```
``\tfrac`` **inline example** :math:`\tfrac{\tfrac{1}{x}+\tfrac{1}{y}}{y-z}`
``\dfrac`` **inline example** :math:`\dfrac{\dfrac{1}{x}+\dfrac{1}{y}}{y-z}`

```

Line spacing
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. … `\tfrac` **inline example** \tfrac{\tfrac{1}{x}+\tfrac{1}{y}}{y-z} At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. … `\tfrac` **inline example** \dfrac{\dfrac{1}{x}+\dfrac{1}{y}}{y-z} At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
