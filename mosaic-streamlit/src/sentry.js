const { init } =
  process.type === "browser"
    ? require("@sentry/electron/dist/main")
    : require("@sentry/electron/dist/renderer");

const SENTRY_DSN = "https://f0e4038c64dc4c79b5404c93608df210@o184107.ingest.sentry.io/5780285"

const setupSentry = () => {
  init({ dsn: SENTRY_DSN })
}

export default setupSentry
