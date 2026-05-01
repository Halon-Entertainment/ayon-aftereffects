import pyblish.api

from ayon_aftereffects.api import get_stub


class RestoreCompName(pyblish.api.InstancePlugin):
    """Restore comp to its original name after local render publish.

    When ``rename_comp_to_product_name`` is enabled in the creator
    settings, compositions are renamed to the product name at create
    time. This plugin reverts that rename once the local render has
    been extracted and integrated so the artist sees the original
    composition name in After Effects.
    """

    label = "Restore comp name"
    order = pyblish.api.IntegratorOrder + 8.0
    hosts = ["aftereffects"]
    families = ["render.local"]
    optional = True

    def process(self, instance):
        orig_comp_name = instance.data.get("orig_comp_name")
        if not orig_comp_name:
            self.log.debug("No original comp name stored, skipping restore.")
            return

        comp_id = instance.data.get("comp_id")
        if not comp_id:
            self.log.warning("No comp_id found, cannot restore name.")
            return

        stub = get_stub()
        current_name = instance.data.get("comp_name", "")
        self.log.info(
            "Restoring comp name from '%s' to '%s'",
            current_name,
            orig_comp_name,
        )
        stub.rename_item(comp_id, orig_comp_name)
