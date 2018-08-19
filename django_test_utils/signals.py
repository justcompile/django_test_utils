"""
Signal related utils
"""
import ast
import inspect

from django.apps import apps
from django.db.models.signals import ModelSignal


def disconnect_signals(signal_module):
    signal_attrs = [
        x
        for x in inspect.getmembers(signal_module)
        if not x[0].startswith('__')
    ]

    django_signals = dict(
        (name, func)
        for name, func in signal_attrs
        if isinstance(func, ModelSignal)
    )

    module_signals = [
        signal
        for _, signal in signal_attrs
        if signal.__module__ == signal_module.__name__
    ]

    for signal_func in module_signals:
        module = ast.parse(inspect.getsource(signal_func))
        for decorator in module.body[0].decorator_list:
            if decorator.func.id == 'receiver':
                django_signals[decorator.args[0].id].disconnect(
                    signal_func,
                    sender=apps.get_model(
                        app_label=signal_module.__name__.split('.')[0],
                        model_name=decorator.keywords[0].value.id,
                    ),
                )
