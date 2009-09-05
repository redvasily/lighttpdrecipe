import jinja2

def render_template(search_paths, template_name, buildout, options,
    filters=None, tests=None):

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(search_paths))
    env.filters['split'] = lambda x: x.split()
    env.filters['splitlines'] = lambda x: [s.strip() for s in x.splitlines()]
    
    if filters is not None:
        env.filters.update(filters)

    if tests is not None:
        env.tests.update(tests)

    template = env.get_template(template_name)

    context = dict(options)
    context['buildout'] = buildout
    context['options'] = options
    for key, value in buildout.iteritems():
        if key not in context:
            context[key] = value

    result = template.render(context)
    return result
