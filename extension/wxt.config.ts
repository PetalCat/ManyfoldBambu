import { defineConfig } from "wxt";

export default defineConfig({
  modules: ["wxt-module-sveltekit"],
  hooks: {
    "build:before": () => {
      const { execSync } = require("node:child_process");
      const path = require("node:path");

      console.log("Creating host.zip...");
      const hostDir = path.resolve("..", "host");
      const publicDir = path.resolve("public");
      const zipPath = path.join(publicDir, "host.zip");

      // Ensure public dir exists
      execSync(`mkdir -p "${publicDir}"`);

      // Zip command (assumes 'zip' is installed on system, valid for Mac/Linux)
      // -j: junk paths (flatten structure)
      const cmd = `zip -j "${zipPath}" "${path.join(hostDir, "bambu_host.py")}" "${path.join(hostDir, "install_host.sh")}" "${path.join(hostDir, "install_host.bat")}"`;

      try {
        execSync(cmd);
        console.log("Successfully created host.zip");
      } catch (e: any) {
        console.error("Failed to crate host.zip:", e.message);
      }
    },
  },
  manifest: {
    name: "ManyFold2Bambu",
    icons: {
      16: "/logo.png",
      32: "/logo.png",
      48: "/logo.png",
      128: "/logo.png",
    },
    permissions: [
      "downloads",
      "nativeMessaging",
      "activeTab",
      "scripting",
      "webNavigation",
    ],
    host_permissions: ["<all_urls>"],
    web_accessible_resources: [
      {
        resources: ["icon.ico", "host.zip"],
        matches: ["<all_urls>"],
      },
    ],
  },
  webExt: {
    binaries: {
      edge: "/Users/hasenkap/Applications/exedgenoprx.sh",
    },
  },
});
