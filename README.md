# ASL Methods Sections Parameter Generator

A comprehensive solution for extracting and generating Arterial Spin Labeling (ASL) parameters for scientific method sections. This project includes a Python package, web application, and API service.

## Project Overview

The ASL Methods Sections Parameter Generator is designed to streamline the process of extracting and formatting ASL parameters for use in scientific publications. It provides multiple interfaces to accommodate different workflows:

- **Python Package** (`pyaslreport`): Core library for ASL parameter processing
- **Web Application**: Modern React/Next.js frontend for interactive parameter generation
- **API Service**: FastAPI backend for programmatic access

## Components

### 1. Python Package (`pyaslreport`)

The core library that handles ASL parameter extraction, validation, and report generation.

**Features:**
- Comprehensive ASL parameter validation
- M0 data analysis and processing
- TSV file processing for volume types and timing
- Error detection and reporting
- Extensible architecture for new modalities

**Installation:**
```bash
cd package
pip install -e .
```

**Quick Start:**
```python
from pyaslreport import generate_report

data = {
    "modality": "asl",
    "files": ["asl.json", "m0scan.json", "data.tsv"],
    "nifti_file": "asl.nii",
    "dcm_files": ["dicom1.dcm", "dicom2.dcm"]  # Optional
}

result = generate_report(data)
```

### 2. Web Application

A modern, responsive web interface built with Next.js, React, and Tailwind CSS.

**Features:**
- Interactive report generation
- Dark/light theme support
- Mobile-responsive design

**Setup:**
```bash
cd apps/frontend
npm install
npm run dev
```

**Technologies:**
- Next.js 15.3.3
- React 19
- TypeScript
- Tailwind CSS
- Radix UI components
- Shadcn/ui

### 3. API Service

FastAPI backend service providing RESTful endpoints for ASL parameter processing.

**Features:**
- RESTful API endpoints
- CORS support
- Comprehensive error handling
- JSON response formatting

**Setup:**
```bash
cd apps/backend
pip install -r requirements.txt
fastapi dev
```

**Technologies:**
- FastAPI
- Python 3.7+
- Pydantic for data validation

## 📁 Project Structure

```
ASL Generator/
├── package/                 # Python package (pyaslreport)
│   ├── src/pyaslreport/    # Core package source
│   │   ├── pyproject.toml      # Package configuration
│   │   └── README.md          # Package documentation
│   ├── apps/
│   │   ├── frontend/          # Next.js web application
│   │   │   ├── src/           # React components and pages
│   │   │   ├── package.json   # Frontend dependencies
│   │   │   └── next.config.ts # Next.js configuration
│   │   └── backend/           # FastAPI backend service
│   │       ├── app/           # API source code
│   │       └── requirements.txt # Backend dependencies
│   └── docs/                  # Project documentation
```

## Supported Modalities

### ASL (Arterial Spin Labeling)

- **Parameter Validation**: ASL-specific parameters (labeling duration, post-labeling delay, etc.)
- **M0 Data Analysis**: M0 reference scan processing
- **TSV File Processing**: Volume types and timing information
- **Error Detection**: Major errors, minor errors, and warnings

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](package/LICENSE) file for details.

## 👥 Authors

- **Ibrahim Abdelazim** - [ibrahim.abdelazim@fau.de](mailto:ibrahim.abdelazim@fau.de)
- **Hanliang Xu** - [hxu110@jh.edu](mailto:hxu110@jh.edu)

## 🏢 Organization

This project is part of **The ISMRM Open Science Initiative for Perfusion Imaging**.

### Supervisors
- Jan Petr
- David Thomas