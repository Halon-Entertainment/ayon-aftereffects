AfterEffects Addon (Halon Fork)
================================

This is Halon Entertainment's fork of the [Ynput ayon-aftereffects](https://github.com/ynput/ayon-aftereffects) addon, forked from upstream version **0.2.12**. The major version was incremented to **1.x** to clearly distinguish Halon builds from upstream Ynput releases (0.x).

## Halon-specific changes

- **Shot comp naming**: New Shot Comp button uses the task type short name from AYON project settings (e.g. `sh010_comp_HLN_v001`)
- **Render Queue auto-setup**: Automatically configures a PNG sequence Render Queue item when publishing if one is missing
- **Version Up**: Adds a Version Up button to the AYON panel in After Effects
- **Burnin data**: Render instances carry folder/task entity references and camera data for slate and burnin

## Upstream

### Implemented features

- publishing workfile
- publishing `render` product type (multiple composition supported)
   - render locally or on farm (Deadline - `ayon-deadline` addon required)
- loading image/image sequences
- load background layers respecting their order (`background` product with `.json` metadata file)
- manage version of loaded containers
- dynamic setup of first workfile via Workfile Builder and placeholders (example:  
      "for first workfile always load latest version of `render` product in current context")

Requirements: This extension requires use of Javascript engine, which is
available since CC 16.0.
Please check your `File > Project Settings > Expressions > Expressions Engine`

## Setup

The After Effects integration requires two components to work: `extension` and `server`.

### Extension

Easiest way how to install AE extension is to enable `ayon+settings://aftereffects/auto_install_extension`.
This will check and automatically install latest version of extension to user's `AppData` at each start of AE.

You could also install it manually, if necessary. Follow these steps:

To install the extension manually download [Extension Manager Command Line tool (ExManCmd)](https://github.com/Adobe-CEP/Getting-Started-guides/tree/master/Package%20Distribute%20Install#option-2---exmancmd).

```
ExManCmd /install {path to addon}/api/extension.zxp
```
OR
download [Anastasiy’s Extension Manager](https://install.anastasiy.com/)

`{path to addon}` will be most likely in your AppData (on Windows, in your user data folder in Linux and MacOS.)

## Usage

The After Effects extension can be found under `Window > Extensions > AYON`. Once launched you should be presented with a panel like this:

![Ayon Panel](panel.png "Ayon Panel")

## Developing

### Extension
When developing the extension you can load it [unsigned](https://github.com/Adobe-CEP/CEP-Resources/blob/master/CEP_9.x/Documentation/CEP%209.0%20HTML%20Extension%20Cookbook.md#debugging-unsigned-extensions).

When signing the extension you can use this [guide](https://github.com/Adobe-CEP/Getting-Started-guides/tree/master/Package%20Distribute%20Install#package-distribute-install-guide).

```
ZXPSignCmd -selfSignedCert NA NA Ayon Avalon-After-Effects Ayon extension.p12
ZXPSignCmd -sign {path to addon}/api/extension {path to addon}/api/extension.zxp extension.p12 Ayon
```

!!! Always bump up `ExtensionBundleVersion` in `https://github.com/ynput/ayon-aftereffects/blob/develop/client/ayon_aftereffects/api/extension/CSXS/manifest.xml` and build `.zxp` file.
(Without it auto-install won't work.)

### Plugin Examples

Expected deployed extension location on default Windows:
`c:\Users\YOUR_USER\AppData\Roaming\Adobe\CEP\extensions\` (auto install)
OR
`C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\io.ynput.AE.panel`  (manual install)

For easier debugging of Javascript:
https://community.adobe.com/t5/download-install/adobe-extension-debuger-problem/td-p/10911704?page=1

1. Add (optional) `--enable-blink-features=ShadowDOMV0,CustomElementsV0` when starting Chrome
2. Then go to `localhost:8092`

Or use Visual Studio Code https://medium.com/adobetech/extendscript-debugger-for-visual-studio-code-public-release-a2ff6161fa01

## Resources
  - https://javascript-tools-guide.readthedocs.io/introduction/index.html
  - https://github.com/Adobe-CEP/Getting-Started-guides
  - https://github.com/Adobe-CEP/CEP-Resources
