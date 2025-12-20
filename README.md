# Quarto Website - Blog

A fast, optimized Quarto website hosted on GitHub Pages with custom domain support.

## Table of Contents

- [Prerequisites](#prerequisites)
- [How Quarto Websites Work](#how-quarto-websites-work)
- [How This Website Works](#how-this-website-works)
- [Adding a New Blog Post](#adding-a-new-blog-post)
- [Rendering and Previewing](#rendering-and-previewing)
- [Building with Optimizations](#building-with-optimizations)
- [Website Maintenance](#website-maintenance)
- [Deploying to GitHub Pages](#deploying-to-github-pages)
- [Troubleshooting](#troubleshooting)
- [Quick Reference](#quick-reference)

## Prerequisites

Before working with this website, ensure you have:

1. **Quarto** installed ([Installation Guide](https://quarto.org/docs/get-started/))
   ```bash
   # Verify installation
   quarto --version
   ```

2. **Python 3** installed (for HTML optimization)
   ```bash
   python3 --version
   ```

3. **BeautifulSoup4** Python package (for HTML optimization)
   ```bash
   pip install beautifulsoup4
   ```

## How Quarto Websites Work

Quarto is a publishing system that converts markdown files (`.qmd`) into HTML websites. Here's how it works:

### Basic Concepts

1. **Source Files**: Quarto uses `.qmd` files (Quarto Markdown) that contain:
   - YAML frontmatter (metadata like title, author, date)
   - Markdown content
   - Code blocks that can be executed

2. **Rendering**: The `quarto render` command converts `.qmd` files into HTML files that browsers can display.

3. **Project Structure**: A Quarto website project has:
   - `_quarto.yml` - Configuration file
   - Source files (`.qmd`) - Content files
   - Output directory - Where HTML files are generated

4. **Automatic Discovery**: Quarto automatically finds and processes files based on the project structure, so you don't need to manually register pages.

### Blog System

Quarto's blog system works by:
- Scanning a `posts/` directory for subdirectories
- Each subdirectory represents a blog post
- Each post must have an `index.qmd` file
- Quarto automatically generates a blog listing page
- Posts are discovered automatically - no manual registration needed

## How This Website Works

This website uses Quarto's automatic blog listing system. Here's the specific structure:

### Project Structure

```
quarto_website/
├── _quarto.yml          # Quarto project configuration
├── index.qmd            # Homepage
├── about.qmd            # About page
├── posts.qmd            # Blog listing page (auto-generated from posts/)
├── posts/               # Blog posts directory
│   ├── _metadata.yml    # Post metadata defaults
│   ├── welcome/         # Example post
│   │   ├── index.qmd
│   │   └── thumbnail.jpg
│   └── your-post/       # New posts go here
├── build.sh             # Build script (render + optimize)
├── optimize_html.py     # HTML optimization script
├── docs/                # Output directory (deployed to GitHub Pages)
└── styles.css           # Custom CSS
```

### Key Components

1. **`_quarto.yml`** - Main configuration:
   - Defines the navbar (Home, About, Blog/posts)
   - Sets output directory to `docs/`
   - Configures theme and styling

2. **`posts.qmd`** - Blog listing page that automatically:
   - Scans the `posts/` directory for all subdirectories
   - Lists each post as a card with title, date, author, and categories
   - Sorts posts by date (newest first)
   - Shows categories for filtering

3. **`posts/` directory** - Contains all blog posts:
   - Each post is a subdirectory (e.g., `posts/welcome/`, `posts/bash-scheduler/`)
   - Each subdirectory must contain an `index.qmd` file
   - Quarto automatically discovers posts - no manual registration needed

4. **`posts/_metadata.yml`** - Default settings for all posts:
   - Applies `title-block-banner: true` to all posts
   - Sets `freeze: false` (allows code execution)

### How Posts Are Discovered

Quarto automatically:
- Finds all subdirectories in `posts/`
- Reads the `index.qmd` file in each subdirectory
- Extracts metadata (title, date, author, categories) from YAML frontmatter
- Generates the blog listing page
- Creates individual post pages at `posts/your-post-name/`

**You don't need to edit `posts.qmd` or any configuration file** - just add a new directory with `index.qmd` and Quarto handles the rest!

## Adding a New Blog Post

To add a new blog post to this website, follow these steps:

### Step 1: Create Post Directory

Create a new directory for the post inside the `posts/` folder:

```bash
mkdir posts/your-post-title
```

**Naming Guidelines:**
- Use lowercase letters, hyphens, and numbers
- Avoid spaces and special characters
- Keep it short and descriptive (this becomes the URL)
- Examples: `bash-scheduler`, `r-tutorial`, `data-analysis-2024`

### Step 2: Create the Post File

Create an `index.qmd` file in the new directory:

```bash
touch posts/your-post-title/index.qmd
```

**Important:** The file **must** be named `index.qmd` - this is how Quarto identifies it as a post.

### Step 3: Write the Post

Open `posts/your-post-title/index.qmd` and add the content with YAML frontmatter:

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

### Post Metadata Options

The YAML front matter supports these options:

- `title`: Post title (required)
- `author`: Author name
- `date`: Publication date in YYYY-MM-DD format (required for sorting)
- `categories`: Array of categories (e.g., `[news, tutorial]`)
- `image`: Path to thumbnail image (relative to post directory)
- `draft`: Set to `true` to hide from listing (optional)

### Adding Images

To include images in a post:

1. Place image files in the post directory:
   ```bash
   posts/your-post-title/
   ├── index.qmd
   ├── thumbnail.jpg      # For post listing
   └── image1.png         # For post content
   ```

2. Reference them in the post:
   ```markdown
   ![](image1.png)
   ```

### Complete Post Example

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

## Rendering and Previewing

Understanding the difference between rendering and previewing is important for working with this website.

### What is Rendering?

**Rendering** converts Quarto (`.qmd`) files into HTML files that can be viewed in a browser. It's a one-time conversion process that creates static HTML files in the `docs/` directory.

**Key points:**
- Creates actual HTML files
- Files are saved to disk
- Required before deploying
- Can be done with or without optimizations

### What is Previewing?

**Previewing** starts a local web server to view the website in a browser. It can work with rendered files or render on-the-fly.

**Key points:**
- Starts a local server (doesn't create files by default)
- Shows the site in a browser
- Can auto-reload on changes
- Useful for development and testing

### The Difference

| Rendering | Previewing |
|-----------|------------|
| Converts `.qmd` to HTML files | Shows website in browser |
| Creates files on disk | Runs a local server |
| Required for deployment | Optional for development |
| One-time process | Continuous (while server runs) |
| Can include optimizations | Usually shows unoptimized version |

### Rendering Methods

#### Method 1: Basic Render (Quick Development)

For quick previews during development:

```bash
quarto render
```

**What it does:**
- Converts all `.qmd` files to HTML
- Outputs files to the `docs/` directory
- **Does NOT apply performance optimizations**
- Fast and good for checking content

**When to use:**
- Quick content checks
- Testing markdown formatting
- Development work

#### Method 2: Render Specific Files

Render only specific files instead of the entire site:

```bash
# Render a single post
quarto render posts/your-post/index.qmd

# Render multiple specific files
quarto render posts/post1/index.qmd posts/post2/index.qmd

# Render only the blog listing page
quarto render posts.qmd
```

**When to use:**
- Testing a single post
- Faster iteration during development
- Fixing issues in specific pages

#### Method 3: Render with Options

Customize rendering behavior:

```bash
# Render and watch for changes (auto-render on file changes)
quarto render --watch

# Render to a different output format
quarto render --to html

# Render with cache (faster for code-heavy posts)
quarto render --cache
```

### Previewing Methods

#### Method 1: Quarto Preview (Recommended)

The easiest way to preview with live reload:

```bash
quarto preview
```

**What it does:**
- Starts a local web server
- Automatically opens the browser
- Watches for file changes and auto-reloads
- Shows the site at `http://localhost:4200` (default port)
- Can render on-the-fly (no need to render first)

**Advantages:**
- Automatic browser refresh on changes
- No need to manually render first
- Integrated with Quarto workflow
- Shows exactly how the site will look

**Usage:**
```bash
# Start preview server
quarto preview

# Preview on a specific port
quarto preview --port 8080

# Preview and render on changes
quarto preview --render
```

**To stop:** Press `Ctrl+C` in the terminal

#### Method 2: Python HTTP Server

If you've already rendered and want a simple static server:

```bash
cd docs
python3 -m http.server 8000
```

Then open `http://localhost:8000` in the browser.

**Advantages:**
- Simple and lightweight
- Good for testing final output
- No dependencies beyond Python

**To stop:** Press `Ctrl+C` in the terminal

#### Method 3: Live Server (VS Code Extension)

If you use VS Code:

1. Install the "Live Server" extension
2. Right-click on `docs/index.html`
3. Select "Open with Live Server"

**Advantages:**
- Integrated with the editor
- Auto-reload on file changes
- Easy to use

### Recommended Workflow

**For adding a new post:**

1. Create and edit the post: `posts/my-post/index.qmd`
2. Start preview: `quarto preview` (renders automatically)
3. Make changes and see them update automatically
4. When satisfied, build for production: `./build.sh`
5. Preview final output: `cd docs && python3 -m http.server 8000`
6. Deploy when ready

**For quick checks:**

1. Render: `quarto render` (fast, no optimizations)
2. Preview: `cd docs && python3 -m http.server 8000`

**For production:**

1. Build: `./build.sh` (render + optimize)
2. Preview: `cd docs && python3 -m http.server 8000`
3. Deploy

### Preview Tips

When previewing, do the following:
- Check all pages: Navigate through Home, About, Blog listing, and individual posts
- Test responsive design: Resize the browser window
- Check images: Ensure all images load correctly
- Test links: Click all internal and external links
- Check categories: Verify categories appear and filter correctly
- Mobile preview: Use browser DevTools to test mobile view

## Building with Optimizations

For production deployment, always use the optimized build process.

### Production Build

The `build.sh` script renders the site and applies performance optimizations:

```bash
./build.sh
```

Or manually run both steps:

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

**Important:** Always use `./build.sh` before deploying to production. The optimizations improve page load speed and user experience.

### Performance Optimizations Included

This website includes automatic performance optimizations:

- **Script deferral**: Non-critical scripts load asynchronously
- **CSS preloading**: Critical CSS loads early
- **Resource hints**: Preconnect for external resources
- **Optimized HTML**: Better parsing and rendering

See `PERFORMANCE_OPTIMIZATION.md` for detailed information.

## Website Maintenance

### Regular Workflow

Follow these steps to maintain the website:

1. **Add/Edit Posts**: Create or modify posts in `posts/` directory
2. **Preview Changes**: Use `quarto preview` to check locally
3. **Build Site**: Run `./build.sh` to render and optimize
4. **Deploy**: Commit and push `docs/` directory to GitHub

### File Organization

```
posts/
├── _metadata.yml          # Default settings (don't edit often)
├── welcome/               # Post 1
│   ├── index.qmd
│   └── thumbnail.jpg
├── bash-scheduler/        # Post 2
│   └── index.qmd
└── your-new-post/         # New posts go here
    ├── index.qmd
    └── images/            # Optional: organize images in subfolder
```

### Post Metadata Best Practices

- **Date Format**: Always use `YYYY-MM-DD` (e.g., `"2024-12-19"`)
  - This ensures proper sorting on the blog page
- **Categories**: Use consistent category names
  - Examples: `[tutorial, bash]`, `[R, data-science]`, `[news]`
  - Categories appear as filters on the blog listing page
- **Title**: Keep titles concise but descriptive
- **Author**: Currently set to "Yousuf Ali" (can be customized per post)

### Updating Existing Posts

To edit an existing post, follow these steps:

1. Navigate to `posts/post-name/index.qmd`
2. Make the changes
3. Preview: `quarto preview` (optional)
4. Rebuild: `./build.sh`
5. Commit and push the changes

### Deleting Posts

To remove a post, follow these steps:

1. Delete the entire post directory: `rm -rf posts/post-name/`
2. Rebuild: `./build.sh`
3. Commit the deletion

### Managing Categories

Categories are defined in each post's YAML frontmatter. To add a new category:
- Use it in a post: `categories: [new-category]`
- It will automatically appear in the category filter on the blog page

### Common Tasks

**Change blog page title:**
- Edit `posts.qmd` and change `title: "Blog"`

**Change post sorting:**
- Edit `posts.qmd` and change `sort: "date desc"` to `sort: "date asc"` for oldest first

**Change default post settings:**
- Edit `posts/_metadata.yml` (affects all posts)

**Add a new page to navbar:**
- Edit `_quarto.yml` and add to `navbar.right` section

## Deploying to GitHub Pages

### Initial Setup

1. **Push the code to GitHub**:
   ```bash
   git add .
   git commit -m "Initial Quarto website setup"
   git push origin main
   ```

2. **Configure GitHub Pages**:
   - Go to the repository → Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` (or the default branch)
   - Folder: `/docs`
   - Click Save

### After Each Build

1. **Build the site**:
   ```bash
   ./build.sh
   ```

2. **Commit and push**:
   ```bash
   git add docs/
   git commit -m "Update site: Add new post and optimizations"
   git push origin main
   ```

GitHub Pages will automatically deploy the changes (usually within 1-2 minutes).

### Custom Domain

If you have a custom domain:

1. Add a `CNAME` file in the `docs/` directory with the domain:
   ```
   yourdomain.com
   ```

2. Configure DNS records as per GitHub Pages documentation

3. The `CNAME` file is already included in your repo

## Troubleshooting

### Build Script Fails

**Error**: `python3: command not found`
- **Solution**: Install Python 3 or use `python` instead

**Error**: `ModuleNotFoundError: No module named 'bs4'`
- **Solution**: Install BeautifulSoup4: `pip install beautifulsoup4`

**Error**: `Permission denied: ./build.sh`
- **Solution**: Make script executable: `chmod +x build.sh`

### Rendering Issues

**Posts not rendering:**
- Check for syntax errors in YAML frontmatter
- Ensure `index.qmd` file exists in post directory
- Verify date format is `YYYY-MM-DD`

**Code blocks not executing:**
- Check `posts/_metadata.yml` - `freeze: false` allows execution
- Ensure required packages/languages are installed

### Preview Issues

**Preview server won't start:**
- Check if port is already in use (try different port: `quarto preview --port 8080`)
- Ensure Quarto is properly installed: `quarto --version`

**Changes not showing in preview:**
- Save files (unsaved changes won't be detected)
- Try stopping and restarting preview server
- Clear browser cache

### Posts Not Appearing

- Ensure the post has a valid `date` in YYYY-MM-DD format
- Check that `draft: true` is not set in post metadata
- Verify the post directory name doesn't have spaces or special characters
- Rebuild the site: `./build.sh`

### Images Not Loading

- Use relative paths: `![](image.jpg)` not absolute paths
- Ensure image files are in the same directory as `index.qmd` (or use correct relative path)
- Check file names match exactly (case-sensitive)
- Verify images are committed to git

### Performance Issues

- Always use `./build.sh` instead of just `quarto render`
- Clear browser cache when testing
- Check browser DevTools Network tab for loading issues
- Verify optimizations were applied (check HTML source for deferred scripts)

## Quick Reference

### Complete Workflow: Adding a New Post

```bash
# 1. Create post directory
mkdir posts/my-new-post

# 2. Create and edit the post file
# Edit posts/my-new-post/index.qmd with the content

# 3. Preview while editing (optional but recommended)
quarto preview

# 4. Build and optimize for production
./build.sh

# 5. Preview final output (optional)
cd docs && python3 -m http.server 8000

# 6. Deploy to GitHub Pages
git add posts/my-new-post/
git add docs/
git commit -m "Add new post: My New Post"
git push origin main
```

### Daily Maintenance Commands

```bash
# Preview site with live reload
quarto preview

# Build site (after making changes)
./build.sh

# Preview built site
cd docs && python3 -m http.server 8000

# Deploy changes
git add .
git commit -m "Update site"
git push origin main
```

### Render Commands

```bash
# Basic render (no optimizations)
quarto render

# Render specific file
quarto render posts/my-post/index.qmd

# Render with watch mode
quarto render --watch

# Production build (render + optimize)
./build.sh
```

### Preview Commands

```bash
# Quarto preview (recommended)
quarto preview

# Preview on specific port
quarto preview --port 8080

# Python HTTP server (after rendering)
cd docs && python3 -m http.server 8000
```

### Post Template

When creating a new post, use the following template:

```yaml
---
title: "Your Post Title"
author: "Yousuf Ali"
date: "2024-12-19"  # Use current date in YYYY-MM-DD format
categories: [category1, category2]  # Optional but recommended
---

Your post content starts here...

Use Markdown for formatting:
- **Bold text**
- *Italic text*
- Code blocks with syntax highlighting
- Lists and more
```

---

**Happy Blogging!**
