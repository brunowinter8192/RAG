<!-- source: https://docs.searxng.org/admin/buildhosts.html -->

# Buildhosts
To get best results from build, it’s recommend to install additional packages on build hosts (see [utils/searxng.sh](https://docs.searxng.org/utils/searxng.sh.html#searxng-sh)).
## Build and Development tools
To Install tools used by build and development tasks in once:
SearXNG’s development tools
```
$ sudo -H ./utils/searxng.sh install buildhost

```

This will install packages needed by SearXNG:
Ubuntu / debianArch LinuxFedora / RHEL
```
$ sudo -H apt-get install -y \
    python3-dev python3-babel python3-venv python-is-python3 \
    uwsgi uwsgi-plugin-python3 \
    git build-essential libxslt-dev zlib1g-dev libffi-dev libssl-dev

```

```
$ sudo -H pacman -S --noconfirm \
    python python-pip python-lxml python-babel \
    uwsgi uwsgi-plugin-python \
    git base-devel libxml2

```

```
$ sudo -H dnf install -y \
    python python-pip python-lxml python-babel python3-devel \
    uwsgi uwsgi-plugin-python3 \
    git @development-tools libxml2 openssl

```

and packages needed to build documentation and run tests:
Ubuntu / debianArch LinuxFedora / RHEL
```
$ sudo -H apt-get install -y \
    graphviz imagemagick texlive-xetex librsvg2-bin \
    texlive-latex-recommended texlive-extra-utils fonts-dejavu \
    latexmk shellcheck

```

```
$ sudo -H pacman -S --noconfirm \
    graphviz imagemagick texlive-bin extra/librsvg \
    texlive-core texlive-latexextra ttf-dejavu shellcheck

```

```
$ sudo -H dnf install -y \
    graphviz graphviz-gd ImageMagick librsvg2-tools \
    texlive-xetex-bin texlive-collection-fontsrecommended \
    texlive-collection-latex dejavu-sans-fonts dejavu-serif-fonts \
    dejavu-sans-mono-fonts ShellCheck

```

## Build docs
Sphinx build needs
  * [ImageMagick](https://www.imagemagick.org)
  * [Graphviz](https://graphviz.gitlab.io)
  * [XeTeX](https://tug.org/xetex/)
  * [dvisvgm](https://dvisvgm.de/)

Most of the sphinx requirements are installed from [git://setup.py](https://github.com/searxng/searxng/blob/master/setup.py) and the docs can be build from scratch with `make docs.html`. For better math and image processing additional packages are needed. The [XeTeX](https://tug.org/xetex/) needed not only for PDF creation, it’s also needed for [Math equations](https://docs.searxng.org/dev/reST.html#math) when HTML output is build.
To be able to do [Math support for HTML outputs in Sphinx](https://www.sphinx-doc.org/en/master/usage/extensions/math.html#math-support "\(in Sphinx v9.1.0\)") without CDNs, the math are rendered as images (`sphinx.ext.imgmath` extension).
Here is the extract from the [git://docs/conf.py](https://github.com/searxng/searxng/blob/master/docs/conf.py) file, setting math renderer to `imgmath`:
```
html_math_renderer = 'imgmath'
imgmath_image_format = 'svg'
imgmath_font_size = 14

```

If your docs build (`make docs.html`) shows warnings like this:
```
WARNING: dot(1) not found, for better output quality install \
         graphviz from https://www.graphviz.org
..
WARNING: LaTeX command 'latex' cannot be run (needed for math \
         display), check the imgmath_latex setting

```

you need to install additional packages on your build host, to get better HTML output ([install buildhost](https://docs.searxng.org/admin/buildhosts.html#searxng-sh-install-buildhost)).
Ubuntu / debianArch LinuxFedora / RHEL
```
$ sudo apt install graphviz imagemagick texlive-xetex librsvg2-bin

```

```
$ sudo pacman -S graphviz imagemagick texlive-bin extra/librsvg

```

```
$ sudo dnf install graphviz graphviz-gd ImageMagick texlive-xetex-bin librsvg2-tools

```

For PDF output you also need:
Ubuntu / debianArch LinuxFedora / RHEL
```
$ sudo apt texlive-latex-recommended texlive-extra-utils ttf-dejavu

```

```
$ sudo pacman -S texlive-core texlive-latexextra ttf-dejavu

```

```
$ sudo dnf install \
    texlive-collection-fontsrecommended texlive-collection-latex \
    dejavu-sans-fonts dejavu-serif-fonts dejavu-sans-mono-fonts

```

## Lint shell scripts
To lint shell scripts we use [ShellCheck](https://github.com/koalaman/shellcheck) - a shell script static analysis tool ([install buildhost](https://docs.searxng.org/admin/buildhosts.html#searxng-sh-install-buildhost)).
Ubuntu / debianArch LinuxFedora / RHEL
```
$ sudo apt install shellcheck

```

```
$ sudo pacman -S shellcheck

```

```
$ sudo dnf install ShellCheck

```
