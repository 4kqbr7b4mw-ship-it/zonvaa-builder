import governance


def test_operational_metrics_notifications_public_api_is_complete():
    expected = (
        "OperationalMetricAggregationRule",
        "OperationalMetricDefinition",
        "OperationalMetricObservation",
        "OperationalMetricPackage",
        "OperationalMetricSnapshot",
        "OperationalMetricUnit",
        "OperationalMetricUncertaintyStatus",
        "OperationalMetricValidationError",
        "OperationalMetricValidator",
        "OperationalNotificationDecisionStatus",
        "OperationalNotificationDeliveryStatus",
        "OperationalNotificationEvidence",
        "OperationalNotificationExcludedContent",
        "OperationalNotificationMessageType",
        "OperationalNotificationPackage",
        "OperationalNotificationPolicy",
        "OperationalNotificationRecipientCategory",
        "OperationalNotificationSeverity",
        "OperationalNotificationSnapshot",
        "OperationalNotificationSourceType",
        "OperationalNotificationTriggerCondition",
        "OperationalNotificationTriggerReason",
        "OperationalNotificationValidationError",
        "OperationalNotificationValidator",
    )
    for name in expected:
        assert name in governance.__all__
        assert getattr(governance, name) is not None
