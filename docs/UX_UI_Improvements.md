# UX/UI Improvement Plan

## 1. Prioritized UX/UI Changes
1. **Quick Add Task on Landing Page** – always-visible input bar with autofocus to reduce steps.
2. **Mobile-first Layout** – sticky bottom navigation, single-column card list, no horizontal scroll.
3. **Joyful Visual Design** – brand blue `#1565C0`, rounded corners, Inter font, subtle shadows.
4. **Task List Enhancements** – search/filter bar, swipe gestures, progress badges.
5. **Accessibility & Feedback** – focus states, ARIA labels, toast confirmations with undo.

## 2. Visual Mockups / Sketches
```
Mobile Home
┌──────────────────────────────────────────┐
│ Quick Add… [______________][Add]        │ ← Fixed at top
├──────────────────────────────────────────┤
│ Today                                    │
│ ┌ TaskCard ─────────────┐               │
│ │ • Drill bits           │ [Due today]  │
│ └────────────────────────┘              │
│ ┌ TaskCard ─────────────┐              │
│ │ • Hammer               │ [Due 3d]     │
│ └────────────────────────┘              │
└──────────────────────────────────────────┘
Bottom Nav: [Tools] [Tasks] [+] [People] [Report]
```

## 3. Implementation Plan
1. Configure Tailwind and import Inter font. Set brand color `#1565C0`.
2. Implement `QuickAddTask`, `TaskCard`, and `BottomNav` React components.
3. Replace table views with card layout and integrate sticky bottom navigation.
4. Add micro-interactions (hover/press states, slide-in confirmations).
5. Test across common mobile/desktop browsers.

## 4. Acceptance Criteria
- Users can add a task on mobile with a single input and tap; new task appears instantly.
- UI uses Inter font, brand blue for primary actions, and rounded corners.
- Bottom navigation stays fixed with buttons ≥44px and provides clear active state.
- Layout reflows to single column with no horizontal overflow on screens ≤375px.
- Toast notifications provide feedback with undo option for destructive actions.
