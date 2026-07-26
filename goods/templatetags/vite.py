import json

from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()

_manifest_path = settings.BASE_DIR / 'static' / 'dist' / '.vite' / 'manifest.json'


def _manifest():
    return json.loads(_manifest_path.read_text())


@register.simple_tag
def vite_asset(entry):
    return static(f"dist/{_manifest()[entry]['file']}")


@register.simple_tag
def vite_css(entry):
    manifest = _manifest()
    css_files = []
    seen = set()

    def collect(key):
        if key in seen:
            return
        seen.add(key)
        chunk = manifest[key]
        css_files.extend(chunk.get('css', []))
        for imported in chunk.get('imports', []):
            collect(imported)

    collect(entry)
    return [static(f'dist/{css}') for css in dict.fromkeys(css_files)]
