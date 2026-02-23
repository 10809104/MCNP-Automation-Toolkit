# MCNP-Automation-Toolkit 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)]()
[![C Language](https://img.shields.io/badge/language-C-green.svg)]()
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()
[![Python Lint](https://github.com/10809104/MCNP-Automation-Toolkit/actions/workflows/python-lint.yml/badge.svg)](https://github.com/10809104/MCNP-Automation-Toolkit/actions/workflows/python-lint.yml)
[![C Build](https://github.com/10809104/MCNP-Automation-Toolkit/actions/workflows/c-build.yml/badge.svg)](https://github.com/10809104/MCNP-Automation-Toolkit/actions/workflows/c-build.yml)

**A high‑performance workflow suite for MCNP6 simulations, bridging the gap between resource‑aware task orchestration and lightning‑fast data post‑processing.**

---

## 🌐 Language / 語言選擇
- [**English Description**](./README.md)
- [**中文說明文件**](./讀我.md)

---

## 🌟 Why This Toolkit?

Running MCNP simulations often involves tedious manual work: babysitting system resources to avoid freezes, manually organizing piles of output files, and extracting tally data by hand. 

**MCNP-Automation-Toolkit** eliminates that drudgery with a dual‑engine approach:

- **The Orchestrator (Python)** – intelligently manages your hardware and schedules tasks so your PC stays responsive.
- **The Parser (C)** – extracts simulation results at blazing speed, turning messy `.o` files into clean spreadsheets.

Whether you're running a single case or a hundred, this toolkit lets you focus on science, not housekeeping.

---

## 📦 Core Components

| Component | Language | What it does |
|-----------|----------|--------------|
| [**Runner / Orchestrator**](./Runner/README.md) | Python | Monitors CPU/RAM, queues input files, launches MCNP instances, and provides a retro‑style dashboard while you wait. |
| [**Data Parser**](./Parser/README.md) | C | Scans gigabytes of `.o` files, aligns tally results with your `source.csv`, and produces consolidated reports in CSV format. |

Both tools can be used independently, or you can chain them together for a fully automated workflow.

---

## 🚀 Quick Start

### 1️⃣ Clone the repository
```bash
git clone https://github.com/10809104/MCNP-Automation-Toolkit.git
cd MCNP-Automation-Toolkit
```

### 2️⃣ Build the C Parser (optional – pre‑built executables are also available)
```bash
cd Parser
gcc -o MCNP_Parser.exe main.c -lcomdlg32 -lshell32 -lgdi32 -lwininet -lurlmon -lshlwapi
```
> **Note**: You can skip this step by downloading `MCNP_Parser.exe` from the [Releases](https://github.com/10809104/MCNP-Automation-Toolkit/releases) page.

### 3️⃣ Install Python dependencies (if running from source)
```bash
cd ../Runner
pip install -r requirements.txt   # only requires psutil
```

### 4️⃣ Run the full workflow
- **Option A (source)**: `python MCNP_Runner.py`
- **Option B (pre‑built)**: Download `MCNP_Runner.exe` from Releases and double‑click.

The GUI will guide you through selecting:
- Your MCNP environment batch file (e.g., `mcnp_630_env.bat`)
- The working directory containing your `model parameter`
- The specific input files to run
- CPU and RAM usage limits

**After all simulations finish, you can run `MCNP_Parser.exe`**

The GUI will guide you to:
- Click **HELP** to understand the required file structure and placement
- Select the source CSV files
- Choose the working directory containing your `.o` output files
- After processing completes, decide whether to merge the results into a single `.xlsx` file

---

## 📂 Project Structure

```
MCNP-Automation-Toolkit/
├── Runner/                     # Python source for the Orchestrator
│   ├── MCNP_Runner.py          # Main entry point
│   ├── requirements.txt        # Python dependencies
│   └── README.md               # Component‑specific docs
│
├── Parser/                      # C source for the Data Parser (flat structure for Dev‑C++)
│   ├── main.c                   # Main program (originally in src/)
│   ├── config.h                 # Configuration header
│   ├── tools.h                  # Core parsing functions
│   ├── merge.ps1                # PowerShell script for Excel integration
│   ├── MCNP_Parser.dev          # Dev-c++
│   ├── MCNP_Parser.ico          # Application icon (optional)
│   ├── MCNP_Parser.rc           # Application icon config
│   ├── version.txt              # for auto update
│   └── README.md                # Component‑specific docs
│
├── Examples/                     # Result screenshots and sample outputs
│   ├── runner_demo.png
│   ├── parser_demo.png
│   └── sample_report.csv
│
└── README.md                      # This file
```

> **Note for Dev‑C++ users**: All C source files are kept in the same directory (`Parser/`) for easy opening with Dev‑C++ projects. Simply open `main.c` and compile.

---

## 🖼️ Examples

### Runner in Action
![Runner Demo](./Examples/runner_demo.png)
*The retro‑style dashboard showing active tasks and resource usage*

### Parser Output
![Parser Demo](./Examples/parser_demo.png)
*Clean, aligned CSV output ready for analysis*

---

## 📜 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

> **Developer's Note**: This toolkit was born from real nuclear engineering research. You may encounter mixed Chinese/English comments in the source – a mark of its "battle‑tested" origins.

---
About ``` Parser/ ```You can get more from[MCNP-Data-Toolkit](https://github.com/10809104/MCNP-Data-Toolkit/)

**Now go automate your MCNP workflow!**  
*Made with ❤️ by KikKoh*
