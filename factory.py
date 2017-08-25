

def factory(func_map=None, ctrl_map=None, stack=None, pipe=None):
    def exchange(state=None):
        def controller(key=None, halt=None, *args, **kwargs):
            def execute(*_args, **_kwargs):
                stack.append(func_map[key](*_args, **_kwargs))
                return exchange(key)

            if key is None:
                temp = stack[:]
                stack.clear()

                if pipe is None:
                    return temp
                if pipe.__code__.co_code == factory.__code__.co_code:
                    return pipe(func_map, ctrl_map, temp, pipe if halt is None else halt)
                return pipe(temp, *args, **kwargs)
            if state is None or key in ctrl_map[state]:
                return execute
            raise ValueError('\'{}\' has no access to \'{}\' '
                             'in its state-graph, please try: {}'.format(state, key, ctrl_map[state]))
        return controller
    return exchange()

"""
def factory(func_map=None, ctrl_map=None):
    def build(stack=None, pipe=None):
        stack = [] if None else stack[:]

        def exchange(state=None):
            def controller(key=None, halt=None, *args, **kwargs):
                def execute(*_args, **_kwargs):
                    stack.append(func_map[key](*_args, **_kwargs))
                    return exchange(key)

                print(key)
                if key is None:
                    if pipe is None:
                        return stack
                    if pipe.__code__.co_code == factory.__code__.co_code:
                        return build(stack, pipe if halt is None else halt)
                    return pipe(stack, *args, **kwargs)
                if state is None or key in ctrl_map[state]:
                    return execute
                raise ValueError('\'{}\' has no access to \'{}\' '
                                 'in its state-graph, please try: {}'.format(state, key, ctrl_map[state]))
            return controller
        return exchange()
    return build
"""


if __name__ == '__main__':
    def to_str(stack):
        return ', '.join(stack) + '!'

    f_map = {
        '1': lambda x: '1 x {}'.format(x),
        '2': lambda x: '2 x {}'.format(x),
        '3': lambda x: '3 x {}'.format(x),
        '4': lambda x: '4 x {}'.format(x),
        '5': lambda x: '5 x {}'.format(x),
        '6': lambda x: '6 x {}'.format(x),
    }

    c_map = {
        '1': '2',
        '2': '3',
        '3': '4',
        '4': '5',
        '5': '6',
        '6': 'NONE'
    }

    process_a = factory(f_map, c_map, [], factory)

    print(process_a('3')('bears')('4')('moose')()('1')('tick')(halt=to_str)())
