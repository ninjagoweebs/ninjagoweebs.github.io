# NinjagoWeebs

Personal blog for security writeups, CTF walkthroughs, and educational posts.

- Live site: <https://ninjagoweebs.github.io/>
- Theme: [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) (Jekyll)
- Hosting: GitHub Pages (GitHub Actions)

## Local development

```bash
cd site

# Install gems inside the project to avoid system permission errors.
bundle config set --local path vendor/bundle
bundle install

# Chirpy static assets live in a git submodule.
git submodule update --init --recursive

# Preview at http://127.0.0.1:4000
bundle exec jekyll serve --livereload
```

Production build:

```bash
JEKYLL_ENV=production bundle exec jekyll build
```

## Publishing

Push to `main`. The workflow in `.github/workflows/pages-deploy.yml` builds and
deploys the site. In the repository settings, set **Pages → Source** to
**GitHub Actions**.

The repository must be named `ninjagoweebs.github.io` to serve the site at
`https://ninjagoweebs.github.io/`. For any other repository name, set
`baseurl: "/<repository-name>"` in `_config.yml`.

## Documentation

See [docs/GUIDE.md](docs/GUIDE.md) for:

- creating and formatting posts,
- changing the About page,
- changing favicons, avatars, and social icons,
- enabling comments,
- deployment and troubleshooting.

## Project layout

```text
site/
├── _config.yml       # site settings
├── _posts/           # published posts
├── _drafts/          # drafts
├── _tabs/            # About, Archives, Categories, Tags pages
├── _data/            # contact and share icons
├── assets/img/       # your images, avatar, favicons
├── docs/GUIDE.md     # editing and deployment guide
└── index.html        # home page
```

## License

The blog content is © NinjagoWeebs. The Chirpy theme is MIT licensed.
