# QuantEase — Design System

## 1. Purpose

This document defines the visual and interaction principles for the QuantEase frontend.

The purpose of the design system is to keep the application visually consistent across:

- Landing pages
- Authentication screens
- Dashboard
- Strategy configuration
- Backtesting forms
- Results pages
- Charts
- Tables
- Cards
- Navigation
- Alerts
- Loading and error states

Frontend implementations should follow this document unless an explicit design decision overrides it.

---

## 2. Brand Identity

### Product Name

**QuantEase**

The name combines:

- **Quant** — quantitative analysis, quantitative finance, and systematic trading
- **Ease** — making quantitative backtesting easier and more accessible

The visual identity should communicate:

- Quantitative precision
- Technical credibility
- Modern software
- Financial data
- Clarity
- Trust
- Efficiency

The interface should avoid unnecessary visual complexity.

---

## 3. Brand Assets

Recommended repository structure:

```text
assets/
├── quantease-logo.png
├── quantease-mascot.png
└── ...
```

### Logo

The official QuantEase logo should be used consistently across:

- Navigation
- Authentication pages
- Landing page
- Application branding
- Documentation where appropriate

Do not recreate or substantially alter the logo through CSS or generated graphics.

Reference:

```text
../assets/quantease-logo.png
```

### Mascot

The QuantEase mascot is part of the application's visual identity.

It may be used in:

- Landing pages
- Onboarding
- Authentication screens
- Informational sections
- Sign-in/Sign-up pages

Reference:
```text
../frontend/mascot.svg
```

The mascot should not be used in in data-dense dashboard areas.

---

## 4. Color System
Background color #f4f4f4
Primary color #020d20
secondary color #3d7c1f


Trading-related colors should remain semantically consistent.

For example:

- Positive / profitable result → success semantic color
- Negative / losing result → danger semantic color
- Neutral state → neutral/text color

Do not use colors arbitrarily when displaying financial results.

---

## 5. Typography

Fonts Should be directly imported from Google Fonts

### Primary Typeface


`Open Sans`

Use for:

- Body text
- Forms
- Navigation
- Tables
- General UI

### Heading Typeface

`Montserrat`

Use for:

- Page headings
- Section headings
- Major dashboard titles

If the same typeface is used throughout the application, maintain hierarchy through:

- Font size
- Font weight
- Line height
- Spacing

---

## 6. Typography Hierarchy

A consistent hierarchy should be maintained.

Suggested structure:

```text
Page Title
    ↓
Section Heading
    ↓
Card Heading
    ↓
Body Text
    ↓
Supporting / Muted Text
```

Avoid excessive font sizes or decorative typography.

The dashboard should prioritize readability of quantitative information.

---

## 7. Layout Principles

QuantEase should use a clear and structured layout.

Primary principles:

- Strong visual hierarchy
- Consistent spacing
- Clear grouping
- Minimal visual clutter
- Responsive behavior
- Easy navigation
- High information density without sacrificing readability

Dashboard layouts should prioritize important information first.

---

## 8. Spacing

Use a consistent spacing scale throughout the interface.

Suggested base scale:

```text
4px
8px
12px
16px
24px
32px
48px
64px
```

Avoid arbitrary spacing values when an existing spacing token provides the required result.

---

## 9. Border Radius

Use consistent corner radii across:

- Cards
- Buttons
- Inputs
- Modals
- Dropdowns

Suggested system:

```text
Small controls: 6px
Standard components: 8px
Large cards/panels: 12px
```

These values are guidelines and should be replaced if the finalized QuantEase visual identity specifies different values.

---

## 10. Cards

Cards are appropriate for grouping:

- Account information
- Strategy parameters
- Performance metrics
- Trade statistics
- Backtest summaries
- Charts
- Status information

Cards should have:

- Clear hierarchy
- Consistent padding
- Consistent radius
- Subtle visual separation
- Minimal decoration

Do not use excessive cards merely to make the dashboard look more complex.

---

## 11. Buttons

Buttons should communicate hierarchy.

### Primary Button

Used for the main action on a page.

Examples:

- Run Backtest
- Create Strategy
- Sign In
- Save Strategy

### Secondary Button

Used for supporting actions.

Examples:

- Cancel
- Reset
- View Details

### Destructive Button

Used for irreversible actions.

Examples:

- Delete Strategy
- Delete Account

Destructive actions must require appropriate confirmation when necessary.

---

## 12. Forms

Forms should:

- Clearly label every input
- Use meaningful placeholders where helpful
- Validate user input
- Display useful error messages
- Preserve entered information when possible
- Avoid unnecessary fields

Strategy configuration forms should make quantitative parameters easy to understand.

---

## 13. Dashboard Design

The QuantEase dashboard is a data-dense environment.

Priority information should generally follow:

```text
Backtest Configuration
        ↓
Execution / Status
        ↓
Performance Summary
        ↓
Equity / Performance Charts
        ↓
Trade Statistics
        ↓
Detailed Trade Data
```

Important metrics should be visually prominent.

Examples include:

- Total trades
- Win rate
- Profit/loss
- Maximum drawdown
- Profit factor
- Average trade
- Risk/reward information
- Equity information

Metrics should not be visually exaggerated in a way that could mislead the user about their statistical importance.

---

## 14. Charts

Charts should prioritize:

- Accurate representation
- Readability
- Clear axes
- Meaningful labels
- Consistent units
- Useful tooltips

Potential QuantEase charts include:

- Equity curve
- Drawdown
- Cumulative P&L
- Trade distribution
- Performance by period
- Strategy comparison

Chart colors must follow the established color system.

Do not use decorative chart effects that reduce interpretability.

---

## 15. Tables

Tables should be used when users need detailed numerical information.

Potential tables include:

- Trade history
- Backtest results
- Strategy configurations
- Performance statistics

Tables should support:

- Clear column headings
- Consistent number formatting
- Appropriate alignment
- Readable spacing
- Responsive behavior where possible

Numerical values should use consistent decimal precision appropriate to the underlying data.

---

## 16. Loading States

Long-running backtests should communicate that processing is occurring.

A loading state should:

- Clearly indicate that the request is being processed
- Prevent accidental duplicate submissions where appropriate
- Avoid misleading progress percentages unless actual progress is available

Example:

```text
Running backtest...
Processing historical data...
Calculating performance...
```

Do not fabricate progress information.

---

## 17. Error States

Errors should be:

- Clear
- Specific
- Actionable where possible
- Visually distinct

Avoid exposing sensitive implementation details to end users.

For example, prefer:

> "Unable to run the backtest. Please check the selected strategy parameters."

over displaying a raw Python traceback.

Developer logs may contain more detailed diagnostic information.

---

## 18. Empty States

Empty states should explain:

1. What is missing
2. Why the area is empty
3. What the user can do next

Example:

> No backtests yet. Configure a strategy and run your first backtest.

Avoid empty states that contain only "No data."

---

## 19. Responsive Design

The frontend should work across:

- Desktop
- Laptop
- Tablet
- Mobile where practical

The dashboard should prioritize essential information on smaller screens rather than simply shrinking every component.

Complex charts and tables should remain usable on smaller displays.

---

## 20. Accessibility

Frontend implementations should consider:

- Sufficient text contrast
- Keyboard navigation
- Semantic HTML
- Form labels
- Accessible buttons
- Meaningful error messages
- Non-color-only indicators

Financial/quantitative information should not rely exclusively on color to communicate meaning.

For example, a profitable/losing state should ideally include a textual or symbolic indication in addition to color.

---

## 21. Frontend Technology Boundary

The current frontend technology direction is:

- HTML
- CSS
- JavaScript
- plotly.js for Visualizing the Equity Curve

The existing architecture should be respected.

Do not introduce a frontend framework or major dependency unless explicitly requested by the developer.

---

## 22. AI Agent Frontend Rules

When implementing frontend work, the AI coding agent should:

- Inspect the existing frontend before creating new components.
- Reuse existing styles and components where possible.
- Follow this design system.
- Preserve existing API contracts.
- Avoid changing backend business logic.
- Avoid changing backtesting behavior.
- Avoid introducing unnecessary dependencies.
- Keep changes focused on the requested feature.
- Test frontend behavior where practical.

---

## 23. Design Philosophy

The QuantEase interface should feel:

**Professional + Quantitative + Modern + Clear + Strict usage of Minimalism **

It should not feel:

**Overly decorative + cluttered + gamified + unnecessarily complex**

The primary objective of the interface is to help users understand and interact with quantitative backtesting results.

---

## 24. Design System Status

This document is a living specification.

Changes to the visual system should be documented here so that future frontend development remains consistent.
