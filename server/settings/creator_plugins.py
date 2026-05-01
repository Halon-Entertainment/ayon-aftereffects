from ayon_server.settings import BaseSettingsModel, SettingsField


class CreateRenderPlugin(BaseSettingsModel):
    mark_for_review: bool = SettingsField(
        True,
        title="Review",
        description="Add review family to render instances so ExtractReview generates reviewable outputs with burnin and slate.",
    )
    default_variants: list[str] = SettingsField(
        default_factory=list,
        title="Default Variants",
        description="Variant names shown in the creator dropdown (e.g. Main, Preview).",
    )
    force_setting_values: bool = SettingsField(
        True,
        title="Force resolution and duration values from Task",
        description="Override composition resolution, frame range, and FPS with values from the AYON task entity when creating a render instance.",
    )
    rename_comp_to_product_name: bool = SettingsField(
        False,
        title="Rename composition to product name",
        description=(
            "Rename composition to product name when creating render instance "
            "or when updating product name, e.g. on variant change."
        )
    )


class AfterEffectsCreatorPlugins(BaseSettingsModel):
    RenderCreator: CreateRenderPlugin = SettingsField(
        title="Create Render",
        default_factory=CreateRenderPlugin,
    )
