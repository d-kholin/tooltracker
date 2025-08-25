# Tool Tracker

A modern web application for tracking tools and equipment lending. Built with Flask, React, and a clean, consistent design system.

## Features

- **Tool Management**: Add, edit, and track tools with descriptions, values, and images
- **Lending System**: Lend tools to people and track returns
- **People Management**: Maintain a database of people who borrow tools
- **Reporting**: View current loans and lending history
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## UI/UX Improvements

### Design System
- **Consistent Color Palette**: Uses a cohesive blue-based color scheme with proper contrast
- **Typography**: Inter font family for excellent readability
- **Spacing**: Consistent spacing using Tailwind CSS spacing scale
- **Shadows & Borders**: Subtle shadows and borders for depth and hierarchy

### Navigation
- **Single Navigation**: Removed redundant bottom navigation, keeping only the top header
- **Mobile-First**: Responsive navigation with mobile menu toggle
- **Clear Hierarchy**: Logical grouping of navigation items

### Forms & Controls
- **Consistent Styling**: All forms use the same design patterns
- **Better Labels**: Clear, descriptive labels with required field indicators
- **Visual Feedback**: Hover states, focus rings, and loading states
- **Error Handling**: Clear error messages and validation feedback

### Cards & Tables
- **Enhanced Tool Cards**: Rich information display with status indicators
- **Interactive Elements**: Hover effects and smooth transitions
- **Status Badges**: Color-coded status indicators for tool availability
- **Action Buttons**: Consistent button styling with icons

### User Experience
- **Loading States**: Spinner animations for better perceived performance
- **Empty States**: Helpful messages when no data is available
- **Confirmation Dialogs**: Safety confirmations for destructive actions
- **Success Feedback**: Visual confirmation for completed actions

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: React with Tailwind CSS
- **Styling**: Custom CSS with Tailwind utilities
- **Icons**: Heroicons (SVG)
- **Fonts**: Inter (Google Fonts)

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your browser to `http://localhost:5000`

## File Structure

```
tooltracker/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles and design system
│   ├── js/
│   │   ├── app.js        # Main React application
│   │   └── lend.js       # Lending functionality
│   └── images/           # Tool images
└── templates/
    ├── base.html         # Base template with navigation
    ├── index.html        # Main tools page
    ├── add_tool.html     # Add tool form
    ├── edit_tool.html    # Edit tool form
    ├── people.html       # People management
    ├── edit_person.html  # Edit person form
    ├── lend_tool.html    # Lend tool form
    └── report.html       # Lending report
```

## Design Principles

1. **Consistency**: All UI elements follow the same design patterns
2. **Accessibility**: Proper contrast ratios and focus indicators
3. **Responsiveness**: Mobile-first design approach
4. **Performance**: Optimized loading and smooth interactions
5. **Usability**: Clear visual hierarchy and intuitive navigation

## Contributing

When contributing to the UI/UX:

1. Follow the established design system
2. Use consistent spacing and typography
3. Ensure responsive behavior on all screen sizes
4. Maintain accessibility standards
5. Test interactions and user flows

## License

This project is open source and available under the MIT License.
