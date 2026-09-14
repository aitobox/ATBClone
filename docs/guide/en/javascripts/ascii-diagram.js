/**
 * ATBCmder Documentation - ASCII / Unicode Box Diagram Monospace Normalizer
 *
 * In web browsers, proportional CJK fallback fonts and system emoji fonts render
 * at variable widths (e.g. 1.0em-1.2em / 14-18px), whereas Western monospace fonts
 * render at ~0.6em per character (2 chars = 1.2em).
 *
 * This causes lines with CJK text or emojis in ASCII box diagrams to drift out of
 * vertical alignment with pure ASCII / box-drawing borders.
 *
 * This script identifies code blocks containing box-drawing characters and wraps
 * all wide characters (CJK characters, fullwidth punctuation, and emojis) in
 * <span class="cjk-char"> with CSS `display: inline-block; width: 2ch;`,
 * ensuring mathematical 2:1 alignment without altering clipboard/copy text.
 */
(function () {
  'use strict';

  var WIDE_REGEX = /([\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3000-\u303f\uff01-\uff60\uffe0-\uffe6]|[\u{1f300}-\u{1faff}][\ufe0e\ufe0f]?|[\u{1f000}-\u{1f2ff}][\ufe0e\ufe0f]?|[\u2600-\u27bf]\ufe0f|\u2699|\u26a1|\u2702|\u270f|\u2795)/gu;
  var BOX_CHARS_REGEX = /[┌─│┼├┤┴┬└┘╭╮╰╯═║╔╗╚╝╠╣╦╩╬]/;

  function normalizeCodeBlock(code) {
    if (code.getAttribute('data-ascii-aligned') === 'true') {
      return;
    }

    var text = code.textContent;
    if (!BOX_CHARS_REGEX.test(text) && !(/\+[-=]{2,}\+/.test(text) && text.indexOf('|') !== -1)) {
      return;
    }

    var walker = document.createTreeWalker(code, NodeFilter.SHOW_TEXT, null, false);
    var textNodes = [];
    var node;

    while ((node = walker.nextNode())) {
      WIDE_REGEX.lastIndex = 0;
      if (WIDE_REGEX.test(node.nodeValue)) {
        textNodes.push(node);
      }
    }

    for (var i = 0; i < textNodes.length; i++) {
      var tn = textNodes[i];
      var parent = tn.parentNode;
      if (parent && parent.classList && parent.classList.contains('cjk-char')) {
        continue;
      }

      var frag = document.createDocumentFragment();
      var str = tn.nodeValue;
      var lastIndex = 0;
      WIDE_REGEX.lastIndex = 0;
      var match;

      while ((match = WIDE_REGEX.exec(str)) !== null) {
        if (match.index > lastIndex) {
          frag.appendChild(document.createTextNode(str.slice(lastIndex, match.index)));
        }
        var span = document.createElement('span');
        span.className = 'cjk-char';
        span.textContent = match[0];
        frag.appendChild(span);
        lastIndex = WIDE_REGEX.lastIndex;
      }

      if (lastIndex < str.length) {
        frag.appendChild(document.createTextNode(str.slice(lastIndex)));
      }

      if (parent) {
        parent.replaceChild(frag, tn);
      }
    }

    code.setAttribute('data-ascii-aligned', 'true');
  }

  function alignAllDiagrams(container) {
    var root = container || document;
    var codeBlocks = root.querySelectorAll('.highlight code, pre code');
    for (var i = 0; i < codeBlocks.length; i++) {
      normalizeCodeBlock(codeBlocks[i]);
    }
  }

  // Initial trigger
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      alignAllDiagrams(document);
    });
  } else {
    alignAllDiagrams(document);
  }

  // Support for Material for MkDocs instant navigation / PJAX
  if (typeof window.document$ !== 'undefined') {
    window.document$.subscribe(function () {
      alignAllDiagrams(document);
    });
  }
})();
