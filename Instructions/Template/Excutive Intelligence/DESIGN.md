---
name: Executive Intelligence
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#45464d'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#006c49'
  on-secondary: '#ffffff'
  secondary-container: '#6cf8bb'
  on-secondary-container: '#00714d'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#3e0500'
  on-tertiary-container: '#cf644e'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffdad3'
  tertiary-fixed-dim: '#ffb4a5'
  on-tertiary-fixed: '#3e0500'
  on-tertiary-fixed-variant: '#802918'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display-xl:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-lg:
    fontFamily: Outfit
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  body-lg:
    fontFamily: Outfit
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Outfit
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Outfit
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Outfit
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-padding: 32px
  gutter: 24px
  card-gap: 24px
  section-margin: 48px
---

## Brand & Style

The design system is engineered for "Executive Intelligence," a brand identity that communicates high-level clarity, analytical depth, and premium reliability. The target audience includes decision-makers and analysts who require complex data to be presented with poise and precision.

The aesthetic is a sophisticated hybrid of **Glassmorphism**, **Aurora UI**, and **Neumorphism**. These styles are not used simultaneously but are applied to specific architectural layers to maintain a balanced, modern interface:
- **Glassmorphism** is reserved for navigational surfaces (sidebars and top bars) to maintain a sense of space and context.
- **Aurora UI** serves as the primary environmental backdrop, using organic gradients to reduce visual fatigue and inject a premium feel.
- **Neumorphism** is applied sparingly to tactile interactive elements—buttons, toggles, and status cards—to provide a distinct physical feedback loop.

The emotional response should be one of "calm authority"—the UI feels expansive yet structured, providing a high-contrast environment where data is the protagonist.

## Colors

The palette is anchored by **Deep Indigo (#0F172A)**, used for primary typography and structural icons to ensure maximum legibility against light surfaces. **Forest Green** acts as the success indicator, while **Muted Terracotta** provides a sophisticated, non-aggressive warning state.

The environment utilizes a "Soft Alabaster" base. When the Aurora theme is active, a background mesh gradient of indigos, teals, and amethysts is used at low saturation (10-15%) behind the primary content area. 

For Neumorphic elements, the background color and element color must be identical (#F1F5F9) to allow shadows to define the form. Glassmorphic panels use a high-refraction blur (20px to 30px) to ensure background colors bleed through without sacrificing text clarity.

## Typography

The typography system relies exclusively on **Outfit** to maintain a geometric, clean, and forward-thinking appearance. 

The scale is built on a tight 4px baseline grid. Display and Headline levels use a slight negative letter spacing to create a "dense," authoritative look common in high-end editorial and financial reporting. Body text remains at standard tracking for accessibility. Label styles are intentionally uppercase or high-weight to distinguish them from data values in dense dashboard views.

## Layout & Spacing

This design system employs a **Fixed Grid** philosophy for data density, transitioning to a **Fluid Grid** for content-heavy sections.

- **Desktop (1280px+):** 12-column grid with 24px gutters and 32px side margins. Cards typically span 3, 4, or 6 columns.
- **Tablet (768px - 1279px):** 8-column grid with 20px gutters. Navigation sidebars collapse into a glassmorphic overlay menu.
- **Mobile (<768px):** 4-column grid with 16px gutters. Padding is reduced to 16px to maximize screen real estate.

Spacing rhythm follows a strict 8px incremental scale (8, 16, 24, 32, 48, 64). Larger gaps (48px+) are used to separate major analytical sections, creating a clear visual hierarchy between distinct data sets.

## Elevation & Depth

Elevation is achieved through three distinct methodologies based on the component's role:

1.  **Glassmorphic Navigation:** Use `backdrop-filter: blur(24px)` with a 1px solid border of `rgba(255,255,255, 0.4)`. This creates a sense of "above-the-content" positioning without a heavy shadow.
2.  **Aurora Floating Cards:** Data cards sit on the Aurora background with a soft, neutral shadow: `0 10px 15px -3px rgba(0, 0, 0, 0.05)`. This makes the "solid white" cards feel light and airy.
3.  **Neumorphic Tactility:** Interactive elements (buttons, switches) use two shadows for the "extruded" effect:
    - **Top-left:** Light shadow (e.g., `white` or `rgba(255,255,255,0.8)`)
    - **Bottom-right:** Soft dark shadow (e.g., `rgba(203, 213, 225, 0.5)`)
    - **Active/Inset State:** Reverse the shadows to create an "inner shadow" effect, indicating the element has been pressed.

## Shapes

The design system uses a **Rounded** (Level 2) shape language to soften the analytical nature of the data. 

- **Standard Elements:** 0.5rem (8px) radius (e.g., small buttons, input fields).
- **Large Elements (Lg):** 1rem (16px) radius (e.g., data cards, modal windows).
- **Extra Large (Xl):** 1.5rem (24px) radius (e.g., large Aurora background containers).

The consistency of these radii ensures that even with varying depth effects (Glass vs. Neumorphic), the UI feels like part of the same ecosystem.

## Components

### Buttons
- **Primary:** Neumorphic "extruded" style with Deep Indigo text. On hover, the shadow intensity increases slightly.
- **Secondary:** Glassmorphic "ghost" style with a 1px white border and blur.

### Data Cards
- Pure white background with 16px corner radius.
- Padding should be a minimum of 24px (Spacing unit x3).
- Used to house charts, tables, and KPIs.

### Input Fields
- Inset Neumorphic style (concave). The field should look "carved" into the surface.
- Focus state: A thin 1px border of Deep Indigo (#0F172A).

### Chips & Tags
- Used for category filtering.
- 50% opacity of their respective status colors (Green/Terracotta) with high-contrast text.

### Navigation Sidebar
- Glassmorphic panel with a 1px right-side border. 
- Active states use a solid Deep Indigo "pill" indicator that sits behind the label.

### Metric Cards
- Small, tactile blocks using the Neumorphic extrusion. 
- The primary number should be in Display-XL size for immediate impact.