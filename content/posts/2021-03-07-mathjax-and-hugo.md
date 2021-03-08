---
title: MathJax and Hugo
draft: false
---

The is a [marvelous article](https://bwaycer.github.io/hugo_tutorial.hugo/tutorials/mathjax/) which explains how to use [Hugo](https://gohugo.io/) and [MathJax](https://www.mathjax.org/) in close harmony. Unfortunately it was written a while ago and only works for MathJax 2.x. This article updates the content of the original to MathJax > 3.1. The original is still worth reading as it nicely explains the functionality.

Firstly MathJax > 3.0 likes to have pollyfill. So the script inclusion should look like this:

```html
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
```

The solution to the problem of having to escape _many_ characters in LaTeX markup is solved in a simlar manner, however a combination of Hugo now using the [Goldmark](https://github.com/yuin/goldmark) renderer and the MathJax API changing quite significantly at version 3.0, it largely needs re-writing. Firstly the script to add the class to the code blocks now looks like this:

```html
<script>
  window.MathJax = {
    tex: {
      inlineMath: [['$','$'], ['\\(','\\)']],
      displayMath: [['$$','$$'], ['\[','\]']],
      processEscapes: true,
      processEnvironments: true
    },
    options: {
      skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
    },
    startup: {
      pageReady() {
        return MathJax.startup.defaultPageReady().then(function () {
          var all = window.MathJax.startup.document.getMathItemsWithin(document.body), i;
          for(i = 0; i < all.length; i += 1) {
            console.log(all[i])
            all[i].start.node.parentNode.className += ' has-jax';
          }
        });
      }
    }
  };
  </script>
```

Now, by default, the Goldmark renderer does not permit raw html in markdown, instead converting it to a comment. To change this behaviour the Hugo configuration needs the following code added:

```toml
[markup]
  [markup.goldmark]
    [markup.goldmark.renderer]
      unsafe = true
```

Now, LaTeX can be included in `<div>` tags without worrying about having to escape either `_` or `\` characters. The following code:

```html
<div>
$$
\begin{align*}
  \phi(x,y) &= \phi \left(\sum_{i=1}^n x_ie_i, \sum_{j=1}^n y_je_j \right) \\
  &= \sum_{i=1}^n \sum_{j=1}^n x_i y_j \phi(e_i, e_j) \\
  &= (x_1, \ldots, x_n) \left( \begin{array}{ccc}
      \phi(e_1, e_1) & \cdots & \phi(e_1, e_n) \\
      \vdots & \ddots & \vdots \\
      \phi(e_n, e_1) & \cdots & \phi(e_n, e_n)
    \end{array} \right)
  \left( \begin{array}{c}
      y_1 \\
      \vdots \\
      y_n
    \end{array} \right)
\end{align*}
$$
</div>
```

renders as:
<div>
$$
\begin{align*}
  \phi(x,y) &= \phi \left(\sum_{i=1}^n x_ie_i, \sum_{j=1}^n y_je_j \right) \\
  &= \sum_{i=1}^n \sum_{j=1}^n x_i y_j \phi(e_i, e_j) \\
  &= (x_1, \ldots, x_n) \left( \begin{array}{ccc}
      \phi(e_1, e_1) & \cdots & \phi(e_1, e_n) \\
      \vdots & \ddots & \vdots \\
      \phi(e_n, e_1) & \cdots & \phi(e_n, e_n)
    \end{array} \right)
  \left( \begin{array}{c}
      y_1 \\
      \vdots \\
      y_n
    \end{array} \right)
\end{align*}
$$
</div>