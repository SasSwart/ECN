

def factory(func_map, ctrl_map, stack, pipe):
    def exchange(current=None):
        def controller(key=None):
            def execute(*args):
                stack.append(func_map[key](*args))
                return exchange(key)

            if key is None:
                terminal = pipe(stack)
                stack.clear()
                return terminal
            if current is None or key in ctrl_map[current]:
                return execute
            raise ValueError('\'{}\' has no access to \'{}\' '
                             'in its flow-graph, please try: {}'.format(current, key, ctrl_map[current]))
        return controller
    return exchange


"""
class ControlledFactory(dict):
    def __init__(self, states):
        super(ControlledFactory, self).__init__(**states)

        self._current = None
        self._flwctrl = defaultdict(str)

    def __getitem__(self, key):
        if self._current is None:
            self._current = key
            return super(ControlledFactory, self).__getitem__(key)
        if key in self._flwctrl[self._current]:
            self._current = key
            return super(ControlledFactory, self).__getitem__(key)
        raise ValueError('{} has no access to {} '
                         'in its flow-graph, please try: {}'.format(self._current, key, self._flwctrl[self._current]))

    def __setitem__(self, key, val):
        self._flwctrl[key] = val

    def reset(self):
        self._current = None

    def get_control(self, key):
        return self._flwctrl[key]
"""
