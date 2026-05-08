"""Copy rendered files to a delivery (footage) folder during publish.

Resolves an anatomy delivery template and appends transfer entries
so IntegrateAsset copies files to both the publish path and the
delivery location in a single atomic file transaction.
"""

import os
import re
import copy
import logging

import pyblish.api

log = logging.getLogger(__name__)


class IntegrateDeliveryCopy(pyblish.api.InstancePlugin):
    """Queue delivery copies for rendered files.

    Runs before IntegrateAsset. For each representation, resolves
    the configured delivery anatomy template and appends
    ``(src, dst)`` entries to ``instance.data["transfers"]``.
    IntegrateAsset then processes them as part of its file
    transaction.
    """

    label = "Delivery Copy"
    order = pyblish.api.IntegratorOrder - 0.05
    families = ["render", "render.local"]
    hosts = ["aftereffects"]

    enabled = False
    delivery_template_name = "default"

    def process(self, instance):
        anatomy = instance.context.data["anatomy"]

        template_obj = anatomy.get_template_item(
            "delivery",
            self.delivery_template_name,
            "path",
            default=None,
        )
        if template_obj is None:
            self.log.warning(
                "Delivery template '%s' not found in anatomy, skipping.",
                self.delivery_template_name,
            )
            return

        # Verify that roots referenced in the delivery template are
        # configured in project anatomy.  Missing roots would cause
        # IntegrateAsset's path validation to fail later.
        delivery_templates = anatomy.templates.get("delivery", {})
        required_roots = anatomy.root_names_from_templates(delivery_templates)
        configured_roots = set(anatomy.roots.keys())
        missing = required_roots - configured_roots
        if missing:
            self.log.warning(
                "Delivery template references root(s) %s that are not "
                "configured in project anatomy. Delivery copy will be "
                "skipped to avoid a publish failure.",
                ", ".join(sorted(missing)),
            )
            return

        representations = instance.data.get("representations")
        if not representations:
            return

        anatomy_data = copy.deepcopy(instance.data["anatomyData"])
        anatomy_data.pop("root", None)

        transfers = instance.data.setdefault("transfers", [])
        count = 0

        for repre in representations:
            staging_dir = repre.get("stagingDir") or instance.data.get(
                "stagingDir"
            )
            if not staging_dir:
                self.log.warning(
                    "No staging directory for representation '%s', "
                    "skipping.",
                    repre.get("name"),
                )
                continue

            repre_data = copy.deepcopy(anatomy_data)
            repre_data["representation"] = repre["name"]
            repre_data["ext"] = repre["ext"]
            variant = instance.data.get("variant", "")
            if variant.lower() == "main":
                variant = ""
            repre_data["variant"] = variant

            files = repre["files"]
            if isinstance(files, str):
                files = [files]

            is_sequence = len(files) > 1

            for filename in files:
                src = os.path.join(staging_dir, filename)

                file_data = copy.deepcopy(repre_data)
                if is_sequence:
                    frame = _extract_frame_from_filename(filename)
                    if frame is not None:
                        file_data["frame"] = frame

                try:
                    delivery_path = template_obj.format_strict(file_data)
                except (KeyError, TypeError) as exc:
                    self.log.warning(
                        "Could not resolve delivery path for '%s': %s",
                        filename,
                        exc,
                    )
                    continue

                delivery_path = delivery_path.replace("..", ".")
                delivery_path = os.path.normpath(
                    delivery_path.replace("\\", "/")
                ).rstrip()

                transfers.append((src, delivery_path))
                count += 1
                self.log.debug("Delivery: %s -> %s", src, delivery_path)

        if count:
            self.log.info(
                "Queued %d file(s) for delivery template '%s'.",
                count,
                self.delivery_template_name,
            )


def _extract_frame_from_filename(filename):
    """Extract trailing frame number from a sequence filename."""
    base = os.path.splitext(filename)[0]
    match = re.search(r"(\d+)$", base)
    if match:
        return int(match.group(1))
    return None
