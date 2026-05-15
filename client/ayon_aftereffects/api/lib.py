from __future__ import annotations
import os
import re
import json
import contextlib
import logging
import pyblish
from typing import Union

from ayon_core.pipeline.context_tools import get_current_task_entity

from .ws_stub import get_stub

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@contextlib.contextmanager
def maintained_selection():
    """Maintain selection during context."""
    selection = get_stub().get_selected_items(True, False, False)
    try:
        yield selection
    finally:
        pass


def get_extension_manifest_path():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "extension",
        "CSXS",
        "manifest.xml"
    )


def get_unique_item_name(items, name):
    """Creates unique name for 'item'.

    Gets all item names (compositions|containers) and if 'name' is
    present in them, increases suffix by 1 (eg. creates unique item name
      - for Loader)

    Args:
        items (list): of strings, names only
        name (string):  checked value

    Returns:
        (string): name_00X (without version)
    """
    names = {}
    index_regex = re.compile(r"_\d{3}$")
    for item in items:
        item_name = index_regex.sub("", item)
        names.setdefault(item_name, 0)
        names[item_name] += 1
    occurrences = names.get(name, 0)

    return "{}_{:0>3d}".format(name, occurrences + 1)


def get_background_layers(file_url):
    """
        Pulls file name from background json file, enrich with folder url for
        AE to be able import files.

        Order is important, follows order in json.

        Args:
            file_url (str): abs url of background json

        Returns:
            (list): of abs paths to images
    """
    with open(file_url) as json_file:
        data = json.load(json_file)

    layers = list()
    bg_folder = os.path.dirname(file_url)
    for child in data['children']:
        if child.get("filename"):
            layers.append(os.path.join(bg_folder, child.get("filename")).
                          replace("\\", "/"))
        else:
            for layer in child['children']:
                if layer.get("filename"):
                    layers.append(os.path.join(bg_folder,
                                               layer.get("filename")).
                                  replace("\\", "/"))
    return layers


def get_entity_attributes(entity: dict) -> dict[str, Union[float, int]]:
    """Get attributes of folder or task entity.

    Returns:
        dict: Scene data.

    """
    attrib: dict = entity["attrib"]
    fps = attrib.get("fps", 0)
    frame_start = attrib.get("frameStart", 0)
    frame_end = attrib.get("frameEnd", 0)
    handle_start = attrib.get("handleStart", 0)
    handle_end = attrib.get("handleEnd", 0)
    resolution_width = attrib.get("resolutionWidth", 0)
    resolution_height = attrib.get("resolutionHeight", 0)
    duration = (frame_end - frame_start + 1) + handle_start + handle_end

    if not fps:
        log.warning(
            "Entity has no fps attribute set (got %r). "
            "Composition fps will not be updated — check AYON shot settings.",
            fps,
        )

    return {
        "fps": fps,
        "frameStart": frame_start,
        "frameEnd": frame_end,
        "handleStart": handle_start,
        "handleEnd": handle_end,
        "resolutionWidth": resolution_width,
        "resolutionHeight": resolution_height,
        "duration": duration
    }


def set_settings(
        frames, resolution, comp_ids=None, print_msg=True, entity=None):
    """Sets number of frames and resolution to selected comps.

    Args:
        frames (bool): True if set frame info
        resolution (bool): True if set resolution
        comp_ids (list[int]): specific composition ids, if empty
            it tries to look for currently selected
        print_msg (bool): True throw JS alert with msg
        entity (Optional[dict]): Entity to use attributes from to define the
            frame range, fps and resolution from. If not provided, current
            task entity is used.
    """
    frame_start = frames_duration = fps = width = height = None

    if entity is None:
        entity = get_current_task_entity()
    settings = get_entity_attributes(entity)

    msg = ''
    if frames:
        frame_start = settings["frameStart"] - settings["handleStart"]
        frames_duration = settings["duration"]
        fps = settings["fps"]
        if not fps:
            log.warning(
                "Entity fps is 0 or missing — skipping fps/frame update. "
                "Check AYON shot settings."
            )
            fps = None
            frame_start = None
            frames_duration = None
        msg += f"frame start:{frame_start}, duration:{frames_duration}, "\
               f"fps:{fps}"
    if resolution:
        width = settings["resolutionWidth"]
        height = settings["resolutionHeight"]
        msg += f"width:{width} and height:{height}"

    stub = get_stub()
    if not comp_ids:
        comps = stub.get_selected_items(True, False, False)
        comp_ids = [comp.id for comp in comps]
    if not comp_ids:
        stub.print_msg("Select at least one composition to apply settings.")
        return

    for comp_id in comp_ids:
        msg = f"Setting for comp {comp_id} " + msg
        log.debug(msg)
        stub.set_comp_properties(comp_id, frame_start, frames_duration,
                                 fps, width, height)
        if print_msg:
            stub.print_msg(msg)


def _get_next_version(stub, base_name):
    """Determine the next version number for a comp name.

    Scans existing compositions for names matching ``base_name_v###``
    and returns the next version string (e.g. ``v002``).  Returns
    ``v001`` when no matching comps exist.

    Args:
        stub (AfterEffectsServerStub): Connection stub.
        base_name (str): Comp name prefix without version suffix.

    Returns:
        str: Version string like ``v001``.
    """
    version_re = re.compile(
        r"^" + re.escape(base_name) + r"_v(\d{3})$", re.IGNORECASE
    )
    max_version = 0
    for comp in stub.get_items(comps=True, folders=False, footages=False):
        match = version_re.match(comp.name)
        if match:
            max_version = max(max_version, int(match.group(1)))
    return f"v{max_version + 1:03d}"


def create_shot_comp():
    """Create a new composition with AYON task settings applied.

    Creates a comp following Halon anatomy naming:
    ``<shot>_<Task>_HAL_<version>`` (e.g. ``sh010_Comp_HAL_v001``).
    Applies frame range, fps, and resolution from the task entity
    attributes automatically.
    """
    entity = get_current_task_entity()
    settings = get_entity_attributes(entity)

    folder_path = os.environ.get("AYON_FOLDER_PATH", "")
    shot = folder_path.rsplit("/", 1)[-1] if folder_path else "shot"
    task = entity.get("taskType", entity.get("name", "comp"))

    log.info(
        "Creating shot comp with context — folder_path: %s, task: %s",
        folder_path,
        task,
    )

    stub = get_stub()

    base_name = f"{shot}_{task}_HAL"
    version = _get_next_version(stub, base_name)
    comp_name = f"{base_name}_{version}"

    if not settings["fps"]:
        log.warning(
            "Entity fps is 0 or missing for '%s' — composition fps will "
            "not be set. Check AYON shot settings for this folder.",
            folder_path,
        )

    comp_id = stub.add_item(comp_name, "COMP")

    set_settings(
        frames=True,
        resolution=True,
        comp_ids=[comp_id],
        print_msg=False,
        entity=entity,
    )

    stub.setup_render_queue(comp_id)

    from ayon_aftereffects.api.launch_logic import version_up
    version_up()

    msg = (
        f"Created comp '{comp_name}' — "
        f"fps:{settings['fps']}, "
        f"frames:{settings['frameStart']}-{settings['frameEnd']}, "
        f"res:{settings['resolutionWidth']}x{settings['resolutionHeight']}"
    )
    log.info(msg)
    stub.print_msg(msg)


def find_close_plugin(close_plugin_name, log):
    if close_plugin_name:
        plugins = pyblish.api.discover()
        for plugin in plugins:
            if plugin.__name__ == close_plugin_name:
                return plugin

    log.debug("Close plugin not found, app might not close.")


def publish_in_test(log, close_plugin_name=None):
    """Loops through all plugins, logs to console. Used for tests.

    Args:
        log (Logger)
        close_plugin_name (Optional[str]): Name of plugin with responsibility
            to close application.
    """

    # Error exit as soon as any error occurs.
    error_format = "Failed {plugin.__name__}: {error} -- {error.traceback}"
    close_plugin = find_close_plugin(close_plugin_name, log)

    for result in pyblish.util.publish_iter():
        for record in result["records"]:
            # Why do we log again? pyblish logger is logging to stdout...
            log.info("{}: {}".format(result["plugin"].label, record.msg))

        if not result["error"]:
            continue

        # QUESTION We don't break on error?
        error_message = error_format.format(**result)
        log.error(error_message)
        if close_plugin:  # close host app explicitly after error
            context = pyblish.api.Context()
            try:
                close_plugin().process(context)
            except Exception as exp:
                print(exp)
