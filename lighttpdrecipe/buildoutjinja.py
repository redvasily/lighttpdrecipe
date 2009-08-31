import jinja2

def render_template(template, buildout, options, filters=None):
    env = jinja2.Environment()
    env.filters['split'] = lambda x: x.split()
    env.filters['splitlines'] = lambda x: [s.strip() for s in x.splitlines()]
    
    if filters is not None:
        env.filters.update(filters)

    template = env.from_string(template)

    context = dict(options)
    context['buildout'] = buildout
    for key, value in buildout.iteritems():
        if key not in context:
            context[key] = value

    result = template.render(context)
    return result
