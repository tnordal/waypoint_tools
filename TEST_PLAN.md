# DJI Waypoint Tools - Test Plan

**Version:** 1.0.0  
**Date:** 2026-03-07  
**Tester:** _________________________  
**Test Environment:** Windows _____ (10/11)

---

## 1. Installation & Startup Tests

### 1.1 First Launch
- [ ] **Test:** Run `DJI Waypoint Tools.exe` for the first time
- [ ] **Expected:** Application launches without errors
- [ ] **Expected:** Database folder created at `~/.waypoint_tools/data/`
- [ ] **Expected:** Main window appears with empty mission list
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 1.2 Single Instance Check
- [ ] **Test:** Launch the application twice simultaneously
- [ ] **Expected:** Second instance shows "Another instance is already running"
- [ ] **Expected:** Second instance closes automatically
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 1.3 Window State Persistence
- [ ] **Test:** Resize/move window, close app, reopen
- [ ] **Expected:** Window opens at same size and position
- [ ] **Test:** Adjust splitter between mission list and preview
- [ ] **Expected:** Splitter position is remembered
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

---

## 2. Mission Import Tests

### 2.1 Import from Folder (Parent Folder)
- [ ] **Test:** Click "Import Folder", select `test_data` folder
- [ ] **Expected:** Shows "Updated 1 existing mission(s)" or "Imported 1 new mission(s)"
- [ ] **Expected:** Mission appears in list with UUID and waypoint count
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 2.2 Import from Folder (Mission Folder Directly)
- [ ] **Test:** Click "Import Folder", select UUID folder inside `test_data`
- [ ] **Expected:** Successfully imports the single mission
- [ ] **Expected:** Shows appropriate message (new or updated)
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 2.3 Import Empty Folder
- [ ] **Test:** Click "Import Folder", select a folder with no missions
- [ ] **Expected:** Shows "No missions found in the selected folder"
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 2.4 Import Duplicate Mission
- [ ] **Test:** Import the same mission twice
- [ ] **Expected:** First time: "Imported 1 new mission(s)"
- [ ] **Expected:** Second time: "Updated 1 existing mission(s)"
- [ ] **Expected:** No duplicate entries in list
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

---

## 3. Mission List & Search Tests

### 3.1 Mission Display
- [ ] **Test:** Verify mission list shows imported missions
- [ ] **Expected:** Shows UUID (truncated), waypoint count, date
- [ ] **Expected:** Format: "2B12AF14... | 12 pts | 2026-03-07"
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 3.2 Search Functionality
- [ ] **Test:** Type partial UUID in search box
- [ ] **Expected:** List filters to matching missions
- [ ] **Test:** Clear search box
- [ ] **Expected:** All missions reappear
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 3.3 Tag Filter (After Adding Tags)
- [ ] **Test:** Add tags to a mission, use tag filter dropdown
- [ ] **Expected:** "All" shows all missions
- [ ] **Expected:** Selecting a tag shows only missions with that tag
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 3.4 Mission Selection
- [ ] **Test:** Click on a mission in the list
- [ ] **Expected:** Preview panel updates with mission details
- [ ] **Expected:** Selected mission is highlighted
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

---

## 4. Mission Preview Tests

### 4.1 Mission Summary Display
- [ ] **Test:** Select a mission, verify preview panel shows:
  - [ ] Mission name/UUID
  - [ ] Waypoint count
  - [ ] Total distance (meters)
  - [ ] Estimated flight time
  - [ ] Altitude range (min-max)
  - [ ] Flight speed
  - [ ] Center coordinates
  - [ ] Finish action
  - [ ] Drone type
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 4.2 Waypoints Table
- [ ] **Test:** Verify waypoints table displays correctly
- [ ] **Expected:** Columns: #, Latitude, Longitude, Altitude, Speed
- [ ] **Expected:** All waypoints listed
- [ ] **Expected:** Table is scrollable for long lists
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 4.3 Thumbnail Strip
- [ ] **Test:** Verify thumbnail strip shows up to 5 thumbnails
- [ ] **Expected:** Images load correctly (180x135 or scaled)
- [ ] **Expected:** Strip is horizontally scrollable
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 4.4 Thumbnail Grid Viewer
- [ ] **Test:** Click "View All (X thumbnails)" button
- [ ] **Expected:** Dialog opens with all thumbnails in grid
- [ ] **Expected:** Grid is scrollable
- [ ] **Expected:** Images display at 200x200
- [ ] **Test:** Close dialog
- [ ] **Expected:** Returns to preview panel
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

---

## 5. Edit Mission Tests

### 5.1 Open Edit Dialog
- [ ] **Test:** Select mission, click "Edit" button in preview
- [ ] **Expected:** Edit dialog opens with current values pre-filled
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 5.2 Edit Friendly Name
- [ ] **Test:** Enter a friendly name (e.g., "Test Flight 1")
- [ ] **Test:** Click OK
- [ ] **Expected:** Mission list updates with friendly name
- [ ] **Expected:** Preview panel header shows friendly name
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 5.3 Edit Location
- [ ] **Test:** Enter location (e.g., "Central Park, NYC")
- [ ] **Test:** Click OK
- [ ] **Expected:** Location appears in preview panel
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 5.4 Edit Notes
- [ ] **Test:** Enter multi-line notes
- [ ] **Test:** Click OK
- [ ] **Expected:** Notes section appears in preview with full text
- [ ] **Expected:** Text wraps correctly
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 5.5 Add Tags
- [ ] **Test:** Type a tag, press Enter
- [ ] **Test:** Add multiple tags (e.g., "aerial", "park", "test")
- [ ] **Test:** Click OK
- [ ] **Expected:** Tags appear in preview panel
- [ ] **Expected:** Tags appear in tag filter dropdown
- [ ] **Expected:** Mission list shows tag count
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 5.6 Remove Tags
- [ ] **Test:** Select a tag chip, press Delete
- [ ] **Test:** Click OK
- [ ] **Expected:** Tag is removed from mission
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 5.7 Cancel Edit
- [ ] **Test:** Make changes but click Cancel
- [ ] **Expected:** Changes are not saved
- [ ] **Expected:** Preview shows original values
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 5.8 Data Persistence
- [ ] **Test:** Edit mission, close app, reopen
- [ ] **Expected:** Edits are preserved
- [ ] **Expected:** Database file updated at `~/.waypoint_tools/data/missions.json`
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

---

## 6. Settings Tests

### 6.1 Open Settings Dialog
- [ ] **Test:** Click "Settings" button
- [ ] **Expected:** Settings dialog opens
- [ ] **Expected:** Shows current theme and backup folder
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 6.2 Theme Switching (Light to Dark)
- [ ] **Test:** Select "Dark" theme
- [ ] **Expected:** Live preview shows dark theme immediately
- [ ] **Test:** Click OK
- [ ] **Expected:** Theme persists after dialog closes
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 6.3 Theme Switching (Dark to Light)
- [ ] **Test:** Select "Light" theme
- [ ] **Expected:** Live preview shows light theme immediately
- [ ] **Test:** Click OK
- [ ] **Expected:** Theme persists after dialog closes
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 6.4 Theme Persistence
- [ ] **Test:** Set theme, close app, reopen
- [ ] **Expected:** Selected theme is remembered
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 6.5 Cancel Theme Change
- [ ] **Test:** Change theme, click Cancel
- [ ] **Expected:** Theme reverts to previous setting
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 6.6 Set Backup Folder
- [ ] **Test:** Click "Browse", select a folder
- [ ] **Expected:** Selected path appears in text field
- [ ] **Test:** Click OK
- [ ] **Expected:** Backup folder setting saved
- [ ] **Expected:** Status bar shows new backup location
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

---

## 7. RC 2 Controller Tests

### 7.1 No Controller Connected
- [ ] **Test:** Check toolbar status with no RC 2 connected
- [ ] **Expected:** Shows "RC 2: Not Connected"
- [ ] **Expected:** "Import from RC 2" button is disabled
- [ ] **Expected:** "Export to RC 2" button is disabled
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 7.2 Controller Connection Detection
- [ ] **Test:** Connect RC 2 via USB while app is running
- [ ] **Expected:** Within ~3 seconds, status changes to "RC 2: Connected (device name)"
- [ ] **Expected:** Status text turns green
- [ ] **Expected:** Import/Export buttons become enabled
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 7.3 Controller Disconnection Detection
- [ ] **Test:** Disconnect RC 2 while app is running
- [ ] **Expected:** Within ~3 seconds, status changes to "RC 2: Not Connected"
- [ ] **Expected:** Status text returns to normal color
- [ ] **Expected:** Import/Export buttons become disabled
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 7.4 Import from RC 2 Dialog
- [ ] **Test:** With RC 2 connected, click "Import from RC 2"
- [ ] **Expected:** Dialog opens showing missions on controller
- [ ] **Expected:** Shows count: "Found X mission(s) on controller"
- [ ] **Expected:** Lists missions with checkboxes
- [ ] **Expected:** Shows "(already imported)" for existing missions
- [ ] **Expected:** Shows "(new)" for new missions
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 7.5 Import Single Mission from RC 2
- [ ] **Test:** Check one mission, click OK
- [ ] **Expected:** Progress dialog appears
- [ ] **Expected:** Mission copies from controller to PC
- [ ] **Expected:** Success message: "Successfully imported 1 mission(s)"
- [ ] **Expected:** Mission appears in database
- [ ] **Expected:** Mission files in temp folder are cleaned up
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 7.6 Import Multiple Missions from RC 2
- [ ] **Test:** Check "Select All", click OK
- [ ] **Expected:** Progress dialog shows each mission being imported
- [ ] **Expected:** Success message shows total imported
- [ ] **Expected:** All missions appear in list
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 7.7 Cancel Import
- [ ] **Test:** Start import, click Cancel during progress
- [ ] **Expected:** Import stops
- [ ] **Expected:** Partial imports are handled gracefully
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 7.8 Import with No Selection
- [ ] **Test:** Open import dialog, click OK without selecting missions
- [ ] **Expected:** Warning: "Please select at least one mission to import"
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 7.9 Export to RC 2 Dialog
- [ ] **Test:** With RC 2 connected, click "Export to RC 2"
- [ ] **Expected:** Dialog opens showing missions in database
- [ ] **Expected:** Shows count: "X mission(s) available to export"
- [ ] **Expected:** Lists missions with checkboxes
- [ ] **Expected:** Shows "(already on controller)" for existing missions
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 7.10 Export Single Mission to RC 2
- [ ] **Test:** Check one mission, click OK
- [ ] **Expected:** Confirmation dialog: "Export 1 mission(s) to RC 2 controller?"
- [ ] **Test:** Click Yes
- [ ] **Expected:** Progress dialog appears
- [ ] **Expected:** Mission copies from PC to controller
- [ ] **Expected:** Success message: "Successfully exported 1 mission(s)"
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 7.11 Export Multiple Missions to RC 2
- [ ] **Test:** Check "Select All", click OK, confirm
- [ ] **Expected:** Progress dialog shows each mission being exported
- [ ] **Expected:** Success message shows total exported
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 7.12 Cancel Export
- [ ] **Test:** Start export, click Cancel during progress
- [ ] **Expected:** Export stops
- [ ] **Expected:** Partial exports are handled gracefully
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 7.13 Export with No Selection
- [ ] **Test:** Open export dialog, click OK without selecting missions
- [ ] **Expected:** Warning: "Please select at least one mission to export"
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

---

## 8. Refresh Tests

### 8.1 Manual Refresh
- [ ] **Test:** Click "Refresh" button
- [ ] **Expected:** Mission list reloads from database
- [ ] **Expected:** Preview panel updates if mission was selected
- [ ] **Expected:** Status bar updates mission count
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 8.2 Auto-Refresh After Import
- [ ] **Test:** Import missions from folder or controller
- [ ] **Expected:** Mission list automatically refreshes
- [ ] **Expected:** New missions appear immediately
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

---

## 9. UI/UX Tests

### 9.1 Empty State
- [ ] **Test:** Start with no missions in database
- [ ] **Expected:** Preview panel shows "Select a mission to view details"
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 9.2 Scrolling
- [ ] **Test:** Import many missions (15+), verify scrolling
- [ ] **Expected:** Mission list scrolls smoothly
- [ ] **Expected:** Preview panel scrolls smoothly
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 9.3 Window Resize
- [ ] **Test:** Resize window to very small size
- [ ] **Expected:** UI elements adjust appropriately
- [ ] **Expected:** No overlapping or hidden critical elements
- [ ] **Test:** Maximize window
- [ ] **Expected:** Content expands to fill space
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 9.4 Splitter Behavior
- [ ] **Test:** Drag splitter to extreme left
- [ ] **Expected:** Mission list doesn't disappear completely
- [ ] **Test:** Drag splitter to extreme right
- [ ] **Expected:** Preview panel doesn't disappear completely
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

---

## 10. Error Handling Tests

### 10.1 Invalid KMZ File
- [ ] **Test:** Try to import folder with corrupt .kmz file
- [ ] **Expected:** Error logged, mission skipped
- [ ] **Expected:** Import continues for valid missions
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 10.2 Database Corruption
- [ ] **Test:** Corrupt `missions.json` file manually
- [ ] **Test:** Restart application
- [ ] **Expected:** New database created
- [ ] **Expected:** Warning logged but app doesn't crash
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 10.3 Missing Thumbnails
- [ ] **Test:** Import mission with missing thumbnail files
- [ ] **Expected:** Preview shows "Not found" for missing thumbnails
- [ ] **Expected:** App doesn't crash
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 10.4 Disk Full (Simulated)
- [ ] **Test:** Fill disk to capacity, try to import
- [ ] **Expected:** Graceful error message
- [ ] **Expected:** App doesn't crash
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

---

## 11. Performance Tests

### 11.1 Large Mission Import
- [ ] **Test:** Import folder with 50+ missions
- [ ] **Expected:** Import completes within reasonable time (< 2 min)
- [ ] **Expected:** UI remains responsive
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 11.2 Search Performance
- [ ] **Test:** With 50+ missions, use search
- [ ] **Expected:** Results filter immediately (< 100ms)
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 11.3 Preview Load Time
- [ ] **Test:** Select different missions rapidly
- [ ] **Expected:** Preview updates quickly (< 500ms)
- [ ] **Expected:** Thumbnails load progressively if needed
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 11.4 Memory Usage
- [ ] **Test:** Run app for extended period (30+ minutes)
- [ ] **Expected:** Memory usage stable (< 200MB)
- [ ] **Expected:** No memory leaks observed
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

---

## 12. Edge Cases

### 12.1 Mission with No Waypoints
- [ ] **Test:** Import mission with 0 waypoints (if possible)
- [ ] **Expected:** Handles gracefully, shows 0 waypoints
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 12.2 Mission with Very Long Name
- [ ] **Test:** Edit mission, enter 200+ character name
- [ ] **Expected:** Name is saved
- [ ] **Expected:** UI displays with truncation/wrapping
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 12.3 Special Characters in Name
- [ ] **Test:** Use special characters in name: `!@#$%^&*()`
- [ ] **Expected:** Characters are saved correctly
- [ ] **Expected:** Display correctly in UI
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 12.4 Unicode Characters
- [ ] **Test:** Use emoji and non-English characters: `测试 🚁 Тест`
- [ ] **Expected:** Characters save and display correctly
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

---

## 13. Integration Tests

### 13.1 End-to-End: Import → Edit → Export
- [ ] **Test:** Complete workflow:
  1. Import mission from folder
  2. Edit metadata (name, tags, notes)
  3. Export to RC 2 (if available)
- [ ] **Expected:** All steps complete successfully
- [ ] **Expected:** Metadata is preserved
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 13.2 End-to-End: RC 2 Import → Edit → PC Backup
- [ ] **Test:** Complete workflow:
  1. Import mission from RC 2
  2. Add friendly name and tags
  3. Verify in database
  4. Close and reopen app
  5. Verify data persisted
- [ ] **Expected:** All data preserved correctly
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 13.3 Mission Roundtrip Test (Critical!)
- [ ] **Test:** If you have RC 2 and drone:
  1. Create waypoint mission on RC 2
  2. Import to PC using app
  3. Edit metadata in app
  4. Export back to RC 2
  5. **Verify mission still works on drone**
- [ ] **Expected:** Mission executes correctly on drone
- [ ] **Expected:** No data corruption
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

---

## 14. Final Checks

### 14.1 Status Bar Accuracy
- [ ] **Test:** Verify status bar always shows correct info:
  - Mission count matches actual missions
  - Backup folder path is correct
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

### 14.2 Close Application
- [ ] **Test:** Close app normally
- [ ] **Expected:** No error dialogs
- [ ] **Expected:** Window state saved
- [ ] **Expected:** No hanging processes in Task Manager
- **Result:** ☐ Pass  ☐ Fail  
- **Notes:**
  ```
  
  
  ```

---

## Test Summary

**Total Tests:** 100+  
**Passed:** _____  
**Failed:** _____  
**Pass Rate:** _____%

### Critical Issues Found
```







```

### Non-Critical Issues Found
```







```

### Recommendations
```







```

### Overall Assessment
☐ Ready for Release  
☐ Needs Minor Fixes  
☐ Needs Major Fixes  
☐ Not Ready

**Tester Signature:** _________________________  
**Date:** _________________________
