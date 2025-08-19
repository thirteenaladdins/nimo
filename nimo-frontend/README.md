# Nimo Frontend

A simple Svelte frontend for the Nimo plotter service. Upload an image URL and instantly see the plot-ready SVG output.

## Features

- Simple, clean interface
- Image URL input
- Real-time SVG generation
- Responsive design
- Built with Svelte and Vite

## Development

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

4. Preview production build:
   ```bash
   npm run preview
   ```

## Configuration

Update the API endpoint in `src/App.svelte` to point to your deployed plotter service:

```javascript
const api = "https://your-deployed-service.com/generate-svg"
```

## Usage

1. Enter an image URL in the input field
2. Click "Generate SVG" 
3. View the generated SVG output
4. The SVG is ready for plotting!

## Tech Stack

- **Svelte** - Reactive UI framework
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework (via CDN classes)
