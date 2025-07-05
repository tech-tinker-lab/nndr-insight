# NNDR Insight Frontend

A modern, responsive web application for exploring and analyzing UK geospatial data and Non-Domestic Rates (NNDR) information. Built with React, TypeScript, and Tailwind CSS.

## 🚀 Features Overview

### Core Functionality
- **Interactive Dashboard** - Real-time statistics and data overview
- **Property Search & Analysis** - Comprehensive NNDR property database
- **Geospatial Data Exploration** - UK postcodes, UPRNs, and place names
- **Advanced Analytics** - Regional coverage and density analysis
- **Interactive Maps** - Visual geospatial data representation
- **Data Upload & Management** - Bulk data ingestion capabilities
- **User Settings & Preferences** - Customizable interface

## 📊 Functional Areas

### 1. Dashboard
**Purpose**: Central hub providing overview of all data and system status

**Features**:
- Real-time statistics cards (Properties, Postcodes, Places, LADs)
- Regional coverage visualization with interactive charts
- Data growth trends over time
- Recent activity feed
- Quick action buttons for common tasks

**User Guide**:
- View overall system health and data statistics
- Monitor data ingestion progress
- Access quick actions for common workflows
- Track regional data coverage

### 2. Properties
**Purpose**: Search and explore NNDR (Non-Domestic Rates) property data

**Features**:
- Advanced property search by address, postcode, or description
- Grid and list view modes
- Detailed property information modal
- Filtering by region, property type, and value ranges
- Export capabilities

**User Guide**:
1. **Search Properties**: Use the search bar to find properties by address, postcode, or description
2. **View Details**: Click the eye icon or "View Details" button to see comprehensive property information
3. **Filter Results**: Use the filter panel to narrow down results by region, property type, or value ranges
4. **Switch Views**: Toggle between grid and list view using the view mode button
5. **Export Data**: Use the export button in property details to download property information

**Data Displayed**:
- BA Reference (Business Rates reference)
- Property description and address
- Rateable value and financial information
- Administrative area and locality
- Effective dates and category codes

### 3. Analytics
**Purpose**: Data analysis and insights across all datasets

**Features**:
- Regional coverage analysis
- Property density mapping
- Postcode distribution analysis
- Interactive charts and visualizations
- Comparative statistics

**User Guide**:
1. **Coverage Analysis**: View data coverage by UK regions
2. **Density Analysis**: Analyze property density across different areas
3. **Regional Statistics**: Compare statistics between regions
4. **Postcode Analysis**: Explore postcode distribution patterns

### 4. Maps
**Purpose**: Visual representation of geospatial data

**Features**:
- Interactive map interface
- Property location visualization
- Spatial query capabilities
- Boundary overlays
- Custom map layers

**User Guide**:
1. **Navigate Map**: Use mouse to pan and zoom
2. **Search Locations**: Enter postcodes or addresses to find locations
3. **View Properties**: Click on map markers to see property details
4. **Spatial Queries**: Draw areas to find properties within specific boundaries
5. **Toggle Layers**: Switch between different data layers (properties, boundaries, etc.)

### 5. Upload
**Purpose**: Data ingestion and management

**Features**:
- File upload interface
- Progress tracking
- Data validation
- Batch processing
- Error handling and reporting

**User Guide**:
1. **Select Files**: Choose CSV or other supported file formats
2. **Configure Settings**: Set data type and processing options
3. **Monitor Progress**: Track upload and processing status
4. **Review Results**: Check for errors and successful imports
5. **Manage Data**: View and manage uploaded datasets

### 6. Settings
**Purpose**: User preferences and system configuration

**Features**:
- User profile management
- Interface customization
- Data preferences
- System configuration
- Export settings

## 🎯 What We've Achieved

### Technical Achievements
- **Modern React Architecture**: Built with functional components, hooks, and modern React patterns
- **Responsive Design**: Fully responsive interface that works on desktop, tablet, and mobile
- **Real-time Data**: Live data integration with backend APIs
- **Interactive Visualizations**: Charts and graphs using Recharts library
- **Type Safety**: TypeScript implementation for better code quality
- **Performance Optimization**: Efficient rendering and data loading

### User Experience Achievements
- **Intuitive Navigation**: Clear, logical navigation structure
- **Fast Search**: Real-time property search with instant results
- **Rich Data Display**: Comprehensive property information with detailed modals
- **Visual Feedback**: Loading states, error handling, and success notifications
- **Accessibility**: Keyboard navigation and screen reader support

### Data Integration Achievements
- **Multi-Dataset Support**: Integration with UPRN, postcodes, place names, and NNDR data
- **Spatial Data**: Geospatial data visualization and querying
- **Real-time Statistics**: Live dashboard with current data metrics
- **Export Capabilities**: Data export in multiple formats

## 🚀 What We Can Achieve

### Short-term Enhancements (1-3 months)
1. **Enhanced Map Features**:
   - Leaflet/Mapbox integration for better map performance
   - Custom map layers and overlays
   - Heat maps for property density
   - Clustering for large datasets
   - Drawing tools for spatial queries

2. **Advanced Analytics**:
   - Predictive analytics for property values
   - Trend analysis and forecasting
   - Comparative analysis tools
   - Custom report generation

3. **User Management**:
   - User authentication and authorization
   - Role-based access control
   - User preferences and saved searches
   - Collaborative features

### Medium-term Goals (3-6 months)
1. **Advanced Visualization**:
   - 3D building visualization
   - Time-series data visualization
   - Interactive dashboards with drag-and-drop
   - Custom chart creation tools

2. **Mobile Application**:
   - React Native mobile app
   - Offline data access
   - GPS-based property search
   - Field data collection

3. **API Integration**:
   - Integration with external property APIs
   - Real-time market data
   - Planning permission data
   - Environmental data overlays

### Long-term Vision (6+ months)
1. **AI-Powered Features**:
   - Property value prediction using machine learning
   - Automated data quality checks
   - Intelligent search suggestions
   - Anomaly detection in property data

2. **Enterprise Features**:
   - Multi-tenant architecture
   - Advanced reporting and analytics
   - Integration with business systems
   - Custom branding and white-labeling

3. **Advanced Geospatial**:
   - 3D city modeling
   - Virtual reality property tours
   - Augmented reality property viewing
   - Real-time sensor data integration

## 🗺️ Visual Maps Implementation

### Current Map Capabilities
- Basic map interface with property markers
- Postcode and address search
- Property detail popups
- Basic spatial querying

### Planned Map Enhancements

#### 1. Interactive Map Layers
```javascript
// Example implementation structure
const mapLayers = {
  properties: {
    type: 'marker',
    data: propertiesData,
    style: { color: '#3B82F6', size: 8 }
  },
  boundaries: {
    type: 'polygon',
    data: ladBoundaries,
    style: { fillColor: '#10B981', opacity: 0.3 }
  },
  heatmap: {
    type: 'heatmap',
    data: propertyDensity,
    style: { radius: 25, blur: 15 }
  }
};
```

#### 2. Advanced Spatial Queries
- **Radius Search**: Find properties within a specified distance
- **Polygon Selection**: Draw custom areas for property search
- **Buffer Analysis**: Create buffer zones around features
- **Intersection Analysis**: Find properties intersecting with boundaries

#### 3. Real-time Data Visualization
- **Live Updates**: Real-time property data updates
- **Traffic Flow**: Movement and activity patterns
- **Environmental Data**: Air quality, noise levels, etc.
- **Market Trends**: Property value changes over time

#### 4. 3D Visualization
- **Building Heights**: 3D building models
- **Terrain Mapping**: Elevation and topography
- **Underground Infrastructure**: Utilities and services
- **Future Development**: Proposed building projects

### Map Technology Stack
- **Leaflet.js**: Open-source mapping library
- **Mapbox GL JS**: Advanced vector mapping
- **Turf.js**: Geospatial analysis library
- **D3.js**: Data visualization for custom overlays

### Map Features Roadmap
1. **Phase 1**: Basic interactive maps with property markers
2. **Phase 2**: Advanced spatial queries and filtering
3. **Phase 3**: Real-time data and live updates
4. **Phase 4**: 3D visualization and AR integration

## 🛠️ Technical Stack

### Frontend Technologies
- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type-safe JavaScript development
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **Recharts**: Data visualization library
- **Lucide React**: Icon library
- **React Hot Toast**: Notification system

### Development Tools
- **Vite**: Fast build tool and development server
- **ESLint**: Code linting and quality
- **Prettier**: Code formatting
- **Husky**: Git hooks for code quality

## 📱 Responsive Design

The application is fully responsive and optimized for:
- **Desktop**: Full-featured interface with sidebar navigation
- **Tablet**: Adaptive layout with touch-friendly controls
- **Mobile**: Mobile-first design with collapsible navigation

## 🔧 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running (see backend README)

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
npm run dev
```

### Build
```bash
npm run build
```

### Testing
```bash
npm run test
```

## 🎨 Design System

### Color Palette
- **Primary**: Blue (#3B82F6)
- **Success**: Green (#10B981)
- **Warning**: Yellow (#F59E0B)
- **Error**: Red (#EF4444)
- **Neutral**: Gray scale (#F9FAFB to #111827)

### Typography
- **Headings**: Inter font family
- **Body**: System font stack
- **Monospace**: For data and code

### Components
- Consistent button styles and interactions
- Modal dialogs for detailed information
- Card layouts for data presentation
- Form elements with validation

## 🔮 Future Roadmap

### Phase 1: Enhanced Maps (Q1 2024)
- [ ] Leaflet/Mapbox integration
- [ ] Custom map layers
- [ ] Spatial query tools
- [ ] Heat map visualization

### Phase 2: Advanced Analytics (Q2 2024)
- [ ] Predictive analytics
- [ ] Custom reporting
- [ ] Data export enhancements
- [ ] User management

### Phase 3: Mobile & AI (Q3 2024)
- [ ] Mobile application
- [ ] AI-powered features
- [ ] Real-time data
- [ ] 3D visualization

### Phase 4: Enterprise Features (Q4 2024)
- [ ] Multi-tenant support
- [ ] Advanced integrations
- [ ] Custom branding
- [ ] API marketplace

## 🎯 Key Achievements

### Completed Features
✅ **Responsive Layout**: Sidebar and main content properly aligned
✅ **Property Search**: Real-time search with NNDR data integration
✅ **Dashboard Analytics**: Live statistics and data visualization
✅ **Data Integration**: Backend API connectivity working
✅ **Error Handling**: Proper 404 and 500 error resolution
✅ **User Interface**: Modern, intuitive design with Tailwind CSS

### Technical Milestones
✅ **React 18**: Modern React patterns and hooks
✅ **TypeScript**: Type-safe development environment
✅ **API Integration**: Seamless backend communication
✅ **Performance**: Optimized rendering and data loading
✅ **Accessibility**: Keyboard navigation and screen reader support

## 🚀 Next Steps

### Immediate Priorities
1. **Map Implementation**: Integrate Leaflet.js for interactive maps
2. **Data Visualization**: Add more charts and analytics
3. **User Authentication**: Implement login and user management
4. **Mobile Optimization**: Enhance mobile experience

### Short-term Goals
1. **Enhanced Search**: Advanced filtering and sorting
2. **Export Features**: Data export in multiple formats
3. **Real-time Updates**: Live data synchronization
4. **Performance**: Further optimization and caching

### Long-term Vision
1. **AI Integration**: Machine learning for property insights
2. **3D Visualization**: Advanced geospatial rendering
3. **Mobile App**: React Native mobile application
4. **Enterprise Features**: Multi-tenant and advanced reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Contact the development team

---

**NNDR Insight Frontend** - Transforming UK geospatial data into actionable insights. 