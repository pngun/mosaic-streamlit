#!/usr/bin/env bash

set -e

if [[ -z "${APPLE_DEVELOPER_ID}" ]]; then
    echo "Set APPLE_DEVELOPER_ID, it's required."
    exit 1
fi

if [[ -z "${APPLE_ID}" ]]; then
    echo "Set APPLE_ID, it's required."
    exit 1
fi

if [[ -z "${APPLE_PASSWORD}" ]]; then
    echo "Set APPLE_PASSWORD, it's required."
    exit 1
fi

PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd )"
BUILD_ROOT="$PROJECT_ROOT/build"
ENTITLEMENTS_PATH="$BUILD_ROOT/entitlements.plist"
ELECTRON_ROOT="$PROJECT_ROOT/mosaic-streamlit"
ELECTRON_OUTPUT="$ELECTRON_ROOT/out/Tapestri Insights v4-darwin-x64"
APP_NAME="Tapestri Insights v4.app"
APP_PATH="$ELECTRON_OUTPUT/$APP_NAME"

echo "APPLE_DEVELOPER_ID: $APPLE_DEVELOPER_ID"
echo "APPLE_ID: $APPLE_ID"
echo "PROJECT_ROOT: $PROJECT_ROOT"
echo "BUILD_ROOT: $BUILD_ROOT"
echo "ELECTRON_ROOT: $ELECTRON_ROOT"
echo "ELECTRON_OUTPUT: $ELECTRON_OUTPUT"
echo "APP_NAME: $APP_NAME"
echo "APP_PATH: $APP_PATH"
echo " - - - - - "

. "$BUILD_ROOT/build-macos.sh"

cd $ELECTRON_ROOT
rm -rf .webpack out runnable
cp -R "$BUILD_ROOT/dist/runnable" "$ELECTRON_ROOT/"
yarn package
ls "$ELECTRON_OUTPUT"

cd "$ELECTRON_OUTPUT"
find "$APP_PATH" -name "*so" -exec codesign -s "$APPLE_DEVELOPER_ID" --force --timestamp  {}  \;
find "$APP_PATH" -name "*.dylib" -exec codesign -s "$APPLE_DEVELOPER_ID" --force --timestamp {} \;
codesign -s "$APPLE_DEVELOPER_ID" --timestamp --options=runtime --entitlements "$ENTITLEMENTS_PATH" "$APP_PATH/Contents/Resources/runnable/Contents/Resources/pyarrow/plasma-store-server"
codesign -s "$APPLE_DEVELOPER_ID" --timestamp --options=runtime --entitlements "$ENTITLEMENTS_PATH" "$APP_PATH/Contents/Frameworks/Squirrel.framework/Resources/ShipIt"
codesign -s "$APPLE_DEVELOPER_ID" --force --all-architectures --timestamp --options=runtime --entitlements "$ENTITLEMENTS_PATH" --deep "$APP_PATH/Contents/Resources/runnable/"
codesign -s "$APPLE_DEVELOPER_ID" --force --all-architectures --timestamp --options=runtime --entitlements "$ENTITLEMENTS_PATH" --deep "$APP_PATH"

codesign --verbose --verify "$APP_PATH"
spctl -vvv --assess --type exec "$APP_PATH"

cd "$ELECTRON_ROOT"
yarn make --skip-package
DMG_PATH=$(find "$ELECTRON_ROOT/out/make" -name "Tapestri Insights v4-*.dmg")
if [ ! -f "$DMG_PATH" ]; then
    echo "Something is wrong, DMG file doesn't exist."
    exit 1
fi
codesign -s "$APPLE_DEVELOPER_ID" "$DMG_PATH"
echo "DMG_PATH: $DMG_PATH"

NOTARIZE_APP=$(xcrun altool --notarize-app --primary-bundle-id "com.electron.tapestri-insights-v4" -u $APPLE_ID -p $APPLE_PASSWORD -f "$DMG_PATH")
echo "NOTARIZE_APP:\n$NOTARIZE_APP"

# NID="- Request UUID (see $NOTARIZE_APP) -"
# Check progress: xcrun altool --notarization-info $NID -u $APPLE_ID -p $APPLE_PASSWORD

for (( ; ; ))
do
    xcrun stapler staple "$DMG_PATH"
    exit_status=$?
    if [ "${exit_status}" = "65" ]
    then
        echo "Waiting for notarization to complete"
        sleep 30
    else
        echo "Stapler status: ${exit_status}"
        break
    fi
done

spctl --assess --type open --context context:primary-signature --verbose $DMG_PATH
