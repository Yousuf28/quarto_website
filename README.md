# Quarto Website - Blog

A fast, optimized Quarto website hosted on GitHub Pages with custom domain support.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Adding a New Blog Post](#adding-a-new-blog-post)
- [Rendering the Website](#rendering-the-website)
- [Building with Optimizations](#building-with-optimizations)
- [Deploying to GitHub Pages](#deploying-to-github-pages)
- [Performance Optimizations](#performance-optimizations)

## 🔧 Prerequisites

Before you begin, ensure you have:

1. **Quarto** installed ([Installation Guide](https://quarto.org/docs/get-started/))
   ```bash
   # Verify installation
   quarto --version
   ```

2. **Python 3** installed
   ```bash
   python3 --version
   ```

3. **BeautifulSoup4** Python package (for HTML optimization)
   ```bash
   pip install beautifulsoup4
   ```

## 📁 Project Structure

```
quarto_website/
├── _quarto.yml          # Quarto project configuration
├── index.qmd            # Homepage
├── about.qmd            # About page
├── posts.qmd            # Blog listing page
├── posts/               # Blog posts directory
│   ├── _metadata.yml    # Post metadata defaults
│   ├── welcome/         # Example post
│   │   ├── index.qmd
│   │   └── thumbnail.jpg
│   └── your-post/       # Your new posts go here
├── build.sh             # Build script (render + optimize)
├── optimize_html.py     # HTML optimization script
├── docs/                # Output directory (deployed to GitHub Pages)
└── styles.css           # Custom CSS
```

## ✍️ Adding a New Blog Post

### Step 1: Create Post Directory

Create a new directory for your post inside the `posts/` folder:

```bash
mkdir posts/your-post-title
```

**Note:** Use lowercase letters, hyphens, and numbers. Avoid spaces and special characters.

### Step 2: Create the Post File

Create an `index.qmd` file in your new directory:

```bash
touch posts/your-post-title/index.qmd
```

### Step 3: Write Your Post

Open `posts/your-post-title/index.qmd` and add your content:

```yaml
---
title: "Your Post Title"
author: "Yousuf Ali"
date: "2024-12-20"
categories: [news, tutorial, analysis]  # Optional categories
image: "thumbnail.jpg"                  # Optional: post thumbnail
---

Your post content goes here!

You can use **Markdown** formatting, code blocks, and more.

## Section Heading

- Bullet points
- More points

### Code Example

```python
def hello_world():
    print("Hello, World!")
```

### Adding Images

If you want to include images in your post:

1. Place image files in your post directory:
   ```bash
   posts/your-post-title/
   ├── index.qmd
   ├── thumbnail.jpg      # For post listing
   └── image1.png         # For post content
   ```

2. Reference them in your post:
   ```markdown
   ![](image1.png)
   ```

### Post Metadata Options

The YAML front matter supports these options:

- `title`: Post title (required)
- `author`: Author name
- `date`: Publication date in YYYY-MM-DD format
- `categories`: Array of categories (e.g., `[news, tutorial]`)
- `image`: Path to thumbnail image (relative to post directory)
- `draft`: Set to `true` to hide from listing (optional)

### Example: Complete Post

```yaml
---
title: "Getting Started with R"
author: "Yousuf Ali"
date: "2024-12-20"
categories: [tutorial, R, data-science]
image: "r-logo.png"
---

# Introduction

This post covers the basics of R programming.

## Installing R

```{r}
# R code example
x <- 1:10
mean(x)
```

## Conclusion

R is a powerful language for data analysis!
```

## 🎨 Rendering the Website

### Quick Render (Development)

For quick previews during development:

```bash
quarto render
```

This generates HTML files in the `docs/` directory but **without performance optimizations**.

### Preview Locally

After rendering, you can preview locally:

```bash
# Using Python's built-in server
cd docs
python3 -m http.server 8000

# Or using Quarto preview
quarto preview
```

Then open `http://localhost:8000` in your browser.

## 🚀 Building with Optimizations

**Always use this for production builds!**

The `build.sh` script renders your site and applies performance optimizations:

```bash
./build.sh
```

Or manually:

```bash
quarto render
python3 optimize_html.py
```

### What the Build Script Does

1. **Renders** all Quarto files to HTML (`quarto render`)
2. **Optimizes** HTML files for performance (`optimize_html.py`):
   - Defers non-critical JavaScript
   - Moves scripts to end of body
   - Adds CSS preload hints
   - Formats scripts for better parsing
   - Adds resource hints (preconnect)

### Build Output

Optimized files are written to the `docs/` directory, ready for deployment.

## 📤 Deploying to GitHub Pages

### Initial Setup

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Add new blog post: Your Post Title"
   git push origin main
   ```

2. **Configure GitHub Pages**:
   - Go to your repository → Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` (or your default branch)
   - Folder: `/docs`
   - Click Save

### After Each Build

1. **Build your site**:
   ```bash
   ./build.sh
   ```

2. **Commit and push**:
   ```bash
   git add docs/
   git commit -m "Update site: Add new post and optimizations"
   git push origin main
   ```

GitHub Pages will automatically deploy your changes (usually within 1-2 minutes).

### Custom Domain

If you have a custom domain:

1. Add a `CNAME` file in the `docs/` directory with your domain:
   ```
   yourdomain.com
   ```

2. Configure DNS records as per GitHub Pages documentation

3. The `CNAME` file is already included in your repo

## ⚡ Performance Optimizations

This website includes automatic performance optimizations:

- ✅ **Script deferral**: Non-critical scripts load asynchronously
- ✅ **CSS preloading**: Critical CSS loads early
- ✅ **Resource hints**: Preconnect for external resources
- ✅ **Optimized HTML**: Better parsing and rendering

See `PERFORMANCE_OPTIMIZATION.md` for detailed information.

## 🔍 Troubleshooting

### Build Script Fails

**Error**: `python3: command not found`
- **Solution**: Install Python 3 or use `python` instead

**Error**: `ModuleNotFoundError: No module named 'bs4'`
- **Solution**: Install BeautifulSoup4: `pip install beautifulsoup4`

### Posts Not Appearing

- Ensure your post has a valid `date` in YYYY-MM-DD format
- Check that `draft: true` is not set in post metadata
- Verify the post directory name doesn't have spaces or special characters

### Images Not Loading

- Use relative paths: `![](image.jpg)` not absolute paths
- Ensure image files are in the same directory as `index.qmd`
- Check file names match exactly (case-sensitive)

### Performance Issues

- Always use `./build.sh` instead of just `quarto render`
- Clear browser cache when testing
- Check browser DevTools Network tab for loading issues

## 📚 Additional Resources

- [Quarto Documentation](https://quarto.org/docs/)
- [Quarto Websites Guide](https://quarto.org/docs/websites/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)

## 📝 Quick Reference

```bash
# Add new post
mkdir posts/my-new-post
# Edit posts/my-new-post/index.qmd

# Build and optimize
./build.sh

# Preview locally
quarto preview

# Deploy
git add docs/
git commit -m "Update site"
git push origin main
```

---

**Happy Blogging! 🎉**

