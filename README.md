# Tool Tracker

A modern web application for tracking tools and equipment lending. Built with Flask, React, and a clean, consistent design system.

![Homepage Screenshot](pub/homepage.png)

## Features

- **Tool Management**: Add, edit, and track tools with descriptions, values, and images
- **Lending System**: Lend tools to people and track returns
- **People Management**: Maintain a database of people who borrow tools
- **Reporting**: View current loans and lending history
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: React with Tailwind CSS
- **Styling**: Custom CSS with Tailwind utilities
- **Icons**: Heroicons (SVG)
- **Fonts**: Inter (Google Fonts)
- **Database**: SQLite
- **Containerization**: Docker with GitHub Container Registry (GHCR)

## Getting Started

### Option 1: Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd tooltracker
   ```

2. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   Open your browser to `http://localhost:5000`

### Option 2: Direct Docker

1. **Pull the pre-built image:**
   ```bash
   docker pull ghcr.io/d-kholin/tooltracker/tooltracker:latest
   ```

2. **Run the container:**
   ```bash
   docker run -d -p 5000:5000 -v tooltracker_data:/app ghcr.io/d-kholin/tooltracker/tooltracker:latest
   ```

## File Structure

```
tooltracker/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── .dockerignore         # Docker build exclusions
├── .github/
│   └── workflows/
│       └── docker-publish.yml  # GitHub Actions CI/CD
├── docs/
│   └── UX_UI_Improvements.md   # Design documentation
├── frontend/
│   └── components/       # React components
│       ├── BottomNav.jsx
│       ├── QuickAddTask.jsx
│       └── TaskCard.jsx
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles and design system
│   ├── js/
│   │   ├── app.js        # Main React application
│   │   └── lend.js       # Lending functionality
│   └── images/           # Tool images (persisted in volumes)
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

## Docker Volumes and Data Persistence

The application uses Docker volumes to ensure data persistence across container restarts and deployments:

### Volume Structure
```
tooltracker_data:/app    # Main application data
├── tooltracker.db       # SQLite database
├── static/images/       # Uploaded tool images
└── logs/                # Application logs (if generated)
```

### Data Persistence Features
- **SQLite Database**: All tool, people, and loan data is stored persistently
- **Uploaded Images**: Tool images are preserved across deployments
- **Automatic Creation**: Volumes are created automatically on first run
- **CI/CD Ready**: Works seamlessly in production environments

### Volume Management Commands

```bash
# View volume information
docker volume ls | grep tooltracker

# Inspect volume details
docker volume inspect tooltracker_tooltracker_data

# Backup volume data
docker run --rm -v tooltracker_tooltracker_data:/data -v $(pwd):/backup alpine tar czf /backup/tooltracker_data_backup.tar.gz -C /data .

# Restore volume data
docker run --rm -v tooltracker_tooltracker_data:/data -v $(pwd):/backup alpine tar xzf /backup/tooltracker_data_backup.tar.gz -C /data

# Remove volumes (WARNING: This will delete all data)
docker-compose down -v
```

## CI/CD and Deployment

### GitHub Actions Workflow
The repository includes an automated CI/CD pipeline that:
- Builds Docker images on push to main/master branches
- Publishes to GitHub Container Registry (GHCR)
- Automatically tags images with semantic versions
- Supports both development and production deployments

### Image Tags
- `latest` - Most recent build from main/master
- `v1.0.0` - Semantic version tags
- `main-abc1234` - Branch-specific builds with commit SHA

### Production Deployment
```bash
# Pull latest production image
docker pull ghcr.io/d-kholin/tooltracker/tooltracker:latest

# Run with persistent volumes
docker run -d -p 5000:5000 -v tooltracker_data:/app ghcr.io/d-kholin/tooltracker/tooltracker:latest
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
