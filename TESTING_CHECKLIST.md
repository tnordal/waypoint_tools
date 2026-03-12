# Export/Import Controller UUID Testing Checklist

## Prerequisites
- [ ] RC 2 controller connected via USB
- [ ] At least 2 waypoint missions already on the controller
- [ ] At least 1 local mission in the app

---

## Test 1: Basic Export Flow
- [ ] Open the app
- [ ] Click "Export to RC 2"
- [ ] Step 1: Select ONE local mission from the list
- [ ] Click "Next"
- [ ] Step 2: See list of controller missions to replace
- [ ] Select a controller mission to replace
- [ ] Click "Export"
- [ ] Confirm the confirmation dialog shows correct mission names
- [ ] Click "Yes" to confirm
- [ ] Verify success message appears
- [ ] Check mission list shows "✓ Exported" next to the exported mission

---

## Test 2: Export Replaces Controller Files
- [ ] After Test 1, check controller using DJI Pilot app
- [ ] Verify the replaced controller mission now contains the exported waypoints
- [ ] Verify no duplicate missions were created

---

## Test 3: No Controller Missions Error
- [ ] Delete ALL missions from RC 2 controller (using DJI Pilot)
- [ ] In app, click "Export to RC 2"
- [ ] Select a local mission
- [ ] Click "Next"
- [ ] Verify error message: "No waypoints on controller to replace"

---

## Test 4: Re-Export to Same Slot
- [ ] Re-add missions to controller if needed
- [ ] Export Mission A to controller slot 1
- [ ] Verify mission list shows "✓ Exported" for Mission A
- [ ] Export Mission B to controller slot 1 (same slot)
- [ ] Verify Mission A still shows "✓ Exported" (keeps history)
- [ ] Verify Mission B now shows "✓ Exported"

---

## Test 5: Export Indicator Persists
- [ ] Export a mission to controller
- [ ] Close the app completely
- [ ] Reopen the app
- [ ] Verify mission still shows "✓ Exported" indicator

---

## Test 6: Import New Mission from Controller
- [ ] Create a NEW mission on controller (not exported from app)
- [ ] In app, click "Import from RC 2"
- [ ] Verify new mission shows as "(new)"
- [ ] Check the mission checkbox
- [ ] Click "OK"
- [ ] Verify success message shows "New: 1"
- [ ] Verify mission appears in mission list

---

## Test 7: Import Previously Exported Mission (Update Behavior)
- [ ] Export Mission A from app to controller slot 1
- [ ] Note Mission A's UUID in the mission list
- [ ] Using DJI Pilot, modify Mission A on controller (add/remove waypoint)
- [ ] In app, click "Import from RC 2"
- [ ] Verify Mission A shows as "(already imported)"
- [ ] Check Mission A checkbox
- [ ] Click "OK"
- [ ] Verify success message shows "Updated: 1" (NOT "New: 1")
- [ ] Verify Mission A still has same UUID (not duplicated)
- [ ] Verify Mission A's waypoints were refreshed with controller changes
- [ ] Verify friendly name/tags/notes were preserved

---

## Test 8: Previously Exported Indicator in Export Dialog
- [ ] Export Mission A to controller slot 1
- [ ] Click "Export to RC 2" again
- [ ] Select a different mission
- [ ] Click "Next"
- [ ] Verify controller slot 1 shows "(Previously: Mission A)"

---

## Test 9: Multiple Missions Export/Import
- [ ] Export Mission A to controller slot 1
- [ ] Export Mission B to controller slot 2
- [ ] Both should show "✓ Exported"
- [ ] Import both missions from controller
- [ ] Verify both show "Updated: 2"
- [ ] Verify no duplicates created

---

## Test 10: Cancel Operations
- [ ] Click "Export to RC 2"
- [ ] Select a mission, click "Next"
- [ ] Click "Cancel" - verify dialog closes, no changes
- [ ] Click "Export to RC 2"
- [ ] Select mission, click "Next", select controller mission
- [ ] Click "Export" then "No" on confirmation - verify no changes
- [ ] Click "Import from RC 2"
- [ ] Click "Cancel" - verify dialog closes

---

## Results Summary

**Date:** _____________

**Passed:** ___ / 10

**Failed:** ___ / 10

**Notes:**
