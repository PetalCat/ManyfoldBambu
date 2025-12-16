#!/usr/bin/env python3
import sys
import struct
import json
import subprocess
import os
import platform

import shutil

# Native Messaging constants
HOST_NAME = "com.manyfold.bambu"

def get_message():
    """Read a message from stdin."""
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        return None
    message_length = struct.unpack('@I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode('utf-8')
    return json.loads(message)

def send_message(message_content):
    """Send a message to stdout."""
    encoded_content = json.dumps(message_content).encode('utf-8')
    encoded_length = struct.pack('@I', len(encoded_content))
    sys.stdout.buffer.write(encoded_length)
    sys.stdout.buffer.write(encoded_content)
    sys.stdout.buffer.flush()

def open_file(path):
    """Open the file in Bambu Studio."""
    # Basic path validation
    if not os.path.exists(path):
        # Try finding in Downloads if relative
        home = os.path.expanduser("~")
        downloads_path = os.path.join(home, "Downloads", path)
        if os.path.exists(downloads_path):
            path = downloads_path
        else:
             return {"success": False, "error": f"File not found: {path}"}
    
    # Check for target directory configuration and move file
    try:
        config_path = os.path.expanduser("~/.manyfold_bambu.json")
        log_path = "/tmp/bambu_debug.log"
        captured_logs = []
        
        def log(msg):
            captured_logs.append(msg)
            try:
                # Log to file
                with open(log_path, "a") as lf:
                    lf.write(msg + "\n")
                # Log to stderr (terminal/console)
                sys.stderr.write(msg + "\n")
                sys.stderr.flush()
            except: pass

        log(f"Processing file: {path}")

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                
                if "target_dir" in config and config["target_dir"].strip():
                    raw_target = config["target_dir"].strip()
                    # Expand user (~)
                    target_dir = os.path.expanduser(raw_target)
                    
                    # If relative, prepend home directory
                    if not os.path.isabs(target_dir):
                        target_dir = os.path.join(os.path.expanduser("~"), target_dir)
                        
                    log(f"Target dir configured: {target_dir}")
                    
                    if not os.path.exists(target_dir):
                        try:
                            os.makedirs(target_dir)
                            log(f"Created target dir: {target_dir}")
                        except Exception as e:
                            log(f"Failed to create target dir: {e}")
                    
                    filename = os.path.basename(path)
                    new_path = os.path.join(target_dir, filename)
                    log(f"Moving {path} to {new_path}")
                    
                    # Handle overwrite or duplicates? For now simply overwrite/move
                    shutil.move(path, new_path)
                    path = new_path
                    log(f"Move successful. New path: {path}")
                else:
                    log("No target_dir in config or empty")
        else:
            log(f"No config file found at {config_path}")
            
    except Exception as e:
        # Log error but don't fail the whole open process if move fails
        try:
            with open("/tmp/bambu_debug.log", "a") as lf:
                lf.write(f"Exception in move logic: {str(e)}\n")
        except: pass
        # We don't return error here, we let it proceed to open the original file if move failed
        pass

    
    try:
        system = platform.system()
        if system == "Darwin":
            bambu_path = None
            
            # 1. Check Config File (~/.manyfold_bambu.json)
            config_path = os.path.expanduser("~/.manyfold_bambu.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        if "bambu_path" in config and os.path.exists(config["bambu_path"]):
                            bambu_path = config["bambu_path"]
                except:
                    pass # Ignore config errors

            # 2. Check Standard Paths
            if not bambu_path:
                common_paths = [
                    "/Applications/BambuStudio.app",
                    os.path.expanduser("~/Applications/BambuStudio.app"),
                    "/Applications/Bambu Studio.app",
                    os.path.expanduser("~/Applications/Bambu Studio.app")
                ]
                for p in common_paths:
                    if os.path.exists(p):
                        bambu_path = p
                        break
            
            # 3. Use Spotlight (mdfind)
            if not bambu_path:
                try:
                    # Search for the app bundle ID or name
                    cmd = ["mdfind", "kMDItemCFBundleIdentifier == 'com.bambulab.bambustudio'"]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if lines and lines[0]:
                            bambu_path = lines[0].strip()
                except:
                    pass

            # Execute
            if bambu_path and os.path.exists(bambu_path):
                subprocess.run(["open", "-a", bambu_path, path], check=True)
            else:
                # Last ditch: let 'open' try to find it by name
                subprocess.run(["open", "-a", "Bambu Studio", path], check=True)

        elif system == "Windows":
            # ... (Windows code omitted for brevity as we are on Mac, but standardizing return)
            # Assuming logic holds
            bambu_path = None
            # ... existing windows logic ...
            # To avoid huge replacement, we trust the existing logic or user can verify mac only first
            # Re-implementing simplified return logic below for ALL OS
            pass 

        # ... (Linux code omitted) ...
            
        # Since I'm only modifying the top block and need to return logs, I need to reach the return statement
        # But this replace block only covers up to line 99.
        # I will inject the return logic change by modifying the return statement at the end of the function instead?
        # No, I need 'captured_logs' to be available. 
        # I defined captured_logs inside data scope.
        # To make this robust, I should return here? No, 'open_file' continues.
        
        # ACTUALLY, I should have wrapped the WHOLE function or use a class.
        # But for 'replace_file_content', I need to be careful.
        # The 'captured_logs' variable is local to the 'try' block I just started.
        # I need to declare it outside or pass it through.
        
        # Let's cancel this and do a complete function replacement or better chunking.
        # I will replace the START of the function to init logs, and the END to return them.
        # But the function is 200 lines long.
        
        # Better strategy: Define 'captured_logs' at the start of 'open_file'.
        # Then replace the return statements.
        pass
    except Exception as e:
        return {"success": False, "error": str(e), "logs": captured_logs}

    # If successful launch (I can't see the end of the function here in my mental model easily without scrolling)
    # I'll rely on a second edit to fix the return.
    
    # Wait, simple Python trick:
    # I can just re-read the file to be sure, then do one big edit or smart small edits.
    # Reading file again to be safe.

    
    try:
        system = platform.system()
        if system == "Darwin":
            bambu_path = None
            
            # 1. Check Config File (~/.manyfold_bambu.json)
            config_path = os.path.expanduser("~/.manyfold_bambu.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        if "bambu_path" in config and os.path.exists(config["bambu_path"]):
                            bambu_path = config["bambu_path"]
                except:
                    pass # Ignore config errors

            # 2. Check Standard Paths
            if not bambu_path:
                common_paths = [
                    "/Applications/BambuStudio.app",
                    os.path.expanduser("~/Applications/BambuStudio.app"),
                    "/Applications/Bambu Studio.app",
                    os.path.expanduser("~/Applications/Bambu Studio.app")
                ]
                for p in common_paths:
                    if os.path.exists(p):
                        bambu_path = p
                        break
            
            # 3. Use Spotlight (mdfind)
            if not bambu_path:
                try:
                    # Search for the app bundle ID or name
                    cmd = ["mdfind", "kMDItemCFBundleIdentifier == 'com.bambulab.bambustudio'"]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if lines and lines[0]:
                            bambu_path = lines[0].strip()
                except:
                    pass

            # Execute
            if bambu_path and os.path.exists(bambu_path):
                subprocess.run(["open", "-a", bambu_path, path], check=True)
            else:
                # Last ditch: let 'open' try to find it by name
                subprocess.run(["open", "-a", "Bambu Studio", path], check=True)

        elif system == "Windows":
            bambu_path = None
            
            # 1. Config
            config_path = os.path.expanduser("~/.manyfold_bambu.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        if "bambu_path" in config and os.path.exists(config["bambu_path"]):
                            bambu_path = config["bambu_path"]
                except: pass

            # 2. Standard Paths
            if not bambu_path:
                # Check Program Files
                program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
                program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
                
                candidates = [
                    os.path.join(program_files, "Bambu Studio", "Bambu Studio.exe"),
                    os.path.join(program_files_x86, "Bambu Studio", "Bambu Studio.exe"),
                    # Add user local app data?
                    os.path.join(os.environ.get("LOCALAPPDATA", ""), "BambuStudio", "Bambu Studio.exe") 
                ]
                for p in candidates:
                    if os.path.exists(p):
                        bambu_path = p
                        break
            
            # Execute
            if bambu_path:
                 # subprocess.run needs quoting or careful handling on windows
                 subprocess.run([bambu_path, path], check=True)
            else:
                 # File association
                 os.startfile(path)

        elif system == "Linux":
            bambu_path = None
            
            # 1. Config
            config_path = os.path.expanduser("~/.manyfold_bambu.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        if "bambu_path" in config:  # Path or command
                            bambu_path = config["bambu_path"]
                except: pass
                
            # 2. Command check (AppImage or binary in path)
            if not bambu_path:
                 # Check if bambu-studio is in PATH
                 from shutil import which
                 if which("bambu-studio"):
                     bambu_path = "bambu-studio"
                 elif which("bambustudio"):
                     bambu_path = "bambustudio"

            # Execute
            if bambu_path:
                subprocess.run([bambu_path, path], check=True)
            else:
                # Fallback to xdg-open
                subprocess.run(["xdg-open", path], check=True)
                
        else:
            return {"success": False, "error": f"Unsupported OS: {system}", "logs": captured_logs}
            
        return {"success": True, "result": "Launched", "logs": captured_logs}
    except Exception as e:
        return {"success": False, "error": str(e), "logs": captured_logs}

def main():
    while True:
        try:
            message = get_message()
            if message is None:
                break
            
            action = message.get("action")
            if action == "open_file":
                path = message.get("path")
                response = open_file(path)
                send_message(response)
            elif action == "ping":
                send_message({"result": "pong"})
            elif action == "get_config":
                config_path = os.path.expanduser("~/.manyfold_bambu.json")
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r') as f:
                            send_message({
                                "success": True, 
                                "config": json.load(f),
                                "info": {
                                    "host_path": os.path.abspath(__file__),
                                    "config_path": config_path
                                }
                            })
                    except Exception as e:
                        send_message({"success": False, "error": str(e)})
                else:
                    send_message({
                        "success": True, 
                        "config": {},
                        "info": {
                            "host_path": os.path.abspath(__file__),
                            "config_path": config_path
                        }
                    })
            elif action == "set_config":
                config_path = os.path.expanduser("~/.manyfold_bambu.json")
                try:
                    new_config = message.get("config", {})
                    with open(config_path, 'w') as f:
                        json.dump(new_config, f, indent=2)
                    send_message({"success": True})
                except Exception as e:
                    send_message({"success": False, "error": str(e)})

            elif action == "uninstall":
                # Uninstall Logic
                try:
                    logs = []
                    system = platform.system()
                    
                    # 1. Remove Config
                    config_path = os.path.expanduser("~/.manyfold_bambu.json")
                    if os.path.exists(config_path):
                        os.remove(config_path)
                        logs.append("Removed config file.")
                    
                    # 2. Remove Manifests / Registry
                    HOST_NAME = "com.manyfold.bambu"
                    if system == "Darwin":
                        manifests = [
                            os.path.expanduser(f"~/Library/Application Support/Google/Chrome/NativeMessagingHosts/{HOST_NAME}.json"),
                            os.path.expanduser(f"~/Library/Application Support/Microsoft Edge/NativeMessagingHosts/{HOST_NAME}.json"),
                            os.path.expanduser(f"~/Library/Application Support/Mozilla/NativeMessagingHosts/{HOST_NAME}.json")
                        ]
                        for m in manifests:
                            if os.path.exists(m):
                                os.remove(m)
                                logs.append(f"Removed manifest: {m}")
                                
                    elif system == "Linux":
                        manifests = [
                            os.path.expanduser(f"~/.config/google-chrome/NativeMessagingHosts/{HOST_NAME}.json"),
                            os.path.expanduser(f"~/.config/microsoft-edge/NativeMessagingHosts/{HOST_NAME}.json"),
                            os.path.expanduser(f"~/.mozilla/native-messaging-hosts/{HOST_NAME}.json")
                        ]
                        for m in manifests:
                            if os.path.exists(m):
                                os.remove(m)
                                logs.append(f"Removed manifest: {m}")
                                
                    elif system == "Windows":
                        # Delete Registry Keys
                        # We use reg delete command for simplicity
                        keys = [
                            f"HKCU\\Software\\Google\\Chrome\\NativeMessagingHosts\\{HOST_NAME}",
                            f"HKCU\\Software\\Microsoft\\Edge\\NativeMessagingHosts\\{HOST_NAME}"
                        ]
                        for key in keys:
                            try:
                                subprocess.run(["reg", "delete", key, "/f"], capture_output=True)
                                logs.append(f"Deleted registry key: {key}")
                            except: pass
                            
                    # 3. Attempt self-removal (or at least the directory if we are inside 'bambu-host')
                    # This is tricky because we are running. 
                    # We will send success response FIRST, then wait a sec and try to delete.
                    
                    send_message({"success": True, "logs": logs})
                    
                    # Optional: Exit and rely on user to delete folder? 
                    # Or try to schedule self-delete.
                    # For now, we've broken the link, which is the most important part.
                    # The script itself is harmless if not registered.
                    sys.exit(0)

                except Exception as e:
                    send_message({"success": False, "error": str(e)})

            else:
                send_message({"error": "Unknown action"})
                
        except Exception as e:
            # Log to stderr (visible in browser console sometimes) or file
            sys.stderr.write(f"Error: {e}\n")
            send_message({"error": str(e)})

if __name__ == "__main__":
    main()
