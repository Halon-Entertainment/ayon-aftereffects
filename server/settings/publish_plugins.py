from ayon_server.settings import BaseSettingsModel, SettingsField


class CollectReviewPluginModel(BaseSettingsModel):
    enabled: bool = SettingsField(
        True,
        title="Enabled",
        description="Add 'review' family to instances with mark_for_review enabled so ExtractReview processes them.",
    )


class ValidateSceneSettingsModel(BaseSettingsModel):
    """Validate naming of products and layers"""

    # _isGroup = True
    enabled: bool = SettingsField(True, title="Enabled")
    optional: bool = SettingsField(
        False,
        title="Optional",
        description="Allow artists to skip this validation during publish.",
    )
    active: bool = SettingsField(
        True,
        title="Active",
        description="Run this validation by default when publishing.",
    )
    skip_resolution_check: list[str] = SettingsField(
        default_factory=list,
        title="Skip Resolution Check for Tasks",
        description="Regex patterns for task names where resolution validation is skipped.",
    )
    skip_timelines_check: list[str] = SettingsField(
        default_factory=list,
        title="Skip Timeline Check for Tasks",
        description="Regex patterns for task names where frame range validation is skipped.",
    )


class IntegrateDeliveryCopyModel(BaseSettingsModel):
    """Copy rendered files to a delivery folder on publish."""

    enabled: bool = SettingsField(False, title="Enabled")
    delivery_template_name: str = SettingsField(
        "default",
        title="Delivery Template Name",
        description=(
            "Name of the delivery template defined in project anatomy. "
            "The template's root must be configured as a project root."
        ),
    )


class AfterEffectsPublishPlugins(BaseSettingsModel):
    CollectReview: CollectReviewPluginModel = SettingsField(
        default_factory=CollectReviewPluginModel,
        title="Collect Review",
    )
    ValidateSceneSettings: ValidateSceneSettingsModel = SettingsField(
        default_factory=ValidateSceneSettingsModel,
        title="Validate Scene Settings",
    )
    IntegrateDeliveryCopy: IntegrateDeliveryCopyModel = SettingsField(
        default_factory=IntegrateDeliveryCopyModel,
        title="Delivery Copy",
    )


AE_PUBLISH_PLUGINS_DEFAULTS = {
    "CollectReview": {"enabled": True},
    "ValidateSceneSettings": {
        "enabled": True,
        "optional": True,
        "active": True,
        "skip_resolution_check": [".*"],
        "skip_timelines_check": [".*"],
    },
    "IntegrateDeliveryCopy": {
        "enabled": False,
        "delivery_template_name": "default",
    },
}
