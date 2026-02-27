# Web UI Guide

## Overview

The Observational Memory Web UI provides a visual interface for managing and analyzing observations.

## Features

### 📊 Dashboard
- Real-time statistics (sessions, observations, tokens, embeddings)
- Recent sessions overview
- Quick metrics at a glance

### 📝 Sessions
- Browse all sessions with pagination
- Search sessions by ID
- View observation details
- Delete sessions

### 🔍 Semantic Search
- Search observations by meaning
- Adjustable similarity threshold
- Configurable result count
- Detailed result display

### 📈 Analytics
- Priority distribution (pie chart)
- Session timeline (line chart)
- Token usage by session (bar chart)
- Visual insights into memory patterns

## Installation

```bash
# Install dependencies
pip install streamlit plotly

# Or use requirements.txt
pip install -r requirements.txt
```

## Usage

### Start the Web UI

```bash
streamlit run app.py
```

The application will open in your default browser at http://localhost:8501.

### Navigation

Use the sidebar to navigate between pages:
- **Dashboard**: Overview and statistics
- **Sessions**: Browse and manage sessions
- **Search**: Semantic search interface
- **Analytics**: Visual analytics and charts

## Features in Detail

### Dashboard

The dashboard provides a quick overview:
- **Total Sessions**: Number of unique sessions
- **Total Observations**: Total observations across all sessions
- **Total Tokens**: Estimated token count
- **Vector Embeddings**: Number of indexed embeddings

Recent sessions table shows:
- Session ID
- Number of observations
- Token count
- Last updated timestamp

### Sessions Page

Browse and manage sessions:
- **Search**: Filter sessions by ID
- **Pagination**: Navigate through sessions (10 per page)
- **View Details**: Expand to see full observations
- **Delete**: Remove sessions and their embeddings

### Search Page

Semantic search interface:
- **Query Input**: Enter natural language query
- **Top K**: Number of results to return (1-20)
- **Min Similarity**: Threshold for filtering results (0.0-1.0)
- **Results**: Displays session ID, similarity score, and observation text

### Analytics Page

Visual analytics:
- **Priority Distribution**: Pie chart showing 🔴 High / 🟡 Medium / 🟢 Low distribution
- **Session Timeline**: Line chart of observations over time
- **Token Usage**: Bar chart of token usage by session (top 10)

## Configuration

### Port

Change the default port:

```bash
streamlit run app.py --server.port 8080
```

### Theme

Streamlit supports light and dark themes. Toggle in the settings menu (top right).

### Data Directory

The app uses the current working directory. To use a different directory:

```python
# In app.py, modify:
workspace_dir = Path("/path/to/your/workspace")
```

## API Integration

The Web UI uses the same managers as the Python API:
- ObservationalMemoryManager: For session management
- VectorSearchManager: For semantic search

You can extend the UI by adding new pages or features using these managers.

## Troubleshooting

### Port Already in Use

```bash
streamlit run app.py --server.port 8501
```

### No Data Displayed

Ensure observations exist in memory/observations/ directory.

### Search Not Working

Verify vector embeddings are indexed:

```python
from observational_memory_vector import VectorSearchManager
manager = VectorSearchManager(Path.cwd())
stats = manager.get_statistics()
print(stats)
```

## Development

### Adding New Pages

```python
# In app.py
elif page == "🆕 New Page":
    st.title("🆕 New Page")
    # Your code here
```

### Custom Visualizations

```python
import plotly.express as px

# Create custom chart
fig = px.scatter(df, x="x", y="y", title="Custom Chart")
st.plotly_chart(fig, use_container_width=True)
```

## Performance

- **Load Time**: < 2s for typical datasets
- **Search**: < 1s for 100+ embeddings
- **Rendering**: Optimized with Streamlit caching

## Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Search
![Search](docs/screenshots/search.png)

### Analytics
![Analytics](docs/screenshots/analytics.png)

## Future Enhancements

- [ ] Export sessions to CSV/JSON
- [ ] Batch operations (delete multiple sessions)
- [ ] Advanced filtering (date range, priority)
- [ ] Real-time updates (WebSocket)
- [ ] User authentication
- [ ] Multi-workspace support

## License

MIT License - see [LICENSE](../LICENSE) file for details.
