"""AgentSpring: A modular, extensible agentic API framework inspired by the spirit of Spring—growth, flexibility, and rapid development."""

__version__ = "0.1.0"

# AgentSpring extension hooks

admin_panels = []
metrics_hooks = []
background_tasks = []
event_hooks = {"pre_request": [], "post_request": []}


def register_admin_panel(panel_func):
    admin_panels.append(panel_func)
    return panel_func


def register_metrics_hook(hook_func):
    metrics_hooks.append(hook_func)
    return hook_func


def register_background_task(task_func):
    background_tasks.append(task_func)
    return task_func


def register_event_hook(event, hook_func):
    if event not in event_hooks:
        event_hooks[event] = []
    event_hooks[event].append(hook_func)
    return hook_func
