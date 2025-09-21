# PLC Mentor - Technical Implementation Details

## Architecture Overview
- **Framework**: Flask 2.3.3 web application
- **Purpose**: Educational PLC code analysis for junior engineers
- **Target**: GX Works2 (.gxw) file analysis and CODESYS conversion

## Core Modules

### 1. GXW Parser (`app/parser/gxw_parser.py`)
- **Function**: Parses Mitsubishi GX Works2 project files
- **Formats**: ZIP and binary GXW file support
- **Features**: Educational example data fallback, device extraction, ladder rung parsing
- **Key Methods**:
  - `parse(file_path)`: Main parsing entry point
  - `_parse_zip_format()`: ZIP-based GXW handling
  - `_get_example_data()`: Educational example generation

### 2. CODESYS Converter (`app/converter/codesys_converter.py`)
- **Function**: Converts ladder logic to CODESYS ST and LD formats
- **Features**: Educational comments, safety guidelines, option-based conversion
- **Key Methods**:
  - `convert()`: Basic conversion
  - `convert_with_options()`: Advanced conversion with customization
  - `_convert_to_structured_text()`: ST code generation
  - `_convert_to_ladder_diagram()`: LD code generation

### 3. PLC Educator (`app/educator/plc_educator.py`)
- **Function**: Provides educational explanations and tutorials
- **Features**: Korean language support, step-by-step guidance, safety focus
- **Content**: Device explanations, instruction tutorials, safety guidelines

### 4. Ladder Visualizer (`app/visualizer/ladder_visualizer.py`)
- **Function**: Visual representation of ladder logic
- **Formats**: ASCII, HTML, SVG output
- **Features**: Complexity analysis, educational annotations
- **Key Methods**:
  - `visualize_ladder()`: Multi-format visualization
  - `analyze_ladder_complexity()`: Complexity metrics

## Web Interface

### Templates Structure
- **base.html**: Common layout with Bootstrap 5.1.3 and Font Awesome 6.0.0
- **index.html**: Landing page with feature overview
- **analyze.html**: File upload and analysis interface
- **learn.html**: Educational tutorials and content
- **convert.html**: CODESYS conversion interface

### JavaScript Implementation
- **File Selection**: Real-time feedback with `handleFileSelection()`
- **Upload Progress**: Visual indicators during processing
- **Result Display**: Dynamic content rendering with error handling
- **User Experience**: Clear state management and status indicators

## Flask Routes
```python
@app.route('/')                    # Landing page
@app.route('/upload', methods=['POST'])  # File upload and analysis
@app.route('/analyze')             # Analysis interface
@app.route('/learn')               # Educational content
@app.route('/convert')             # Conversion interface
@app.route('/convert', methods=['POST']) # Conversion processing
@app.route('/api/examples')        # Example files API
@app.route('/favicon.ico')         # Favicon handling
```

## Configuration
- **Upload Folder**: `uploads/` directory
- **File Size Limit**: 16MB maximum
- **Supported Formats**: .gxw, .gx2, .gx3
- **Development Server**: 0.0.0.0:5000 with debug mode

## Dependencies
```
Flask==2.3.3
Werkzeug==2.3.7
zipfile36==0.1.3
chardet==5.2.0
requests==2.32.5  # Added for testing
```

## Key Features Implementation

### Educational Focus
- Korean language explanations throughout
- Step-by-step instruction breakdown
- Safety-first approach with warnings
- Beginner-friendly device descriptions

### Error Handling
- Comprehensive file validation
- Graceful fallback to example data
- Clear error messages for users
- JavaScript error prevention

### File Processing Workflow
1. File upload validation (size, format)
2. GXW parsing with format detection
3. Educational explanation generation
4. Ladder visualization creation
5. CODESYS conversion with options
6. Results presentation with download option

## Resolved Issues
- **HTML Rendering**: Fixed escape character issues in templates
- **JavaScript Errors**: Complete rewrite with proper function definitions
- **CDN Dependencies**: Corrected Bootstrap and Font Awesome links
- **File Selection UX**: Added clear status indicators
- **Browser Compatibility**: Removed template literal syntax issues

## Testing Validation
- All HTTP endpoints return 200 status
- File upload workflow fully functional
- JavaScript console error-free
- Multi-format conversion working
- Educational content properly displayed

## Performance Considerations
- Minimal dependencies for fast startup
- Efficient file processing with fallback examples
- Client-side validation to reduce server load
- Progressive enhancement for better UX