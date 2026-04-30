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


class AfterEffectsPublishPlugins(BaseSettingsModel):
    CollectReview: CollectReviewPluginModel = SettingsField(
        default_factory=CollectReviewPluginModel,
        title="Collect Review",
    )
    ValidateSceneSettings: ValidateSceneSettingsModel = SettingsField(
        default_factory=ValidateSceneSettingsModel,
        title="Validate Scene Settings",
    )


AE_PUBLISH_PLUGINS_DEFAULTS = {
    "CollectReview": {
        "enabled": True
    },
    "ValidateSceneSettings": {
        "enabled": True,
        "optional": True,
        "active": True,
        "skip_resolution_check": [
            ".*"
        ],
        "skip_timelines_check": [
            ".*"
        ]
    },
}
