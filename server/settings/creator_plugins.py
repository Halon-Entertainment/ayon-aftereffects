from ayon_server.settings import BaseSettingsModel, SettingsField


class CreateRenderPlugin(BaseSettingsModel):
    mark_for_review: bool = SettingsField(True, title="Review")
    default_variants: list[str] = SettingsField(
        default_factory=list,
        title="Default Variants"
    )
    force_setting_values: bool = SettingsField(
        True, title="Force resolution and duration values from Task")
    rename_comp_to_product_name: bool = SettingsField(
        False,
        title="Rename composition to product name",
        description=(
            "Rename composition to product name when creating render instance "
            "or when updating product name, e.g. on variant change."
        )
    )
    output_module_template: str = SettingsField(
        "PNG",
        title="Output module template",
        description=(
            "Name used to match an After Effects output module template "
            "when auto-configuring the Render Queue. Matched as a "
            "case-insensitive substring (e.g. 'PNG', 'TIFF', 'Lossless'). "
            "Falls back to TIFF if no match is found."
        )
    )


class AfterEffectsCreatorPlugins(BaseSettingsModel):
    RenderCreator: CreateRenderPlugin = SettingsField(
        title="Create Render",
        default_factory=CreateRenderPlugin,
    )
