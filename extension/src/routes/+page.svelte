<script lang="ts">
  import { onMount } from "svelte";

  let bambuPath = "";
  let targetDir = "";
  let status = "Loading...";
  let isSaved = false;
  let isError = false;
  let isHostMissing = false;
  let extensionId = "";
  let hostInfo = { host_path: "", config_path: "" };
  let showDebug = false;

  const HOST_NAME = "com.manyfold.bambu";

  onMount(async () => {
    // Get Extension ID
    try {
      extensionId = chrome.runtime.id;
    } catch (e) {}

    try {
      // Fetch current config
      chrome.runtime.sendNativeMessage(
        HOST_NAME,
        { action: "get_config" },
        (response) => {
          if (chrome.runtime.lastError) {
            // If lastError is present, it usually means the host isn't there
            console.log(
              "Host missing error:",
              chrome.runtime.lastError.message,
            );
            status = chrome.runtime.lastError.message;
            isHostMissing = true;
          } else if (response && response.success) {
            bambuPath = response.config.bambu_path || "";
            targetDir = response.config.target_dir || "";
            if (response.info) {
              hostInfo = response.info;
            }
            status = "Ready";
          } else {
            status = "Host error: " + (response?.error || "Unknown");
            isError = true;
          }
        },
      );
    } catch (e: any) {
      status = "Extension error: " + e.message;
      isError = true;
    }
  });

  function saveConfig() {
    status = "Saving...";
    isSaved = false;
    isError = false;

    chrome.runtime.sendNativeMessage(
      HOST_NAME,
      {
        action: "set_config",
        config: { bambu_path: bambuPath, target_dir: targetDir },
      },
      (response) => {
        if (chrome.runtime.lastError) {
          status = "Error saving: " + chrome.runtime.lastError.message;
          isError = true;
        } else if (response && response.success) {
          status = "Saved successfully!";
          isSaved = true;
          setTimeout(() => (isSaved = false), 2000);
        } else {
          status = "Save failed: " + (response?.error || "Unknown");
          isError = true;
        }
      },
    );
  }

  function downloadHost() {
    // URL to the raw file on GitHub
    const url =
      "https://github.com/PetalCat/ManyfoldBambu/raw/main/extension/public/host.zip";
    const a = document.createElement("a");
    a.href = url;
    a.download = "manyfold-bambu-host.zip";
    a.click();
  }

  function copyCommand(cmd: string) {
    navigator.clipboard.writeText(cmd);
    const originalStatus = status;
    status = "Copied to clipboard!";
    setTimeout(
      () => (status = isHostMissing ? "Native Host not detected." : "Ready"),
      1500,
    );
  }
</script>

<main
  class="w-[340px] bg-white p-5 font-sans text-slate-900 dark:bg-slate-900 dark:text-slate-50"
>
  <div class="mb-6 flex items-center gap-3">
    <img
      src="/logo.png"
      alt="Logo"
      class="h-10 w-10 rounded-lg drop-shadow-sm"
    />
    <div>
      <h1 class="text-xl leading-tight font-bold">Bambu Helper</h1>
      <p class="text-xs text-slate-500 dark:text-slate-400">
        Manyfold Extension
      </p>
    </div>
  </div>

  {#if isHostMissing}
    <div class="space-y-4">
      <div
        class="rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs leading-relaxed text-amber-800 dark:border-amber-800 dark:bg-amber-900/20 dark:text-amber-200"
      >
        <strong>Native Host Not Found.</strong><br />
        To control Bambu Studio, you must install the helper script.
      </div>

      <div>
        <button
          on:click={downloadHost}
          class="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-slate-100 py-2 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
        >
          <svg
            class="h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            ><path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            ></path></svg
          >
          1. Download Installer
        </button>
        <p class="mt-1 text-center text-[10px] text-slate-400">
          Unzip "manyfold-bambu-host.zip" to a folder.
        </p>
      </div>

      <div>
        <p
          class="mb-1 text-xs font-semibold text-slate-600 dark:text-slate-400"
        >
          2. Run Command (Terminal/PowerShell):
        </p>

        {#if navigator.appVersion.includes("Win")}
          <!-- Windows Command -->
          <button
            class="group relative w-full rounded bg-slate-950 p-2 text-left font-mono text-[10px] break-all text-slate-300"
            on:click={() =>
              copyCommand(
                `PowerShell -Command "Expand-Archive -Force \\"$env:USERPROFILE\\Downloads\\manyfold-bambu-host.zip\\" -DestinationPath \\"$env:USERPROFILE\\bambu-host\\"; cd \\"$env:USERPROFILE\\bambu-host\\"; .\\install_host.bat ${extensionId}"`,
              )}
          >
            <span class="opacity-50">&gt;</span> PowerShell -Command
            "Expand-Archive..."
            <div
              class="absolute top-2 right-2 rounded bg-slate-700 px-1 text-[9px] text-white opacity-0 group-hover:opacity-100"
            >
              Copy
            </div>
          </button>
          <p class="mt-1 text-[9px] text-slate-400">
            Detecting Windows. Automates unzip & install from Downloads.
          </p>
        {:else}
          <!-- Mac/Linux Command -->
          <button
            class="group relative w-full rounded bg-slate-950 p-2 text-left font-mono text-[10px] break-all text-slate-300"
            on:click={() =>
              copyCommand(
                `mkdir -p ~/bambu-host && unzip -o ~/Downloads/manyfold-bambu-host.zip -d ~/bambu-host && cd ~/bambu-host && sh install_host.sh ${extensionId}`,
              )}
          >
            <span class="opacity-50">$</span> mkdir -p ~/bambu-host && unzip...
            <div
              class="absolute top-2 right-2 rounded bg-slate-700 px-1 text-[9px] text-white opacity-0 group-hover:opacity-100"
            >
              Copy
            </div>
          </button>
          <p class="mt-1 text-[9px] text-slate-400">
            Detecting Mac/Linux. Automates unzip & install from Downloads.
          </p>
        {/if}
      </div>
    </div>
  {:else}
    <!-- Settings UI -->
    <div class="mb-5">
      <label
        class="mb-2 block text-xs font-semibold tracking-wider text-slate-500 uppercase dark:text-slate-400"
        for="bambuPath"
      >
        Bambu Studio Path
      </label>
      <div class="relative">
        <input
          id="bambuPath"
          type="text"
          bind:value={bambuPath}
          placeholder="Auto-detecting..."
          class="w-full rounded-lg border border-slate-200 bg-slate-50 p-2.5 text-sm transition-all placeholder:text-slate-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 focus:outline-none dark:border-slate-700 dark:bg-slate-800"
        />
      </div>
      <p
        class="mt-2 text-[10px] leading-relaxed text-slate-500 dark:text-slate-400"
      >
        Leave empty to auto-detect. <br />
        <span class="opacity-75">Windows: use double backslashes (\\).</span>
      </p>
    </div>

    <div class="mb-5">
      <label
        class="mb-2 block text-xs font-semibold tracking-wider text-slate-500 uppercase dark:text-slate-400"
        for="targetDir"
      >
        Target Download Directory
      </label>
      <div class="relative">
        <input
          id="targetDir"
          type="text"
          bind:value={targetDir}
          placeholder="Default (Downloads folder)"
          class="w-full rounded-lg border border-slate-200 bg-slate-50 p-2.5 text-sm transition-all placeholder:text-slate-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 focus:outline-none dark:border-slate-700 dark:bg-slate-800"
        />
      </div>
      <p
        class="mt-2 text-[10px] leading-relaxed text-slate-500 dark:text-slate-400"
      >
        Where files will be moved to. <br />
        <span class="opacity-75">Leave empty to keep in Downloads.</span>
      </p>
    </div>

    <button
      on:click={saveConfig}
      class="flex w-full items-center justify-center gap-2 rounded-lg bg-green-600 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-green-500 hover:shadow active:scale-[0.98]"
    >
      {#if status === "Saving..."}
        <svg
          class="h-4 w-4 animate-spin text-white"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          ><circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          ></circle><path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path></svg
        >
        Saving...
      {:else}
        Save Settings
      {/if}
    </button>

    <div class="mt-6 border-t border-slate-100 pt-4 dark:border-slate-800">
      <div class="flex items-center justify-between">
        <button
          on:click={() => (showDebug = !showDebug)}
          class="text-xs text-slate-400 transition-colors hover:text-slate-600 dark:hover:text-slate-300"
        >
          {showDebug ? "Hide Info" : "Show Info"}
        </button>

        <button
          on:click={() => {
            if (
              confirm(
                "Are you sure you want to uninstall the host script? This will remove the integration.",
              )
            ) {
              chrome.runtime.sendNativeMessage(
                HOST_NAME,
                { action: "uninstall" },
                (response) => {
                  if (response && response.success) {
                    status = "Host uninstalled.";
                    isHostMissing = true;
                    // Clear config cache in UI
                    bambuPath = "";
                    targetDir = "";
                    hostInfo = { host_path: "", config_path: "" };
                  } else {
                    status =
                      "Uninstall failed: " + (response?.error || "Unknown");
                    isError = true;
                  }
                },
              );
            }
          }}
          class="text-xs text-red-500 underline decoration-dotted transition-colors hover:text-red-600"
        >
          Uninstall Host
        </button>
      </div>

      {#if showDebug && hostInfo.host_path}
        <div
          class="mt-3 space-y-2 rounded bg-slate-50 p-2 font-mono text-[10px] break-all text-slate-500 dark:bg-slate-800/50"
        >
          <div>
            <span class="font-bold text-slate-400 uppercase">Host Script:</span
            ><br />
            {hostInfo.host_path}
          </div>
          <div>
            <span class="font-bold text-slate-400 uppercase">Config File:</span
            ><br />
            {hostInfo.config_path}
          </div>
        </div>
      {/if}
    </div>
  {/if}

  <div
    class="mt-4 flex min-h-[1.5rem] items-center justify-center text-sm font-medium"
  >
    {#if isSaved}
      <span
        class="flex items-center gap-1.5 text-green-600 dark:text-green-400"
      >
        <svg
          class="h-4 w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          ><path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M5 13l4 4L19 7"
          ></path></svg
        >
        Saved successfully
      </span>
    {:else if isError || isHostMissing}
      <span class="text-center text-xs text-amber-600 dark:text-amber-400"
        >{status}</span
      >
    {:else}
      <span
        class="flex items-center gap-1.5 text-xs text-slate-400 dark:text-slate-500"
      >
        <div
          class={`h-2 w-2 rounded-full ${status === "Ready" ? "bg-green-500" : "bg-slate-300"}`}
        ></div>
        {status}
      </span>
    {/if}
  </div>

  <div class="mt-2 text-center">
    <a
      href="https://github.com/PetalCat/ManyfoldBambu/blob/main/PRIVACY.md"
      target="_blank"
      class="text-[10px] text-slate-300 hover:text-slate-500 dark:text-slate-600 dark:hover:text-slate-400"
    >
      Privacy Policy
    </a>
  </div>
</main>
