---
name: Lumina Noir
colors:
  surface: '#0e1513'
  surface-dim: '#0e1513'
  surface-bright: '#343b39'
  surface-container-lowest: '#090f0e'
  surface-container-low: '#161d1b'
  surface-container: '#1a211f'
  surface-container-high: '#252b2a'
  surface-container-highest: '#2f3634'
  on-surface: '#dde4e1'
  on-surface-variant: '#bbcac6'
  inverse-surface: '#dde4e1'
  inverse-on-surface: '#2b3230'
  outline: '#859490'
  outline-variant: '#3c4947'
  surface-tint: '#4fdbc8'
  primary: '#4fdbc8'
  on-primary: '#003731'
  primary-container: '#14b8a6'
  on-primary-container: '#00423b'
  inverse-primary: '#006b5f'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#e49200'
  on-tertiary-container: '#543300'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#71f8e4'
  primary-fixed-dim: '#4fdbc8'
  on-primary-fixed: '#00201c'
  on-primary-fixed-variant: '#005048'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0e1513'
  on-background: '#dde4e1'
  surface-variant: '#2f3634'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  headline-sm:
    fontFamily: Outfit
    fontSize: 20px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-bold:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base-unit: 4px
  container-max-width: 1280px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
  stack-gap: 12px
  section-gap: 64px
---

## Brand & Style

The design system is a premium "Deep Dark" interface designed for high-end fashion and lifestyle product discovery. The aesthetic is rooted in **Glassmorphism** and **Minimalism**, creating an immersive, atmospheric experience that allows high-quality product imagery to shine. 

The UI evokes a sense of exclusivity, precision, and futuristic elegance. By utilizing deep black voids contrasted with translucent layers and vibrant teal highlights, the system creates a multi-dimensional digital space that feels both tactile and ethereal.

- **Atmosphere:** Immersive, luxurious, and high-tech.
- **Visual Strategy:** Layers of transparency (glass) over an absolute dark base to create depth without relying on heavy shadows.
- **Target Audience:** Trend-conscious shoppers looking for a curated, premium discovery experience.

## Colors

The palette is centered on a "Deep Dark" foundation, utilizing `#0a0a0a` as the base canvas to ensure maximum contrast for product visuals and teal accents.

- **Primary (Teal):** Used for primary actions, active states, and critical branding elements.
- **Secondary (Emerald):** Used for success states and as a secondary gradient stop for headers.
- **Tertiary (Amber):** Reserved for "Limited Edition," "Trending," or "Sale" badges to provide a warm, high-contrast counterpoint to the cool teal tones.
- **Neutral (Surface):** Rather than solid grays, the system uses white at low opacities (5-10%) combined with background blurs to create "glass" surfaces.

## Typography

This design system uses a dual-font strategy to balance character with legibility. 

- **Outfit (Headlines):** A modern geometric sans-serif that provides a clean, premium look. For top-level displays, use a linear gradient: `from teal-400 to emerald-600` at a 135-degree angle.
- **Inter (Body & Labels):** A highly legible, systematic typeface for all functional text, product descriptions, and metadata.

**Styling Notes:**
- All headlines should use a slight negative letter spacing to feel more "tight" and editorial.
- Labels for categories or status tags should use uppercase with generous letter spacing for a refined, boutique feel.

## Layout & Spacing

The layout follows a **Fluid Grid** model with generous white space (or "dark space") to emphasize the luxury aspect. 

- **Desktop:** 12-column grid with a 1280px max-width.
- **Mobile:** Single column with 16px side margins.
- **Rhythm:** An 8px linear scale is used for all internal component spacing, while section gaps use a 16px scale (e.g., 64px, 80px) to provide significant breathing room between discovery modules.

Components should be grouped in "stacks" with 12px or 16px gaps to maintain a clear visual relationship between headers and content.

## Elevation & Depth

Elevation is achieved through **Glassmorphism** rather than traditional drop shadows.

- **Base Layer (Level 0):** `#0a0a0a` solid background.
- **Glass Layer (Level 1):** `bg-white/5` with a `backdrop-blur-md` (12px-16px blur). 
- **Active Layer (Level 2):** `bg-white/10` with a subtle teal-tinted outer glow (0px 4px 20px rgba(20, 184, 166, 0.15)).
- **Outlines:** All glass elements must have a `1px` border using `white/10` to define the edges against the dark background.

**Visual Cue:** When an item is focused or hovered, increase the border opacity to `white/20` and the backdrop blur intensity.

## Shapes

The shape language is "Rounded," striking a balance between modern tech and approachable luxury. 

- **Cards/Containers:** Use `rounded-2xl` (1.5rem / 24px) to create a soft, high-end feel.
- **Buttons/Inputs:** Use `rounded-lg` (0.5rem / 8px) for a more precise, functional appearance.
- **Interactive Tags:** Small chips and badges should use a full "pill" radius for distinct categorization.

## Components

### Buttons
- **Primary:** Solid Teal (#14b8a6) with black text for maximum visibility.
- **Secondary:** Glass background (`white/10`) with white text and a `white/20` border.
- **Ghost:** No background, teal text, subtle hover state with `white/5` fill.

### Product Cards (Discovery)
- **Background:** `white/5` backdrop with `backdrop-blur-md`.
- **Border:** `1px solid white/10`.
- **Hover State:** Subtle scale-up (1.02x) and the border shifts to `teal/40`. The background blur increases slightly.
- **Image:** Full-width top section with a slight bottom-to-top dark gradient overlay to ensure text legibility if labels overlap the image.

### Chips & Badges
- **Trending:** Amber background with black text.
- **Category:** Transparent with a `white/10` border and `Inter Label-Bold` typography.

### Input Fields
- **Search Bar:** Large `white/5` glass bar with `backdrop-blur-xl`. The placeholder text should be `white/40`. On focus, the border glows with a soft teal tint.

### Lists & Navigation
- **Navigation Links:** Simple Inter font with a horizontal teal line appearing below the active item.
- **Dropdowns:** High-density glass (`white/15`) to ensure they pop against the underlying content layers.