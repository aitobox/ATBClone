"""Theme constants and color definitions for ATBClone modern GUI."""


class Theme:
    """Design tokens and color palette matching Apple macOS Human Interface Guidelines."""

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
    BTN_PURPLE = "#AF52DE"       # Apple System Purple

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

    # Apple HIG Typography Scale
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


