import sentry_sdk

SENTRY_DSN = "https://f0e4038c64dc4c79b5404c93608df210@o184107.ingest.sentry.io/5780285"


def setup_sentry():
    sentry_sdk.init(SENTRY_DSN, traces_sample_rate=1.0)
