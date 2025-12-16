export default defineBackground(() => {
  // Listen for messages from content script
  browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "DOWNLOAD_AND_OPEN") {
      handleDownload(message.url)
        .then(() => sendResponse({ success: true }))
        .catch((err) =>
          sendResponse({ success: false, error: err.message || String(err) }),
        );
      return true; // Keep channel open for async response
    }
  });

  // Listen for navigation events (history state updates for SPAs)
  browser.webNavigation.onHistoryStateUpdated.addListener((details) => {
    // We only care about main frame (frameId 0)
    if (details.frameId === 0) {
      console.log("[Background] Navigation detected:", details.url);
      browser.tabs.sendMessage(details.tabId, {
        type: "SCAN_DROPDOWNS",
        url: details.url,
      });
    }
  });

  async function handleDownload(fileUrl: string) {
    try {
      // start download
      const dlId = await browser.downloads.download({ url: fileUrl });

      // wait for download complete
      return new Promise<void>((resolve, reject) => {
        const listener = (delta: any) => {
          if (
            delta.id === dlId &&
            delta.state &&
            delta.state.current === "complete"
          ) {
            browser.downloads.onChanged.removeListener(listener);

            // find the downloaded path
            browser.downloads.search({ id: dlId }).then((results) => {
              if (!results || results.length === 0) {
                reject(new Error("Download failed (no results)"));
                return;
              }
              const filename = results[0].filename;

              // We need to resolve the absolute path if possible, or send what we have.
              // Chrome usually returns a path relative to Downloads or absolute.
              // Native host will need to handle resolution if it's relative.

              // Send explicit message to Native Host
              // @ts-expect-error - onMessageExternal/sendNativeMessage might need types
              browser.runtime
                .sendNativeMessage("com.manyfold.bambu", {
                  action: "open_file",
                  path: filename,
                })
                .then(
                  (response: any) => {
                    if (response && response.logs) {
                      console.log(
                        "[Native Host Logs]:\n" + response.logs.join("\n"),
                      );
                    }

                    if (response && response.success) {
                      resolve();
                    } else {
                      reject(new Error(response?.error || "Native host error"));
                    }
                  },
                  (err: any) => {
                    reject(new Error("Native host failed: " + err.message));
                  },
                );
            });
          } else if (
            delta.id === dlId &&
            delta.state &&
            delta.state.current === "interrupted"
          ) {
            browser.downloads.onChanged.removeListener(listener);
            reject(new Error("Download interrupted"));
          }
        };
        browser.downloads.onChanged.addListener(listener);
      });
    } catch (e) {
      console.error("Download failed:", e);
      throw e;
    }
  }
});
