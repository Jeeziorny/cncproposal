# CNC Cutting Application - System Architecture

## Table of Contents
- [System Overview](#system-overview)
- [High-Level Architecture](#high-level-architecture)
- [Component Details](#component-details)
- [Communication Protocol](#communication-protocol)
- [Data Models](#data-models)
- [Security & Licensing](#security--licensing)
- [Deployment & Updates](#deployment--updates)
- [Development Considerations](#development-considerations)

## System Overview

The CNC Cutting Application is a desktop solution for importing DXF files, processing geometric data, and generating G-code instructions for CNC machines with endless blade capability. The application features a hybrid architecture combining Electron frontend for UI and Python backend for computational tasks.

### Core Functionality
- **File Processing**: Import/export DXF and G-code files
- **Geometric Manipulation**: Edit, transform, and validate 2D geometric shapes
- **Path Generation**: Create optimized cutting paths with blade rotation control
- **Simulation**: Real-time cutting simulation with configurable parameters
- **Project Management**: Save/load complete project states

### Target Users
- CNC machine operators
- Manufacturing engineers
- CAD/CAM professionals

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Electron Frontend                     │
├─────────────────┬───────────────────┬───────────────────┤
│   UI Components │   Canvas Renderer │  Simulation Module│
│   - File Manager│   - Geometry      │  - Real-time      │
│   - Toolbars    │   - Grid/Axes     │  - Controls       │
│   - Dialogs     │   - Selection     │  - Parameters     │
│   - Presets     │   - Measurements  │                   │
└─────────────────┴───────────────────┴───────────────────┘
                            │
                    ┌───────┴───────┐
                    │  IPC Protocol │ (JSON-based)
                    └───────┬───────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   Python Backend                        │
├─────────────────┬───────────────────┬───────────────────┤
│  File Processors│  Geometry Engine  │  G-code Generator │
│  - DXF Parser   │  - Validation     │  - Path Planning  │
│  - G-code I/O   │  - Transformations│  - Optimization   │
│  - Project I/O  │  - Calculations   │  - Blade Rotation │
└─────────────────┴───────────────────┴───────────────────┘
```

## Component Details

### 1. Electron Frontend

#### 1.1 Core Responsibilities
- **User Interface**: Multi-language support (English/Polish)
- **Canvas Rendering**: Real-time visualization of geometric data
- **User Interactions**: Selection, transformation, measurement tools
- **Light Computations**: Basic geometric operations (moves, selections)
- **Cutting Simulation**: Visual representation of machining process

#### 1.2 Key Modules

**UI Components**
- File management (import/export, recent files)
- Toolbar and menu system
- Property panels and dialogs
- Preset shape library with visual icons

**Canvas System**
- Zoom, pan, fit-to-screen functionality
- Grid and axis display with configurable spacing
- Selection and measurement tools
- Coordinate display and cursor tracking

**Simulation Module**
- Separate module for cutting simulation logic
- Configurable speed control (1-1000%)
- Playback controls (play, pause, stop, repeat)
- Real-time blade angle display
- CNC parameter visualization

### 2. Python Backend

#### 2.1 Core Responsibilities
- **Heavy Mathematical Computations**: Complex geometric algorithms
- **File Processing**: DXF parsing, G-code generation
- **Validation**: Geometric integrity checks
- **Path Optimization**: Cutting sequence and blade rotation planning

#### 2.2 Key Operations

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `import_dxf` | File path | Canvas State, Status, Metadata | Parse DXF file and extract geometry |
| `import_gcode` | File path | Canvas State, Status, Metadata | Import existing G-code project |
| `export_gcode` | Canvas, Metadata, Filename | Status | Generate optimized G-code |
| `validate` | Canvas, Metadata | Status, Validation Messages | Perform geometry validation |
| `propose_rotation_points` | Canvas State | CuttingPath with rotation points | Suggest optimal blade rotations |
| `save_project` | Project name, Canvas State | Status | Persist project state |
| `load_project` | Filename | Canvas State | Restore project state |

#### 2.3 Validation Rules
- DXF file grammatical correctness
- Single 2D figure constraint
- Closed figure requirement
- No intersecting lines
- No overlapping lines
- No redundant points

## Communication Protocol

### 3.1 Inter-Process Communication (IPC)
- **Transport**: Standard input/output (stdin/stdout)
- **Format**: JSON-based message protocol
- **Schema**: Defined in `protocol.json`,
- **Error Handling**: Structured error responses with codes

### 3.2 Request Structure
```json
{
  "id": "unique-request-id",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "operation": "operation_name",
  "params": {
    // Optional operation-specific parameters
  }
}
```

### 3.3 Response Structure
```json
{
  "correlated_request_id": "unique-request-id",
  "timestamp": "2024-01-01T12:00:00.000Z", 
  "status": "success|error",
  "data": {
    // Present on successful operations
  },
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {
      // Optional additional error context
    }
  }
}
```

**Key Protocol Features:**
- **Request ID Correlation**: Each request gets a unique ID that's returned in the response's `correlated_request_id` field
- **ISO 8601 Timestamps**: All timestamps use standard date-time format
- **Conditional Fields**: `params` is optional for requests; `data` and `error` are mutually exclusive based on status
- **Structured Error Codes**: Predefined error codes for consistent error handling
- **Schema Validation**: Full protocol validation defined in `protocol.json`

## Data Models

### 4.1 Core Entities
Data structures are fully defined in `definitions.json` with JSON Schema validation:

- **Point**: 2D coordinate (x, y)
- **Vertex**: Point with optional bulge for arc segments
- **Geometry Types**: LWPolyline, Line, Arc, Circle, Block
- **CuttingPath**: Sequence of geometries with blade rotation points
- **ProjectMetadata**: Project information and bounds

### 4.2 Canvas State
The canvas state represents the complete geometric model:
```json
{
  "geometries": [/* Array of geometry objects */],
  "cuttingPaths": [/* Array of cutting path definitions */],
  "metadata": {/* Project metadata */},
  "settings": {/* Display and machining settings */}
}
```

### 4.3 Preset Shapes
Block entities support parametric shape generation:
- Rectangle, Circle, Ellipse, Polygon
- Custom user-defined shapes
- Dicing patterns for material optimization.

