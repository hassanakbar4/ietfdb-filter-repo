import sys, os, argparse

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path = [ basedir ] + sys.path
os.environ["DJANGO_SETTINGS_MODULE"] = "ietf.settings"

virtualenv_activation = os.path.join(basedir, "env", "bin", "activate_this.py")
if os.path.exists(virtualenv_activation):
    execfile(virtualenv_activation, dict(__file__=virtualenv_activation))

import django
django.setup()

from django.conf import settings

from ietf.doc.models import Document
from ietf.name.models import FormalLanguageName
from ietf.utils.draft import Draft

parser = argparse.ArgumentParser()
parser.add_argument("--document", help="specific document name")
parser.add_argument("--words", action="store_true", help="fill in word count")
parser.add_argument("--formlang", action="store_true", help="fill in formal languages")
args = parser.parse_args()

formal_language_dict = { l.pk: l for l in FormalLanguageName.objects.all() }


docs_qs = Document.objects.filter(type="draft")

if args.document:
    docs_qs = docs_qs.filter(docalias__name=args.document)

for doc in docs_qs.prefetch_related("docalias_set", "formal_languages"):
    canonical_name = doc.name
    for n in doc.docalias_set.all():
        if n.name.startswith("rfc"):
            canonical_name = n.name

    if canonical_name.startswith("rfc"):
        path = os.path.join(settings.RFC_PATH, canonical_name + ".txt")
    else:
        path = os.path.join(settings.INTERNET_ALL_DRAFTS_ARCHIVE_DIR, canonical_name + "-" + doc.rev + ".txt")

    if not os.path.exists(path):
        print "skipping", doc.name, "no txt file found at", path
        continue

    with open(path, 'r') as f:
        d = Draft(f.read(), path)

        updated = False

        updates = {}

        if args.words:
            words = d.get_wordcount()
            if words != doc.words:
                updates["words"] = words

        if args.formlang:
            langs = d.get_formal_languages()

            new_formal_languages = set(formal_language_dict[l] for l in langs)
            old_formal_languages = set(doc.formal_languages.all())

            if new_formal_languages != old_formal_languages:
                for l in new_formal_languages - old_formal_languages:
                    doc.formal_languages.add(l)
                    updated = True
                for l in old_formal_languages - new_formal_languages:
                    doc.formal_languages.remove(l)
                    updated = True

        if updates:
            Document.objects.filter(pk=doc.pk).update(**updates)
            updated = True

        if updated:
            print "updated", canonical_name

