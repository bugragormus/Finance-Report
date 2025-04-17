# Financial Performance Analysis Dashboard

A comprehensive financial analysis dashboard built with Streamlit that provides detailed insights into financial performance metrics, trends, and comparative analysis.

## 🚀 Features

- **Interactive Dashboard**: User-friendly interface with real-time data visualization
- **Comprehensive Analysis**:
  - KPI Panels
  - Category Analysis
  - Comparative Analysis
  - Trend Analysis
  - Pivot Tables
  - Automated Insights
- **Data Processing**:
  - Excel file upload support
  - Advanced filtering capabilities
  - Data preview and validation
- **Reporting**:
  - PDF report generation
  - Customizable metrics
  - Warning system for negative values

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## 🔧 Installation

1. Clone the repository:

```bash
git clone [your-repository-url]
cd Finance-Report
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## 🎮 Usage

1. Start the application:

```bash
streamlit run main.py
```

2. Open your web browser and navigate to `http://localhost:8501`

3. Upload your Excel file (ZFMR0003 report format)

4. Use the sidebar to:

   - Apply filters
   - Select months for analysis
   - Configure visualization settings

5. Explore different analysis sections:

   - KPI Panel
   - Category Analysis
   - Comparative Analysis
   - Trend Analysis
   - Pivot Tables

6. Generate PDF reports as needed

## 📊 Data Format

The application expects Excel files in the ZFMR0003 report format. Ensure your data includes the following columns:

- Date/Time information
- Financial metrics
- Category information
- Transaction details

## 🛠️ Project Structure

```
Finance-Report/
├── main.py              # Main application file
├── config/              # Configuration files
├── utils/               # Utility functions
│   ├── loader.py        # Data loading utilities
│   ├── filters.py       # Data filtering functions
│   ├── metrics.py       # Metric calculations
│   ├── report.py        # PDF report generation
│   └── ...              # Other utility modules
├── assets/              # Static assets
└── requirements.txt     # Project dependencies
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

streamlit run main.py --theme.base="light" --theme.primaryColor="#6eb52f" --theme.backgroundColor="#f0f0f5" --theme.secondaryBackgroundColor="#e0e0ef" --theme.textColor="#262730" --theme.font="sans serif"

streamlit run main.py --server.port 8080 --theme.base="light" --theme.primaryColor="#6eb52f" --theme.backgroundColor="#f0f0f5" --theme.secondaryBackgroundColor="#e0e0ef" --theme.textColor="#262730" --theme.font="sans serif"
