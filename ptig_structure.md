# .ptigprj File Format Specification

## Overview

A `.ptigprj` file is a JSON document that defines a Pytigon project (Django-based). The filename (without extension) is the project name, e.g. `schportal.ptigprj` produces the project folder `pytigon_standard_prj/prj/schportal/`.

Projects whose name starts with `_` (e.g. `_schtools`, `_schdata`) are library/internal projects that provide reusable apps for other projects. Projects without `_` (e.g. `schportal`, `scheditor`, `schdevtools`) are standalone runnable applications.

## Architecture: Database as Source of Truth

The `schdevtools` project (in `pytigon_standard_prj/prj/schdevtools/`) manages the entire project lifecycle through its `schbuilder` app. The project structure lives in the database as `schbuilder` models (`SChProject`, `SChApp`, `SChTable`, `SChField`, `SChView`, `SChTemplate`, `SChForm`, `SChFormField`, `SChTask`, `SChChannelConsumer`, `SChAppMenu`, `SChChoice`, `SChChoiceItem`, `SChStatic`, `SChFile`, `SChLocale`, `SChTranslate`).

The lifecycle works in four stages:

1. **Database editing**: All editing happens against the database via the `schdevtools` IDE UI. The database is the *source of truth*.

2. **Export to `.ptigprj`** (`prj_export_to_str()` in `schbuilder/views.py`): Serializes the entire model tree into the JSON format described in this document. Uses the `EX_IMP` dict to define the parent-child hierarchy.

3. **Import from `.ptigprj`** (`prj_import_from_str()`): Imports the JSON back into the database. The new project version gets `main_view=True`; previous versions with the same name are archived (version stamped with date, `main_view` set to `False`).

4. **Build to Django project** (`build_prj()`): Transforms the database structure into a runnable Django project in `pytigon_standard_prj/prj/<project_name>/` using generator templates (in `schdevtools/templates/schbuilder/wzr/`).

### Round-trip preservation: `#[[START]]` / `#[[END]]` markers

When `build_prj()` generates files, it wraps every piece of user-injected code in special comment markers:

```
#[[START SChTable.42.table_code]]
...user code...
#[[END]]
```

Format: `#[[START <prefix?><Model>.<pk>.<field_name>]]`

- **No prefix** → start section (injected *before* generated content, via `first_section`)
- **`+` prefix** (e.g. `#[[START +SChApp.42.model_code]]`) → end section (injected *after* generated content, via `second_section`)

When re-building in "milestone" mode, the generator reads existing files, extracts content between matching markers, and updates the database. This enables round-trip editing: database → generated file → manual edit → re-import.

### The `$$$` separator: `first_section` / `second_section`

Several code fields support a two-section split using `$$$`. The `first_section` template filter returns text *before* `$$$`; `second_section` returns text *after* `$$$`. If `$$$` is absent, the entire value is `first_section`.

| Field | Model | File | `first_section` (before generated content) | `second_section` (after generated content) |
|---|---|---|---|---|
| `additional_settings` | `SChProject` | `settings_app.py` | After `MEDIA_ROOT`/`UPLOAD_PATH`, before `init()` call | After database config + env parsing, before `finish()` |
| `model_code` | `SChApp` | `models.py` | After imports, before choice lists + model classes | After all model classes + `admin_register()` |
| `view_code` | `SChApp` | `views.py` | After imports, before `PFORM` + form classes | After all form classes + view functions |
| `urls_code` | `SChApp` | `urls.py` | After `gen = generic_table_start(...)`, before `gen.standard()` calls | After all `gen.standard()`/`gen.for_field()` calls |
| `tasks_code` | `SChApp` | `tasks.py` | After imports, before task functions | After all task functions |
| `consumer_code` | `SChApp` | `consumers.py` | After imports, before consumer classes | After all consumer classes |
| `extra_code` | `SChView` | `views.py` | Before the view function (decorator area) | After the view function body |

**Example**: `model_code` with `$$$` (from `_schbusiness.ptigprj`):
```
# first_section: injected before model classes
import pyarrow
import duckdb
$$$e = schelements.models.Element
e.add_type("I-DEV-C", "Item/Device/Computer", "Computers", "Computer", "schhardware")
```
Generates in `models.py`:
```python
# ... standard imports ...
import pyarrow
import duckdb
# ... choice lists ...
# ... model class definitions ...
admin_register(OtherDevice)
e = schelements.models.Element
e.add_type("I-DEV-C", "Item/Device/Computer", "Computers", "Computer", "schhardware")
```

### The `ext_apps` `@` prefix

Entries in `ext_apps` prefixed with `@` are handled differently by `SChProject`:
- **Without `@`** (normal, e.g. `_schwiki.schwiki`): Added to `APPS` in `apps.py`. Installed via `get_app_config()` and registered in `INSTALLED_APPS`.
- **With `@`** (e.g. `@schelements`): Added to `APPS_EXT` in `apps.py`. Installed directly via `INSTALLED_APPS.append()`.

The `apps.py` template:
```python
APPS=['schbrowser','_schwiki.schwiki','_schtools.schtasks']  # local + ext (without @)
APPS_EXT=[]  # ext apps with @ prefix
PUBLIC = True  # from prj.public
```

### Related projects and static files

`SChProject.get_related_projects()` scans `ext_apps` (extracting pack names before `.`) and `custom_tags` (extracting pack names before `/`). For each related project, the build process adds their `static/` directory to `STATICFILES_DIRS`, enabling shared static resources.

---

## Top-Level Structure

```json
{
    "model": "SChProject",
    "attributes": { ... },
    "children": [ ... ]
}
```

The root is always `"model": "SChProject"`. The `children` array contains `SChApp`, `SChStatic`, and `SChLocale` nodes. Each `SChApp` has its own `children` array.

### Export/import hierarchy (`EX_IMP`)

The JSON tree mirrors this exact parent-child structure:

```
SChProject
├── SChApp
│   ├── SChChoice
│   │   └── SChChoiceItem
│   ├── SChTable
│   │   └── SChField
│   ├── SChView
│   ├── SChTemplate
│   ├── SChAppMenu
│   ├── SChForm
│   │   └── SChFormField
│   ├── SChTask
│   ├── SChFile
│   └── SChChannelConsumer
├── SChStatic
└── SChLocale
    └── SChTranslate
```

---

## Generated Project File Structure

When `build_prj()` runs, it produces this tree in `pytigon_standard_prj/prj/<project_name>/`:

```
<project_name>/
├── __init__.py              # Generated from wzr/init.html template
├── apps.py                  # Generated from wzr/apps.html: APPS + APPS_EXT + PUBLIC
├── settings_app.py          # Generated from wzr/settings_app.html
├── manage.py                # Generated from wzr/manage.html
├── asgi.py                  # Generated from wzr/asgi.html
├── wsgi.py                  # Generated from wzr/wsgi.html
├── install.ini              # From install_file attribute (+ PRJ_NAME, PRJ_TITLE, GEN_TIME)
├── README.md                # From readme_file
├── LICENSE                  # From license_file
├── env                      # From SChStatic type "O" name "env" (.env content)
├── templates/               # Compiled .html templates
│   ├── theme/
│   │   └── *.html           # From template_desktop/smartphone/tablet/schweb/theme
│   └── <app_name>/
│       └── <template_name>.html  # From SChTemplate (if name has no ".")
├── templates_src/           # Source .ihtml templates (before compilation)
│   ├── theme/
│   └── <app_name>/
│       └── <template_name>.ihtml
├── plugins/                 # From SChFile type "p"/"i"
│   └── <app_name>/
│       └── <plugin_name>/
│           ├── __init__.py
│           └── *.html
├── static/
│   └── <project_or_app_name>/
│       ├── js/               # SChStatic type "J"/"P" → compiled
│       ├── css/              # SChStatic type "C"/"I" → compiled
│       └── components/       # SChStatic type "R" → compiled
└── <app_name>/              # One per SChApp
    ├── __init__.py          # From wzr/app_init.html (ModuleName, Title, Urls, etc.)
    ├── models.py            # From wzr/models.html (choices + model classes + model_code)
    ├── views.py             # From wzr/views.html (PFORM + forms + view functions)
    ├── urls.py              # From wzr/urls.html (urlpatterns + gen.standard/for_field)
    ├── tasks.py             # From wzr/tasks.html (task functions)
    ├── consumers.py         # From wzr/consumers.html (consumer classes)
    ├── applib/              # Library code
    │   ├── __init__.py
    │   └── <name>.py        # From SChFile type "l"
    ├── templatetags/
    │   └── <name>.py        # From SChFile type "f" or "t"
    ├── management/
    │   └── commands/
    │       └── <name>.py    # From SChFile type "m"
    ├── migrations/
    ├── static/
    │   └── <app_name>/
    │       └── views/
    │           ├── <name>.js     # From SChFile type "j" (python→js)
    │           └── <name>.html   # From SChFile type "T" (ihtml→html)
    └── <custom_files>       # From SChFile type "c"
```

---

## SChProject Attributes

### Identity & Display

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | *(required)* | Project name. Must match filename without `.ptigprj`. Becomes `PRJ_NAME` in settings. |
| `title` | string | *(required)* | Human-readable title. Becomes `PRJ_TITLE` in settings. |
| `version` | string | `"latest"` | Version string. On import, previous versions are archived with date-stamped version. |
| `icon` | string | `"None"` | Project icon. Formats: `"None"`, `"png://path.png"`, `"fa://icon.png"`, wxPython icon ID, or null for `icon_code` SVG. |
| `icon_size` | string | `"1"` | `"0"`=small, `"1"`=medium, `"2"`=large. |
| `icon_code` | string\|null | null | SVG icon code. If present, `get_icon()` returns `"data:image/svg+xml;utf8," + icon_code`. |

### Application Composition

| Field | Type | Default | Description |
|---|---|---|---|
| `ext_apps` | string\|null | null | External apps to include. Comma, semicolon, or newline separated. Format: `<pack>.<app>`. Entries with `@` prefix go to `APPS_EXT`. Example: `"_schwiki.schwiki\n_schtools.schcommander"`. |
| `plugins` | string\|null | null | Semicolon-separated plugin list. Example: `"standard/keymap;standard/tablefilter"`. |
| `main_view` | bool | true | If true, project appears in the main view selector. On import, new version gets `main_view=True`, old versions archived with `main_view=False`. |
| `main` | bool | false | If true, this is the primary entry project (only one per deployment). |
| `public` | bool | false | If true, project is publicly accessible. Becomes `PUBLIC` in `apps.py`. |
| `login_required` | bool | false | If true, login required. Becomes `SHOW_LOGIN_WIN = True` in settings. |

### GUI Configuration

| Field | Type | Default | Description |
|---|---|---|---|
| `gui_type` | string | `"modern"` | Main GUI type: `"standard"`, `"modern"`, `"tree"`, `"tray"`, `"dialog"`, `"one_form"`. |
| `gui_elements` | string\|null | null | GUI element configuration: `"toolbar(file(open,exit),clipboard)"`, `"toolbar(file(open,save,save_as,exit),clipboard)"`, `"toolbar(browse)"`. |
| `desktop_gui_type` | string | `"auto"` | Desktop GUI: `"auto"`, `"desktop_standard"`, `"desktop_modern"`, `"tablet_standard"`, `"tablet_modern"`, `"smartphone_standard"`, `"smartphone_modern"`. Stored in `THEMES[0]`. |
| `smartphone_gui_type` | string | `"auto"` | Smartphone GUI. Stored in `THEMES[1]`. |
| `tablet_gui_type` | string | `"auto"` | Tablet GUI. Stored in `THEMES[2]`. |
| `start_page` | string\|null | null | Default start page URL. Becomes `START_PAGE` in settings. If null, becomes `"None"`. |
| `components_initial_state` | string\|null | null | JS object literal for component init state. Example: `"username: \"\", theme: \"\""`. |

### Templates (Django/iHTML)

These fields contain iHTML template code compiled to Django templates. Saved to `templates/theme/` and `templates_src/theme/`.

| Field | Type | Description |
|---|---|---|
| `template_desktop` | string\|null | Desktop mode. Extends `theme/desktop_base.html`. |
| `template_smartphone` | string\|null | Smartphone mode. Extends `theme/smartphone_base.html`. |
| `template_tablet` | string\|null | Tablet mode. Extends `theme/tablet_base.html`. |
| `template_schweb` | string\|null | wxPython web client. Extends `theme/schweb_base.html`. Defines `toolbars_start` block. |
| `template_theme` | string\|null | Base theme. Extends `theme_base.html`. Blocks: `ext_css_links`, `botstrap_css` (typo preserved), `ext_js_scripts`, `js_app_init`, `component_init`, `logo`, `login_background`. |

### Code Injection Fields (Embedded Python)

#### `user_app_template` (string|null)

Controls generation of `settings_app.py`. Uses special marker syntax:

- **`###<|init(...)> settings_app.py`** — Specifies the init call. Text after `> settings_app.py` is additional code appended to `settings_app.py`.

  Example from `_schall.ptigprj`:
  ```
  ###<|init(PRJ_NAME, ROOT_PATH, DATA_PATH, PRJ_PATH, STATIC_ROOT, [MEDIA_ROOT, UPLOAD_PATH])> settings_app.py
  from pytigon_lib.schtools.main_paths import get_main_paths
  paths = get_main_paths()
  app_pack_folders = []
  for base_apps_path in (paths['PRJ_PATH'], paths['PRJ_PATH_ALT']):
      ...
  ```

- **`###<|from ... import ...> settings_app.py`** — Alternative init form (imports a function).

  Example from `scheditor.ptigprj`:
  ```
  ###<|from pytigon_lib.schtools.install_init import init> settings_app.py
  # Custom settings code follows...
  ```

- **`###> <filename>`** — Creates a separate file. Content following the marker is written to that file.

  Example from `_schtools.ptigprj`:
  ```
  ###> schsimplescripts/__init__.py
  from django.utils.translation import gettext_lazy as _
  def AdditionalUrls(app_pack, lang):
      from .models import Script
      ret = []
      ...
  ```
  Creates `schsimplescripts/__init__.py` with `AdditionalUrls()` which dynamically generates menu entries from database content.

#### `additional_settings` (string)

Raw Python injected into `settings_app.py`. Has access to:
- `INSTALLED_APPS` (list), `APPS`, `APPS_EXT`
- `platform_name()` — returns `"Android"`, `"Linux"`, etc.
- `ENV("KEY")` — reads environment variable / `.env` flag
- `os`, `sys`, `json`
- `REST_FRAMEWORK` (dict), `GRAPHQL`, `REST`, `ALLAUTH` (feature flags from `.env`)
- `DATABASES`, `TEMPLATES`, `LOCALE_PATHS`, `STATICFILES_DIRS`
- All Django settings variables

Supports `$$$` separator (see above). Without `$$$`, entire value is `first_section` (injected early, before `init()` call).

**Example with `$$$`:**
```python
# first_section: before init() and database config
INSTALLED_APPS.append('explorer')
EXPLORER_CONNECTIONS = { 'Default': 'default' }
$$$
# second_section: after database config, before finish()
PWA_APP_NAME = "SCDevTools"
PWA_APP_DESCRIPTION = "Pytigon developer tools"
```

**Common patterns:**
```python
# Platform-conditional apps
if platform_name()!='Android':
    INSTALLED_APPS.append('easy_thumbnails')
    INSTALLED_APPS.append('filer')
    THUMBNAIL_PROCESSORS = (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
    )

# Bootstrap theme
BOOTSTRAP_TEMPLATE = "bootswatch/materia"

# OAuth2 / REST
if REST:
    REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
        "oauth2_provider.contrib.rest_framework.TokenHasReadWriteScope",
    ]

# Allauth social providers
if ENV("ALLAUTH"):
    INSTALLED_APPS.append('allauth.socialaccount.providers.google')
    INSTALLED_APPS.append('allauth.socialaccount.providers.facebook')

# Remove app in serverless mode
if "_schserverless.schnocompress" in INSTALLED_APPS:
    INSTALLED_APPS.remove("_schserverless.schnocompress")
```

#### `install_file` (string|null)

INI-like format. Each line is `KEY=VALUE`. Written to `install.ini` (with `PRJ_NAME`, `PRJ_TITLE`, `GEN_TIME` prepended).

| Key | Description |
|---|---|
| `PIP` | Space-separated pip packages: `PIP=polars kaleido` |
| `GUI_COMMAND` | GUI command-line flags: `GUI_COMMAND=--embededtaskqueue` |
| `ANDROID_WEB` | `1` to enable Android web mode |
| `ANDROID_WEB_PORT` | Android web server port |
| `ANDROID_WEB_HOST` | Android web server host |
| `ANDROID_WEB_HREF` | Android web access href |
| `ANDROID_KIVY` | `1` to enable Kivy on Android |
| `SHORTCUT_DESKTOP` | `1` to create desktop shortcut |
| `SHORTCUT_MENU` | `1` to create menu shortcut |
| `SHORTCUT_ANDROID` | `1` to create Android shortcut |
| `SHORTCUT_TITLE` | Shortcut title |
| `ICON` | Icon path for shortcuts |

#### `custom_tags` (string)

Newline or semicolon-separated web component JS files. Format: `<pack>/components/<component_name>.js`. Pack names extracted here also contribute to `get_related_projects()` (shared static dirs).

Example:
```
_schcomponents/components/ptig-codeeditor.js
_schcomponents/components/ptig-form.js
_schcomponents/components/ptig-plotly.js
```

#### `encoded_zip` (string|null)

Base64-encoded ZIP. On build, decoded and extracted into the project directory. Used for embedding binary/static resources (templates, interfaces, wasm files).

#### `app_main` (string|null)

Main application entrypoint parameters. Comma-separated values.

#### `doc` (string|null)

Documentation string. Plain text, can contain structured content.

### Author Metadata

| Field | Type | Description |
|---|---|---|
| `git_repository` | string\|null | Git repository URL. Used by `view_importfromgit` to clone/pull. |
| `author_name` | string\|null | Author name |
| `author_email` | string\|null | Author email |
| `author_www` | string\|null | Author website |
| `readme_file` | string\|null | README content (markdown). Written to `README.md`. |
| `license_file` | string\|null | License content (plain text). Written to `LICENSE`. |

---

## Child Models

### SChStatic

Static files, environment config, and web components at the **project level**.

| Field | Type | Description |
|---|---|---|
| `type` | string | File type (see below) |
| `name` | string | File name or path. For `.env`: `"env"` or `".env"`. For components: tag name or path. |
| `content` | string | File content. Format depends on `type`. |
| `doc` | string\|null | Documentation |

**`type` values and build placement:**

| Type | Description | Build placement | Content processing |
|---|---|---|---|
| `"O"` | Other project file | `static/<prj>/` or project root (for `env`/`.env`) | Raw text. `.env` → `KEY=VALUE` lines. `.py` → raw Python. |
| `"R"` | Web component | `static/<prj>/components/<name>.js` | Python → JS via Transcrypt (`py_to_js`) |
| `"C"` | CSS | `static/<prj>/css/<name>.css` | Django template rendered, then raw CSS |
| `"J"` | JavaScript | `static/<prj>/js/<name>.js` | Django template rendered, then raw JS |
| `"P"` | Python to JS | `static/<prj>/js/<name>.js` | Django template rendered, then Python→JS via Transcrypt |
| `"I"` | Sass to CSS | `static/<prj>/css/<name>.css` | SCSS compiled (`sass.compile`), then Django template rendered |
| `"U"` | Custom file | `static/<prj>/<name>` | Extension-based: `.pyj`→`.js` (type P), `.sass`→`.css` (type I), `.webc`→`.js` (type R) |
| `"B"` | Base64-encoded | `static/<prj>/<name>` | Base64-decoded to binary |

**`.env` file example** (type `"O"`, name `env`):
```
GRAPHQL=true
REST=true
ALLAUTH=true
```
Becomes `env` file in project root. Accessed via `ENV("GRAPHQL")`, etc.

**Web component example** (type `"R"`):
```python
TAG = 'ptig-time'
TEMPLATE = """slot"""
with DefineWebComponent(TAG, True) as comp:
    comp.options['template'] = TEMPLATE
    def init(component):
        def _on_time():
            d = Date()
            component.set_state({"time": d.toISOString()[11:19]})
        component.timer = setInterval(_on_time, 250)
    comp.options["init"] = init
```

### SChApp

Defines a Django application. Each `SChApp` generates a `<app_name>/` subdirectory.

| Field | Type | Description |
|---|---|---|
| `name` | string | App name (Django app label). Becomes directory name. |
| `title` | string | Human-readable title. Becomes `Title` in `__init__.py`. |
| `module_name` | string | Module category. Becomes `ModuleName` in `__init__.py`. |
| `module_title` | string | Module title (translated). Becomes `ModuleTitle` in `__init__.py`. |
| `perms` | bool | If true, `Perms = True`. |
| `index` | string\|null | Index URL. `"None"` or null = no index. |
| `icon` | string | App icon path or `"None"`. |
| `icon_size` | string | Icon size. |
| `icon_code` | string\|null | SVG icon code. |
| `user_param` | string | User parameters (newline-separated `key=value`). Becomes `UserParam` dict. |
| `doc` | string\|null | Documentation. |

#### Code Fields (Embedded Python) — all support `$$$`

| Field | Type | File | `first_section` (before generated content) | `second_section` (after generated content) |
|---|---|---|---|---|
| `model_code` | string\|null | `models.py` | After imports, before choices + model classes | After all model classes + `admin_register()` |
| `view_code` | string\|null | `views.py` | After imports, before `PFORM` + forms | After all forms + view functions |
| `urls_code` | string\|null | `urls.py` | After `gen = generic_table_start(...)`, before `gen.standard()` | After all `gen.standard()`/`gen.for_field()` |
| `tasks_code` | string | `tasks.py` | After imports, before task functions | After all task functions |
| `consumer_code` | string | `consumers.py` | After imports, before consumer classes | After all consumer classes |

**`model_code` example** (from `_schbusiness.ptigprj`):
```python
# first_section
import pyarrow
import duckdb
$$$e = schelements.models.Element
e.add_type("I-DEV-C", "Item/Device/Computer", "Computers", "Computer", "schhardware")
```

**`urls_code` example** (from `_schdata.ptigprj`):
```python
# first_section: after gen = generic_table_start(...), before gen.standard calls
gen.for_field('DocType', 'dochead_set', 'Documents', prefix="doc", template_name="schelements/dochead2.html")
```

#### Generated `__init__.py` (from `wzr/app_init.html`)

```python
from django.utils.translation import gettext_lazy as _

ModuleName = "config"
ModuleTitle = _("Config")
Name = "schbrowser"
Title = _("Browser")
Perms = False
Index = ""
Urls = (
    ("table/bookmarks/0/form/tree?view_in=desktop", _("Bookmarks"), None, """client://actions/bookmark-new.png"""),
    ("table/history/-/form/list?view_in=desktop", _("History"), None, """client://emblems/emblem-photos.png"""),
)
UserParam = {}
```

`Urls` tuple generated from `SChAppMenu` children. Each entry: `(url_with_view_in, title, perms, icon)`. `UserParam` parsed from `user_param` string (`key=value` lines → dict).

#### SChApp Children

##### SChChoice / SChChoiceItem

Choices list for model fields. Generated as module-level lists in `models.py`, before model classes.

```json
{
    "model": "SChChoice",
    "attributes": { "name": "device_type_choices", "verbose_name": "Device type" },
    "children": [
        { "model": "SChChoiceItem", "attributes": { "name": "C", "value": "Computer" } },
        { "model": "SChChoiceItem", "attributes": { "name": "M", "value": "Monitor" } }
    ]
}
```

Generates:
```python
device_type_choices = [
    ("C", "Computer"),
    ("M", "Monitor"),
    ]
```

Referenced by `SChField` via `choices` attribute (set to choice name).

##### SChTable / SChField

Defines a Django model. Generated from `wzr/models.html` template.

**SChTable attributes:**

| Field | Type | Description |
|---|---|---|
| `base_table` | string\|null | Base class. `null`→`models.Model`. `"JSONModel"`→JSON-backed. `"schelements.Element"`→extends Element. `"Device"`→multi-table inheritance from same-app table. `"pack.app.Model"`→cross-app. |
| `name` | string | Model class name. |
| `verbose_name` | string | Singular verbose name (translated). |
| `verbose_name_plural` | string | Plural verbose name (translated). |
| `metaclass_code` | string\|null | Meta class body. Examples: `"abstract=True"`, `"permissions = [(\"admin_xxx\", \"Can administer xxx\"),]"`. |
| `table_code` | string\|null | Model methods. Wrapped in `#[[START]]`/`#[[END]]` markers. |
| `ordering` | string | Default ordering: `"['id']"`, `"['-date']"`, or `"-"` for none. |
| `generic` | bool | If true, auto-generates CRUD URLs via `gen.standard()`. |
| `url_params` | string\|null | Extra URL parameters. |
| `proxy_model` | string\|null | Proxy model base. Generates `proxy=True` in Meta. |
| `doc` | string\|null | Documentation (becomes docstring). |

**Model inheritance patterns:**

| `base_table` | `metaclass_code` | Generated class | Description |
|---|---|---|---|
| `null` | `null` | `class MyModel(models.Model)` | Standard model |
| `null` | `null` + `proxy_model="Base"` | `class MyModel(Base)` + `proxy=True` | Proxy model |
| `"JSONModel"` | `null` | `class MyModel(JSONModel)` | JSON-backed model |
| `"schelements.Element"` | `null` | `class MyModel(schelements.models.Element)` | Multi-table inheritance |
| `"Device"` | `"abstract=True"` | `class Sub(Device)` + `abstract=True` | Abstract base |
| `"StandardComputer"` | `null` + `generic=true` | `class Computer(StandardComputer)` | Concrete subclass |
| `null` + `PtigTreeForeignKey` field | `null` | `class MyModel(TreeModel)` | Auto-promoted to TreeModel if tree FK present and no base_table |

**`table_code` common methods:**

```python
# Called on new row creation - returns default field values
def init_new(self, request, view, param=None):
    return { 'type': 'I-DEV-C', 'device_type': 'C' }

# Override save to set computed fields
def save(self, force_insert=False, force_update=False):
    self.device_type = 'C'
    super().save(force_insert, force_update)

# Provide default form/view/template from DB-stored code
def get_form_if_empty(self, request, template_name, ext, extra_context, target):
    return PRJ_FORM
def get_view_if_empty(self, request, template_name, ext, extra_context, target):
    return PRJ_VIEW
def get_template_if_empty(self, request, template_name, ext, extra_context, target):
    return PRJ_TEMPLATE

# Custom form class
def get_form_class(self, view, request, create):
    base_form = view.get_form_class()
    class form_class(base_form):
        class Meta(base_form.Meta):
            labels = { 'code': _('Identification number'), }
    return form_class

# Transform form before rendering
def transform_form(self, form, new):
    form.fields['type'].widget = form.fields['type'].hidden_widget()

# Load data (BI models)
def load_data(self):
    data_path = os_path.join(settings.DATA_PATH, settings.PRJ_NAME)
    ...
```

**SChField attributes:**

| Field | Type | Description |
|---|---|---|
| `name` | string | Field name (Python attribute). |
| `description` | string | Verbose name. |
| `type` | string | Django field type (see below). |
| `null` | bool | `null=True` for DB NULL. |
| `blank` | bool | `blank=True` for form validation. |
| `editable` | bool | `editable=False` hides from forms. |
| `unique` | bool | Unique constraint. |
| `db_index` | bool | Database index. |
| `default` | string\|null | Default as Python expression: `null`, `"''"`, `"'S'"`, `"False"`, `"True"`, `"0"`. |
| `help_text` | string\|null | Help text. |
| `choices` | string\|null | `SChChoice` name reference. |
| `rel_to` | string\|null | Relation target: `"Project"`, `"Page"`, `"'self'"`, `"pack.app.Model"`. |
| `param` | string\|null | Extra kwargs: `"max_length=64"`, `"auto_now=True"`, `"upload_to='upload/'"`, `"related_name='children'"`. |
| `url_params` | string\|null | URL parameters. |

**Field types:**

| Type | Generated as | Notes |
|---|---|---|
| `CharField` | `models.CharField` | Requires `param: "max_length=N"` |
| `TextField` | `models.TextField` | Usually `editable: false` |
| `IntegerField` | `models.IntegerField` | |
| `PositiveIntegerField` | `models.PositiveIntegerField` | |
| `SmallIntegerField` | `models.SmallIntegerField` | |
| `BigIntegerField` | `models.BigIntegerField` | |
| `FloatField` | `models.FloatField` | |
| `DecimalField` | `models.DecimalField` | |
| `BooleanField` | `models.BooleanField` | |
| `NullBooleanField` | `models.BooleanField` + `null=True` | Auto-converted |
| `DateField` | `models.DateField` | `param: "auto_now=True"` or `"auto_now_add=True"` |
| `DateTimeField` | `models.DateTimeField` | |
| `TimeField` | `models.TimeField` | |
| `EmailField` | `models.EmailField` | |
| `URLField` | `models.URLField` | |
| `SlugField` | `models.SlugField` | |
| `GenericIPAddressField` | `models.GenericIPAddressField` | |
| `FileField` | `models.FileField` | `param: "upload_to='upload/'"` |
| `ImageField` | `models.ImageField` | |
| `FilePathField` | `models.FilePathField` | |
| `PtigForeignKey` | `ext_models.PtigForeignKey` | Requires `rel_to`. Auto-adds `on_delete=models.CASCADE`. Renders as dropdown with lookup. |
| `PtigHiddenForeignKey` | `ext_models.PtigHiddenForeignKey` | Hidden FK (auto-set, not in form) |
| `PtigForeignKeyWithIcon` | `ext_models.PtigForeignKeyWithIcon` | FK with icon |
| `PtigManyToManyField` | `ext_models.PtigManyToManyField` | M2M with Pytigon UI |
| `PtigManyToManyFieldWithIcon` | | M2M with icons |
| `PtigTreeForeignKey` | `ext_models.PtigTreeForeignKey` | Tree FK (auto-promotes table to `TreeModel`) |
| `PtigHiddenTreeForeignKey` | | Hidden tree FK |
| `UserField` | Custom (from `param`) | References User model. `param` defines the actual field, e.g. `"user_field=forms.CharField(max_length=100)"`. |

**Field declaration generation** (`SChField.as_declaration()`):

```python
# CharField: name="serial_number", description="Serial number", param="max_length=64"
serial_number = models.CharField('Serial number', null=False, blank=False, editable=True, max_length=64)

# PtigHiddenForeignKey: name="parent", rel_to="'self'", null=true, blank=true
parent = ext_models.PtigHiddenForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, editable=True, verbose_name='Parent')

# CharField with choices: name="status", choices="status_choice", param="max_length=1"
status = models.CharField('Status', null=False, blank=False, editable=True, max_length=1, choices=status_choice)

# PtigForeignKey: name="parent", rel_to="Project"
parent = ext_models.PtigForeignKey(Project, on_delete=models.CASCADE, null=False, blank=False, editable=True, verbose_name='Parent')

# ManyToManyField: name="tags", rel_to="Tag"
tags = ext_models.PtigManyToManyField(Tag, editable=True, verbose_name='Tags')
```

Relation field types ending with `!` in `Field_CHOICES` (e.g. `"PtigForeignKey!"`) use `ext_models.` prefix; others use `models.` prefix.

Each non-abstract model is registered: `admin_register(ModelName)`.

##### SChView

Defines a URL view. Generated from `wzr/views.html` + `wzr/urls.html`.

| Field | Type | Description |
|---|---|---|
| `name` | string | View function name. If contains `/` or `#`, the name is split for action views. |
| `view_type` | string | `"u"`=user view (standalone URL), `"t"`=table action (`gen_tab_action`), `"r"`=row action (`gen_row_action`). |
| `param` | string | URL parameter names: `"prj_name"`, `"pk"`, `"**argv"`, `"page_id, line_number"`. For `"u"` type defaults to `"**argv"`. |
| `url` | string | URL pattern. Can be Django path (`"search/"`) or regex (`"^(?P<name>\\w+)/$"`). Regex detected by `(?P` presence. |
| `view_code` | string | Python view body. NOT split by `$$$` — goes directly into function body. |
| `url_params` | string | JSON kwargs: `"{}"`. |
| `ret_type` | string | Return type (see below). Determines decorator applied. |
| `asynchronous` | bool | If true, `async def`. |
| `extra_code` | string\|null | Supports `$$$`: `first_section` goes before function (decorators), `second_section` after function body. |
| `doc` | string\|null | Documentation (becomes docstring). |

**`ret_type` values and decorators:**

| Code | Decorator | Template | View should return |
|---|---|---|---|
| `"U"` | *(none)* | — | `HttpResponse`, `JsonResponse`, `HttpResponseRedirect`, or dict |
| `"T"` | `@dict_to_template('<app>/v_<name>.html')` | `<app>/v_<name>.html` | Dict of context variables |
| `"J"` | `@dict_to_json` | — | Dict or JSON-serializable object |
| `"P"` | `@dict_to_pdf('<app>/v_<name>_pdf.html')` | `<app>/v_<name>_pdf.html` | Dict |
| `"O"` | `@dict_to_odf('<app>/v_<name>.ods')` | `<app>/v_<name>.ods` | Dict |
| `"S"` | `@dict_to_ooxml('<app>/v_<name>.xlsx')` | `<app>/v_<name>.xlsx` | Dict |
| `"X"` | `@dict_to_xml` | — | Dict |
| `"t"` | `@dict_to_txt('<app>/v_<name>_txt.html')` | `<app>/v_<name>_txt.html` | Dict |
| `"H"` | `@dict_to_hdoc('<app>/v_<name>_hdoc.html')` | `<app>/v_<name>_hdoc.html` | Dict |

**Generated view function:**
```python
# SChView: name="search", view_type="u", url="search/", ret_type="U"
def search(request):
    q = request.GET.get('term', request.POST.get('term', None))
    ...
    return HttpResponse(json_data, content_type="application/x-javascript")
```

```python
# SChView: name="task_stats", view_type="u", url="task_stats/", ret_type="J"
@dict_to_json
def task_stats(request, **argv):
    counts = {}
    for p in ('L','M','H'):
        counts[p] = models.Task.objects.filter(priority=p).count()
    return counts
```

**Generated URL pattern** (`SChView.get_url()`):

For `view_type="u"`:
```python
# Simple path (no ?P in url):
path('search/', views.search, name='schbrowser_search')
# With extra params:
path('search/', views.search, {}, name='schbrowser_search')
# Regex (has ?P in url):
re_path(r'^(?P<name>\w+)/$', views.search, name='schbrowser_search')
```

For `view_type="t"` (table action):
```python
gen_tab_action('TableName', 'action_name', views.action_name)
```

For `view_type="r"` (row action):
```python
gen_row_action('TableName', 'action_name', views.action_name)
```

##### SChTemplate

Defines a Django/iHTML template. Generated from `wzr/` templates.

| Field | Type | Description |
|---|---|---|
| `name` | string | Template name. If contains `.` and not `.ihtml`, saved as-is to `templates/<app>/<name>`. Otherwise saved as `templates/<app>/<name>.html` (compiled) and `templates_src/<app>/<name>.ihtml` (source). |
| `direct_to_template` | bool\|null | If true, creates standalone URL via `TemplateView.as_view()`. |
| `url` | string\|null | URL pattern (when `direct_to_template`). |
| `url_parm` | string\|null | Extra params as JSON string. |
| `template_code` | string | iHTML source code. |
| `tags_mount` | string\|null | Custom template tag mount point. |
| `asynchronous` | bool | If true, async template. |

**`direct_to_template` URL generation:**
```python
# Simple path:
path('terminal/', TemplateView.as_view(template_name='schadmin/terminal.html'), {})
# Regex:
re_path(r'^terminal', TemplateView.as_view(template_name='schadmin/terminal.html'), {})
```

**iHTML format syntax:**

| Syntax | Meaning |
|---|---|
| `% extends "base.html"` | `{% extends "base.html" %}` |
| `% load exfiltry` | `{% load exfiltry %}` |
| `%% block_name` | `{% block block_name %}` (indentation = block content) |
| `div class=container` | `<div class="container">` (indentation = children) |
| `,,,` | Attribute separator |
| `...` | Text content: `h1...Title` = `<h1>Title</h1>` |
| `.` | Alt text prefix: `.Hello` = text node |
| `% if condition:` | `{% if condition %}` |
| `% for item in list:` | `{% for item in list %}` |
| `{{ variable }}` | Django variable |
| `===>` | Raw HTML passthrough |
| `#` | Comment line |
| `script language=python` | Embedded Python in template |

**Common template blocks:**

| Block | Purpose |
|---|---|
| `all` | Main content wrapper (often wraps with `table_type`, `form_width`, etc.) |
| `scroll` | Scrollable area |
| `content` | Main content area |
| `list_page` | List page content |
| `list_content_actions` | Actions above list (new row buttons) |
| `list_row_header` | Table header row |
| `list_row` | Table data row |
| `list_row_actions` | Per-row action buttons |
| `row_edit` | Edit form layout |
| `form_header` | Form header |
| `pythoncode` | Embedded Python code block |
| `extrahead` | Extra head content |
| `ext_css_links` | CSS links |
| `ext_js_scripts` | JS scripts |

**Template example (iHTML):**
```
% extends "forms/form.html"

% load exfiltry
% load exsyntax

%% all
    % with table_type='datatable':
        {{ block.super }}

%% list_content_actions
    % new_row "New project"

%% list_row_header
    th..._(Name)
    th..._(Description)

%% list_row
    td...{{ object.name }}
    td...{{ object.description }}

%% list_row_actions
    % row_actions:
        .edit
        .delete

%% row_edit
    % form:
        .name, description
```

**Row actions syntax:**
```
% row_actions:
    .edit                              # Standard edit
    .delete                            # Standard delete
    .show_prj,Show prj,url={{base_path}}schbi/project_view/{{object.name}}/,target=_parent
    .field_edit/refresh_data,refresh data   # Edit specific field
```

**Form layout syntax:**
```
% form:
    .field1, field2, field3            # Fields on same row
    .parent:!, type:!, device_type:!   # Hidden fields (:! suffix)
```

##### SChAppMenu

Menu entry in navigation.

| Field | Type | Description |
|---|---|---|
| `name` | string | Menu item display name. |
| `url` | string | URL pattern. Added to `Urls` in `__init__.py`. |
| `url_type` | string | Controls `?view_in=` param and placement. |
| `perms` | string\|null | Permission: `"-"`=none, null=inherit, or `"app.perm_name"`. |
| `icon` | string | Icon: `"fa://icon.png"`, `"png://path.png"`, `"client://path.png"`, `"wx.ART_REDO"`. |
| `icon_size` | string | Icon size. |
| `icon_code` | string\|null | SVG icon. |

**`url_type` → `view_in` mapping:**

| Value | `view_in` param | Description |
|---|---|---|
| `"-"` | *(none)* | Default — all views |
| `"desktop"` | `desktop` | Desktop only |
| `"panel"` | `panel` | Desktop panel |
| `"header"` | `header` | Desktop header |
| `"footer"` | `footer` | Desktop footer |
| `"script"` | *(none)* | JavaScript action |
| `"pscript"` | *(none)* | Python script action |
| `"browser"` | `browser` | Browser only |
| `"browser_panel"` | `browser_panel` | Browser panel |
| `"browser_header"` | `browser_header` | Browser header |
| `"browser_footer"` | `browser_footer` | Browser footer |

**Generated `Urls` entry:**
```python
# SChAppMenu: name="Bookmarks", url="table/bookmarks/0/form/tree", url_type="desktop"
("table/bookmarks/0/form/tree?view_in=desktop", _("Bookmarks"), None, """client://actions/bookmark-new.png"""),
```

##### SChForm / SChFormField

Django Form class. Generated in `views.py`.

**SChForm attributes:**

| Field | Type | Description |
|---|---|---|
| `name` | string | Form class name. Also generates `view_<name>` function and URL `form/<name>/`. If starts with `_`, URL is private (not generated). |
| `module` | string\|null | Module reference. |
| `process_code` | string | Code for `process()` method body. Receives `request`, `queryset`. Returns dict. |
| `end_class_code` | string | Code appended to form class body (e.g. `clean()`, `render_to_response()`). |
| `end_code` | string | Code appended after class definition. |
| `asynchronous` | bool | If true, `async def process(...)`. |
| `doc` | string | Documentation. |

**SChFormField attributes:**

| Field | Type | Description |
|---|---|---|
| `name` | string | Field name. |
| `type` | string | Form field type: `CharField`, `ChoiceField`, `IntegerField`, `FloatField`, `BooleanField`, `DateField`, `DateTimeField`, `EmailField`, `FileField`, `NullBooleanField`, `UserField`, etc. |
| `required` | bool | Required field. Default: true. |
| `label` | string | Field label (translated). |
| `initial` | string\|null | Initial value as Python expression. |
| `widget` | string\|null | Widget specification. |
| `help_text` | string\|null | Help text. |
| `error_messages` | string\|null | Error messages. |
| `param` | string\|null | Extra kwargs: `"max_length=None, min_length=None"`, `"choices=models.choice_name"`, `"widget=forms.ClearableFileInput(attrs={'accept': '.ptig'})"`. |

**Generated form example:**
```python
PFORM = form_with_perms("schbrowser")

class MultiDownload(forms.Form):
    base_address = forms.CharField(
        label=_("Base address"), required=True,
        initial="http://learningenglish.voanews.com",
        max_length=None, min_length=None,
    )
    source_page = forms.CharField(
        label=_("Source page"), required=False,
        initial="/archive/...", max_length=None, min_length=None,
    )
    levels = forms.IntegerField(
        label=_("Levels"), required=True,
        initial="10", max_value=None, min_value=None,
    )
    test_only = forms.BooleanField(label=_("Test only"), required=False, initial=True)

    def process(self, request, queryset=None):
        parm = {}
        parm["base_address"] = self.cleaned_data["base_address"]
        ...
        return {"ret": task_id}

def view_multidownload(request, *argi, **argv):
    return PFORM(request, MultiDownload, "schbrowser/formmultidownload.html", {})
```

Form template name: `Form<form_name>` (lowercased in URL: `form/<form_name>/`).

##### SChTask

Async task via django-q. Generated from `wzr/tasks.html`.

| Field | Type | Description |
|---|---|---|
| `name` | string | Task function name. |
| `code` | string | Function body. Signature: `def <name>(cproxy=None, **kwargs):`. |
| `doc` | string\|null | Documentation (docstring). |
| `perms` | string\|null | Required permissions. |
| `publish` | bool\|null | If true, wraps with `@publish("group")` decorator. |
| `publish_group` | string\|null | Publish group name. |

**Generated task:**
```python
@publish("cleanup")
def cleanup_old_tasks(cproxy=None, **kwargs):
    """Cleanup old tasks"""
    import datetime
    old = datetime.datetime.now() - datetime.timedelta(days=30)
    count, _ = models.Task.objects.filter(created__lt=old).delete()
    if cproxy:
        cproxy.log(f"Deleted {count} old tasks")
```

Invoked via `async_task("app.tasks.task_name", user_parm=...)` or `cproxy.add_task('system', 'Title', "@app:task_name", user_parm=...)`.

##### SChChannelConsumer

Django Channels websocket consumer. Generated from `wzr/consumers.html`.

| Field | Type | Description |
|---|---|---|
| `name` | string | Consumer class name. |
| `consumer_type` | string | Base class (see below). |
| `url` | string | URL path for websocket route. Added to `CHANNELS_URL_TAB` in settings. |
| `consumer_code` | string | Consumer class body. |
| `doc` | string\|null | Documentation. |

**`consumer_type` values:**

| Value | Base class |
|---|---|
| `"WebsocketConsumer"` | `WebsocketConsumer` |
| `"AsyncWebsocketConsumer"` | `AsyncWebsocketConsumer` |
| `"JsonWebsocketConsumer"` | `JsonWebsocketConsumer` |
| `"AsyncJsonWebsocketConsumer"` | `AsyncJsonWebsocketConsumer` |
| `"AsyncHttpConsumer"` | `AsyncHttpConsumer` |
| `"AsyncConsumer"` | `AsyncConsumer` |
| `"SyncConsumer"` | `SyncConsumer` |

**Generated consumer:**
```python
class ShellConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        ...
    def receive(self, text_data=None, bytes_data=None):
        ...
    def disconnect(self, close_code):
        ...
```

For async types, methods use `async def` / `await`.

The `url` is registered in `settings_app.py` via `CHANNELS_URL_TAB`:
```python
CHANNELS_URL_TAB += [
    (URL_ROOT_PREFIX+"shell", 'schcommander.ShellConsumer'),
]
```

##### SChFile

File within an app. Placement depends on `type`.

| Field | Type | Description |
|---|---|---|
| `type` | string | File type (see below). |
| `name` | string | File name or path. Can include relative paths (`"../sched.py"`, `"editor_proxy/test_template"`). |
| `content` | string | File content (raw Python, JS, HTML, etc.). |
| `doc` | string\|null | Documentation. |

**`type` values and build placement:**

| Type | Description | Build placement | Content processing |
|---|---|---|---|
| `"f"` | Template filters | `templatetags/<name>.py` | Raw Python |
| `"t"` | Template tags | `templatetags/<name>.py` | Raw Python |
| `"c"` | Custom file | `<app>/<name>` (relative to app dir) | Raw text. `applib/__init__.py` auto-created. |
| `"m"` | Management command | `management/commands/<name>` (name includes `.py`) | Raw Python (Django Command class) |
| `"p"` | Plugin code | `plugins/<app>/<plugin_name>/<file_name>.py` | Raw Python (wxPython plugin) |
| `"i"` | Plugin template | `plugins/<app>/<plugin_name>/<file_name>.html` | iHTML → HTML compiled |
| `"l"` | Library code | `applib/<name>.py` | Raw Python. `applib/__init__.py` auto-created. |
| `"s"` | GraphQL schema | GraphQL schema file | Auto-generated from template if empty |
| `"r"` | REST API | REST API definition | Auto-generated from template if empty |
| `"j"` | Frontend view | `static/<app>/views/<name>.js` | Python → JS via Transcrypt |
| `"T"` | Frontend template | `static/<app>/views/<name>.html` | iHTML → HTML compiled |
| `"n"` | Nim extension | Nim source file | Raw Nim |
| `"N"` | Nim executable | Nim source file | Raw Nim |
| `"E"` | Nimpy extension | Nim Python extension | Raw Nim |
| `"U"` | Custom (translated) | `static/<app>/<name>` (extension-based processing) | `.pyj`→JS, `.sass`→CSS, `.webc`→component JS |
| `"C"` | CSS | `static/<app>/css/<name>.css` | Django template rendered |
| `"J"` | JavaScript | `static/<app>/js/<name>.js` | Django template rendered |
| `"P"` | Python to JS | `static/<app>/js/<name>.js` | Python → JS via Transcrypt |
| `"R"` | Web component | `static/<app>/components/<name>.js` | Python → JS via Transcrypt |
| `"I"` | Sass to CSS | `static/<app>/css/<name>.css` | SCSS compiled |
| `"O"` | Other app file | `<app>/<name>` | Raw text |
| `"B"` | Base64-encoded | `<app>/<name>` | Base64-decoded |

**Management command example** (type `"m"`, name `"smtpd.py"`):
```python
from django.core.management.base import BaseCommand
class Command(BaseCommand):
    help = 'run smtpd server'
    def add_arguments(self, parser):
        parser.add_argument('port', nargs='+', type=int)
    def handle(self, *args, **options):
        ...
```

**Frontend view example** (type `"j"`):
```python
def request(param, complete):
    context = { 'template': ".", }
    complete(context)
```
Runs in browser via Pyodide/Transcrypt.

**Frontend template example** (type `"T"`):
```
div class=ajax-region
    nav class=navbar bg-light
        h2...To Do list
        input type=text,,,name=task,,,placeholder=task...
```

**Library code example** (type `"l"`, name `"perms"`):
```python
from django.conf import settings
def if_rest(user, perm):
    return user.has_perm(perm) and hasattr(settings, "REST") and settings.REST
def if_graphql(user, perm):
    return user.has_perm(perm) and hasattr(settings, "GRAPHQL") and settings.GRAPHQL
```
Saved as `applib/perms.py`, importable as `from .applib.perms import if_rest`.

### SChLocale / SChTranslate

Locale/translation management for i18n.

**SChLocale** (child of `SChProject`):

| Field | Type | Description |
|---|---|---|
| `name` | string | Locale code: `"pl"`, `"en"`, `"de"`. Max 16 chars. |

**SChTranslate** (child of `SChLocale`):

| Field | Type | Description |
|---|---|---|
| `description` | string | Source string (msgid). Max 1024 chars. |
| `translation` | string\|null | Translated string (msgstr). Max 1024 chars. |
| `status` | string\|null | `"OK"`=translated, `"#"`=pending, `""`=new. Not editable. |

The `schdevtools` IDE `translate_sync` view:
1. Runs `compiletemplates` to extract strings from iHTML templates
2. Reads/writes `<project>/locale/<lang>/LC_MESSAGES/django.po`
3. Updates `SChTranslate` records from `.po` file
4. Writes translations back to `.po`
5. Compiles to `.mo` via `locale_gen_internal()`

**Example:**
```json
{
    "model": "SChLocale",
    "attributes": { "name": "pl" },
    "children": [
        {
            "model": "SChTranslate",
            "attributes": {
                "description": "Hello world",
                "translation": "Witaj świecie",
                "status": "OK"
            }
        }
    ]
}
```

---

## Naming Conventions & Patterns

### Project naming
- `_` prefix (e.g. `_schtools`, `_schdata`, `_schcomponents`) → **library projects** providing reusable apps.
- No `_` prefix (e.g. `schportal`, `scheditor`, `schdevtools`) → **standalone applications**.
- Only one project per deployment should have `main: true`.

### App composition
- `ext_apps` references apps from other projects: `<pack>.<app>`.
  - `_schwiki.schwiki` = app `schwiki` from project `_schwiki`.
- Local apps (from `SChApp` children) have no pack prefix.
- Combined in `apps.py`:
  ```python
  APPS = ['schbrowser', '_schwiki.schwiki', '_schtools.schtasks']  # local + ext (no @)
  APPS_EXT = []  # ext apps with @ prefix
  PUBLIC = False
  ```

### Icon path formats
| Format | Example | Description |
|---|---|---|
| `fa://` | `fa://pencil-square.png` | Font Awesome |
| `png://` | `png://apps/utilities-terminal.png` | PNG from static |
| `client://` | `client://devices/computer.png` | Client-side resource |
| `wx.ART_*` | `wx.ART_REDO` | wxPython built-in |
| `"None"` | | No icon |
| `icon_code` (SVG) | | `data:image/svg+xml;utf8,...` |

### `.env` environment flags
Set via `SChStatic` (type `"O"`, name `"env"` or `".env"`):
- `GRAPHQL=true/false` — Enable GraphQL API
- `REST=true/false` — Enable REST API
- `ALLAUTH=true/false` — Enable allauth social login
- `MCP_SERVER=true/false` — Enable MCP server

Accessed via `ENV("GRAPHQL")`, `ENV("ALLAUTH")`, etc. in `additional_settings`.

### `gen` helper functions (in `urls.py`)

The `generic_table_start` creates a `gen` object with:

```python
gen = generic_table_start(urlpatterns, 'app_name', views)

# Auto-generates CRUD URLs for a model (table/list/edit/delete)
gen.standard('ModelName', _('Singular'), _('Plural'))

# Auto-generates URLs for a reverse relation field
gen.for_field('RelatedModel', 'related_set_name', _('Title'), _('Plural'),
               prefix="doc", template_name="app/template.html")
```

---

## Complete Project Example

```json
{
    "model": "SChProject",
    "attributes": {
        "name": "myproject",
        "title": "My Project",
        "version": "latest",
        "main_view": true,
        "ext_apps": "_schtools.schcommander\n_schtools.schtools",
        "plugins": null,
        "gui_type": "modern",
        "gui_elements": "toolbar(file(open,exit),clipboard)",
        "login_required": true,
        "public": true,
        "main": false,
        "start_page": null,
        "user_app_template": null,
        "app_main": null,
        "doc": null,
        "desktop_gui_type": "tablet_modern",
        "smartphone_gui_type": "auto",
        "tablet_gui_type": "tablet_modern",
        "additional_settings": "INSTALLED_APPS.append('explorer')\nEXPLORER_CONNECTIONS = { 'Default': 'default' }\nEXPLORER_DEFAULT_CONNECTION = 'default'",
        "custom_tags": "_schcomponents/components/ptig-codeeditor.js",
        "readme_file": null,
        "license_file": null,
        "install_file": "PIP=requests httpx",
        "encoded_zip": null,
        "icon": "None",
        "icon_size": "1",
        "icon_code": null,
        "git_repository": null,
        "author_name": null,
        "author_email": null,
        "author_www": null,
        "components_initial_state": null,
        "template_desktop": null,
        "template_smartphone": null,
        "template_tablet": null,
        "template_schweb": null,
        "template_theme": null
    },
    "children": [
        {
            "model": "SChStatic",
            "attributes": {
                "type": "O",
                "name": "env",
                "content": "REST=true\n",
                "doc": null
            }
        },
        {
            "model": "SChApp",
            "attributes": {
                "name": "myapp",
                "title": "My App",
                "module_name": "Config",
                "module_title": "Config",
                "perms": true,
                "index": null,
                "model_code": "from pytigon_lib.schdjangoext.import_from_db import run_code_from_db_field, ModuleStruct",
                "view_code": "from django.http import JsonResponse\nfrom pytigon_lib.schdjangoext.fastform import form_from_str",
                "urls_code": null,
                "tasks_code": "",
                "consumer_code": "",
                "doc": null,
                "user_param": "",
                "icon": "fa://th-large.png",
                "icon_size": "1",
                "icon_code": null
            },
            "children": [
                {
                    "model": "SChChoice",
                    "attributes": { "name": "priority_choices", "verbose_name": "Priority" },
                    "children": [
                        { "model": "SChChoiceItem", "attributes": { "name": "L", "value": "Low" } },
                        { "model": "SChChoiceItem", "attributes": { "name": "M", "value": "Medium" } },
                        { "model": "SChChoiceItem", "attributes": { "name": "H", "value": "High" } }
                    ]
                },
                {
                    "model": "SChTable",
                    "attributes": {
                        "base_table": null,
                        "name": "Task",
                        "verbose_name": "Task",
                        "verbose_name_plural": "Tasks",
                        "metaclass_code": "permissions = [(\"admin_task\", \"Can administer tasks\"),]",
                        "table_code": "def init_new(self, request, view, param=None):\n    return { 'priority': 'M' }",
                        "ordering": "['id']",
                        "doc": null,
                        "generic": true,
                        "url_params": null,
                        "proxy_model": null
                    },
                    "children": [
                        {
                            "model": "SChField",
                            "attributes": {
                                "name": "title", "description": "Title",
                                "type": "CharField", "null": false, "blank": false,
                                "editable": true, "unique": false, "db_index": false,
                                "default": null, "help_text": null, "choices": null,
                                "rel_to": null, "param": "max_length=128", "url_params": null
                            }
                        },
                        {
                            "model": "SChField",
                            "attributes": {
                                "name": "description", "description": "Description",
                                "type": "TextField", "null": true, "blank": true,
                                "editable": true, "unique": false, "db_index": false,
                                "default": null, "help_text": null, "choices": null,
                                "rel_to": null, "param": null, "url_params": null
                            }
                        },
                        {
                            "model": "SChField",
                            "attributes": {
                                "name": "priority", "description": "Priority",
                                "type": "CharField", "null": false, "blank": false,
                                "editable": true, "unique": false, "db_index": false,
                                "default": "'M'", "help_text": null, "choices": "priority_choices",
                                "rel_to": null, "param": "max_length=1", "url_params": null
                            }
                        },
                        {
                            "model": "SChField",
                            "attributes": {
                                "name": "parent", "description": "Parent",
                                "type": "PtigForeignKey", "null": true, "blank": true,
                                "editable": true, "unique": false, "db_index": false,
                                "default": null, "help_text": null, "choices": null,
                                "rel_to": "'self'", "param": null, "url_params": null
                            }
                        },
                        {
                            "model": "SChField",
                            "attributes": {
                                "name": "created", "description": "Created",
                                "type": "DateTimeField", "null": false, "blank": false,
                                "editable": false, "unique": false, "db_index": false,
                                "default": null, "help_text": null, "choices": null,
                                "rel_to": null, "param": "auto_now_add=True", "url_params": null
                            }
                        }
                    ]
                },
                {
                    "model": "SChView",
                    "attributes": {
                        "name": "task_stats",
                        "view_type": "u",
                        "param": "**argv",
                        "url": "task_stats/",
                        "view_code": "counts = {}\nfor p in ('L','M','H'):\n    counts[p] = models.Task.objects.filter(priority=p).count()\nreturn counts",
                        "url_params": "{}",
                        "ret_type": "J",
                        "asynchronous": false,
                        "extra_code": null,
                        "doc": null
                    }
                },
                {
                    "model": "SChTemplate",
                    "attributes": {
                        "name": "Task",
                        "direct_to_template": null,
                        "url": null,
                        "url_parm": null,
                        "template_code": "% extends \"forms/form.html\"\n\n% load exfiltry\n% load exsyntax\n\n%% all\n    % with table_type='datatable':\n        {{ block.super }}\n\n%% list_content_actions\n    % new_row \"New task\"\n\n%% list_row_header\n    th...Title\n    th...Priority\n\n%% list_row\n    td...{{object.title}}\n    td...{{object.priority}}\n\n%% list_row_actions\n    % row_actions:\n        .edit\n        .delete\n\n%% row_edit\n    % form:\n        .title, priority\n        .description",
                        "tags_mount": null,
                        "asynchronous": false
                    }
                },
                {
                    "model": "SChAppMenu",
                    "attributes": {
                        "name": "Tasks",
                        "url": "table/Task/-/form/list/",
                        "url_type": "desktop",
                        "perms": null,
                        "icon": "fa://th-large.png",
                        "icon_size": "1",
                        "icon_code": null
                    }
                },
                {
                    "model": "SChForm",
                    "attributes": {
                        "name": "QuickAdd",
                        "module": "myapp",
                        "process_code": "title = self.cleaned_data['title']\nif title:\n    t = models.Task(title=title, priority='M')\n    t.save()\nreturn {'object': t}",
                        "end_class_code": "",
                        "end_code": "",
                        "asynchronous": false,
                        "doc": ""
                    },
                    "children": [
                        {
                            "model": "SChFormField",
                            "attributes": {
                                "name": "title", "type": "CharField",
                                "required": true, "label": "Title",
                                "initial": "", "widget": "", "help_text": "",
                                "error_messages": "", "param": ""
                            }
                        }
                    ]
                },
                {
                    "model": "SChTask",
                    "attributes": {
                        "name": "cleanup_old_tasks",
                        "code": "import datetime\nold = datetime.datetime.now() - datetime.timedelta(days=30)\ncount, _ = models.Task.objects.filter(created__lt=old).delete()\nif cproxy:\n    cproxy.log(f\"Deleted {count} old tasks\")",
                        "doc": null,
                        "perms": null,
                        "publish": true,
                        "publish_group": "cleanup"
                    }
                },
                {
                    "model": "SChFile",
                    "attributes": {
                        "type": "l",
                        "name": "helpers",
                        "content": "def get_priority_label(priority):\n    return {'L': 'Low', 'M': 'Medium', 'H': 'High'}.get(priority, 'Unknown')",
                        "doc": null
                    }
                },
                {
                    "model": "SChChannelConsumer",
                    "attributes": {
                        "name": "TaskUpdates",
                        "consumer_type": "AsyncJsonWebsocketConsumer",
                        "url": "task_updates",
                        "consumer_code": "async def connect(self):\n    await self.accept()\n    await self.channel_layer.group_add('task_updates', self.channel_name)\n\nasync def disconnect(self, close_code):\n    await self.channel_layer.group_discard('task_updates', self.channel_name)\n\nasync def receive_json(self, content):\n    await self.channel_layer.group_send('task_updates', {'type': 'chat_message', 'message': content})\n\nasync def chat_message(self, event):\n    await self.send_json(event['message'])",
                        "doc": null
                    }
                }
            ]
        },
        {
            "model": "SChLocale",
            "attributes": { "name": "pl" },
            "children": [
                {
                    "model": "SChTranslate",
                    "attributes": {
                        "description": "New task",
                        "translation": "Nowe zadanie",
                        "status": "OK"
                    }
                },
                {
                    "model": "SChTranslate",
                    "attributes": {
                        "description": "Tasks",
                        "translation": "Zadania",
                        "status": "OK"
                    }
                }
            ]
        }
    ]
}
```
