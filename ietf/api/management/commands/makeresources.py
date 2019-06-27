# Copyright The IETF Trust 2014-2019, All Rights Reserved
# -*- coding: utf-8 -*-


import os
import datetime
import collections
from importlib import import_module

import debug                            # pyflakes:ignore

from django.core.management.base import AppCommand
from django.db import models
from django.template import Template, Context

from tastypie.resources import ModelResource


resource_head_template = """# Autogenerated by the makeresources management command {{date}}
from tastypie.resources import ModelResource
from tastypie.fields import ToManyField                 # pyflakes:ignore
from tastypie.constants import ALL, ALL_WITH_RELATIONS  # pyflakes:ignore
from tastypie.cache import SimpleCache

from ietf import api
from ietf.api import ToOneField                         # pyflakes:ignore

from {{app}}.models import *                            # pyflakes:ignore
"""

resource_class_template = """{% autoescape off %}
{% for model in models %}{% for import in model.imports %}{% if import.module != app_label %}
from ietf.{{ import.module }}.resources import {% for name in import.names %}{% if not forloop.first %}, {%endif%}{{name}}Resource{% endfor %}{% endif %}{% endfor %}
class {{model.name}}Resource(ModelResource):{% if model.foreign_keys %}{% for fk in model.foreign_keys %}
    {{fk.name|ljust:"16"}} = ToOneField({{fk.rmodel_name}}, '{{fk.name}}'{% if fk.field.null %}, null=True{% endif %}){% endfor %}{% endif %}{% if model.m2m_keys %}{% for fk in model.m2m_keys %}
    {{fk.name|ljust:"16"}} = ToManyField({{fk.rmodel_name}}, '{{fk.name}}', null=True){% endfor %}{% endif %}
    class Meta:
        queryset = {{model.name}}.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = '{{model.resource_name}}'
        ordering = ['{{model.pk_name}}', ]
        filtering = { {% for name in model.plain_names %}
            "{{ name }}": ALL,{%endfor%}{% for name in model.fk_names%}
            "{{ name }}": ALL_WITH_RELATIONS,{%endfor%}{% for name in model.m2m_names %}
            "{{ name }}": ALL_WITH_RELATIONS,{%endfor%}
        }
api.{{app_label}}.register({{model.name}}Resource())
{% endfor %}{% endautoescape %}"""

def render(template, dictionary):
    template = Template(template, None, None)
    context = Context(dictionary)
    return template.render(context)

class Command(AppCommand):

    def handle_app_config(self, app, **options):
        # dotted path to app
        if app.name:
            print("\nInspecting %s .." % app.name)
            resource_file_path = os.path.join(app.path, "resources.py")

            app_models = app.get_models()

            app_resources = {}
            if os.path.exists(resource_file_path):
                resources = import_module("%s.resources" % app.name)
                for n,v in resources.__dict__.items():
                    if issubclass(type(v), type(ModelResource)):
                        app_resources[n] = v

            missing_resources = []
            for m in app_models:
                model_name = m.__name__
                rclass_name = model_name + "Resource"
                if not rclass_name in app_resources:
                    missing_resources.append((m, rclass_name))

            if missing_resources:
                print("Updating resources.py for %s" % app.name)
                with open(resource_file_path, "a") as rfile:
                    info = dict(
                        app=app.name,
                        app_label=app.label,
                        date=datetime.datetime.now()
                    )
                    new_models = {}
                    for model, rclass_name in missing_resources:
                        model_name = model.__name__
                        resource_name = model.__name__.lower()
                        imports = collections.defaultdict(lambda: collections.defaultdict(list))
                        print("Adding resource class for %s" % model_name)
                        foreign_keys = []
                        plain_names = []
                        fk_names = []
                        m2m_names = []
                        pk_name = model._meta.pk.name
                        #debug.pprint('dir(model)')
                        for field in model._meta.fields:
                            if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                                #debug.show('field.name')
                                #debug.pprint('dir(field.remote_field.to)')
                                #exit()
                                rel_app=field.remote_field.model._meta.app_label
                                rel_model_name=field.remote_field.model.__name__
                                if rel_model_name == model_name:
                                    # foreign key to self class -- quote
                                    # the rmodel_name
                                    rmodel_name="'%s.resources.%sResource'" % (app.name, rel_model_name)
                                else:
                                    rmodel_name=rel_model_name+"Resource"
                                foreign_keys.append(dict(
                                    field=field,
                                    name=field.name,
                                    app=rel_app,
                                    module=rel_app.split('.')[-1],
                                    model=field.remote_field.model,
                                    model_name=rel_model_name,
                                    rmodel_name=rmodel_name,
                                    resource_name=field.remote_field.model.__name__.lower(),
                                    ))
                                imports[rel_app]["module"] = rel_app
                                imports[rel_app]["names"].append(rel_model_name)
                                fk_names.append(field.name)
                            else:
                                plain_names.append(field.name)
                        m2m_keys = []
                        for field in model._meta.many_to_many:
                                #debug.show('field.name')
                                #debug.pprint('dir(field.remote_field.model)')
                                #exit()
                                rel_app=field.remote_field.model._meta.app_label
                                rel_model_name=field.remote_field.model.__name__
                                if rel_model_name == model_name:
                                    # foreign key to self class -- quote
                                    # the rmodel_name
                                    rmodel_name="'%s.resources.%sResource'" % (app.name, rel_model_name)
                                else:
                                    rmodel_name=rel_model_name+"Resource"
                                m2m_keys.append(dict(
                                    field=field,
                                    name=field.name,
                                    app=rel_app,
                                    module=rel_app.split('.')[-1],
                                    model=field.remote_field.model,
                                    model_name=rel_model_name,
                                    rmodel_name=rmodel_name,
                                    resource_name=field.remote_field.model.__name__.lower(),
                                    ))
                                imports[rel_app]["module"] = rel_app
                                imports[rel_app]["names"].append(rel_model_name)
                                m2m_names.append(field.name)
                        # some special import cases
                        if "auth" in imports:
                            imports["auth"]["module"] = 'utils'
                        if "contenttypes" in imports:
                            imports["contenttypes"]["module"] = 'utils'
                        for k in imports:
                            imports[k]["names"] = set(imports[k]["names"])
                        new_models[model_name] = dict(
                            app=app.name.split('.')[-1],
                            model=model,
                            fields=model._meta.fields,
                            m2m_fields=model._meta.many_to_many,
                            name=model_name,
                            imports=[ v for k,v in list(imports.items()) ],
                            foreign_keys=foreign_keys,
                            m2m_keys=m2m_keys,
                            resource_name=resource_name,
                            plain_names=plain_names,
                            fk_names=fk_names,
                            m2m_names=m2m_names,
                            pk_name=pk_name,
                        )

                    # Sort resources according to internal FK reference depth
                    new_model_list = []
                    # Write out classes with FKs to classes in the same module
                    # lower or equal to 'internal_fk_count_limit.  Start out
                    # by writing only leaf classes, then increase the limit if
                    # needed:
                    internal_fk_count_limit = 0
                    while len(new_models) > 0:
                        list_len = len(new_models)
                        #debug.show('len(new_models)')
                        keys = list(new_models.keys())
                        for model_name in keys:
                            internal_fk_count = 0
                            for fk in new_models[model_name]["foreign_keys"]+new_models[model_name]["m2m_keys"]:
                                #debug.say("if statement comparison on:")
                                #debug.show('fk["model_name"]')
                                #debug.show('model_name')
                                #debug.say('if fk["model_name"] in new_models and not fk["model_name"] == model_name:')
                                if fk["model_name"] in new_models and not fk["model_name"] == model_name:
                                    #print("Not a leaf model: %s: found fk to %s" % (model_name, fk["model"]))
                                    internal_fk_count += 1
                            if internal_fk_count <= internal_fk_count_limit:
                                #print("Ordered: "+model_name)
                                new_model_list.append(new_models[model_name])
                                del new_models[model_name]
                        if list_len == len(new_models):
                            #debug.show('list_len, len(new_models)')
                            print("Circular FK dependencies -- cannot order resource classes")
                            if internal_fk_count_limit < list_len:
                                print("Attempting a partial ordering ...")
                                internal_fk_count_limit += 1
                            else:
                                print("Failed also with partial ordering, writing resource classes without ordering")
                                new_model_list = [ v for k,v in list(new_models.items()) ]
                                break

                    if rfile.tell() == 0:
                        print("Writing resource file head")
                        rfile.write(render(resource_head_template, info))
                    else:
                        print("\nNOTE: Not writing resource file head.\nYou may have to update the import from %s.models" % app.name)

                    info.update(dict(models=new_model_list))
                    rfile.write(render(resource_class_template, info))
            else:
                print("  nothing to do for %s" % app.name)
