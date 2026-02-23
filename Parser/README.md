# MCNP Data Parser (C Engine) 📊

**A high-performance, low-latency parsing engine designed to transform raw MCNP6 output into structured reports.**

---

## 🧬 Evolution & Heritage

This parser is the core data-processing engine of the **MCNP Automation Toolkit**. It is built upon the foundational logic and expertise developed in the [MCNP-Data-Toolkit](https://github.com/10809104/MCNP-Data-Toolkit).

While the original Toolkit focused on the fundamental parsing of MCNP output, this version has been optimized for:

* **Batch Processing**: Handling hundreds of directories simultaneously.
* **Smart Alignment**: Perfectly merging simulation results with source CSV templates.
* **Modern Integration**: Seamlessly working with the Python-based Runner/Orchestrator.

---

## ✨ Key Features

* **Lightning Fast Extraction**: Written in pure C to handle gigabyte-sized `.o` files with minimal memory overhead.
* **Automated Data Matching**: Scans Tally blocks and matches them with corresponding rows in your `source.csv` based on case names.
* **Batch Folder Scan**: Features a Windows-native folder selection UI for batch-processing multiple simulation runs.
* **Zero-Dependency Execution**: Pre-compiled `.exe` works out-of-the-box on Windows without any runtimes (Visual C++ Redistributable, etc.).

---

## 🚀 How to Run

### Option A: Direct Execution (Recommended)

Download the pre-compiled `MCNP_Parser.exe` from the [Releases](https://github.com/10809104/MCNP-Automation-Toolkit/releases) page.

1. Run `MCNP_Parser.exe`.
2. Select your `source.csv` (the template containing your model parameters).
3. Select the folders containing your `.o` files.
4. Click **Batch Process** and get your `Final_Report.csv`.

### Option B: Build from Source

If you wish to compile it yourself, use **MinGW** or any standard C compiler:

```bash
gcc -o MCNP_Parser.exe main.c -lcomdlg32 -lshell32 -lgdi32 -lwininet -lurlmon -lshlwapi

```

---

## 📋 Data Workflow Requirement

To ensure the parser works correctly, your `source.csv` should follow this structure:

| Column 1 (Case ID) | Column 2 (Parameters) | ... |
| --- | --- | --- |
| Model_A | 10.5 | ... |
| Model_B | 20.0 | ... |

The parser will look for `.o` files named `Model_A.o`, `Model_B.o`, etc., extract the Tally data, and append it to the right side of the corresponding row.

### 1. Environment Setup

Place `main.exe`, `merge.ps1`, and `source.csv` in the same directory.
Organize the simulation data files (`.o` files) into subfolders by category within that directory.

### 2. Launch and Version Check

Run `main.exe`.
The system will automatically connect to the internet to check for updates. If a new version is available, click **“Yes”**. The program will automatically update itself and restart.

### 3. One-Click Report Generation

Select the target folder in the interface, then click **“Batch Process”**.
After parsing is complete, the system will invoke PowerShell in the background to perform all Excel formatting tasks and generate the final report file: `MCNP_Total_Summary.xlsx`.


---

## 🛠 Technical Details

* **Tally Key**: The parser searches for the specific string `"   tally   "` (defined in `tools.h`) to locate data blocks.
* **Memory Management**: Uses `DynamicTable` structures to handle variable-length tally data and complex row/column counts.
* **UI**: Implements a lightweight Windows Win32 API for file and folder selection dialogs to keep the binary size small.

---

## 📜 License & Credits

* **Core Logic**: Derived from [MCNP-Data-Toolkit](https://github.com/10809104/MCNP-Data-Toolkit) by 10809104.
* **License**: MIT License.

> **Developer Note**: The C code is "battle-tested" in real nuclear engineering research environments. It prioritizes data integrity and speed over modern code aesthetics. Mixed language comments (Chinese/English) are present as a result of its organic development.