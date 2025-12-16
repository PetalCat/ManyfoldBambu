export default defineContentScript({
  matches: ["<all_urls>"],
  main() {
    let debounceTimer: ReturnType<typeof setTimeout> | null = null;
    let lastUrl = location.href;

    function addBambuItem(dropdown: Element) {
      if (dropdown.querySelector(".bambu-item")) return;

      const bambuLi = document.createElement("li");
      bambuLi.style.cssText =
        "border-bottom: 1px solid #eee; margin-bottom: 4px; padding-bottom: 4px;"; // minimal styling
      bambuLi.role = "presentation";

      const bambuA = document.createElement("a");
      bambuA.className = "dropdown-item bambu-item";
      bambuA.role = "menuitem";
      bambuA.style.cursor = "pointer";
      bambuA.style.display = "flex";
      bambuA.style.alignItems = "center";
      bambuA.style.gap = "8px";

      // Icon and Text
      bambuA.innerHTML = `
        <img class="slicer-icon" alt="Open in Bambu" src="${browser.runtime.getURL("/icon.ico")}" style="width: 20px; height: 20px;">
        <span>Open in Bambu Studio</span>
      `;

      bambuA.onclick = async (e) => {
        e.preventDefault();
        e.stopPropagation();

        // find the existing slicer link url (last one clicked, or just first download link in the same menu)
        // User logic: picks first link with download attribute.
        const originalLinks = dropdown.querySelectorAll("a[download]");
        if (!originalLinks || originalLinks.length === 0) {
          alert("No model link found in this menu.");
          return;
        }

        // pick the first one’s href — the remote model URL
        let fileUrl = (originalLinks[0] as HTMLAnchorElement).href;

        // If it's a known slicer protocol, extract the real file URL
        const urlObj = new URL(fileUrl);
        if (
          [
            "cura:",
            "orcaslicer:",
            "elegooslicer:",
            "prusaslicer:",
            "superslicer:",
            "lycheeslicer:",
          ].includes(urlObj.protocol)
        ) {
          const params = new URLSearchParams(urlObj.search);
          const extracted = params.get("file");
          if (extracted) {
            // Sometimes the file param is just a URL, sometimes it might be encoded again?
            // Usually it's just the value.
            fileUrl = extracted;
            // Lychee slicer uses lycheeslicer://open/URL, so searching params might fail if it's path-based
            // Snippet: lycheeslicer://open/https%3A%2F%2F...
            // The URL constructor might parse "open/..." as path "open/..."?
            // Let's handle generic extraction if search param fails or if it's lychee
          } else if (fileUrl.includes("://open/http")) {
            // Handle "protocol://open/https://..." style
            // Find the http part
            const match =
              fileUrl.match(/https?%3A%2F%2F.+$/) ||
              fileUrl.match(/https?:\/\/.+$/);
            if (match) {
              fileUrl = decodeURIComponent(match[0]);
            }
          }

          // Fallback: checks for 'file=' again in a different way if URLSearchParams failed for some reason
          // (e.g. if the search string wasn't parsed correctly due to the custom protocol)
          if (!fileUrl.startsWith("http")) {
            const fileMatch = fileUrl.match(/[?&]file=([^&]+)/);
            if (fileMatch) {
              fileUrl = decodeURIComponent(fileMatch[1]);
            }
          }
        }

        try {
          const response = await browser.runtime.sendMessage({
            type: "DOWNLOAD_AND_OPEN",
            url: fileUrl,
          });

          if (!response || !response.success) {
            throw new Error(response?.error || "Unknown error");
          }
        } catch (e: any) {
          console.error("Download failed:", e);
          alert("Download failed: " + (e.message || e));
        }
      };

      bambuLi.appendChild(bambuA);

      // insert item at top of the dropdown (before existing slicers)
      dropdown.insertBefore(bambuLi, dropdown.firstChild);
    }

    function scanForDropdowns() {
      // Scan all dropdowns, not just visible ones, to be more robust
      const menus = document.querySelectorAll("ul.dropdown-menu");
      // console.log("[Bambu] Scanning menus. Found:", menus.length);

      menus.forEach((dropdown) => {
        // Check for any supported slicer protocol
        const slicerProtocols = [
          "cura://",
          "orcaslicer://",
          "elegooslicer://",
          "prusaslicer://",
          "superslicer://",
          "lycheeslicer://",
          "bambu-connect://",
        ];

        // Optimized check: only check if we haven't already injected
        if (dropdown.querySelector(".bambu-item")) return;

        const hasSlicer = Array.from(dropdown.querySelectorAll("a")).some((a) =>
          slicerProtocols.some((p) => a.href.startsWith(p)),
        );

        if (hasSlicer) {
          console.log("[Bambu] Found slicer menu:", dropdown);
          addBambuItem(dropdown);
        }
      });
    }

    function handleMutation(mutations: MutationRecord[]) {
      if (location.href !== lastUrl) {
        console.log("[Bambu] URL changed (mutation detected):", location.href);
        lastUrl = location.href;
        scanForDropdowns();
        return;
      }

      // Debounce the scanning
      if (debounceTimer) clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        scanForDropdowns();
      }, 500);
    }

    // --- Navigation Handling ---

    // 1. Listen for messages from background script (webNavigation)
    browser.runtime.onMessage.addListener((message) => {
      if (message.type === "SCAN_DROPDOWNS") {
        console.log(
          "[Bambu] Navigation detected (via background):",
          message.url,
        );
        // Updating lastUrl prevents handleMutation from double-scanning if it triggers too
        lastUrl = message.url;
        scanForDropdowns();
      }
    });

    // 2. Keep MutationObserver for backup (e.g. dynamic loading without URL change)
    // The handleMutation function already handles debouncing.

    // --- Initialization ---

    // run initially
    scanForDropdowns();

    // observe DOM changes (pages often update menus dynamically)
    const observer = new MutationObserver(handleMutation);

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: false, // only care about structure changes generally
    });
  },
});
