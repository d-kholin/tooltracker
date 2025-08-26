# Tool Tracker

A modern web application for tracking tools and equipment lending. Built with Flask, React, and a clean, consistent design system.

![Homepage Screenshot](pub/homepage.png)
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

### Option 1: Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd tooltracker
   ```

2. **Run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   Open your browser to `http://localhost:5000`

**Note**: Data is automatically stored in Docker volumes (`tooltracker_data` and `tooltracker_static`) for persistence across container restarts.

### Option 2: Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open your browser to `http://localhost:5000`**

## Docker Commands

### Start the application:
```bash
docker-compose up
```

### Start in background:
```bash
docker-compose up -d
```

### Stop the application:
```bash
docker-compose down
```

### View logs:
```bash
docker-compose logs -f
```

### Rebuild and restart:
```bash
docker-compose up --build
```

### Manage volumes:
```bash
# List volumes
docker volume ls

# Inspect volume details
docker volume inspect tooltracker_tooltracker_data

# Backup volume data
docker run --rm -v tooltracker_tooltracker_data:/data -v $(pwd):/backup alpine tar czf /backup/tooltracker_data_backup.tar.gz -C /data .

# Restore volume data
docker run --rm -v tooltracker_tooltracker_data:/data -v $(pwd):/backup alpine tar xzf /backup/tooltracker_data_backup.tar.gz -C /data

# Remove volumes (WARNING: This will delete all data)
docker-compose down -v
```

## File Structure

```
tooltracker/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── .dockerignore         # Docker build exclusions
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles and design system
│   ├── js/
│   │   ├── app.js        # Main React application
│   │   └── lend.js       # Lending functionality
│   └── images/           # Tool images (development only)
└── templates/
    ├── base.html         # Base template with navigation
    ├── index.html        # Main tools page
    ├── add_tool.html     # Add tool form
    ├── edit_tool.html    # Edit tool form
    ├── people.html       # People management
    ├── edit_person.html  # Edit person form
    ├── lend_tool.html    # Lend tool form
    └── report.html       # Lending report

# Docker Volumes (created automatically)
tooltracker_tooltracker_data/    # SQLite database and uploaded images
tooltracker_tooltracker_static/  # Static files in production
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
