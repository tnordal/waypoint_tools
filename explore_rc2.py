"""Explore RC 2 folder structure to find waypoint files."""

import win32com.client


def explore_folder(folder, indent=0, max_depth=4):
    """Recursively explore folder structure."""
    if indent > max_depth:
        return
    
    try:
        items = folder.Items()
        for item in items:
            prefix = "  " * indent
            if item.IsFolder:
                print(f"{prefix}📁 {item.Name}/")
                try:
                    subfolder = item.GetFolder
                    explore_folder(subfolder, indent + 1, max_depth)
                except Exception as e:
                    print(f"{prefix}  ⚠️ Error accessing folder: {e}")
            else:
                print(f"{prefix}📄 {item.Name}")
    except Exception as e:
        print(f"{'  ' * indent}⚠️ Error listing items: {e}")


def main():
    """Find and explore RC 2 controller."""
    shell = win32com.client.Dispatch("Shell.Application")
    computer = shell.NameSpace(17)
    
    if not computer:
        print("❌ Could not access Computer namespace")
        return
    
    # Find RC 2
    items = computer.Items()
    rc2_device = None
    
    for item in items:
        if "RC" in item.Name.upper() or "DJI" in item.Name.upper():
            print(f"✅ Found device: {item.Name}")
            rc2_device = item
            break
    
    if not rc2_device:
        print("❌ RC 2 controller not found")
        return
    
    # Get device folder
    device_folder = rc2_device.GetFolder
    if not device_folder:
        print("❌ Could not access device folder")
        return
    
    print("\n📂 Exploring RC 2 folder structure...\n")
    explore_folder(device_folder, indent=0, max_depth=6)


if __name__ == "__main__":
    main()
