/**
 * ATBCmder Documentation - Automatic Browser Language Detection & Redirection
 * Supports 11 languages with client-side routing, URL override, and UI switcher hydration.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'preferred_language';

  var SUPPORTED_LANGS = {
    'en': 'English',
    'zh': '简体中文',
    'zh-hant': '繁體中文',
    'ja': '日本語',
    'de': 'Deutsch',
    'fr': 'Français',
    'es': 'Español',
    'pt': 'Português',
    'ko': '한국어',
    'ru': 'Русский',
    'it': 'Italiano'
  };

  // Helper to extract query parameter (e.g. ?lang=zh or ?lang=ja)
  function getQueryParam(name, searchStr) {
    try {
      var search = searchStr !== undefined ? searchStr : (typeof window !== 'undefined' ? window.location.search : '');
      var match = RegExp('[?&]' + name + '=([^&]*)').exec(search);
      return match ? decodeURIComponent(match[1].replace(/\+/g, ' ')) : null;
    } catch (e) {
      return null;
    }
  }

  // Matches browser locale string against the prefix table
  function matchBrowserLocale(localeStr) {
    if (!localeStr || typeof localeStr !== 'string') return null;
    var l = localeStr.toLowerCase().trim();

    // Traditional Chinese prefixes (must be checked before generic zh)
    if (
      l.indexOf('zh-tw') === 0 ||
      l.indexOf('zh-hk') === 0 ||
      l.indexOf('zh-mo') === 0 ||
      l.indexOf('zh-hant') === 0
    ) {
      return 'zh-hant';
    }

    // Simplified / Generic Chinese prefixes
    if (
      l.indexOf('zh-cn') === 0 ||
      l.indexOf('zh-sg') === 0 ||
      l.indexOf('zh-hans') === 0 ||
      l.indexOf('zh') === 0
    ) {
      return 'zh';
    }

    // Single / standard prefix matches
    if (l.indexOf('ja') === 0) return 'ja';
    if (l.indexOf('de') === 0) return 'de';
    if (l.indexOf('fr') === 0) return 'fr';
    if (l.indexOf('es') === 0) return 'es';
    if (l.indexOf('pt') === 0) return 'pt';
    if (l.indexOf('ko') === 0) return 'ko';
    if (l.indexOf('ru') === 0) return 'ru';
    if (l.indexOf('it') === 0) return 'it';
    if (l.indexOf('en') === 0) return 'en';

    return null;
  }

  // Detect preferred language from navigator.languages or navigator.language
  function detectBrowserLanguage(customNavigator) {
    var nav = customNavigator || (typeof navigator !== 'undefined' ? navigator : null);
    if (!nav) return 'en';

    var langs = [];
    if (nav.languages && nav.languages.length) {
      langs = nav.languages;
    } else if (nav.language) {
      langs = [nav.language];
    } else if (nav.userLanguage) {
      langs = [nav.userLanguage];
    }

    for (var i = 0; i < langs.length; i++) {
      var match = matchBrowserLocale(langs[i]);
      if (match) {
        return match;
      }
    }
    return 'en';
  }

  // Extracts language code from pathname (e.g. /ja/power_tools/ -> ja)
  function getCurrentPageLang(pathname) {
    if (!pathname || typeof pathname !== 'string') return null;
    var match = pathname.match(/(?:^|\/)(zh-hant|en|zh|ja|de|fr|es|pt|ko|ru|it)(?:$|\/)/i);
    return match ? match[1].toLowerCase() : null;
  }

  // Replaces the language prefix in pathname preserving the rest of the path
  function replaceLangInPath(pathname, fromLang, toLang) {
    if (!pathname || typeof pathname !== 'string') {
      return '/' + toLang + '/';
    }
    return pathname.replace(new RegExp('/' + fromLang + '(/|$)', 'i'), '/' + toLang + '$1');
  }

  function runDetector() {
    if (typeof window === 'undefined' || typeof document === 'undefined') return;
    if (window.__atbcmder_lang_detector_initialized) return;
    window.__atbcmder_lang_detector_initialized = true;

    var pathname = window.location.pathname;
    var currentLang = getCurrentPageLang(pathname);

    // Only apply language redirection if we are inside a supported language tree
    if (!currentLang) {
      return;
    }

    // 1. Query parameter ?lang=<code> (explicit user override)
    var explicitLang = getQueryParam('lang');
    var targetLang = null;
    if (explicitLang) {
      explicitLang = explicitLang.toLowerCase();
      if (SUPPORTED_LANGS.hasOwnProperty(explicitLang)) {
        targetLang = explicitLang;
        try {
          localStorage.setItem(STORAGE_KEY, targetLang);
        } catch (e) {}
      }
    }

    // Check internal navigation protection:
    // If the user arrived by clicking an internal link on the same domain,
    // preserve current language without redirecting and save current language.
    var isInternalNav = false;
    try {
      if (document.referrer && window.location.host) {
        var refUrl = new URL(document.referrer);
        if (refUrl.host === window.location.host) {
          isInternalNav = true;
        }
      }
    } catch (e) {}

    // 2. Internal navigation protection
    if (!targetLang && isInternalNav) {
      targetLang = currentLang;
      try {
        localStorage.setItem(STORAGE_KEY, currentLang);
      } catch (e) {}
    }

    // 3. Saved preference
    if (!targetLang) {
      var savedPreference = null;
      try {
        savedPreference = localStorage.getItem(STORAGE_KEY);
      } catch (e) {}
      if (savedPreference) {
        savedPreference = savedPreference.toLowerCase();
        if (SUPPORTED_LANGS.hasOwnProperty(savedPreference)) {
          targetLang = savedPreference;
        }
      }
    }

    // 4. Browser language detection
    if (!targetLang) {
      targetLang = detectBrowserLanguage();
    }

    // 5. Redirection if target language != current page language
    if (targetLang && targetLang !== currentLang) {
      var targetUrl = replaceLangInPath(pathname, currentLang, targetLang) + window.location.search + window.location.hash;
      window.location.replace(targetUrl);
      return;
    }

    // UI Hydration & Interaction
    function hydrateUI() {
      var pageLang = getCurrentPageLang(window.location.pathname) || currentLang || 'en';
      var nativeName = SUPPORTED_LANGS[pageLang] || 'English';

      // 1. Update current language label
      var labels = document.querySelectorAll('#atb-lang-current-label, .atb-lang-current');
      for (var i = 0; i < labels.length; i++) {
        labels[i].textContent = nativeName;
      }

      // 2. Update active class on dropdown items and bind click events
      var items = document.querySelectorAll('.atb-lang-item');
      for (var j = 0; j < items.length; j++) {
        var item = items[j];
        var itemLang = item.getAttribute('data-lang');
        if (itemLang === pageLang) {
          item.classList.add('is-active');
        } else {
          item.classList.remove('is-active');
        }

        item.addEventListener('click', function () {
          var clickedLang = this.getAttribute('data-lang');
          if (clickedLang && SUPPORTED_LANGS.hasOwnProperty(clickedLang)) {
            try {
              localStorage.setItem(STORAGE_KEY, clickedLang);
            } catch (e) {}
          }
        });
      }

      // 3. Close dropdown when clicking outside or pressing Escape
      var switchers = document.querySelectorAll('details#atb-lang-switcher, details.atb-lang-dropdown');
      if (switchers.length > 0) {
        document.addEventListener('click', function (event) {
          for (var k = 0; k < switchers.length; k++) {
            var sw = switchers[k];
            if (sw.hasAttribute('open') && !sw.contains(event.target)) {
              sw.removeAttribute('open');
            }
          }
        });

        document.addEventListener('keydown', function (event) {
          if (event.key === 'Escape' || event.keyCode === 27) {
            for (var k = 0; k < switchers.length; k++) {
              var sw = switchers[k];
              if (sw.hasAttribute('open')) {
                sw.removeAttribute('open');
                var summary = sw.querySelector('summary');
                if (summary) {
                  summary.focus();
                }
              }
            }
          }
        });
      }
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', hydrateUI);
    } else {
      hydrateUI();
    }
  }

  runDetector();

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      STORAGE_KEY: STORAGE_KEY,
      SUPPORTED_LANGS: SUPPORTED_LANGS,
      getQueryParam: getQueryParam,
      matchBrowserLocale: matchBrowserLocale,
      detectBrowserLanguage: detectBrowserLanguage,
      getCurrentPageLang: getCurrentPageLang,
      replaceLangInPath: replaceLangInPath
    };
  }
})();
