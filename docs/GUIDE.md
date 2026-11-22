# NinjagoWeebs Site Guide

This guide explains how to run, edit, and publish this blog. The site uses
[Jekyll](https://jekyllrb.com/) with the [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy)
theme and deploys to GitHub Pages.

> For content strategy, writeup structure, educational writing, formatting,
> SEO, and publishing checklists, see
> [BLOG-GUIDE.md](BLOG-GUIDE.md).
> Ready-to-copy post templates are in [templates/](templates/).

---

## 1. Run the site locally

### First-time setup

```bash
cd site

# Install gems inside the project instead of the system Ruby folder.
# This avoids "permission denied" errors on Linux.
bundle config set --local path vendor/bundle
bundle install

# Chirpy keeps its static assets in a git submodule.
git submodule update --init --recursive
```

### Start a local preview

```bash
bundle exec jekyll serve --livereload
```

Open <http://127.0.0.1:4000>. The page refreshes automatically when you save a
file.

### Build the production site

```bash
JEKYLL_ENV=production bundle exec jekyll build
```

The generated site is written to `_site/`.

### Test for broken links

```bash
bundle exec htmlproofer _site \
  --disable-external \
  --ignore-urls "/^http:\/\/127.0.0.1/,/^http:\/\/0.0.0.0/,/^http:\/\/localhost/"
```

---

## 2. Change the site settings

Most global settings live in `_config.yml`.

| Setting | What it does |
| --- | --- |
| `title` | Site title in the sidebar and browser tab |
| `tagline` | Subtitle under the title |
| `description` | Description used by search engines and the RSS feed |
| `url` | Full site URL, without a trailing slash |
| `baseurl` | Subpath, e.g. `/site` for a project page. Leave empty for `username.github.io` |
| `github.username` | GitHub username used by the theme |
| `social.name` | Author name and copyright owner |
| `social.links` | Social links. The first one is the author link |
| `avatar` | Path or URL to the sidebar avatar image |
| `theme_mode` | `light`, `dark`, or empty to follow the system |
| `toc` | Show the table of contents on posts |
| `paginate` | Number of posts per home page |

After changing `_config.yml`, restart `jekyll serve`.

---

## 3. Create a new post

1. Create a file in `_posts/` named `YYYY-MM-DD-short-title.md`.
   Example: `_posts/2026-11-25-htb-example-writeup.md`
2. Add front matter at the top:

```yaml
---
title: HTB Example Writeup
date: 2026-11-25 20:30:00 +0700
categories: [Writeups, HackTheBox]
tags: [linux, privilege-escalation, nmap]
description: A short summary that appears on the home page and in search results.
pin: false
toc: true
comments: true
---
```

3. Write the post in Markdown below the front matter.

### Front matter fields

| Field | Required | Notes |
| --- | --- | --- |
| `title` | Yes | Post title |
| `date` | Yes | Include the timezone, e.g. `+0700` |
| `categories` | No | Up to two categories |
| `tags` | No | Any number, preferably lowercase |
| `description` | No | Custom summary for the home page and SEO |
| `pin` | No | `true` pins the post to the top of the home page |
| `toc` | No | `false` hides the table of contents for this post |
| `comments` | No | `false` disables comments for this post |
| `image` | No | Preview image (1200×630 recommended) |
| `media_subpath` | No | Folder prefix for images used in the post |
| `math` | No | `true` enables MathJax |
| `mermaid` | No | `true` enables Mermaid diagrams |

### Markdown examples

**Prompt boxes**

```markdown
> This is a tip.
{: .prompt-tip }

> This is a warning.
{: .prompt-warning }
```

**Code block with a filename**

````markdown
```bash
nmap -sC -sV -oA scan 10.10.10.10
```
{: file="scan.sh" }
````

**Inline file path**

```markdown
Edit `_config.yml`{: .filepath } to change the title.
```

**Image**

```markdown
![Screenshot](/assets/img/posts/example/screenshot.png){: w="800" h="450" }
_Caption text_
```

If you set `media_subpath: /assets/img/posts/example/` in the front matter, the
image path can be just `screenshot.png`.

### Drafts

Put unfinished posts in `_drafts/` and preview them with:

```bash
bundle exec jekyll serve --drafts
```

Drafts are not published until you move them to `_posts/` and give them a date.

---

## 4. Change the About page

The About page is `_tabs/about.md`.

```markdown
---
icon: fas fa-info-circle
order: 4
---

Your Markdown content goes here.
```

- `icon` is any [Font Awesome](https://fontawesome.com/icons) class.
- `order` controls the position in the sidebar. Lower numbers appear first.
- The page is published at `/about/`.

You can add more tabs by creating another file in `_tabs/`, for example
`_tabs/projects.md`:

```markdown
---
title: Projects
icon: fas fa-code
order: 5
---

Project list goes here.
```

---

## 5. Change icons

### Favicon (browser tab icon)

The theme provides default favicons from the gem. To replace them:

1. Create `assets/img/favicons/` in this repository.
2. Generate a favicon package at <https://realfavicongenerator.net/> using a
   square image of at least 512×512.
3. Copy the generated `.png`, `.ico`, and `.svg` files into
   `assets/img/favicons/`. Do **not** copy `site.webmanifest`.
4. Rebuild the site.

Files in your repository override the theme's files automatically.

### Sidebar avatar

1. Put an image at `assets/img/avatar.png` (or use any public URL).
2. Set it in `_config.yml`:

```yaml
avatar: /assets/img/avatar.png
```

### Contact and social icons

Edit `_data/contact.yml`. Each entry uses a Font Awesome icon class:

```yaml
- type: github
  icon: "fab fa-github"

- type: email
  icon: "fas fa-envelope"
  noblank: true
```

The theme only shows an entry when the matching URL exists. For example, the
GitHub icon uses `github.username` from `_config.yml`, and the email icon uses
`social.email`.

To add another platform, uncomment or copy a block and set its `url`:

```yaml
- type: linkedin
  icon: "fab fa-linkedin"
  url: "https://www.linkedin.com/in/your-name/"
```

### Share buttons

Edit `_data/share.yml` to choose which platforms appear at the bottom of posts.
The icons use the same Font Awesome classes.

### Icons inside posts

You can use Font Awesome directly in Markdown:

```html
<i class="fas fa-shield-halved"></i> Security note
```

---

## 6. Enable comments (optional)

The site uses [giscus](https://giscus.app/) (GitHub Discussions) as an example.

1. Make the repository public and enable **Discussions** in repository settings.
2. Install the giscus app at <https://github.com/apps/giscus>.
3. Open <https://giscus.app/>, enter the repository, and copy the generated IDs.
4. Fill in `_config.yml`:

```yaml
comments:
  provider: giscus
  giscus:
    repo: ninjagoweebs/ninjagoweebs.github.io
    repo_id: YOUR_REPO_ID
    category: Comments
    category_id: YOUR_CATEGORY_ID
    mapping: pathname
```

Comments are enabled globally once `provider` is set. Use `comments: false` in a
post's front matter to disable them for that post.

---

## 7. Publish to GitHub Pages

### Repository name matters

GitHub Pages builds the URL from the account and repository name:

| Repository | URL |
| --- | --- |
| `ninjagoweebs.github.io` | `https://ninjagoweebs.github.io/` |
| `site` | `https://ninjagoweebs.github.io/site/` |
| `blog` | `https://ninjagoweebs.github.io/blog/` |

This site is configured for the **root URL**, so the repository must be named
`ninjagoweebs.github.io`.

If you use a different repository name, update `_config.yml`:

```yaml
url: "https://ninjagoweebs.github.io"
baseurl: "/site"   # replace with the repository name
```

### First deployment

1. Create the repository `ninjagoweebs.github.io` on GitHub.
2. Push this project to the `main` branch.
3. In the repository, go to **Settings → Pages**.
4. Under **Build and deployment → Source**, choose **GitHub Actions**.
5. Open the **Actions** tab and wait for the "Build and Deploy" workflow.
6. Visit <https://ninjagoweebs.github.io/>.

The workflow is `.github/workflows/pages-deploy.yml`. It:

- checks out the `assets/lib` submodule (`submodules: true`),
- installs Ruby and the gems,
- builds the site with `JEKYLL_ENV=production`,
- runs `htmlproofer`,
- deploys the result to GitHub Pages.

### Custom domain (optional)

1. In **Settings → Pages → Custom domain**, enter your domain.
2. Add the DNS records GitHub shows (usually a `CNAME` for `www` and `A`/`AAAA`
   records for the apex domain).
3. Enable **Enforce HTTPS** after DNS has propagated.
4. Update `url` in `_config.yml` to the custom domain.

---

## 8. Troubleshooting

| Problem | Cause | Fix |
| --- | --- | --- |
| `Permission denied` while installing gems | Bundler is writing to the system Ruby folder | `bundle config set --local path vendor/bundle` then `bundle install` |
| Site has no styling or JavaScript | `assets/lib` submodule is empty | `git submodule update --init --recursive` |
| CSS/links 404 after deployment | Wrong `baseurl` | Set `baseurl` to `/<repository-name>` or use the `username.github.io` repository |
| Post does not appear | Future date, wrong filename, or file not in `_posts/` | Use `YYYY-MM-DD-title.md` and a date that is not in the future |
| Date looks wrong | Missing timezone | Set `timezone` in `_config.yml` and `+/-TTTT` in the post date |
| `htmlproofer` fails | Broken internal link or missing image | Fix the link/path shown in the error |
| GitHub Actions fails on checkout | Submodule not fetched | Keep `submodules: true` in the workflow |
| GitHub Actions fails on deploy | Pages source is not GitHub Actions | Set **Settings → Pages → Source** to **GitHub Actions** |
| Old content still shows after deploy | PWA service worker cache | Hard-refresh, clear site data, or temporarily set `pwa.enabled: false` |
| `bundle: command not found` | Bundler is not installed | `gem install bundler` |

### Useful commands

```bash
# Show the theme gem location
bundle info --path jekyll-theme-chirpy

# Clean generated files
bundle exec jekyll clean

# Check installed gems
bundle check

# Reinstall dependencies
bundle install
```

---

## 9. Project structure

```text
site/
├── _config.yml          # Main site configuration
├── _data/
│   ├── contact.yml      # Sidebar contact/social icons
│   └── share.yml        # Post share buttons
├── _posts/              # Published posts
├── _drafts/             # Unpublished drafts
├── _tabs/               # Sidebar pages (About, Archives, Categories, Tags)
├── _plugins/            # Jekyll plugins from the Chirpy starter
├── assets/
│   ├── img/             # Your images, avatar, favicons
│   └── lib/             # Chirpy static assets (git submodule)
├── .github/workflows/   # GitHub Pages deployment workflow
├── docs/                # This guide (not published)
├── Gemfile
└── index.html           # Home page
```

---

## 10. Quick checklist for a new writeup

1. Create `_posts/YYYY-MM-DD-title.md`.
2. Fill in `title`, `date` (with timezone), `categories`, and `tags`.
3. Add a `description` for the home page.
4. Put images in `assets/img/posts/<post-name>/`.
5. Preview with `bundle exec jekyll serve --livereload`.
6. Build with `JEKYLL_ENV=production bundle exec jekyll build`.
7. Commit and push to `main`.
8. Check the Actions tab and the live site.
