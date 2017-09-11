

class Factory(object):
    def __init__(self, eof_object='HALT'):
        self.path = []  # sequential record of called procedures
        self.loci = []  # sequential record of results of procedure calls
        self.dump = []  # sequential record of provided but unused arguments
        self.logs = []  # sequential record of errors raised by illegal calls

        self.eof_object = eof_object

        self._context = {
            'BIND': self._bind,
            'NAME': self._name,
            'PIPE': self._pipe,
            'LOAD': self._load,
            'DUMP': self._dump,
            'HALT': self.halt
        }
        self.reserved = self._context.keys()

        self._call_as = 'BIND'

    def __call__(self, *args, **kwargs):
        return self._context[self._call_as](*args, **kwargs)

    def call_as(self, desired):
        self._call_as = desired

    def start(self):
        self._call_as = 'PIPE'
        self.path.append('START')

    def halt(self, *args, **kwargs):
        raise NotImplementedError

    def _expect(self, state):
        assert self._call_as == state, 'current state is {}, not \'{}\''.format(self._call_as, state)

    def _bind(self, predicate, alias=None, is_function=True):
        try:
            self._expect('BIND')
        except AssertionError as error:
            self.logs.append(error)

        def bound(func):
            func.predicate = predicate
            func.is_function = is_function

            name = func.__name__ if alias is None else alias
            if name not in self.reserved:
                self._context[func.__name__ if alias is None else alias] = func
            else:
                raise NameError('\'{}\' is a reserved factory function, please change the alias.'.format(name))

            return func

        return bound

    def _name(self, old_name, new_name):
        try:
            self._expect('NAME')
        except AssertionError as error:
            self.logs.append(error)

        self._context[new_name] = self._context.pop(old_name)
        self._call_as = 'PIPE'

        return self

    def _pipe(self, procedure):
        try:
            self._expect('PIPE')
        except AssertionError as error:
            self.logs.append(error)

        if procedure == self.eof_object:
            return self.halt
        try:
            getattr(self._context[procedure], 'predicate')(self)
            self.path.append(procedure)
            self._call_as = 'LOAD'
        except AttributeError:
            self.logs.append(AttributeError('\'{}\' has no defined predicate.'.format(procedure)))
            self._call_as = 'DUMP'
        except KeyError:
            self.logs.append(AttributeError('\'{}\' is not defined within the factory.'.format(procedure)))
            self._call_as = 'DUMP'
        except SyntaxError as error:
            self.logs.append(error)
            self._call_as = 'DUMP'

        return self

    def _load(self, *args, **kwargs):
        try:
            self._expect('LOAD')
        except AssertionError as error:
            self.logs.append(error)

        piped = self._context[self.path[-1]]
        if getattr(piped, 'is_function'):
            self.loci.append(piped(*args, **kwargs))
        else:
            piped(*args, **kwargs)
        self._call_as = 'PIPE'

        return self

    def _dump(self, *args, **kwargs):
        try:
            self._expect('DUMP')
        except AssertionError as error:
            self.logs.append(error)

        self.dump.append((args, kwargs))
        self._call_as = 'PIPE'

        return self

if __name__ == '__main__':
    factory = Factory()

    def _raise(message):
        raise SyntaxError(message)

    @factory(lambda x: True if x.path[-1] == 'START' else _raise('\'START\' must precede \'like_to\'.'))
    def like_to(verb, adverb):
        return 'I like to {} {}.'.format(verb, adverb)

    @factory(lambda x: True if x.path[-1] == 'like_to' else _raise('\'like_to\' must precede \'hate_to\'.'))
    def hate_to(verb, adverb):
        return 'I hate to {} {}.'.format(verb, adverb)

    @factory(lambda x: True if x.path[-1] == 'hate_to' else _raise('\'hate_to\' must precede \'need_to\'.'))
    def need_to(verb, adverb):
        return 'I need to {} {}.'.format(verb, adverb)

    @factory(lambda x: True if x.path[-1] == 'need_to' else _raise('\'need_to\' must precede \'want_to\'.'))
    def want_to(verb, adverb):
        return 'I want to {} {}.'.format(verb, adverb)

    factory.start()
    factory('like_to')('dance', 'idiotically')
    factory('hate_to')('trudge', 'logically')
    factory('need_to')('frolic', 'manically')
    factory('want_to')('sleep', 'peacefully')

    print('path:', factory.path)
    print('loci:', factory.loci)
    print('logs:', factory.logs)
    print('dump:', factory.dump)
