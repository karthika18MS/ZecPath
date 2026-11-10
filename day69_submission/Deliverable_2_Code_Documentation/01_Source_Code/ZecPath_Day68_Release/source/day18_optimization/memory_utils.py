import gc


def cleanup_objects(*objects):
    """
    Request cleanup of temporary objects.

    Note:
    This removes the local references passed to this
    function. The caller should also delete its own
    large temporary references when appropriate.
    """

    for obj in objects:

        del obj

    gc.collect()


def force_garbage_collection():
    """
    Explicitly trigger Python garbage collection.
    """

    return gc.collect()