# Performance Optimization Guide

This document explains the performance optimizations applied to your Quarto website.

## Quick Start

To build and optimize your website:

```bash
./build.sh
```

Or manually:

```bash
quarto render
python3 optimize_html.py
```

## Optimizations Applied

The `optimize_html.py` script automatically applies the following optimizations to all generated HTML files:

### 1. Script Deferral
- **Non-critical scripts** are moved to the end of the `<body>` tag with `defer` attribute
- **Critical scripts** (quarto.js, bootstrap.min.js) remain in `<head>` but are deferred
- This prevents scripts from blocking HTML parsing and rendering

### 2. CSS Preloading
- Critical CSS files (Bootstrap, Bootstrap Icons, Syntax Highlighting) are preloaded
- Browsers can start downloading CSS earlier, improving First Contentful Paint

### 3. Resource Hints
- `preconnect` hints added for external resources (e.g., GitHub)
- Reduces DNS lookup and connection time for external resources

### 4. Script Ordering
- Scripts are ordered to ensure dependencies load correctly
- Critical scripts load before dependent scripts

## Performance Monitoring

The optimization script includes performance monitoring that logs:
- Page load start time
- DOMContentLoaded event timing
- Individual script load times
- Resource load times and sizes
- Window load completion time

Logs are written to `.cursor/debug.log` in NDJSON format.

## Expected Improvements

After optimization, you should see:
- **Faster First Contentful Paint (FCP)**: CSS preloading and script deferral allow content to render sooner
- **Faster Time to Interactive (TTI)**: Scripts don't block rendering
- **Better Lighthouse scores**: Improved performance metrics
- **Reduced blocking time**: Scripts load asynchronously without blocking the main thread

## Testing Performance

1. **Before optimization**: Run `quarto render` and test your site
2. **After optimization**: Run `./build.sh` and test again
3. **Compare**: Use browser DevTools Network tab or Lighthouse to compare load times

## GitHub Pages Deployment

After running the build script, commit and push the optimized files in the `docs/` directory:

```bash
git add docs/
git commit -m "Optimize HTML for performance"
git push
```

## Troubleshooting

If scripts don't work after optimization:
1. Ensure scripts are loaded in the correct order
2. Check browser console for errors
3. Verify that deferred scripts don't have dependencies on non-deferred scripts

## Files Modified

- `optimize_html.py`: Post-processing script for HTML optimization
- `build.sh`: Build script that runs Quarto render + optimization
- `_quarto.yml`: Updated with performance-related settings

