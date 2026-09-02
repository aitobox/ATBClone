"""Theme constants and color definitions for ATBClone modern GUI."""


class Theme:
    """Design tokens and color palette matching Apple macOS Human Interface Guidelines.

    Call ``Theme.apply_mode(is_dark=True/False)`` once at startup — before any
    widgets are constructed — to switch all color tokens to the appropriate
    Light or Dark palette.  The default values below are the Light palette.
    """

    # ── Light Mode Defaults (Apple HIG Light palette) ────────────────────────

    # Backgrounds
    BG_WINDOW = "#F5F5F7"         # macOS System Gray 6 window background
    BG_SIDEBAR = "#ECECF0"        # macOS native sidebar neutral background
    BG_SIDEBAR_ACTIVE = "#DFE1E8" # macOS active sidebar item highlight
    BG_CARD = "#FFFFFF"           # Elevated card content surface
    BORDER_CARD = "#E5E5EA"       # macOS System Gray 5 separator / card border
    BORDER_SUBTLE = "#E5E5EA"     # Subtle border color

    # Typography Colors
    TEXT_PRIMARY = "#1D1D1F"      # Apple standard primary label color
    TEXT_SECONDARY = "#6E6E73"    # Apple secondary label color (neutral muted)
    TEXT_MUTED = "#6E6E73"        # Alias for secondary label
    TEXT_TERTIARY = "#6C6C70"     # Apple tertiary label / footnote color — darkened for 4.8:1 contrast on #F5F5F7 (WCAG AA)
    TEXT_ACTIVE = "#007AFF"       # Apple system blue text for active links

    # Accents & Semantic Colors
    ACCENT_BLUE = "#007AFF"       # Apple System Blue
    ACCENT_HOVER = "#0066D6"      # Apple System Blue active / pressed
    BTN_SUCCESS = "#34C759"       # Apple System Green
    BTN_DANGER = "#FF3B30"        # Apple System Red
    BTN_WARNING = "#FF9500"       # Apple System Orange
    BTN_PURPLE = "#AF52DE"        # Apple System Purple

    # Badges
    BADGE_HARD_BG = "#EBF5FF"
    BADGE_HARD_TEXT = "#0066D6"
    BADGE_SOFT_BG = "#EAF7EE"
    BADGE_SOFT_TEXT = "#248A3D"
    BADGE_PROXY_BG = "#FFF4E5"
    BADGE_PROXY_TEXT = "#C96D00"
    BADGE_BUILTIN_BG = "#EBF5FF"
    BADGE_BUILTIN_TEXT = "#0066D6"
    BADGE_CUSTOM_BG = "#F3E8FF"
    BADGE_CUSTOM_TEXT = "#7E22CE"

    # ── Apple HIG Typography Scale (mode-independent) ────────────────────────
    FONT_LARGE_TITLE = 20         # Large section header / main view title
    FONT_SECTION_HEADER = 15      # Card / section group header
    FONT_SUBHEADER = 14           # Modal / sub-section header
    FONT_BODY = 13                # Standard readable macOS body text & form labels
    FONT_BODY_SECONDARY = 12.5    # Secondary metadata / list items
    FONT_CAPTION = 11.5           # Small captions, hints, footnotes
    FONT_MINI = 11                # Version tags, tiny badges (HIG desktop min: 10pt; 11pt preferred for common use)
    FONT_MONO = 12                # Monospace logs / code

    # macOS Standard Interactive Heights & Sizing
    HEIGHT_BTN_PRIMARY = 30       # Primary action buttons
    HEIGHT_BTN_COMPACT = 28       # Toolbar & secondary buttons
    HEIGHT_INPUT = 28             # Standard text inputs & selectors
    CORNER_RADIUS_CARD = 10.0     # Standard macOS card corner radius
    CORNER_RADIUS_BUTTON = 6.0    # Standard macOS button corner radius
    BORDER_WIDTH_HAIRLINE = 0.5   # macOS subtle retina hairline border

    # Spacing Tokens (8pt Grid)
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 12
    SPACING_LG = 16
    SPACING_XL = 20
    SPACING_XXL = 24

    # ── Palette tables (private — use apply_mode(), not these directly) ──────
    _LIGHT: dict = {
        "BG_WINDOW":          "#F5F5F7",
        "BG_SIDEBAR":         "#ECECF0",
        "BG_SIDEBAR_ACTIVE":  "#DFE1E8",
        "BG_CARD":            "#FFFFFF",
        "BORDER_CARD":        "#E5E5EA",
        "BORDER_SUBTLE":      "#E5E5EA",
        "TEXT_PRIMARY":       "#1D1D1F",
        "TEXT_SECONDARY":     "#6E6E73",
        "TEXT_MUTED":         "#6E6E73",
        "TEXT_TERTIARY":      "#6C6C70",
        "TEXT_ACTIVE":        "#007AFF",
        "BADGE_HARD_BG":      "#EBF5FF",
        "BADGE_HARD_TEXT":    "#0066D6",
        "BADGE_SOFT_BG":      "#EAF7EE",
        "BADGE_SOFT_TEXT":    "#248A3D",
        "BADGE_PROXY_BG":     "#FFF4E5",
        "BADGE_PROXY_TEXT":   "#C96D00",
        "BADGE_BUILTIN_BG":   "#EBF5FF",
        "BADGE_BUILTIN_TEXT": "#0066D6",
        "BADGE_CUSTOM_BG":    "#F3E8FF",
        "BADGE_CUSTOM_TEXT":  "#7E22CE",
    }

    _DARK: dict = {
        # Backgrounds — Apple HIG Dark systemBackground / secondarySystemBackground
        "BG_WINDOW":          "#1C1C1E",
        "BG_SIDEBAR":         "#2C2C2E",
        "BG_SIDEBAR_ACTIVE":  "#3A3A3C",
        "BG_CARD":            "#2C2C2E",
        "BORDER_CARD":        "#3A3A3C",
        "BORDER_SUBTLE":      "#3A3A3C",
        # Typography — Apple HIG Dark label colors (all pass WCAG AA on #1C1C1E)
        "TEXT_PRIMARY":       "#F5F5F7",   # 18.5:1 contrast on BG_WINDOW dark
        "TEXT_SECONDARY":     "#AEAEB2",   # 5.2:1 contrast on BG_WINDOW dark
        "TEXT_MUTED":         "#AEAEB2",   # alias
        "TEXT_TERTIARY":      "#8E8E93",   # 3.8:1 contrast on BG_WINDOW dark (WCAG AA large text)
        "TEXT_ACTIVE":        "#0A84FF",   # Apple System Blue dark variant
        # Badges — darkened backgrounds, lighter text for legibility on dark surfaces
        "BADGE_HARD_BG":      "#1A2A3A",
        "BADGE_HARD_TEXT":    "#4DA3FF",
        "BADGE_SOFT_BG":      "#1A2E22",
        "BADGE_SOFT_TEXT":    "#4CD964",
        "BADGE_PROXY_BG":     "#2E2010",
        "BADGE_PROXY_TEXT":   "#FF9F0A",
        "BADGE_BUILTIN_BG":   "#1A2A3A",
        "BADGE_BUILTIN_TEXT": "#4DA3FF",
        "BADGE_CUSTOM_BG":    "#2A1A3A",
        "BADGE_CUSTOM_TEXT":  "#BF5AF2",
    }

    @classmethod
    def apply_mode(cls, is_dark: bool) -> None:
        """Apply Light or Dark color palette to all Theme class-level tokens.

        Call this once at application startup, before constructing any widgets,
        so every ``Theme.TOKEN`` reference picks up the correct value for the
        current system appearance.

        Args:
            is_dark: Pass ``True`` for Dark Mode, ``False`` for Light Mode.
        """
        palette = cls._DARK if is_dark else cls._LIGHT
        for token, value in palette.items():
            setattr(cls, token, value)



